//! The family judge (CYK) against the generator: every corpus sentence is
//! judged grammatical at depth 0 or 1, every depth-2-bounded derivation at
//! most 2, and the written grammar reads back to the same judge.

use q_lm::family::{Family, Kind, Sym};
use qsystems::lm::Rng;

#[test]
fn judge_agrees_with_generator() {
    for kind in [Kind::Right, Kind::Centre, Kind::Left] {
        let f = Family::generate(kind, 1);
        let trees = f.trees(&Sym::S, 1);
        assert!((20_000.0..=250_000.0).contains(&trees), "{trees}");
        let (corpus, _) = f.corpus();
        let g = Family::parse(&f.text());
        for s in corpus.iter().step_by(corpus.len() / 300 + 1) {
            let d = f.depth(s);
            assert!(matches!(d, Some(0) | Some(1)), "{kind:?} {s:?}: {d:?}");
            assert_eq!(g.depth(s), d);
        }
        // Depth-0 sentences are judged 0.
        for s in f.strings(&Sym::S, 0).iter().take(200) {
            assert_eq!(f.depth(s), Some(0), "{s:?}");
        }
        let mut r = Rng(3);
        let mut twos = 0;
        for _ in 0..200 {
            let s = f.derive(&mut r, 2);
            let d = f.depth(&s).expect("a derivation is grammatical");
            assert!(d <= 2);
            twos += (d == 2) as usize;
        }
        assert!(twos > 0, "{kind:?}: no depth-2 derivations");
        // No clause template has fewer than two symbols: one word is not a
        // sentence.
        assert_eq!(f.depth(&corpus[0][..1]), None);
    }
}
