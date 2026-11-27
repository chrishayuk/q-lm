//! A graph learned from sentences by merging states (k-tails, Biermann and
//! Feldman 1972), made probabilistic by counting.
//!
//! 1. The sentences make a prefix tree: a state for every prefix seen, an
//!    arrow for every word that follows it, counted.
//! 2. Two states are merged when the same continuations of at most `k`
//!    words (END included) can follow them. Merging is the learning: states
//!    that agree on their near future are taken to be the same state, so
//!    paths seen after one become possible after the other.
//! 3. The probability of a word from a set of states is its share of the
//!    counts leaving them. The merged graph may be nondeterministic, so a
//!    prefix is followed to a weighted set of states, as in QSYS-E16.
//!
//! A word with no arrow from any reachable state has probability zero; the
//! report mixes in a small uniform floor so that bits stay finite, and also
//! counts how many sentences are given more than the floor.

use qsystems::lm::END;
use std::collections::{BTreeMap, BTreeSet, HashMap};

pub struct KTails {
    pub k: usize,
    /// For each state: next token → (state, count).
    arrows: Vec<BTreeMap<String, BTreeMap<usize, u64>>>,
    /// For each state: total count leaving it (END included).
    totals: Vec<u64>,
    pub start: usize,
}

impl KTails {
    pub fn train(sentences: &[Vec<String>], k: usize) -> KTails {
        // The prefix tree: node 0 is the empty prefix.
        let mut children: Vec<BTreeMap<String, usize>> = vec![BTreeMap::new()];
        let mut counts: Vec<BTreeMap<String, u64>> = vec![BTreeMap::new()];
        for s in sentences {
            let mut v = 0;
            for w in s.iter().map(String::as_str).chain(std::iter::once(END)) {
                *counts[v].entry(w.to_string()).or_insert(0) += 1;
                if w == END {
                    break;
                }
                v = match children[v].get(w) {
                    Some(&c) => c,
                    None => {
                        children.push(BTreeMap::new());
                        counts.push(BTreeMap::new());
                        let c = children.len() - 1;
                        children[v].insert(w.to_string(), c);
                        c
                    }
                };
            }
        }
        // The k-tails of each node, bottom up: tails(v, j) is the set of
        // continuations of at most j words, ending in END where the sentence
        // ends within them.
        let n = children.len();
        let mut tails: Vec<BTreeSet<Vec<String>>> = vec![BTreeSet::new(); n];
        for _ in 0..k {
            let prev = tails.clone();
            for v in 0..n {
                let mut t = BTreeSet::new();
                if counts[v].contains_key(END) {
                    t.insert(vec![END.to_string()]);
                }
                for (w, &c) in &children[v] {
                    if prev[c].is_empty() {
                        t.insert(vec![w.clone()]);
                    }
                    for tail in &prev[c] {
                        let mut x = vec![w.clone()];
                        x.extend(tail.iter().cloned());
                        t.insert(x);
                    }
                }
                tails[v] = t;
            }
        }
        // Merge nodes with equal tails into one state.
        let mut class: HashMap<&BTreeSet<Vec<String>>, usize> = HashMap::new();
        let mut state = vec![0usize; n];
        for v in 0..n {
            let next = class.len();
            state[v] = *class.entry(&tails[v]).or_insert(next);
        }
        let m = class.len();
        let mut arrows: Vec<BTreeMap<String, BTreeMap<usize, u64>>> = vec![BTreeMap::new(); m];
        let mut totals = vec![0u64; m];
        for v in 0..n {
            for (w, &c) in &counts[v] {
                totals[state[v]] += c;
                let to = if w == END {
                    usize::MAX
                } else {
                    state[children[v][w]]
                };
                *arrows[state[v]]
                    .entry(w.clone())
                    .or_default()
                    .entry(to)
                    .or_insert(0) += c;
            }
        }
        KTails {
            k,
            arrows,
            totals,
            start: state[0],
        }
    }

    pub fn states(&self) -> usize {
        self.arrows.len()
    }

    pub fn size(&self) -> usize {
        self.arrows
            .iter()
            .map(|a| a.values().map(|t| t.len()).sum::<usize>())
            .sum()
    }

    /// The weighted states after a prefix (weights sum to the probability of
    /// the prefix under the automaton).
    pub fn after(&self, prefix: &[String]) -> BTreeMap<usize, f64> {
        let mut st = BTreeMap::from([(self.start, 1.0)]);
        for w in prefix {
            let mut next = BTreeMap::new();
            for (&s, &p) in &st {
                if let Some(to) = self.arrows[s].get(w) {
                    for (&t, &c) in to {
                        if t != usize::MAX {
                            *next.entry(t).or_insert(0.0) += p * c as f64 / self.totals[s] as f64;
                        }
                    }
                }
            }
            st = next;
        }
        st
    }

    /// Whether any state is reached by the prefix.
    pub fn reachable(&self, prefix: &[String]) -> bool {
        !self.after(prefix).is_empty()
    }

    /// P(token | prefix), zero where no arrow carries it.
    pub fn p(&self, prefix: &[String], w: &str) -> f64 {
        let st = self.after(prefix);
        let z: f64 = st.values().sum();
        if z == 0.0 {
            return 0.0;
        }
        let mut p = 0.0;
        for (&s, &q) in &st {
            if let Some(to) = self.arrows[s].get(w) {
                p += q * to.values().sum::<u64>() as f64 / self.totals[s] as f64;
            }
        }
        p / z
    }

    pub fn sample(&self, rng: &mut qsystems::lm::Rng, max: usize) -> Vec<String> {
        let mut s = self.start;
        let mut words = Vec::new();
        while words.len() < max {
            let mut r = ((rng.draw() as f64) / (1u64 << 53) as f64) * self.totals[s] as f64;
            let mut pick = None;
            'outer: for (w, to) in &self.arrows[s] {
                for (&t, &c) in to {
                    if r < c as f64 {
                        pick = Some((w.clone(), t));
                        break 'outer;
                    }
                    r -= c as f64;
                }
            }
            match pick {
                Some((w, t)) if t != usize::MAX => {
                    words.push(w);
                    s = t;
                }
                _ => break,
            }
        }
        words
    }
}
