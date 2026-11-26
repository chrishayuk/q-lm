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
fn sizes(all: usize) -> [usize; 4] {
    [100, 1_000, 10_000, all]
}

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
    let (train, held, confirm) = split(&all, SPLIT_SEED);
    write(&format!("{dir}/train.txt"), train.iter().map(|s| s.join(" ")));
    write(&format!("{dir}/dev.txt"), held.iter().map(|s| s.join(" ")));
    write(&format!("{dir}/confirm.txt"), confirm.iter().map(|s| s.join(" ")));
    // Nested subsets for the learning curves: the first n of the (shuffled)
    // training sentences.
    for n in sizes(train.len()) {
        write(&format!("{dir}/train-{n}.txt"), train.iter().take(n).map(|s| s.join(" ")));
    }
    let deep = deep_sentences(SAMPLES, DEEP_SEED);
    // The vocabulary of the language, given to every learner: the words of
    // the corpus and of the deeper sentences. CE occurs only in the second
    // (DE CE QUE needs two levels of embedding).
    let vocab: BTreeSet<&String> = all.iter().flatten().chain(deep.iter().flat_map(|(_, s)| s)).collect();
    write(&format!("{dir}/vocab.txt"), vocab.iter().map(|w| w.to_string()));
    write(&format!("{dir}/deep.txt"), deep.iter().map(|(t, s)| format!("{t}\t{}", s.join(" "))));
    // A second deeper test with only words of the training sentences, so
    // that depth is tested apart from unseen words. (A smaller training
    // subset may still lack some; the report counts how many are covered.)
    let seen: BTreeSet<&String> = train.iter().flatten().collect();
    let mut deep_seen = Vec::new();
    let mut seed = DEEP_SEED + 1;
    while deep_seen.len() < SAMPLES {
        for (t, s) in deep_sentences(SAMPLES, seed) {
            if deep_seen.len() < SAMPLES && s.iter().all(|w| seen.contains(w)) {
                deep_seen.push((t, s));
            }
        }
        seed += 1;
    }
    write(&format!("{dir}/deep-seen.txt"), deep_seen.iter().map(|(t, s)| format!("{t}\t{}", s.join(" "))));
    println!(
        "{} sentences: {} to train on, {} for development, {} for confirmation; {} deeper sentences, and {} with only words of the training sentences",
        all.len(),
        train.len(),
        held.len(),
        confirm.len(),
        deep.len(),
        deep_seen.len()
    );
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

/// The most any next-token distribution strays from summing to 1, over the
/// prefixes of the first 50 held-out and 50 deeper sentences.
fn normalisation<F: FnMut(&[String], &str) -> f64>(vocab: &[String], sets: [&[Sentence]; 2], mut p: F) -> f64 {
    let mut worst: f64 = 0.0;
    for set in sets {
        for s in set.iter().take(50) {
            for i in 0..=s.len() {
                let z: f64 = vocab.iter().map(|w| p(&s[..i], w)).sum::<f64>() + p(&s[..i], END);
                worst = worst.max((z - 1.0).abs());
            }
        }
    }
    worst
}

struct Row {
    name: String,
    held: f64,
    deep: String,
    deep_seen: String,
    judged: Option<Judged>,
    norm: Option<f64>,
}

fn print(r: &Row) {
    let j = r
        .judged
        .as_ref()
        .map(|j| format!("{} | {} | {}", j.grammatical, j.novel_grammatical, j.deep_grammatical))
        .unwrap_or("– | – | –".into());
    let n = r.norm.map(|n| format!("{n:.1e}")).unwrap_or("–".into());
    println!("| {} | {:.4} | {} | {} | {j} | {n} |", r.name, r.held, r.deep, r.deep_seen);
}

fn report(dir: &str) {
    let train = read(&format!("{dir}/train.txt"));
    let held = read(&format!("{dir}/dev.txt"));
    let deep = read(&format!("{dir}/deep.txt"));
    let deep_seen = read(&format!("{dir}/deep-seen.txt"));
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt")).unwrap().lines().map(String::from).collect();
    let train_set: BTreeSet<&Sentence> = train.iter().collect();
    println!(
        "{} training sentences, {} for development (the confirmation set is not read), {} deeper (of which {} contain CE), {} deeper with only corpus words; {SAMPLES} samples per model\n",
        train.len(),
        held.len(),
        deep.len(),
        deep.iter().filter(|s| s.iter().any(|w| w == "CE")).count(),
        deep_seen.len()
    );
    println!("| model | bits/token, development | bits/token, deeper | bits/token, deeper, corpus words only | grammatical samples | of them not in training | of them deeper | most a distribution strays from 1 |");
    println!("|---|---:|---:|---:|---:|---:|---:|---:|");

    // E16: the true distribution of the corpus.
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
    let (floor, _) = truth_bits(&held);
    let (_, z1) = truth_bits(&deep);
    let (_, z2) = truth_bits(&deep_seen);
    print(&Row {
        name: "the corpus distribution (E16, given every sentence)".into(),
        held: floor,
        deep: format!("∞ ({z1} at zero)"),
        deep_seen: format!("∞ ({z2} at zero)"),
        judged: None,
        norm: None,
    });

    // E17: the report's rules as an open grammar. Given the grammar.
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
    print(&Row {
        name: "the report's rules as an open grammar (E17, given the grammar)".into(),
        held: open_bits(&held),
        deep: format!("{:.4}", open_bits(&deep)),
        deep_seen: format!("{:.4}", open_bits(&deep_seen)),
        judged: Some(judge_all(&open_samples, &train_set)),
        norm: None,
    });

    for n in sizes(train.len()) {
        let sub = &train[..n];
        let sub_set: BTreeSet<&Sentence> = sub.iter().collect();
        let words: BTreeSet<&String> = sub.iter().flatten().collect();
        let covered = deep_seen.iter().filter(|s| s.iter().all(|w| words.contains(w))).count();
        println!("| *{n} training sentences: {covered} of the {} deeper sentences with corpus words use only words of these* | | | | | | | |", deep_seen.len());
        // Kneser–Ney n-grams.
        for order in [3, 4, 6] {
            let t = Instant::now();
            let m = KneserNey::train(sub, &vocab, order, 0.75);
            let secs = t.elapsed().as_secs_f64();
            let p = |prefix: &[String], t: &str| m.p(prefix, t);
            let mut rng = Rng(SAMPLE_SEED);
            let samples: Vec<Sentence> = (0..SAMPLES).map(|_| m.sample(&mut rng, 200)).collect();
            print(&Row {
                name: format!("Kneser–Ney {order}-gram, {n} sentences ({} n-grams, {secs:.2} s)", m.size()),
                held: per_token(&held, p),
                deep: format!("{:.4}", per_token(&deep, p)),
                deep_seen: format!("{:.4}", per_token(&deep_seen, p)),
                judged: Some(judge_all(&samples, &sub_set)),
                norm: Some(normalisation(&vocab, [&held, &deep], p)),
            });
        }
        // Graphs learned by merging states. Bits are from the graph with a
        // floor of 1/1000 mixed in; samples are from the graph alone.
        for k in [2, 3] {
            let t = Instant::now();
            let m = KTails::train(sub, k);
            let secs = t.elapsed().as_secs_f64();
            let v = vocab.len() as f64 + 1.0;
            let p = |prefix: &[String], t: &str| if m.reachable(prefix) { 0.999 * m.p(prefix, t) + 0.001 / v } else { 1.0 / v };
            let allowed = |set: &[Sentence]| set.iter().filter(|s| bits(s, |pr: &[String], t: &str| m.p(pr, t)).is_finite()).count();
            let mut rng = Rng(SAMPLE_SEED);
            let samples: Vec<Sentence> = (0..SAMPLES).map(|_| m.sample(&mut rng, 200)).collect();
            print(&Row {
                name: format!("merged graph, k = {k}, {n} sentences ({} states, {} arrows, {secs:.2} s; bits with the floor, samples without)", m.states(), m.size()),
                held: per_token(&held, p),
                deep: format!("{:.4} ({} allowed)", per_token(&deep, p), allowed(&deep)),
                deep_seen: format!("{:.4} ({} allowed)", per_token(&deep_seen, p), allowed(&deep_seen)),
                judged: Some(judge_all(&samples, &sub_set)),
                norm: Some(normalisation(&vocab, [&held, &deep], p)),
            });
        }
        // Transformers trained by transformer/train.py, every seed.
        let mut files: Vec<String> = fs::read_dir(dir)
            .unwrap()
            .flatten()
            .map(|e| e.file_name().to_string_lossy().to_string())
            .filter(|f| f.starts_with(&format!("transformer-{n}-")) && f.ends_with(".bits"))
            .collect();
        files.sort();
        for f in files {
            let model = f.trim_end_matches(".bits");
            let text = fs::read_to_string(format!("{dir}/{f}")).unwrap();
            let mut it = text.split_whitespace();
            let mut num = || it.next().unwrap().parse::<f64>().unwrap();
            let (h, d, ds, norm) = (num(), num(), num(), num());
            let notes: Vec<&str> = text.split_whitespace().skip(4).collect();
            let samples = read(&format!("{dir}/{model}.samples"));
            print(&Row {
                name: format!("{model} ({})", notes.join(" ")),
                held: h,
                deep: format!("{d:.4}"),
                deep_seen: format!("{ds:.4}"),
                judged: Some(judge_all(&samples, &sub_set)),
                norm: Some(norm),
            });
        }
    }

    // Transformer learning curves: steps to come within 1% and 5% of the
    // floor on held-out sentences.
    println!("\n**Transformer learning curves.** The floor is {floor:.4} bits per token on the development sentences. Steps (of 64 sentences each) until the bits first come within 5% and within 1% of it, from the curve each run writes (bits on the first 2,000 development sentences, every 250 steps).\n");
    println!("| run | within 5% | within 1% | best | at step |");
    println!("|---|---:|---:|---:|---:|");
    let mut curves: Vec<String> = fs::read_dir(dir).unwrap().flatten().map(|e| e.file_name().to_string_lossy().to_string()).filter(|f| f.ends_with(".curve")).collect();
    curves.sort_by_key(|f| (f.split('-').nth(1).and_then(|n| n.parse::<usize>().ok()).unwrap_or(0), f.clone()));
    for f in curves {
        let pts: Vec<(usize, f64)> = fs::read_to_string(format!("{dir}/{f}"))
            .unwrap()
            .lines()
            .map(|l| {
                let mut w = l.split_whitespace();
                (w.next().unwrap().parse().unwrap(), w.next().unwrap().parse().unwrap())
            })
            .collect();
        let first = |frac: f64| pts.iter().find(|(_, b)| *b <= floor * (1.0 + frac)).map(|(s, _)| s.to_string()).unwrap_or("never".into());
        let best = pts.iter().cloned().fold((0, f64::INFINITY), |a, b| if b.1 < a.1 { b } else { a });
        println!("| {} | {} | {} | {:.4} | {} |", f.trim_end_matches(".curve"), first(0.05), first(0.01), best.1, best.0);
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
