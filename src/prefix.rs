//! Exact next-token prediction from a probabilistic grammar in binary form
//! (Jelinek and Lafferty 1991): the probability of each next word is a
//! ratio of prefix probabilities, computed one column at a time as the
//! sentence is read.
//!
//! Notation. inside(i, k, B): B derives exactly words i..k. pre(i, j, A): A
//! derives a string that begins with words i..j. q(C): a derivation from C
//! finishes. The left-corner closure R(A, D) sums every chain of left
//! children from A down to D, each right sibling C on the way weighted by
//! q(C), since it may derive anything:
//!
//!   pre(i, i+1, A) = Σ_B R(A, B) P(B → w_i)
//!   pre(i, j, A)   = Σ_{D → B C} R(A, D) P(D → B C) Σ_k inside(i, k, B) pre(k, j, C)
//!
//! The prefix w_0..w_j has probability pre(0, j, S); the empty prefix q(S).
//! The sentence ends after it with probability inside(0, j, S).

use crate::subst::Subst;
use qsystems::lm::END;
use std::collections::{BTreeMap, HashMap};

pub struct Prefix<'a> {
    pub g: &'a Subst,
    pub q: HashMap<u32, f64>,
    /// R(A, B) by B: the categories A whose left corner can reach B.
    corner: HashMap<u32, Vec<(u32, f64)>>,
    /// For D → B C: every (A, R(A, D) P(D → B C)), by (B, C).
    by_pair: HashMap<(u32, u32), Vec<(u32, f64)>>,
}

/// Where a reading stands after some words: the inside chart of the words
/// so far, and every completed column of prefix probabilities.
pub struct Reading {
    pub words: Vec<u32>,
    inside: Vec<Vec<HashMap<u32, f64>>>,
    /// pre[j][i]: categories → pre(i, j + 1, ·), for each word j read.
    pre: Vec<Vec<HashMap<u32, f64>>>,
    /// The probability of the prefix read so far.
    pub prob: f64,
}

impl<'a> Prefix<'a> {
    pub fn new(g: &'a Subst) -> Prefix<'a> {
        let q = g.termination_all();
        let cats: Vec<u32> = {
            let mut c: Vec<u32> = g.rules.keys().copied().collect();
            c.sort();
            c
        };
        let index: HashMap<u32, usize> = cats.iter().enumerate().map(|(i, &c)| (c, i)).collect();
        let n = cats.len();
        // The left-corner step: P_L(A, B) = Σ_C P(A → B C) q(C).
        let mut step: Vec<Vec<(usize, f64)>> = vec![Vec::new(); n];
        for (&a, rs) in &g.rules {
            let mut row: HashMap<usize, f64> = HashMap::new();
            for (rhs, p) in rs {
                if let crate::subst::Rhs::Pair(b, c) = rhs {
                    *row.entry(index[b]).or_insert(0.0) += p * q.get(c).copied().unwrap_or(0.0);
                }
            }
            step[index[&a]] = row.into_iter().collect();
        }
        // R = I + P_L R, iterated (dense: the grammars here have at most a
        // few thousand categories).
        let mut r = vec![vec![0.0f64; n]; n];
        for (i, row) in r.iter_mut().enumerate() {
            row[i] = 1.0;
        }
        for _ in 0..10_000 {
            let mut next = vec![vec![0.0f64; n]; n];
            let mut change: f64 = 0.0;
            for a in 0..n {
                next[a][a] = 1.0;
                for &(d, p) in &step[a] {
                    let (src, dst) = (&r[d], &mut next[a]);
                    for (x, y) in dst.iter_mut().zip(src) {
                        *x += p * y;
                    }
                }
                for (x, y) in next[a].iter().zip(&r[a]) {
                    change = change.max((x - y).abs());
                }
            }
            r = next;
            if change < 1e-13 {
                break;
            }
        }
        let mut corner: HashMap<u32, Vec<(u32, f64)>> = HashMap::new();
        for (a, row) in r.iter().enumerate() {
            for (b, &v) in row.iter().enumerate() {
                if v > 1e-300 {
                    corner.entry(cats[b]).or_default().push((cats[a], v));
                }
            }
        }
        let mut by_pair: HashMap<(u32, u32), Vec<(u32, f64)>> = HashMap::new();
        for (&d, rs) in &g.rules {
            for (rhs, p) in rs {
                if let crate::subst::Rhs::Pair(b, c) = rhs {
                    if let Some(as_) = corner.get(&d) {
                        let e = by_pair.entry((*b, *c)).or_default();
                        for &(a, v) in as_ {
                            e.push((a, v * p));
                        }
                    }
                }
            }
        }
        // Merge duplicates (A, ·) for the same pair.
        for list in by_pair.values_mut() {
            let mut m: BTreeMap<u32, f64> = BTreeMap::new();
            for &(a, v) in list.iter() {
                *m.entry(a).or_insert(0.0) += v;
            }
            *list = m.into_iter().collect();
        }
        Prefix { g, q, corner, by_pair }
    }

    pub fn start(&self) -> Reading {
        Reading {
            words: Vec::new(),
            inside: vec![vec![HashMap::new()]],
            pre: Vec::new(),
            prob: self.q.get(&self.g.start).copied().unwrap_or(0.0),
        }
    }

    /// The column pre(i, j + 1, ·) for every i ≤ j, if word w came next.
    fn column(&self, r: &Reading, w: u32) -> Vec<HashMap<u32, f64>> {
        let j = r.words.len();
        let mut col: Vec<HashMap<u32, f64>> = vec![HashMap::new(); j + 1];
        if let Some(lex) = self.g.lexical.get(&w) {
            for &(b, p) in lex {
                if let Some(as_) = self.corner.get(&b) {
                    for &(a, v) in as_ {
                        *col[j].entry(a).or_insert(0.0) += v * p;
                    }
                }
            }
        }
        for i in (0..j).rev() {
            let mut cell: HashMap<u32, f64> = HashMap::new();
            for k in i + 1..=j {
                for (&b, &ib) in &r.inside[i][k] {
                    for (&c, &pc) in &col[k] {
                        if let Some(as_) = self.by_pair.get(&(b, c)) {
                            for &(a, v) in as_ {
                                *cell.entry(a).or_insert(0.0) += v * ib * pc;
                            }
                        }
                    }
                }
            }
            col[i] = cell;
        }
        col
    }

    /// The probability of each next word and of END, not normalised: they
    /// sum to the probability of the prefix, `r.prob`, when the grammar
    /// terminates.
    pub fn next(&self, r: &Reading) -> BTreeMap<String, f64> {
        let mut out = BTreeMap::new();
        let j = r.words.len();
        if j > 0 {
            out.insert(END.to_string(), r.inside[0][j].get(&self.g.start).copied().unwrap_or(0.0));
        }
        for (w, &id) in &self.g.words {
            let col = self.column(r, id);
            out.insert(w.clone(), col[0].get(&self.g.start).copied().unwrap_or(0.0));
        }
        out
    }

    /// Read one more word.
    pub fn step(&self, r: &mut Reading, w: u32) {
        let col = self.column(r, w);
        r.prob = col[0].get(&self.g.start).copied().unwrap_or(0.0);
        r.pre.push(col);
        r.words.push(w);
        // Extend the inside chart with spans ending at the new word.
        let j = r.words.len();
        for row in r.inside.iter_mut() {
            row.push(HashMap::new());
        }
        r.inside.push(vec![HashMap::new(); j + 1]);
        if let Some(lex) = self.g.lexical.get(&w) {
            for &(a, p) in lex {
                *r.inside[j - 1][j].entry(a).or_insert(0.0) += p;
            }
        }
        for i in (0..j.saturating_sub(1)).rev() {
            let mut cell: HashMap<u32, f64> = HashMap::new();
            for k in i + 1..j {
                for (&b, &pb) in &r.inside[i][k] {
                    for (&c, &pc) in &r.inside[k][j] {
                        if let Some(as_) = self.g.binary.get(&(b, c)) {
                            for &(a, p) in as_ {
                                *cell.entry(a).or_insert(0.0) += p * pb * pc;
                            }
                        }
                    }
                }
            }
            r.inside[i][j] = cell;
        }
    }
}
