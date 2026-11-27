//! Exact next-token prediction against listing every sentence, on a grammar
//! learned from three sentences whose language is finite.

use q_lm::prefix::Prefix;
use q_lm::subst::Subst;
use qsystems::lm::END;
use std::collections::BTreeMap;

fn words(s: &str) -> Vec<String> {
    s.split(' ').map(String::from).collect()
}

#[test]
fn prefix_probabilities_equal_listing() {
    let train: Vec<Vec<String>> = ["X Y", "X Z", "W Y"].iter().map(|s| words(s)).collect();
    let vocab = words("W X Y Z");
    let g = Subst::train(&train, &vocab);
    // The language: every two-word string the grammar derives.
    let mut lang: BTreeMap<Vec<String>, f64> = BTreeMap::new();
    for a in &vocab {
        for b in &vocab {
            let s = vec![a.clone(), b.clone()];
            let p = g.probability(&s);
            if p > 0.0 {
                lang.insert(s, p);
            }
        }
    }
    let total: f64 = lang.values().sum();
    assert!((total - 1.0).abs() < 1e-12, "the learned language should be all the probability: {lang:?}");
    assert_eq!(lang.len(), 4, "{lang:?}");
    let pf = Prefix::new(&g);
    for s in lang.keys() {
        let mut r = pf.start();
        for i in 0..=s.len() {
            let got = pf.next(&r);
            let z: f64 = got.values().sum();
            assert!((z - r.prob).abs() < 1e-12);
            let mut want: BTreeMap<String, f64> = BTreeMap::new();
            for (t, p) in lang.iter().filter(|(t, _)| t.starts_with(&s[..i])) {
                *want.entry(t.get(i).cloned().unwrap_or(END.into())).or_insert(0.0) += p;
            }
            for (k, v) in &got {
                assert!((v - want.get(k).copied().unwrap_or(0.0)).abs() < 1e-12, "{s:?} at {i}: {k} {v}");
            }
            if i < s.len() {
                pf.step(&mut r, g.word_id(&s[i]).unwrap());
            }
        }
    }
}
