//! qlm data DIR      write the corpus split and the deeper test sentences
//! qlm report DIR    the reference models and the n-gram baselines, and any
//!                   learner whose results are in DIR (see transformer/)
//! qlm judge FILE    judge a file of sentences, one per line, by the report's
//!                   analysis

use q_lm::ktails::KTails;
use q_lm::ngram::KneserNey;
use q_lm::{analyse, bits, corpus, deep_sentences, depth, paraphrase, split, Sentence};
use qsystems::lm::{Lm, Rng, END};
use qsystems::open::{Model, Prior};
use std::collections::BTreeSet;
use std::fs;
use std::time::Instant;

const SPLIT_SEED: u64 = 2026;
const DEEP_SEED: u64 = 7;
const SAMPLE_SEED: u64 = 11;
const SAMPLES: usize = 300;
/// Training-set sizes for the learning curves (the last is all of it).
const SIZES: [usize; 4] = [100, 1_000, 10_000, 118_281];

fn read(path: &str) -> Vec<Sentence> {
    fs::read_to_string(path)
        .unwrap_or_else(|e| panic!("{path}: {e}"))
        .lines()
        .map(|l| l.rsplit('\t').next().unwrap().split(' ').filter(|w| !w.is_empty()).map(String::from).collect())
        .collect()
}

fn write(path: &str, lines: impl Iterator<Item = String>) {
    fs::write(path, lines.collect::<Vec<_>>().join("\n") + "\n").unwrap();
}

fn data(dir: &str) {
    fs::create_dir_all(dir).unwrap();
    let (all, _) = corpus();
    let (train, held) = split(&all, SPLIT_SEED);
    write(&format!("{dir}/train.txt"), train.iter().map(|s| s.join(" ")));
    write(&format!("{dir}/held.txt"), held.iter().map(|s| s.join(" ")));
    // Nested subsets for the learning curves: the first n of the (shuffled)
    // training sentences.
    for n in SIZES {
        write(&format!("{dir}/train-{n}.txt"), train.iter().take(n).map(|s| s.join(" ")));
    }
    let deep = deep_sentences(SAMPLES, DEEP_SEED);
    // The vocabulary of the language, given to every learner: the words of
    // the corpus and of the deeper sentences. CE occurs only in the second
    // (DE CE QUE needs two levels of embedding).
    let vocab: BTreeSet<&String> = all.iter().flatten().chain(deep.iter().flat_map(|(_, s)| s)).collect();
    write(&format!("{dir}/vocab.txt"), vocab.iter().map(|w| w.to_string()));
    write(&format!("{dir}/deep.txt"), deep.iter().map(|(t, s)| format!("{t}\t{}", s.join(" "))));
    println!("{} sentences: {} to train on, {} held out; {} deeper sentences", all.len(), train.len(), held.len(), deep.len());
}

/// Judgement of samples: grammatical, not in the training sentences, and
/// grammatical with two or more levels of embedding.
struct Judged {
    grammatical: usize,
    novel_grammatical: usize,
    deep_grammatical: usize,
}

fn judge_all(samples: &[Sentence], train: &BTreeSet<&Sentence>) -> Judged {
    let sys = paraphrase();
    let mut j = Judged { grammatical: 0, novel_grammatical: 0, deep_grammatical: 0 };
    for s in samples {
        if let Some(t) = analyse(&sys, s) {
            j.grammatical += 1;
            j.novel_grammatical += !train.contains(s) as usize;
            j.deep_grammatical += (depth(&t) >= 2) as usize;
        }
    }
    j
}

fn per_token<F: FnMut(&[String], &str) -> f64>(set: &[Sentence], mut p: F) -> f64 {
    let tokens: usize = set.iter().map(|s| s.len() + 1).sum();
    let total: f64 = set.iter().map(|s| bits(s, &mut p)).sum();
    total / tokens as f64
}

fn row(name: &str, held: f64, deep: String, j: Option<&Judged>) {
    let j = j
        .map(|j| format!("{} | {} | {}", j.grammatical, j.novel_grammatical, j.deep_grammatical))
        .unwrap_or("– | – | –".into());
    println!("| {name} | {held:.4} | {deep} | {j} |");
}

fn report(dir: &str) {
    let train = read(&format!("{dir}/train.txt"));
    let held = read(&format!("{dir}/held.txt"));
    let deep = read(&format!("{dir}/deep.txt"));
    let train_set: BTreeSet<&Sentence> = train.iter().collect();
    assert_eq!(train.len(), SIZES[3]);
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt")).unwrap().lines().map(String::from).collect();
    println!("{} training sentences, {} held out, {} deeper; {SAMPLES} samples per model\n", train.len(), held.len(), deep.len());
    println!("| model | bits/token, held out | bits/token, deeper | grammatical samples | of them not in training | of them deeper |");
    println!("|---|---:|---:|---:|---:|---:|");

    // E16: the graph of all 131,424 sentences, the distribution the corpus
    // was drawn from. It knows the held-out sentences and nothing deeper.
    let (_, graph) = corpus();
    let truth = Lm::new(&graph);
    let truth_bits = |set: &[Sentence]| -> (f64, usize) {
        let (mut total, mut tokens, mut zero) = (0.0, 0, 0);
        for s in set {
            let mut st = truth.start();
            let mut b = 0.0;
            for i in 0..=s.len() {
                let c = truth.next_by_paths(&st);
                let t = s.get(i).map(|x| x.as_str()).unwrap_or(END);
                b -= (*c.get(t).unwrap_or(&0) as f64 / c.values().sum::<u128>() as f64).log2();
                if i < s.len() {
                    st = truth.step(&st, t);
                }
            }
            zero += b.is_infinite() as usize;
            total += b;
            tokens += s.len() + 1;
        }
        (total / tokens as f64, zero)
    };
    let (h, _) = truth_bits(&held);
    let (_, zero) = truth_bits(&deep);
    row("the corpus distribution (E16 graph, given every sentence)", h, format!("∞ ({zero} of {} at zero)", deep.len()), None);

    // E17: the report's rules as an open grammar, q = 1/4. Knows the grammar.
    let prior = Prior { q: 0.25 };
    let open_bits = |set: &[Sentence]| {
        let tokens: usize = set.iter().map(|s| s.len() + 1).sum();
        let mut total = 0.0;
        for s in set {
            let mut m = Model::new(prior, None, true);
            for i in 0..=s.len() {
                let next = m.next();
                let z: f64 = next.values().sum();
                let t = s.get(i).map(|x| x.as_str()).unwrap_or(END);
                total -= (next.get(t).copied().unwrap_or(0.0) / z).log2();
                if i < s.len() {
                    m.step(t);
                }
            }
        }
        total / tokens as f64
    };
    let mut seed = SAMPLE_SEED;
    let open_samples: Vec<Sentence> = (0..SAMPLES).map(|_| qsystems::open::sample(prior, None, &mut seed)).collect();
    row("the report's rules as an open grammar (E17, given the grammar)", open_bits(&held), format!("{:.4}", open_bits(&deep)), Some(&judge_all(&open_samples, &train_set)));

    // Kneser–Ney n-grams, trained on the training sentences only, at each
    // size of training set.
    for n in SIZES {
        let sub = &train[..n];
        let sub_set: BTreeSet<&Sentence> = sub.iter().collect();
        for order in [2, 3, 4, 5, 6] {
            let t = Instant::now();
            let m = KneserNey::train(sub, &vocab, order, 0.75);
            let secs = t.elapsed().as_secs_f64();
            let p = |prefix: &[String], t: &str| m.p(prefix, t);
            let mut rng = Rng(SAMPLE_SEED);
            let samples: Vec<Sentence> = (0..SAMPLES).map(|_| m.sample(&mut rng, 200)).collect();
            row(
                &format!("Kneser–Ney {order}-gram, {n} sentences ({} n-grams stored, trained in {secs:.2} s)", m.size()),
                per_token(&held, p),
                format!("{:.4}", per_token(&deep, p)),
                Some(&judge_all(&samples, &sub_set)),
            );
        }
    }

    // Graphs learned by merging states (k-tails), with a floor of 1/1000
    // mixed in uniformly so that bits stay finite. "above the floor" counts
    // deeper sentences every one of whose tokens the graph allows.
    for n in SIZES {
        let sub = &train[..n];
        let sub_set: BTreeSet<&Sentence> = sub.iter().collect();
        for k in [1, 2, 3, 4] {
            let t = Instant::now();
            let m = KTails::train(sub, k);
            let secs = t.elapsed().as_secs_f64();
            let v = vocab.len() as f64 + 1.0;
            let p = |prefix: &[String], t: &str| 0.999 * m.p(prefix, t) + 0.001 / v;
            let allowed = deep.iter().filter(|s| bits(s, |pr: &[String], t: &str| m.p(pr, t)).is_finite()).count();
            let mut rng = Rng(SAMPLE_SEED);
            let samples: Vec<Sentence> = (0..SAMPLES).map(|_| m.sample(&mut rng, 200)).collect();
            row(
                &format!("merged graph, k = {k}, {n} sentences ({} states, {} arrows, built in {secs:.2} s)", m.states(), m.size()),
                per_token(&held, p),
                format!("{:.4} ({allowed} of {} allowed)", per_token(&deep, p), deep.len()),
                Some(&judge_all(&samples, &sub_set)),
            );
        }
    }

    // Learners trained elsewhere write their per-token bits and samples here.
    for entry in fs::read_dir(dir).unwrap().flatten() {
        let name = entry.file_name().to_string_lossy().to_string();
        if let Some(model) = name.strip_suffix(".bits") {
            let text = fs::read_to_string(entry.path()).unwrap();
            let mut it = text.split_whitespace().map(|x| x.parse::<f64>().unwrap());
            let (h, d) = (it.next().unwrap(), it.next().unwrap());
            let rest: Vec<String> = text.split_whitespace().skip(2).map(String::from).collect();
            let samples = read(&format!("{dir}/{model}.samples"));
            // The training sentences it saw: the first n, n from the name.
            let n: usize = model.rsplit('-').next().and_then(|x| x.parse().ok()).unwrap_or(train.len());
            let sub_set: BTreeSet<&Sentence> = train[..n.min(train.len())].iter().collect();
            row(&format!("{model} ({})", rest.join(" ")), h, format!("{d:.4}"), Some(&judge_all(&samples, &sub_set)));
        }
    }
}

fn judge(path: &str) {
    let sys = paraphrase();
    let samples = read(path);
    let ok = samples.iter().filter(|s| analyse(&sys, s).is_some()).count();
    println!("{ok} of {} grammatical", samples.len());
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    match args.get(1).map(String::as_str) {
        Some("data") => data(args.get(2).map(String::as_str).unwrap_or("data")),
        Some("report") => report(args.get(2).map(String::as_str).unwrap_or("data")),
        Some("judge") => judge(&args[2]),
        _ => eprintln!("usage: qlm data DIR | qlm report DIR | qlm judge FILE"),
    }
}
