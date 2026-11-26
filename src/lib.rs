//! Language modelling on the language of the French grammar of Colmerauer's
//! Q-systems report (C70, section 11), with learners that see only
//! sentences.
//!
//! The historical machine (the `qsystems` crate) supplies three things and
//! is not changed by anything here:
//!
//! - the corpus: every sentence of every tree with at most one level of
//!   embedding, synthesised by the report's rules;
//! - the deeper test sentences, synthesised from trees with two levels;
//! - the judge: a sentence is grammatical if the report's system, inverted,
//!   analyses it to exactly one tree. Its depth is read from that tree.
//!
//! The reference models are QSYS-E16 (the graph of all 131,424 sentences,
//! which is the true distribution of the corpus) and E17 (the report's rules
//! read as an open grammar, which knows the grammar).

pub mod ktails;
pub mod ngram;

use qsystems::lm::Rng;
use qsystems::machine::{apply, strings_text, Arrow, Graph, Limits, System};
use qsystems::report::systems;
use qsystems::syntax::parse_tree;
use qsystems::tree::Tree;

pub const NAMES: [&str; 4] = ["BEAUCEVILLE", "BENOIT", "GAETANE", "RICHARD"];
pub const VERBS: [&str; 3] = ["DETRUIT", "ETONNE", "CONSTATE"];
pub const PARAPHRASE: &str = include_str!("../../q-systems/examples/paraphrase.q");

pub type Sentence = Vec<String>;

pub fn paraphrase() -> Vec<System> {
    systems(PARAPHRASE).unwrap()
}

/// Every normalised clause with at most `depth` levels of embedding.
pub fn clauses(depth: usize) -> Vec<String> {
    let mut args: Vec<String> = NAMES.iter().map(|n| format!("SN({n})")).collect();
    if depth > 0 {
        args.extend(clauses(depth - 1).into_iter().map(|i| format!("PH({i})")));
    }
    let mut out = Vec::new();
    for v in VERBS {
        for a in &args {
            for b in &args {
                out.push(format!("V({v}),{a},{b}"));
            }
        }
    }
    out
}

fn tokens(g: &Graph) -> Vec<Sentence> {
    g.strings(usize::MAX)
        .iter()
        .map(|s| s.iter().map(|t| t.to_string()).collect())
        .collect()
}

/// The graph of every sentence of the given trees, synthesised at once.
pub fn language_graph(trees: &[String]) -> Graph {
    let mut arrows: Vec<Arrow> = trees
        .iter()
        .map(|t| Arrow { from: 0, to: 1, tree: parse_tree(t).unwrap() })
        .collect();
    arrows.push(Arrow { from: 1, to: 2, tree: Tree::leaf(".") });
    apply(&paraphrase()[1], &Graph { arrows, nverts: 3, entry: 0, exit: 2 }, Limits { max_arrows: 10_000_000 }).result
}

/// The 131,424 sentences of the trees with at most one level of embedding,
/// and the graph that holds them.
pub fn corpus() -> (Vec<Sentence>, Graph) {
    let trees: Vec<String> = clauses(1).into_iter().map(|c| format!("PI({c})")).collect();
    let g = language_graph(&trees);
    (tokens(&g), g)
}

/// The sentences of one tree.
pub fn synthesis(tree: &str) -> Graph {
    let g = Graph::from_chain(&[parse_tree(tree).unwrap(), Tree::leaf(".")]);
    apply(&paraphrase()[1], &g, Limits::default()).result
}

/// `n` sentences of trees with exactly two levels of embedding: a random
/// clause that itself embeds one, as subject or object of the main clause,
/// and a random paraphrase of each.
pub fn deep_sentences(n: usize, seed: u64) -> Vec<(String, Sentence)> {
    let deep: Vec<String> = clauses(1).into_iter().filter(|c| c.contains("PH(")).collect();
    let mut rng = Rng(seed);
    (0..n)
        .map(|_| {
            let v = VERBS[(rng.draw() % 3) as usize];
            let a = format!("PH({})", deep[(rng.draw() as usize) % deep.len()]);
            let b = format!("SN({})", NAMES[(rng.draw() % 4) as usize]);
            let tree = if rng.draw().is_multiple_of(2) {
                format!("PI(V({v}),{a},{b})")
            } else {
                format!("PI(V({v}),{b},{a})")
            };
            let s = qsystems::lm::generate(&qsystems::lm::Lm::new(&synthesis(&tree)), false, &mut rng);
            (tree, s)
        })
        .collect()
}

/// Levels of clause embedding in a tree: PH inside PH.
pub fn depth(t: &Tree) -> usize {
    let inner = t.kids.iter().map(depth).max().unwrap_or(0);
    if &*t.label == "PH" {
        inner + 1
    } else {
        inner
    }
}

/// The report's judgement of a sentence: the one tree its inverted system
/// analyses it to, if exactly one.
pub fn analyse(sys: &[System], s: &[String]) -> Option<Tree> {
    if s.is_empty() || s.len() > 400 {
        return None;
    }
    let chain: Vec<Tree> = s.iter().map(|w| parse_tree(w).ok()).collect::<Option<_>>()?;
    let o = apply(&sys[0], &Graph::from_chain(&chain), Limits { max_arrows: 200_000 });
    let r = strings_text(&o.result);
    if o.converged && r.len() == 1 && r[0].starts_with("PI(") && r[0].ends_with(" + .") {
        parse_tree(r[0].trim_end_matches(" + .")).ok()
    } else {
        None
    }
}

/// Split the corpus deterministically: every tenth sentence, in a fixed
/// shuffle, is held out.
pub fn split(corpus: &[Sentence], seed: u64) -> (Vec<Sentence>, Vec<Sentence>) {
    let mut idx: Vec<usize> = (0..corpus.len()).collect();
    let mut rng = Rng(seed);
    for i in (1..idx.len()).rev() {
        let j = (rng.draw() as usize) % (i + 1);
        idx.swap(i, j);
    }
    let (mut train, mut held) = (Vec::new(), Vec::new());
    for (k, &i) in idx.iter().enumerate() {
        if k % 10 == 0 {
            held.push(corpus[i].clone());
        } else {
            train.push(corpus[i].clone());
        }
    }
    (train, held)
}

/// Bits per token (END included) of a sentence under next-token
/// probabilities given by `p(prefix, token)`.
pub fn bits<F: FnMut(&[String], &str) -> f64>(s: &[String], mut p: F) -> f64 {
    let mut b = 0.0;
    for i in 0..=s.len() {
        let t = s.get(i).map(|x| x.as_str()).unwrap_or(qsystems::lm::END);
        b -= p(&s[..i], t).log2();
    }
    b
}
