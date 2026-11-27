//! Pruning by expected count: rules no training sentence uses go, the
//! training sentences stay derivable, and each category's rules still sum to 1.

use q_lm::subst::Subst;

fn words(s: &str) -> Vec<String> {
    s.split(' ').map(String::from).collect()
}

#[test]
fn pruning_keeps_what_the_sentences_use() {
    let train: Vec<Vec<String>> = ["A B", "A B", "A C", "D B", "A B B"].iter().map(|s| words(s)).collect();
    let vocab = words("A B C D");
    let mut g = Subst::train(&train, &vocab);
    g.em(&train, 5, 1e-3);
    let before = g.size();
    g.prune(0.5);
    assert!(g.size() < before, "some rule should go: {before} rules before, {} after", g.size());
    for s in &train {
        assert!(g.probability(s) > 0.0, "{s:?} should stay derivable");
    }
    for rs in g.rules.values() {
        let total: f64 = rs.iter().map(|r| r.1).sum();
        assert!((total - 1.0).abs() < 1e-12);
    }
    let (grammar, data, missing) = g.description_length(&train);
    assert!(grammar > 0.0 && data > 0.0 && missing == 0);
    // Every rule is below an infinite count: nothing is left.
    g.prune(f64::INFINITY);
    assert_eq!(g.size(), 0);
}
