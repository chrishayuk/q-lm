//! Interpolated Kneser–Ney n-gram models (Kneser and Ney 1995; the
//! interpolated form of Chen and Goodman 1998), with one absolute discount.
//! The baseline a learner of sentences has to beat.

use qsystems::lm::END;
use std::collections::{BTreeSet, HashMap};

pub const START: &str = "<S>";

type Counts = HashMap<Vec<String>, HashMap<String, u64>>;

pub struct KneserNey {
    pub order: usize,
    pub discount: f64,
    /// For each order k (index k - 1): context of k - 1 tokens → next token →
    /// count. The highest order counts occurrences; lower orders count the
    /// distinct tokens seen before the k-gram (continuation counts).
    counts: Vec<Counts>,
    /// For each order and context: (total, number of distinct next tokens).
    totals: Vec<HashMap<Vec<String>, (u64, u64)>>,
    pub vocab: Vec<String>,
}

fn padded(s: &[String], order: usize) -> Vec<String> {
    let mut v = vec![START.to_string(); order - 1];
    v.extend(s.iter().cloned());
    v.push(END.into());
    v
}

impl KneserNey {
    /// `vocab`: every token the model may predict (END included); words of it
    /// never seen in training get probability only through the uniform floor.
    pub fn train(sentences: &[Vec<String>], vocab: &[String], order: usize, discount: f64) -> KneserNey {
        let mut top: Counts = HashMap::new();
        let mut vocab: BTreeSet<String> = vocab.iter().cloned().collect();
        vocab.insert(END.into());
        for s in sentences {
            let v = padded(s, order);
            for i in order - 1..v.len() {
                vocab.insert(v[i].clone());
                *top.entry(v[i + 1 - order..i].to_vec()).or_default().entry(v[i].clone()).or_insert(0) += 1;
            }
        }
        // Continuation counts, from each order down.
        let mut counts: Vec<Counts> = vec![HashMap::new(); order];
        counts[order - 1] = top;
        for k in (1..order).rev() {
            let mut lower: Counts = HashMap::new();
            for (ctx, nexts) in &counts[k] {
                for w in nexts.keys() {
                    // ctx has k tokens; drop the first for order k.
                    *lower.entry(ctx[1..].to_vec()).or_default().entry(w.clone()).or_insert(0) += 1;
                }
            }
            counts[k - 1] = lower;
        }
        let totals = counts
            .iter()
            .map(|c| {
                c.iter()
                    .map(|(ctx, n)| (ctx.clone(), (n.values().sum(), n.len() as u64)))
                    .collect()
            })
            .collect();
        KneserNey {
            order,
            discount,
            counts,
            totals,
            vocab: vocab.into_iter().collect(),
        }
    }

    fn p_order(&self, k: usize, ctx: &[String], w: &str) -> f64 {
        let lower = if k == 1 {
            1.0 / self.vocab.len() as f64
        } else {
            self.p_order(k - 1, &ctx[1..], w)
        };
        match self.totals[k - 1].get(ctx) {
            None => lower,
            Some(&(total, types)) => {
                let c = self.counts[k - 1][ctx].get(w).copied().unwrap_or(0) as f64;
                let t = total as f64;
                (c - self.discount).max(0.0) / t + self.discount * types as f64 / t * lower
            }
        }
    }

    /// Entries stored: every (context, next token) count at every order.
    pub fn size(&self) -> usize {
        self.counts.iter().map(|c| c.values().map(|n| n.len()).sum::<usize>()).sum()
    }

    /// P(next token | prefix).
    pub fn p(&self, prefix: &[String], w: &str) -> f64 {
        let mut ctx = vec![START.to_string(); self.order - 1];
        ctx.extend(prefix.iter().cloned());
        let ctx = &ctx[ctx.len() - (self.order - 1)..];
        self.p_order(self.order, ctx, w)
    }

    /// A sentence drawn from the model (at most `max` tokens).
    pub fn sample(&self, rng: &mut qsystems::lm::Rng, max: usize) -> Vec<String> {
        let mut s: Vec<String> = Vec::new();
        while s.len() < max {
            let r = (rng.draw() as f64) / (1u64 << 53) as f64;
            let mut acc = 0.0;
            let mut pick = END.to_string();
            for w in &self.vocab {
                acc += self.p(&s, w);
                if r < acc {
                    pick = w.clone();
                    break;
                }
            }
            if pick == END {
                break;
            }
            s.push(pick);
        }
        s
    }
}
