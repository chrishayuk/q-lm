//! A grammar learned by substitutability (Clark and Eyraud 2007), given
//! sentences only.
//!
//! 1. Every substring of every training sentence is a candidate phrase, and
//!    each occurrence has a context: the words before it and after it, to
//!    the ends of the sentence.
//! 2. Two substrings that occur in the same context are taken to be
//!    interchangeable everywhere. Grouping by this (union-find) gives the
//!    categories. A category may hold single words, longer phrases, or both;
//!    a category holding a word and a phrase containing a member of the same
//!    category is recursive.
//! 3. Rules: a category `[w]` rewrites to `[u] [v]` for every split of every
//!    member `w = u v`, and to the word `a` for every one-word member. Rule
//!    probabilities are relative frequencies, each rule counted once per
//!    occurrence of the member that gives it.
//! 4. A sentence's probability is the inside probability of the start
//!    category: every way the rules derive it, summed.
//!
//! Nothing about the generating grammar is given: not its categories, not
//! its rules, not its trees.

use std::collections::HashMap;

#[derive(Clone)]
pub struct Subst {
    pub words: HashMap<String, u32>,
    pub word_list: Vec<String>,
    /// Category of each word (where a one-word member exists).
    pub lexical: HashMap<u32, Vec<(u32, f64)>>, // word → [(category, P(cat → word))]
    /// Binary rules by right-hand side: (B, C) → [(A, P(A → B C))].
    pub binary: HashMap<(u32, u32), Vec<(u32, f64)>>,
    /// For sampling: each category's rules, with probabilities.
    pub rules: HashMap<u32, Vec<(Rhs, f64)>>,
    pub start: u32,
    pub categories: usize,
    /// Members of each category, for inspection (up to a few each).
    pub examples: HashMap<u32, Vec<String>>,
    pub member_count: HashMap<u32, usize>,
    /// Expected count of each rule (lhs, b, c, lexical) on the training
    /// sentences, from the last E-step of `em`.
    pub expected: HashMap<(u32, u32, u32, bool), f64>,
}

#[derive(Clone, Debug)]
pub enum Rhs {
    Word(u32),
    Pair(u32, u32),
}

fn find(p: &mut [u32], mut x: u32) -> u32 {
    while p[x as usize] != x {
        p[x as usize] = p[p[x as usize] as usize];
        x = p[x as usize];
    }
    x
}

impl Subst {
    pub fn train(sentences: &[Vec<String>], vocab: &[String]) -> Subst {
        let mut words: HashMap<String, u32> = HashMap::new();
        for w in vocab {
            let n = words.len() as u32;
            words.entry(w.clone()).or_insert(n);
        }
        let enc: Vec<Vec<u32>> = sentences
            .iter()
            .map(|s| s.iter().map(|w| words[w]).collect())
            .collect();
        // Distinct substrings, and how often each occurs.
        let mut ids: HashMap<&[u32], u32> = HashMap::new();
        let mut occurrences: Vec<u64> = Vec::new();
        let mut strings: Vec<&[u32]> = Vec::new();
        let mut parent: Vec<u32> = Vec::new();
        // Context → the first substring seen in it.
        let mut by_context: HashMap<(&[u32], &[u32]), u32> = HashMap::new();
        for s in &enc {
            for i in 0..s.len() {
                for j in i + 1..=s.len() {
                    let w = &s[i..j];
                    let id = *ids.entry(w).or_insert_with(|| {
                        strings.push(w);
                        occurrences.push(0);
                        parent.push(parent.len() as u32);
                        (strings.len() - 1) as u32
                    });
                    occurrences[id as usize] += 1;
                    match by_context.get(&(&s[..i], &s[j..])) {
                        Some(&other) => {
                            let (a, b) = (find(&mut parent, id), find(&mut parent, other));
                            if a != b {
                                parent[a as usize] = b;
                            }
                        }
                        None => {
                            by_context.insert((&s[..i], &s[j..]), id);
                        }
                    }
                }
            }
        }
        drop(by_context);
        // Number the categories.
        let mut cat_of: HashMap<u32, u32> = HashMap::new();
        let mut cat = vec![0u32; strings.len()];
        for id in 0..strings.len() {
            let r = find(&mut parent, id as u32);
            let n = cat_of.len() as u32;
            cat[id] = *cat_of.entry(r).or_insert(n);
        }
        // Rule counts.
        let mut counts: HashMap<u32, HashMap<(u32, u32, bool), f64>> = HashMap::new();
        let mut examples: HashMap<u32, Vec<String>> = HashMap::new();
        let mut member_count: HashMap<u32, usize> = HashMap::new();
        let word_list: Vec<String> = {
            let mut v = vec![String::new(); words.len()];
            for (w, &i) in &words {
                v[i as usize] = w.clone();
            }
            v
        };
        for (id, w) in strings.iter().enumerate() {
            let a = cat[id];
            let c = occurrences[id] as f64;
            *member_count.entry(a).or_insert(0) += 1;
            let ex = examples.entry(a).or_default();
            if ex.len() < 6 {
                ex.push(
                    w.iter()
                        .map(|&t| word_list[t as usize].as_str())
                        .collect::<Vec<_>>()
                        .join(" "),
                );
            }
            let rules = counts.entry(a).or_default();
            if w.len() == 1 {
                *rules.entry((w[0], 0, true)).or_insert(0.0) += c;
            } else {
                for k in 1..w.len() {
                    let (b, d) = (cat[ids[&w[..k]] as usize], cat[ids[&w[k..]] as usize]);
                    *rules.entry((b, d, false)).or_insert(0.0) += c;
                }
            }
        }
        let start = cat[ids[enc[0].as_slice()] as usize];
        let mut lexical: HashMap<u32, Vec<(u32, f64)>> = HashMap::new();
        let mut binary: HashMap<(u32, u32), Vec<(u32, f64)>> = HashMap::new();
        let mut rules: HashMap<u32, Vec<(Rhs, f64)>> = HashMap::new();
        for (a, rs) in &counts {
            let total: f64 = rs.values().sum();
            for (&(b, c, lex), &n) in rs {
                let p = n / total;
                if lex {
                    lexical.entry(b).or_default().push((*a, p));
                    rules.entry(*a).or_default().push((Rhs::Word(b), p));
                } else {
                    binary.entry((b, c)).or_default().push((*a, p));
                    rules.entry(*a).or_default().push((Rhs::Pair(b, c), p));
                }
            }
        }
        // A fixed order (most probable first, then by right-hand side), so
        // that sampling repeats.
        let key = |r: &Rhs| match r {
            Rhs::Word(w) => (0, *w, 0),
            Rhs::Pair(b, c) => (1, *b, *c),
        };
        for rs in rules.values_mut() {
            rs.sort_by(|x, y| {
                y.1.partial_cmp(&x.1)
                    .unwrap()
                    .then(key(&x.0).cmp(&key(&y.0)))
            });
        }
        Subst {
            words,
            word_list,
            lexical,
            binary,
            rules,
            start,
            categories: cat_of.len(),
            examples,
            member_count,
            expected: HashMap::new(),
        }
    }

    /// Re-estimate the rule probabilities by inside–outside (EM) on the
    /// training sentences, `iters` times. Every rule keeps a small count
    /// (`smooth`) so that rules no training sentence uses stay possible.
    /// Returns the training log-likelihood (bits) before each iteration.
    pub fn em(&mut self, sentences: &[Vec<String>], iters: usize, smooth: f64) -> Vec<f64> {
        let mut history = Vec::new();
        for _ in 0..iters {
            let mut counts: HashMap<(u32, u32, u32, bool), f64> = HashMap::new();
            let mut ll = 0.0;
            for s in sentences {
                let Some(ws): Option<Vec<u32>> =
                    s.iter().map(|w| self.words.get(w).copied()).collect()
                else {
                    continue;
                };
                let chart = self.inside(&ws);
                let n = ws.len();
                let z = chart[0][n].get(&self.start).copied().unwrap_or(0.0);
                if z <= 0.0 {
                    continue;
                }
                ll += z.log2();
                let mut out: Vec<Vec<HashMap<u32, f64>>> = vec![vec![HashMap::new(); n + 1]; n + 1];
                out[0][n].insert(self.start, 1.0);
                for len in (2..=n).rev() {
                    for i in 0..=n - len {
                        let j = i + len;
                        if out[i][j].is_empty() {
                            continue;
                        }
                        let outer = out[i][j].clone();
                        for k in i + 1..j {
                            let (left, right) = (chart[i][k].clone(), &chart[k][j]);
                            for (&b, &pb) in &left {
                                for (&c, &pc) in right {
                                    if let Some(as_) = self.binary.get(&(b, c)) {
                                        for &(a, p) in as_ {
                                            if let Some(&oa) = outer.get(&a) {
                                                *counts.entry((a, b, c, false)).or_insert(0.0) +=
                                                    oa * p * pb * pc / z;
                                                *out[i][k].entry(b).or_insert(0.0) += oa * p * pc;
                                                *out[k][j].entry(c).or_insert(0.0) += oa * p * pb;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                for i in 0..n {
                    if let Some(cs) = self.lexical.get(&ws[i]) {
                        for &(a, p) in cs {
                            if let Some(&oa) = out[i][i + 1].get(&a) {
                                *counts.entry((a, ws[i], 0, true)).or_insert(0.0) += oa * p / z;
                            }
                        }
                    }
                }
            }
            history.push(ll);
            self.expected = counts.clone();
            // M-step: every existing rule, its expected count plus the smoothing.
            let mut by_lhs: HashMap<u32, Vec<(Rhs, f64)>> = HashMap::new();
            for (&a, rs) in &self.rules {
                for (rhs, _) in rs {
                    let key = match rhs {
                        Rhs::Word(w) => (a, *w, 0, true),
                        Rhs::Pair(b, c) => (a, *b, *c, false),
                    };
                    by_lhs.entry(a).or_default().push((
                        rhs.clone(),
                        counts.get(&key).copied().unwrap_or(0.0) + smooth,
                    ));
                }
            }
            self.set_rules(by_lhs);
        }
        history
    }

    fn set_rules(&mut self, by_lhs: HashMap<u32, Vec<(Rhs, f64)>>) {
        self.lexical.clear();
        self.binary.clear();
        self.rules.clear();
        let key = |r: &Rhs| match r {
            Rhs::Word(w) => (0, *w, 0),
            Rhs::Pair(b, c) => (1, *b, *c),
        };
        for (a, rs) in by_lhs {
            let total: f64 = rs.iter().map(|r| r.1).sum();
            let mut list: Vec<(Rhs, f64)> = rs.into_iter().map(|(r, c)| (r, c / total)).collect();
            list.sort_by(|x, y| {
                y.1.partial_cmp(&x.1)
                    .unwrap()
                    .then(key(&x.0).cmp(&key(&y.0)))
            });
            for (rhs, p) in &list {
                match rhs {
                    Rhs::Word(w) => self.lexical.entry(*w).or_default().push((a, *p)),
                    Rhs::Pair(b, c) => self.binary.entry((*b, *c)).or_default().push((a, *p)),
                }
            }
            self.rules.insert(a, list);
        }
    }

    /// Remove every rule whose expected count (from the last E-step) is below
    /// `tau`, then every category that can no longer finish a derivation or
    /// be reached from the start, and the rules that mention them. The
    /// remaining rules of each category are renormalised. Uses no sentence
    /// beyond those the counts came from.
    pub fn prune(&mut self, tau: f64) {
        let keep = |a: u32, rhs: &Rhs, e: &HashMap<(u32, u32, u32, bool), f64>| {
            let key = match rhs {
                Rhs::Word(w) => (a, *w, 0, true),
                Rhs::Pair(b, c) => (a, *b, *c, false),
            };
            e.get(&key).copied().unwrap_or(0.0) >= tau
        };
        let mut by_lhs: HashMap<u32, Vec<(Rhs, f64)>> = HashMap::new();
        for (&a, rs) in &self.rules {
            let kept: Vec<(Rhs, f64)> = rs.iter().filter(|(r, _)| keep(a, r, &self.expected)).cloned().collect();
            if !kept.is_empty() {
                by_lhs.insert(a, kept);
            }
        }
        // Productive: has a derivation that finishes.
        let mut productive: std::collections::HashSet<u32> = std::collections::HashSet::new();
        loop {
            let before = productive.len();
            for (&a, rs) in &by_lhs {
                if !productive.contains(&a)
                    && rs.iter().any(|(r, _)| match r {
                        Rhs::Word(_) => true,
                        Rhs::Pair(b, c) => productive.contains(b) && productive.contains(c),
                    })
                {
                    productive.insert(a);
                }
            }
            if productive.len() == before {
                break;
            }
        }
        for rs in by_lhs.values_mut() {
            rs.retain(|(r, _)| match r {
                Rhs::Word(_) => true,
                Rhs::Pair(b, c) => productive.contains(b) && productive.contains(c),
            });
        }
        by_lhs.retain(|a, rs| productive.contains(a) && !rs.is_empty());
        // Reachable from the start.
        let mut reach = std::collections::HashSet::from([self.start]);
        let mut todo = vec![self.start];
        while let Some(a) = todo.pop() {
            for (r, _) in by_lhs.get(&a).into_iter().flatten() {
                if let Rhs::Pair(b, c) = r {
                    for x in [*b, *c] {
                        if reach.insert(x) {
                            todo.push(x);
                        }
                    }
                }
            }
        }
        by_lhs.retain(|a, _| reach.contains(a));
        self.categories = by_lhs.len();
        self.set_rules(by_lhs);
    }

    /// Two-part description length, in bits: the grammar, then the training
    /// sentences given the grammar.
    /// - Each category: its number of rules (Elias gamma). Each rule: one bit
    ///   for its kind, then two categories (2 log2 C) or a word (log2 V),
    ///   then its probability at (1/2) log2 N bits, N the training tokens.
    /// - Each sentence: -log2 of 0.999 P(s) + 0.001 (1/(V+1))^(len+1), the
    ///   same floor as the development scores, so that a sentence the
    ///   grammar cannot derive costs a uniform spelling, not infinity.
    ///
    /// Returns (grammar bits, data bits, training sentences not derivable).
    pub fn description_length(&self, sentences: &[Vec<String>]) -> (f64, f64, usize) {
        let c = self.categories.max(2) as f64;
        let v = self.words.len() as f64;
        let n_tokens: f64 = sentences.iter().map(|s| s.len() as f64 + 1.0).sum();
        let gamma = |n: usize| 2.0 * (n as f64).log2().floor() + 1.0;
        let mut g = 0.0;
        for rs in self.rules.values() {
            g += gamma(rs.len());
            for (r, _) in rs {
                g += 1.0 + 0.5 * n_tokens.log2();
                g += match r {
                    Rhs::Word(_) => v.log2(),
                    Rhs::Pair(_, _) => 2.0 * c.log2(),
                };
            }
        }
        let (mut d, mut missing) = (0.0, 0);
        for s in sentences {
            let p = self.probability(s);
            missing += (p == 0.0) as usize;
            let floor = (1.0 / (v + 1.0)).powi(s.len() as i32 + 1);
            d -= (0.999 * p + 0.001 * floor).log2();
        }
        (g, d, missing)
    }

    /// The inside chart of a sentence (as word ids): chart[i][j] maps a
    /// category to the probability that it derives words i..j.
    pub fn inside(&self, ws: &[u32]) -> Vec<Vec<HashMap<u32, f64>>> {
        let n = ws.len();
        let mut chart: Vec<Vec<HashMap<u32, f64>>> = vec![vec![HashMap::new(); n + 1]; n + 1];
        for i in 0..n {
            if let Some(cs) = self.lexical.get(&ws[i]) {
                for &(a, p) in cs {
                    *chart[i][i + 1].entry(a).or_insert(0.0) += p;
                }
            }
        }
        for len in 2..=n {
            for i in 0..=n - len {
                let j = i + len;
                let mut cell: HashMap<u32, f64> = HashMap::new();
                for k in i + 1..j {
                    for (&b, &pb) in &chart[i][k] {
                        for (&c, &pc) in &chart[k][j] {
                            if let Some(as_) = self.binary.get(&(b, c)) {
                                for &(a, p) in as_ {
                                    *cell.entry(a).or_insert(0.0) += p * pb * pc;
                                }
                            }
                        }
                    }
                }
                chart[i][j] = cell;
            }
        }
        chart
    }

    /// The probability that a derivation from the start category finishes:
    /// the least fixed point of q(A) = Σ P(A → rhs) · Π q(children), with
    /// q(word) = 1, found by iterating from 0.
    pub fn termination(&self) -> f64 {
        self.termination_all()[&self.start]
    }

    /// The probability that a derivation from each category finishes.
    pub fn termination_all(&self) -> HashMap<u32, f64> {
        let mut q: HashMap<u32, f64> = self.rules.keys().map(|&a| (a, 0.0)).collect();
        for _ in 0..10_000 {
            let mut change: f64 = 0.0;
            let next: HashMap<u32, f64> = self
                .rules
                .iter()
                .map(|(&a, rs)| {
                    let v: f64 = rs
                        .iter()
                        .map(|(rhs, p)| match rhs {
                            Rhs::Word(_) => *p,
                            Rhs::Pair(b, c) => p * q[b] * q[c],
                        })
                        .sum();
                    change = change.max((v - q[&a]).abs());
                    (a, v)
                })
                .collect();
            q = next;
            if change < 1e-12 {
                break;
            }
        }
        q
    }

    pub fn word_id(&self, w: &str) -> Option<u32> {
        self.words.get(w).copied()
    }

    pub fn size(&self) -> usize {
        self.rules.values().map(|r| r.len()).sum()
    }

    /// The inside probability of a sentence: 0 if the grammar cannot derive
    /// it.
    pub fn probability(&self, s: &[String]) -> f64 {
        let n = s.len();
        if n == 0 {
            return 0.0;
        }
        let Some(ws): Option<Vec<u32>> = s.iter().map(|w| self.words.get(w).copied()).collect()
        else {
            return 0.0;
        };
        let chart = self.inside(&ws);
        chart[0][n].get(&self.start).copied().unwrap_or(0.0)
    }

    /// A sentence derived from the start category, or None if the
    /// derivation passes `max` words.
    pub fn sample(&self, rng: &mut qsystems::lm::Rng, max: usize) -> Option<Vec<String>> {
        let mut stack = vec![Rhs::Pair(self.start, u32::MAX)];
        let mut out = Vec::new();
        let mut steps = 0;
        while let Some(x) = stack.pop() {
            steps += 1;
            if steps > 50 * max || out.len() > max {
                return None;
            }
            match x {
                Rhs::Word(w) => out.push(self.word_list[w as usize].clone()),
                Rhs::Pair(a, u32::MAX) | Rhs::Pair(u32::MAX, a) => {
                    let rs = self.rules.get(&a)?;
                    let mut r = (rng.draw() as f64) / (1u64 << 53) as f64;
                    let mut pick = &rs[rs.len() - 1].0;
                    for (rhs, p) in rs {
                        if r < *p {
                            pick = rhs;
                            break;
                        }
                        r -= p;
                    }
                    match pick {
                        Rhs::Word(w) => stack.push(Rhs::Word(*w)),
                        Rhs::Pair(b, c) => {
                            stack.push(Rhs::Pair(*c, u32::MAX));
                            stack.push(Rhs::Pair(*b, u32::MAX));
                        }
                    }
                }
                Rhs::Pair(_, _) => unreachable!(),
            }
        }
        Some(out)
    }
}
