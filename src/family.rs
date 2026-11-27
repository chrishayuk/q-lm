//! QLM-005: languages from seeded random grammars, and their judge.
//!
//! A family grammar has a clause `S`, arguments `X`, an embedding `E`, and
//! word classes. The only recursion is `X → E` and `E → … S …`. The depth of
//! a tree is the number of `S` nested inside an `E`; the depth of a sentence
//! is the least depth of any of its trees, found by CYK. See
//! docs/qlm005-plan.md.

use qsystems::lm::Rng;
use std::collections::{BTreeSet, HashMap};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Right,
    Centre,
    Left,
}

impl Kind {
    pub fn parse(s: &str) -> Option<Kind> {
        match s {
            "right" => Some(Kind::Right),
            "centre" => Some(Kind::Centre),
            "left" => Some(Kind::Left),
            _ => None,
        }
    }
    pub fn name(self) -> &'static str {
        match self {
            Kind::Right => "right",
            Kind::Centre => "centre",
            Kind::Left => "left",
        }
    }
}

/// A symbol of a template: a nonterminal, a word class, or `S` embedded
/// (`Sub`, which adds one to the depth).
#[derive(Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum Sym {
    S,
    X,
    E,
    Sub,
    Class(String),
}

#[derive(Clone, Debug)]
pub struct Family {
    pub kind: Kind,
    pub seed: u64,
    /// Productions of S, X and E.
    pub s: Vec<Vec<Sym>>,
    pub x: Vec<Vec<Sym>>,
    pub e: Vec<Sym>,
    /// Word classes: name → words.
    pub classes: Vec<(String, Vec<String>)>,
}

fn unit(r: &mut Rng) -> f64 {
    (r.draw() as f64) / (1u64 << 53) as f64
}
fn range(r: &mut Rng, lo: usize, hi: usize) -> usize {
    lo + (r.draw() as usize) % (hi - lo + 1)
}

fn c(name: &str) -> Sym {
    Sym::Class(name.into())
}

impl Family {
    /// The grammar of kind and seed: redrawn, deterministically, until the
    /// corpus (trees of depth at most 1) has 20,000 to 250,000 trees.
    pub fn generate(kind: Kind, seed: u64) -> Family {
        let mut r = Rng(seed.wrapping_mul(0x9E37_79B9_7F4A_7C15) ^ kind as u64);
        loop {
            let f = Family::draw(kind, seed, &mut r);
            let n = f.trees(&Sym::S, 1);
            if (20_000.0..=250_000.0).contains(&n) {
                return f;
            }
        }
    }

    fn draw(kind: Kind, seed: u64, r: &mut Rng) -> Family {
        // Made-up words, all distinct.
        let cons = b"bdfgklmnprstvz";
        let vows = b"aeiou";
        let mut used = BTreeSet::new();
        let mut word = |r: &mut Rng| loop {
            let mut w = String::new();
            for _ in 0..2 {
                w.push(cons[(r.draw() as usize) % cons.len()] as char);
                w.push(vows[(r.draw() as usize) % vows.len()] as char);
            }
            if used.insert(w.clone()) {
                return w;
            }
        };
        let mut class = |name: &str, n: usize, r: &mut Rng| (name.to_string(), (0..n).map(|_| word(r)).collect::<Vec<_>>());
        let mut classes = vec![
            class("N", range(r, 3, 6), r),
            class("V", range(r, 2, 4), r),
            class("A", range(r, 2, 4), r),
            class("C", 1, r),
            class("D", 1, r),
            class("M", 1, r),
            class("P", 1, r),
        ];
        let two_markers = unit(r) < 0.5;
        if !two_markers {
            classes.retain(|(n, _)| n != "P");
        }
        let (x, v, a, m, p) = (Sym::X, c("V"), c("A"), c("M"), c("P"));
        // Clause templates.
        let mut pool: Vec<Vec<Sym>> = vec![
            vec![x.clone(), v.clone(), x.clone()],
            vec![x.clone(), x.clone(), v.clone()],
            vec![v.clone(), x.clone(), x.clone()],
            vec![x.clone(), v.clone()],
            vec![x.clone(), m.clone(), v.clone(), x.clone()],
            vec![x.clone(), v.clone(), m.clone(), x.clone()],
            vec![x.clone(), m.clone(), v.clone(), a.clone(), x.clone()],
            vec![v.clone(), x.clone(), m.clone(), x.clone()],
        ];
        if two_markers {
            pool.push(vec![x.clone(), v.clone(), p.clone(), x.clone()]);
            pool.push(vec![p.clone(), x.clone(), v.clone(), x.clone()]);
        }
        let mut s = Vec::new();
        let k = range(r, 2, 3);
        while s.len() < k {
            let t = pool[(r.draw() as usize) % pool.len()].clone();
            if !s.contains(&t) {
                s.push(t);
            }
        }
        // Argument templates: a noun, optionally modified, and the embedding.
        let xpool = [vec![c("N")], vec![c("A"), c("N")], vec![c("N"), c("A")]];
        let mut xs: Vec<Vec<Sym>> = vec![xpool[(r.draw() as usize) % 3].clone()];
        if unit(r) < 0.5 {
            let t = xpool[(r.draw() as usize) % 3].clone();
            if !xs.contains(&t) {
                xs.push(t);
            }
        }
        xs.push(vec![Sym::E]);
        let e = match kind {
            Kind::Right => vec![c("C"), Sym::Sub],
            Kind::Centre => vec![c("C"), Sym::Sub, c("D")],
            Kind::Left => vec![Sym::Sub, c("C")],
        };
        if kind != Kind::Centre {
            classes.retain(|(n, _)| n != "D");
        }
        Family { kind, seed, s, x: xs, e, classes }
    }

    fn words_of(&self, class: &str) -> &[String] {
        &self.classes.iter().find(|(n, _)| n == class).unwrap().1
    }

    fn productions(&self, a: &Sym) -> Vec<Vec<Sym>> {
        match a {
            Sym::S => self.s.clone(),
            Sym::X => self.x.clone(),
            Sym::E => vec![self.e.clone()],
            Sym::Sub => vec![vec![Sym::S]],
            Sym::Class(_) => vec![],
        }
    }

    /// The number of trees of `a` with depth at most `d`.
    pub fn trees(&self, a: &Sym, d: usize) -> f64 {
        match a {
            Sym::Class(n) => self.words_of(n).len() as f64,
            Sym::Sub => {
                if d == 0 {
                    0.0
                } else {
                    self.trees(&Sym::S, d - 1)
                }
            }
            _ => self
                .productions(a)
                .iter()
                .map(|p| p.iter().map(|y| self.trees(y, d)).product::<f64>())
                .sum(),
        }
    }

    /// Every string of every tree of `a` with depth at most `d`.
    pub fn strings(&self, a: &Sym, d: usize) -> Vec<Vec<String>> {
        match a {
            Sym::Class(n) => self.words_of(n).iter().map(|w| vec![w.clone()]).collect(),
            Sym::Sub => {
                if d == 0 {
                    vec![]
                } else {
                    self.strings(&Sym::S, d - 1)
                }
            }
            _ => {
                let mut out = Vec::new();
                for p in self.productions(a) {
                    let mut acc: Vec<Vec<String>> = vec![vec![]];
                    for y in &p {
                        let ys = self.strings(y, d);
                        let mut next = Vec::with_capacity(acc.len() * ys.len());
                        for a in &acc {
                            for b in &ys {
                                let mut v = a.clone();
                                v.extend(b.iter().cloned());
                                next.push(v);
                            }
                        }
                        acc = next;
                    }
                    out.extend(acc);
                }
                out
            }
        }
    }

    /// The corpus: every distinct sentence of depth at most 1, sorted, and
    /// how many of them have more than one tree.
    pub fn corpus(&self) -> (Vec<Vec<String>>, usize) {
        let all = self.strings(&Sym::S, 1);
        let trees = all.len();
        let set: BTreeSet<Vec<String>> = all.into_iter().collect();
        let distinct = set.len();
        (set.into_iter().collect(), trees - distinct)
    }

    /// A random top-down derivation bounded at depth `max`: each X is an
    /// embedding with probability 1/3 where depth allows.
    pub fn derive(&self, r: &mut Rng, max: usize) -> Vec<String> {
        let mut out = Vec::new();
        self.derive_into(&Sym::S, max, r, &mut out);
        out
    }

    fn derive_into(&self, a: &Sym, d: usize, r: &mut Rng, out: &mut Vec<String>) {
        match a {
            Sym::Class(n) => {
                let ws = self.words_of(n);
                out.push(ws[(r.draw() as usize) % ws.len()].clone());
            }
            Sym::Sub => self.derive_into(&Sym::S, d - 1, r, out),
            Sym::X => {
                let base: Vec<&Vec<Sym>> = self.x.iter().filter(|p| p[0] != Sym::E).collect();
                let p = if d > 0 && unit(r) < 1.0 / 3.0 {
                    vec![Sym::E]
                } else {
                    base[(r.draw() as usize) % base.len()].clone()
                };
                for y in &p {
                    self.derive_into(y, d, r, out);
                }
            }
            _ => {
                let ps = self.productions(a);
                let p = &ps[(r.draw() as usize) % ps.len()];
                for y in p {
                    self.derive_into(y, d, r, out);
                }
            }
        }
    }

    /// The judge: the least depth of any tree of the sentence, or None if
    /// the grammar does not derive it. CYK over the templates, binarised.
    pub fn depth(&self, s: &[String]) -> Option<usize> {
        let n = s.len();
        if n == 0 || n > 400 {
            return None;
        }
        let mut class_of: HashMap<&str, Vec<Sym>> = HashMap::new();
        for (name, ws) in &self.classes {
            for w in ws {
                class_of.entry(w.as_str()).or_default().push(Sym::Class(name.clone()));
            }
        }
        // chart[i][j]: symbol → least depth deriving words i..j. Partial
        // templates are keyed by (lhs, production, symbols matched).
        type Key = (u8, usize, usize); // (lhs: 0 S, 1 X, 2 E, 3 Sub), production, matched
        let lhs_sym = [Sym::S, Sym::X, Sym::E, Sym::Sub];
        let prods: Vec<Vec<Vec<Sym>>> = lhs_sym.iter().map(|a| self.productions(a)).collect();
        let mut full: Vec<Vec<HashMap<Sym, usize>>> = vec![vec![HashMap::new(); n + 1]; n + 1];
        let mut part: Vec<Vec<HashMap<Key, usize>>> = vec![vec![HashMap::new(); n + 1]; n + 1];
        let better = |m: &mut HashMap<Sym, usize>, k: Sym, v: usize| -> bool {
            match m.get(&k) {
                Some(&old) if old <= v => false,
                _ => {
                    m.insert(k, v);
                    true
                }
            }
        };
        for len in 1..=n {
            for i in 0..=n - len {
                let j = i + len;
                if len == 1 {
                    for cl in class_of.get(s[i].as_str()).into_iter().flatten() {
                        full[i][j].insert(cl.clone(), 0);
                    }
                }
                // Partial templates ending at j: extend a partial i..k by a
                // full symbol k..j, or start one with a full symbol i..j.
                loop {
                    let mut changed = false;
                    // Start or extend partials.
                    let mut new_parts: Vec<(Key, usize)> = Vec::new();
                    for (li, ps) in prods.iter().enumerate() {
                        for (pi, p) in ps.iter().enumerate() {
                            if let Some(&d) = full[i][j].get(&p[0]) {
                                new_parts.push(((li as u8, pi, 1), d));
                            }
                            for k in i + 1..j {
                                for (&(l2, p2, m), &d1) in &part[i][k] {
                                    if l2 as usize == li && p2 == pi && m < p.len() {
                                        if let Some(&d2) = full[k][j].get(&p[m]) {
                                            new_parts.push(((li as u8, pi, m + 1), d1.max(d2)));
                                        }
                                    }
                                }
                            }
                        }
                    }
                    for (key, d) in new_parts {
                        let e = part[i][j].entry(key).or_insert(usize::MAX);
                        if d < *e {
                            *e = d;
                            changed = true;
                        }
                    }
                    // Completed partials become full symbols.
                    let done: Vec<(Sym, usize)> = part[i][j]
                        .iter()
                        .filter(|(&(l, p, m), _)| prods[l as usize][p].len() == m)
                        .map(|(&(l, _, _), &d)| {
                            let a = lhs_sym[l as usize].clone();
                            let d = if a == Sym::Sub { d + 1 } else { d };
                            (a, d)
                        })
                        .collect();
                    for (a, d) in done {
                        changed |= better(&mut full[i][j], a, d);
                    }
                    if !changed {
                        break;
                    }
                }
            }
        }
        full[0][n].get(&Sym::S).copied()
    }

    /// The grammar, readable.
    pub fn text(&self) -> String {
        let show = |p: &[Sym]| {
            p.iter()
                .map(|y| match y {
                    Sym::S => "S".to_string(),
                    Sym::X => "X".into(),
                    Sym::E => "E".into(),
                    Sym::Sub => "S".into(),
                    Sym::Class(n) => n.clone(),
                })
                .collect::<Vec<_>>()
                .join(" ")
        };
        let mut t = format!("kind {} seed {}\n", self.kind.name(), self.seed);
        for p in &self.s {
            t += &format!("S -> {}\n", show(p));
        }
        for p in &self.x {
            t += &format!("X -> {}\n", show(p));
        }
        t += &format!("E -> {}   (the S here is one level deeper)\n", show(&self.e));
        for (n, ws) in &self.classes {
            t += &format!("{n} : {}\n", ws.join(" "));
        }
        t
    }

    /// Read back a grammar written by `text`.
    pub fn parse(t: &str) -> Family {
        let mut lines = t.lines();
        let head: Vec<&str> = lines.next().unwrap().split_whitespace().collect();
        let kind = Kind::parse(head[1]).unwrap();
        let seed = head[3].parse().unwrap();
        let (mut s, mut x, mut e, mut classes) = (vec![], vec![], vec![], vec![]);
        for l in lines {
            if let Some((lhs, rhs)) = l.split_once(" -> ") {
                let rhs = rhs.split("   ").next().unwrap();
                let syms: Vec<Sym> = rhs
                    .split_whitespace()
                    .map(|y| match (lhs, y) {
                        ("E", "S") => Sym::Sub,
                        (_, "S") => Sym::S,
                        (_, "X") => Sym::X,
                        (_, "E") => Sym::E,
                        (_, n) => Sym::Class(n.into()),
                    })
                    .collect();
                match lhs {
                    "S" => s.push(syms),
                    "X" => x.push(syms),
                    _ => e = syms,
                }
            } else if let Some((n, ws)) = l.split_once(" : ") {
                classes.push((n.to_string(), ws.split_whitespace().map(String::from).collect()));
            }
        }
        Family { kind, seed, s, x, e, classes }
    }
}
