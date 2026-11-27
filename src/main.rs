//! qlm data DIR      write the corpus split and the deeper test sentences
//! qlm report DIR    the reference models and the n-gram baselines, and any
//!                   learner whose results are in DIR (see transformer/)
//! qlm mdl DIR N     QLM-004: prune the grammar learned from N sentences by
//!                   expected rule count, choosing by description length
//! qlm family DIR KIND SEED   QLM-005: a language from a seeded random
//!                   grammar (KIND right, centre or left), written as `data`
//! qlm compare DIR   QLM-005: the plan's measures on any language directory
//! qlm judge FILE    judge a file of sentences, one per line, by the report's
//!                   analysis

use q_lm::ktails::KTails;
use q_lm::ngram::KneserNey;
use q_lm::{analyse, bits, corpus, deep_sentences, depth, paraphrase, split, Sentence};
use qsystems::lm::{Lm, Rng, END};
use qsystems::open::{Model, Prior};
use std::collections::{BTreeSet, HashMap};
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
        .map(|l| {
            l.rsplit('\t')
                .next()
                .unwrap()
                .split(' ')
                .filter(|w| !w.is_empty())
                .map(String::from)
                .collect()
        })
        .collect()
}

fn write(path: &str, lines: impl Iterator<Item = String>) {
    fs::write(path, lines.collect::<Vec<_>>().join("\n") + "\n").unwrap();
}

fn data(dir: &str) {
    fs::create_dir_all(dir).unwrap();
    let (all, _) = corpus();
    let (train, held, confirm) = split(&all, SPLIT_SEED);
    write(
        &format!("{dir}/train.txt"),
        train.iter().map(|s| s.join(" ")),
    );
    write(&format!("{dir}/dev.txt"), held.iter().map(|s| s.join(" ")));
    write(
        &format!("{dir}/confirm.txt"),
        confirm.iter().map(|s| s.join(" ")),
    );
    // Nested subsets for the learning curves: the first n of the (shuffled)
    // training sentences.
    for n in sizes(train.len()) {
        write(
            &format!("{dir}/train-{n}.txt"),
            train.iter().take(n).map(|s| s.join(" ")),
        );
    }
    let deep = deep_sentences(SAMPLES, DEEP_SEED);
    // The vocabulary of the language, given to every learner: the words of
    // the corpus and of the deeper sentences. CE occurs only in the second
    // (DE CE QUE needs two levels of embedding).
    let vocab: BTreeSet<&String> = all
        .iter()
        .flatten()
        .chain(deep.iter().flat_map(|(_, s)| s))
        .collect();
    write(
        &format!("{dir}/vocab.txt"),
        vocab.iter().map(|w| w.to_string()),
    );
    write(
        &format!("{dir}/deep.txt"),
        deep.iter().map(|(t, s)| format!("{t}\t{}", s.join(" "))),
    );
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
    // Negative test: development sentences with two words swapped, kept only
    // when the report's analysis rejects them. A learner that derives these
    // overgenerates.
    let sys = paraphrase();
    let mut rng = Rng(DEEP_SEED + 100);
    let mut negative: Vec<Sentence> = Vec::new();
    while negative.len() < SAMPLES {
        let mut s = held[(rng.draw() as usize) % held.len()].clone();
        let (i, j) = (
            (rng.draw() as usize) % (s.len() - 1),
            (rng.draw() as usize) % (s.len() - 1),
        );
        if s[i] == s[j] {
            continue;
        }
        s.swap(i, j);
        if analyse(&sys, &s).is_none() {
            negative.push(s);
        }
    }
    write(
        &format!("{dir}/negative.txt"),
        negative.iter().map(|s| s.join(" ")),
    );
    write(
        &format!("{dir}/deep-seen.txt"),
        deep_seen
            .iter()
            .map(|(t, s)| format!("{t}\t{}", s.join(" "))),
    );
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

/// The judge of a language directory: Colmerauer's analysis, or the
/// generating grammar of a family (when DIR/family.txt exists).
enum Judge {
    Colmerauer(Vec<qsystems::machine::System>),
    Family(q_lm::family::Family),
}

impl Judge {
    fn load(dir: &str) -> Judge {
        match fs::read_to_string(format!("{dir}/family.txt")) {
            Ok(t) => Judge::Family(q_lm::family::Family::parse(&t)),
            Err(_) => Judge::Colmerauer(paraphrase()),
        }
    }
    /// The depth of a grammatical sentence; None if ungrammatical.
    fn depth(&self, s: &[String]) -> Option<usize> {
        match self {
            Judge::Colmerauer(sys) => analyse(sys, s).map(|t| depth(&t)),
            Judge::Family(f) => f.depth(s),
        }
    }
}

/// Judgement of samples: grammatical, not in the training sentences, and
/// grammatical with two or more levels of embedding.
struct Judged {
    grammatical: usize,
    novel_grammatical: usize,
    deep_grammatical: usize,
}

fn judge_all(judge: &Judge, samples: &[Sentence], train: &BTreeSet<&Sentence>) -> Judged {
    let mut j = Judged {
        grammatical: 0,
        novel_grammatical: 0,
        deep_grammatical: 0,
    };
    for s in samples {
        if let Some(d) = judge.depth(s) {
            j.grammatical += 1;
            j.novel_grammatical += !train.contains(s) as usize;
            j.deep_grammatical += (d >= 2) as usize;
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
fn normalisation<F: FnMut(&[String], &str) -> f64>(
    vocab: &[String],
    sets: [&[Sentence]; 2],
    mut p: F,
) -> f64 {
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
        .map(|j| {
            format!(
                "{} | {} | {}",
                j.grammatical, j.novel_grammatical, j.deep_grammatical
            )
        })
        .unwrap_or("– | – | –".into());
    let n = r.norm.map(|n| format!("{n:.1e}")).unwrap_or("–".into());
    println!(
        "| {} | {:.4} | {} | {} | {j} | {n} |",
        r.name, r.held, r.deep, r.deep_seen
    );
}

fn report(dir: &str) {
    let judge = Judge::load(dir);
    let train = read(&format!("{dir}/train.txt"));
    let held = read(&format!("{dir}/dev.txt"));
    let deep = read(&format!("{dir}/deep.txt"));
    let deep_seen = read(&format!("{dir}/deep-seen.txt"));
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt"))
        .unwrap()
        .lines()
        .map(String::from)
        .collect();
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
    let open_samples: Vec<Sentence> = (0..SAMPLES)
        .map(|_| qsystems::open::sample(prior, None, &mut seed))
        .collect();
    print(&Row {
        name: "the report's rules as an open grammar (E17, given the grammar)".into(),
        held: open_bits(&held),
        deep: format!("{:.4}", open_bits(&deep)),
        deep_seen: format!("{:.4}", open_bits(&deep_seen)),
        judged: Some(judge_all(&judge, &open_samples, &train_set)),
        norm: None,
    });

    for n in sizes(train.len()) {
        let sub = &train[..n];
        let sub_set: BTreeSet<&Sentence> = sub.iter().collect();
        let words: BTreeSet<&String> = sub.iter().flatten().collect();
        let covered = deep_seen
            .iter()
            .filter(|s| s.iter().all(|w| words.contains(w)))
            .count();
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
                name: format!(
                    "Kneser–Ney {order}-gram, {n} sentences ({} n-grams, {secs:.2} s)",
                    m.size()
                ),
                held: per_token(&held, p),
                deep: format!("{:.4}", per_token(&deep, p)),
                deep_seen: format!("{:.4}", per_token(&deep_seen, p)),
                judged: Some(judge_all(&judge, &samples, &sub_set)),
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
            let p = |prefix: &[String], t: &str| {
                if m.reachable(prefix) {
                    0.999 * m.p(prefix, t) + 0.001 / v
                } else {
                    1.0 / v
                }
            };
            let allowed = |set: &[Sentence]| {
                set.iter()
                    .filter(|s| bits(s, |pr: &[String], t: &str| m.p(pr, t)).is_finite())
                    .count()
            };
            let mut rng = Rng(SAMPLE_SEED);
            let samples: Vec<Sentence> = (0..SAMPLES).map(|_| m.sample(&mut rng, 200)).collect();
            print(&Row {
                name: format!("merged graph, k = {k}, {n} sentences ({} states, {} arrows, {secs:.2} s; bits with the floor, samples without)", m.states(), m.size()),
                held: per_token(&held, p),
                deep: format!("{:.4} ({} allowed)", per_token(&deep, p), allowed(&deep)),
                deep_seen: format!("{:.4} ({} allowed)", per_token(&deep_seen, p), allowed(&deep_seen)),
                judged: Some(judge_all(&judge, &samples, &sub_set)),
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
                judged: Some(judge_all(&judge, &samples, &sub_set)),
                norm: Some(norm),
            });
        }
    }

    // Transformer learning curves: steps to come within 1% and 5% of the
    // floor on held-out sentences.
    println!("\n**Transformer learning curves.** The floor is {floor:.4} bits per token on the development sentences. Steps (of 64 sentences each) until the bits first come within 5% and within 1% of it, from the curve each run writes (bits on the first 2,000 development sentences, every 250 steps).\n");
    println!("| run | within 5% | within 1% | best | at step |");
    println!("|---|---:|---:|---:|---:|");
    let mut curves: Vec<String> = fs::read_dir(dir)
        .unwrap()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().to_string())
        .filter(|f| f.ends_with(".curve"))
        .collect();
    curves.sort_by_key(|f| {
        (
            f.split('-')
                .nth(1)
                .and_then(|n| n.parse::<usize>().ok())
                .unwrap_or(0),
            f.clone(),
        )
    });
    for f in curves {
        let pts: Vec<(usize, f64)> = fs::read_to_string(format!("{dir}/{f}"))
            .unwrap()
            .lines()
            .map(|l| {
                let mut w = l.split_whitespace();
                (
                    w.next().unwrap().parse().unwrap(),
                    w.next().unwrap().parse().unwrap(),
                )
            })
            .collect();
        let first = |frac: f64| {
            pts.iter()
                .find(|(_, b)| *b <= floor * (1.0 + frac))
                .map(|(s, _)| s.to_string())
                .unwrap_or("never".into())
        };
        let best = pts
            .iter()
            .cloned()
            .fold((0, f64::INFINITY), |a, b| if b.1 < a.1 { b } else { a });
        println!(
            "| {} | {} | {} | {:.4} | {} |",
            f.trim_end_matches(".curve"),
            first(0.05),
            first(0.01),
            best.1,
            best.0
        );
    }
}

/// QLM-003: the substitutability learner at each training size.
fn subst(dir: &str, largest: usize) {
    let judge = Judge::load(dir);
    use q_lm::subst::Subst;
    let train = read(&format!("{dir}/train.txt"));
    let dev = read(&format!("{dir}/dev.txt"));
    let deep = read(&format!("{dir}/deep.txt"));
    let deep_seen = read(&format!("{dir}/deep-seen.txt"));
    let negative = read(&format!("{dir}/negative.txt"));
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt"))
        .unwrap()
        .lines()
        .map(String::from)
        .collect();
    let v = vocab.len() as f64 + 1.0;
    println!("| training sentences | categories | rules | trained in | development: derivable | bits/token | deeper: derivable | deeper, corpus words: derivable | ungrammatical: derivable | P(derivation finishes) | samples finished | grammatical | of them not in training | of them deeper |");
    println!("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|");
    for n in sizes(train.len()).into_iter().filter(|&n| n <= largest) {
        let sub = &train[..n];
        let sub_set: BTreeSet<&Sentence> = sub.iter().collect();
        for em in [0usize, 5] {
            let t = Instant::now();
            let mut m = Subst::train(sub, &vocab);
            if em > 0 {
                m.em(sub, em, 1e-3);
            }
            let secs = t.elapsed().as_secs_f64();
            let derivable =
                |set: &[Sentence]| set.iter().filter(|s| m.probability(s) > 0.0).count();
            // Bits: the grammar with a floor, a uniform model of one part in a
            // thousand mixed in at the level of the sentence.
            let (mut total, mut tokens, mut ok) = (0.0, 0usize, 0);
            for s in &dev {
                let p = m.probability(s);
                ok += (p > 0.0) as usize;
                let floor = (1.0 / v).powi(s.len() as i32 + 1);
                total -= (0.999 * p + 0.001 * floor).log2();
                tokens += s.len() + 1;
            }
            let mut rng = Rng(SAMPLE_SEED);
            let drawn: Vec<Option<Sentence>> =
                (0..SAMPLES).map(|_| m.sample(&mut rng, 200)).collect();
            let finished: Vec<Sentence> = drawn.into_iter().flatten().collect();
            let j = judge_all(&judge, &finished, &sub_set);
            println!(
            "| {n}{} | {} | {} | {secs:.2} s | {ok} of {} | {:.4} | {} of {} | {} of {} | {} of {} | {:.6} | {} | {} | {} | {} |",
            if em > 0 { format!(", then {em} rounds of inside–outside") } else { String::new() },
            m.categories,
            m.size(),
            dev.len(),
            total / tokens as f64,
            derivable(&deep),
            deep.len(),
            derivable(&deep_seen),
            deep_seen.len(),
            derivable(&negative),
            negative.len(),
            m.termination(),
            finished.len(),
            j.grammatical,
            j.novel_grammatical,
            j.deep_grammatical
        );
            // The largest categories, for inspection.
            let mut cats: Vec<(&u32, &usize)> = m.member_count.iter().collect();
            cats.sort_by(|a, b| b.1.cmp(a.1));
            for (c, count) in cats.iter().take(6) {
                eprintln!(
                    "  {n}: category {c}, {count} members: {}",
                    m.examples[c].join(" | ")
                );
            }
        }
    }
}

/// QLM-003 qualification: the learned grammar as an autoregressive model.
fn prefix(dir: &str, n: usize) {
    use q_lm::prefix::Prefix;
    use q_lm::subst::Subst;
    let train = read(&format!("{dir}/train.txt"));
    let dev = read(&format!("{dir}/dev.txt"));
    let deep_seen = read(&format!("{dir}/deep-seen.txt"));
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt")).unwrap().lines().map(String::from).collect();
    let mut g = Subst::train(&train[..n], &vocab);
    g.em(&train[..n], 5, 1e-3);
    let t = Instant::now();
    let pf = Prefix::new(&g);
    println!("{n} training sentences: {} categories, {} rules; P(derivation finishes) {:.9}; left-corner closure in {:.2} s", g.categories, g.size(), pf.q[&g.start], t.elapsed().as_secs_f64());
    // Identities: next-token probabilities (END included) sum to the prefix
    // probability; their product along a sentence is its inside probability.
    let (mut norm, mut chain, mut tokens, mut secs, mut bits): (f64, f64, usize, f64, f64) = (0.0, 0.0, 0, 0.0, 0.0);
    for (set, name) in [(&dev[..200], "development"), (&deep_seen[..100], "deeper, corpus words")] {
        let (mut b, mut toks) = (0.0, 0);
        for s in set {
            let mut r = pf.start();
            let mut logp = 0.0;
            for i in 0..=s.len() {
                let t = Instant::now();
                let next = pf.next(&r);
                secs += t.elapsed().as_secs_f64();
                tokens += 1;
                let z: f64 = next.values().sum();
                norm = norm.max(((z - r.prob) / r.prob).abs());
                let w = s.get(i).map(|x| x.as_str()).unwrap_or(END);
                logp += (next[w] / z).log2();
                if i < s.len() {
                    pf.step(&mut r, g.word_id(w).unwrap());
                }
            }
            let direct = g.probability(s).log2();
            chain = chain.max((logp - direct).abs());
            b -= logp;
            toks += s.len() + 1;
        }
        bits = b / toks as f64;
        println!("  {name}: {} sentences, {:.4} bits/token read word by word", set.len(), bits);
    }
    let _ = bits;
    println!("  most a next-token distribution strays from the prefix probability (relative): {norm:.2e}");
    println!("  most the chain of next-token probabilities strays from the sentence probability: {chain:.2e} bits");
    println!("  {:.2} ms per next-token distribution ({} distributions)", 1000.0 * secs / tokens as f64, tokens);
    // Sampling agreement: the first word, from 20,000 derivations drawn
    // directly, against the exact distribution.
    let exact = pf.next(&pf.start());
    let z: f64 = exact.values().sum();
    let mut rng = Rng(SAMPLE_SEED);
    let mut seen: std::collections::BTreeMap<String, f64> = Default::default();
    let mut drawn = 0.0;
    for _ in 0..20_000 {
        if let Some(s) = g.sample(&mut rng, 400) {
            *seen.entry(s[0].clone()).or_insert(0.0) += 1.0;
            drawn += 1.0;
        }
    }
    let tv: f64 = exact.iter().map(|(w, p)| (p / z - seen.get(w).copied().unwrap_or(0.0) / drawn).abs()).sum::<f64>() / 2.0;
    println!("  first word: total variation between exact and 20,000 direct samples {tv:.4} ({drawn} finished)");
}

/// Bits per token (END included) of a learned grammar, with the floor used
/// throughout: 0.999 P(s) + 0.001 of a uniform spelling.
fn floored(m: &q_lm::subst::Subst, set: &[Sentence], v: f64) -> f64 {
    let (mut total, mut tokens) = (0.0, 0usize);
    for s in set {
        let floor = (1.0 / v).powi(s.len() as i32 + 1);
        total -= (0.999 * m.probability(s) + 0.001 * floor).log2();
        tokens += s.len() + 1;
    }
    total / tokens as f64
}

/// Inside–outside convergence: the grammar learned from n sentences, scored
/// after each of a set of rounds.
fn em_curve(dir: &str, n: usize) {
    let judge = Judge::load(dir);
    use q_lm::subst::Subst;
    let train = read(&format!("{dir}/train.txt"));
    let dev = read(&format!("{dir}/dev.txt"));
    let deep_seen = read(&format!("{dir}/deep-seen.txt"));
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt")).unwrap().lines().map(String::from).collect();
    let v = vocab.len() as f64 + 1.0;
    let sub = &train[..n];
    let sub_set: BTreeSet<&Sentence> = sub.iter().collect();
    let mut m = Subst::train(sub, &vocab);
    println!("| rounds | training bits/token | development (first 200) bits/token | deeper, corpus words (first 100) bits/token | P(finishes) | grammatical samples | not in training | deeper | seconds so far |");
    println!("|---:|---:|---:|---:|---:|---:|---:|---:|---:|");
    let t = Instant::now();
    let mut done = 0;
    for r in [0usize, 1, 2, 3, 5, 8, 12, 20, 30, 40] {
        if r > done {
            m.em(sub, r - done, 1e-3);
        }
        done = r;
        let tb = floored(&m, sub, v);
        let mut rng = Rng(SAMPLE_SEED);
        let finished: Vec<Sentence> = (0..SAMPLES).filter_map(|_| m.sample(&mut rng, 200)).collect();
        let j = judge_all(&judge, &finished, &sub_set);
        println!(
            "| {r} | {tb:.4} | {:.4} | {:.4} | {:.6} | {} of {} | {} | {} | {:.0} |",
            floored(&m, &dev[..200], v), floored(&m, &deep_seen[..100], v), m.termination(),
            j.grammatical, finished.len(), j.novel_grammatical, j.deep_grammatical, t.elapsed().as_secs_f64()
        );
    }
}

/// QLM-005: a language from a seeded random grammar, written as `data`
/// writes Colmerauer's (docs/qlm005-plan.md).
fn family_data(dir: &str, kind: &str, seed: u64) {
    use q_lm::family::{Family, Kind};
    let f = Family::generate(Kind::parse(kind).expect("kind: right, centre or left"), seed);
    fs::create_dir_all(dir).unwrap();
    fs::write(format!("{dir}/family.txt"), f.text()).unwrap();
    let (all, ambiguous) = f.corpus();
    let (train, held, confirm) = split(&all, SPLIT_SEED);
    let j = |v: &Vec<Sentence>| v.iter().map(|s| s.join(" ")).collect::<Vec<_>>().into_iter();
    write(&format!("{dir}/train.txt"), j(&train));
    write(&format!("{dir}/dev.txt"), j(&held));
    write(&format!("{dir}/confirm.txt"), j(&confirm));
    for n in sizes(train.len()) {
        write(&format!("{dir}/train-{n}.txt"), train.iter().take(n).map(|s| s.join(" ")));
    }
    // Deeper sentences: depth exactly 2 by the judge, at most 60 words.
    let seen: BTreeSet<&String> = train.iter().flatten().collect();
    let (mut deep, mut deep_seen) = (Vec::new(), Vec::new());
    let mut rng = Rng(DEEP_SEED);
    while deep.len() < SAMPLES || deep_seen.len() < SAMPLES {
        let s = f.derive(&mut rng, 2);
        if s.len() > 60 || f.depth(&s) != Some(2) {
            continue;
        }
        if deep.len() < SAMPLES {
            deep.push(s.clone());
        } else if s.iter().all(|w| seen.contains(w)) {
            deep_seen.push(s);
        }
    }
    let mut negative: Vec<Sentence> = Vec::new();
    let mut rng = Rng(DEEP_SEED + 100);
    while negative.len() < SAMPLES {
        let mut s = held[(rng.draw() as usize) % held.len()].clone();
        let (a, b) = ((rng.draw() as usize) % s.len(), (rng.draw() as usize) % s.len());
        if s[a] == s[b] {
            continue;
        }
        s.swap(a, b);
        if f.depth(&s).is_none() {
            negative.push(s);
        }
    }
    let vocab: BTreeSet<&String> = all.iter().flatten().chain(deep.iter().flatten()).collect();
    write(&format!("{dir}/vocab.txt"), vocab.iter().map(|w| w.to_string()));
    write(&format!("{dir}/deep.txt"), j(&deep));
    write(&format!("{dir}/deep-seen.txt"), j(&deep_seen));
    write(&format!("{dir}/negative.txt"), j(&negative));
    fs::write(format!("{dir}/corpus-size.txt"), format!("{} {}\n", all.len(), ambiguous)).unwrap();
    print!("{}", f.text());
    println!(
        "{} sentences ({} trees share a sentence with another): {} to train on, {} for development, {} for confirmation; {} words",
        all.len(), ambiguous, train.len(), held.len(), confirm.len(), vocab.len()
    );
}

/// QLM-005: the plan's measures on one language directory.
fn compare(dir: &str) {
    use q_lm::prefix::Prefix;
    use q_lm::subst::Subst;
    let judge = Judge::load(dir);
    let train = read(&format!("{dir}/train.txt"));
    let dev = read(&format!("{dir}/dev.txt"));
    let deep = read(&format!("{dir}/deep.txt"));
    let deep_seen = read(&format!("{dir}/deep-seen.txt"));
    let negative = read(&format!("{dir}/negative.txt"));
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt")).unwrap().lines().map(String::from).collect();
    let v = vocab.len() as f64 + 1.0;
    let size: f64 = fs::read_to_string(format!("{dir}/corpus-size.txt"))
        .map(|t| t.split_whitespace().next().unwrap().parse().unwrap())
        .unwrap_or(f64::NAN);
    let dev_tokens: usize = dev.iter().map(|s| s.len() + 1).sum();
    if let Ok(t) = fs::read_to_string(format!("{dir}/family.txt")) {
        println!("```\n{t}```\n");
    }
    println!(
        "{} training sentences, {} development, {} deeper; floor (uniform over the {size} corpus sentences) {:.4} bits/token on development\n",
        train.len(), dev.len(), deep.len(), size.log2() * dev.len() as f64 / dev_tokens as f64
    );
    println!("| model | categories | rules | development | deeper | deeper, corpus words | deeper derivable | deeper, corpus words derivable | ungrammatical derivable | grammatical samples | not in training | deeper samples | ms per next token |");
    println!("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|");
    let count = |m: &Subst, set: &[Sentence]| set.iter().filter(|s| m.probability(s) > 0.0).count();
    let ms = |m: &Subst| {
        let pf = Prefix::new(m);
        let (mut secs, mut k) = (0.0, 0);
        for s in &dev[..20] {
            let mut r = pf.start();
            for i in 0..=s.len() {
                let t = Instant::now();
                let _ = pf.next(&r);
                secs += t.elapsed().as_secs_f64();
                k += 1;
                if i < s.len() {
                    match m.word_id(&s[i]) {
                        Some(w) => pf.step(&mut r, w),
                        None => break,
                    }
                }
            }
        }
        1000.0 * secs / k as f64
    };
    for n in sizes(train.len()) {
        let sub = &train[..n];
        let sub_set: BTreeSet<&Sentence> = sub.iter().collect();
        println!("| *{n} training sentences* | | | | | | | | | | | | |");
        let row = |name: String, m: &Subst, timed: bool| {
            let mut rng = Rng(SAMPLE_SEED);
            let finished: Vec<Sentence> = (0..SAMPLES).filter_map(|_| m.sample(&mut rng, 200)).collect();
            let j = judge_all(&judge, &finished, &sub_set);
            println!(
                "| {name} | {} | {} | {:.4} | {:.4} | {:.4} | {} | {} | {} | {} of {} | {} | {} | {} |",
                m.categories, m.size(),
                floored(m, &dev, v), floored(m, &deep, v), floored(m, &deep_seen, v),
                count(m, &deep), count(m, &deep_seen), count(m, &negative),
                j.grammatical, finished.len(), j.novel_grammatical, j.deep_grammatical,
                if timed { format!("{:.2}", ms(m)) } else { "–".into() }
            );
        };
        for order in [3, 6] {
            let m = KneserNey::train(sub, &vocab, order, 0.75);
            let p = |prefix: &[String], t: &str| m.p(prefix, t);
            let mut rng = Rng(SAMPLE_SEED);
            let samples: Vec<Sentence> = (0..SAMPLES).map(|_| m.sample(&mut rng, 200)).collect();
            let j = judge_all(&judge, &samples, &sub_set);
            println!(
                "| Kneser–Ney {order}-gram | | {} | {:.4} | {:.4} | {:.4} | | | | {} of {SAMPLES} | {} | {} | |",
                m.size(), per_token(&dev, p), per_token(&deep, p), per_token(&deep_seen, p),
                j.grammatical, j.novel_grammatical, j.deep_grammatical
            );
        }
        let mut m = Subst::train(sub, &vocab);
        let mut done = 0;
        let mut base = None;
        for r in [2usize, 5, 20] {
            m.em(sub, r - done, 1e-3);
            done = r;
            if r == 5 {
                base = Some(m.clone());
            }
            row(format!("grammar, {r} rounds{}", if r == 20 { " (reported)" } else { " (diagnostic)" }), &m, r == 20);
        }
        // Pruning: the threshold by development bits; the description-length
        // choice beside it.
        let base = base.unwrap();
        let (mut by_dev, mut by_dl): ((f64, f64, Option<Subst>), (f64, f64, Option<Subst>)) =
            ((f64::INFINITY, 0.0, None), (f64::INFINITY, 0.0, None));
        for tau in [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0] {
            let mut p = base.clone();
            p.prune(tau);
            if !p.rules.contains_key(&p.start) {
                break;
            }
            p.em(sub, 5, 1e-3);
            let d = floored(&p, &dev, v);
            let (g, data, _) = p.description_length(sub);
            if d < by_dev.0 {
                by_dev = (d, tau, Some(p.clone()));
            }
            if g + data < by_dl.0 {
                by_dl = (g + data, tau, Some(p));
            }
        }
        row(format!("grammar, pruned at {} (chosen by development)", by_dev.1), by_dev.2.as_ref().unwrap(), true);
        row(format!("grammar, pruned at {} (shortest description)", by_dl.1), by_dl.2.as_ref().unwrap(), true);
        let mut files: Vec<String> = fs::read_dir(dir)
            .unwrap()
            .flatten()
            .map(|e| e.file_name().to_string_lossy().to_string())
            .filter(|f| {
                ["transformer", "llama", "gpt2"].iter().any(|a| f.starts_with(&format!("{a}-{n}-"))) && f.ends_with(".bits")
            })
            .collect();
        files.sort();
        for f in files {
            let model = f.trim_end_matches(".bits");
            let text = fs::read_to_string(format!("{dir}/{f}")).unwrap();
            let x: Vec<f64> = text.split_whitespace().take(3).map(|t| t.parse().unwrap()).collect();
            let samples = read(&format!("{dir}/{model}.samples"));
            let j = judge_all(&judge, &samples, &sub_set);
            println!(
                "| {model} | | {} weights | {:.4} | {:.4} | {:.4} | | | | {} of {SAMPLES} | {} | {} | |",
                text.split_whitespace().find_map(|t| t.strip_prefix("params=")).unwrap_or("?"),
                x[0], x[1], x[2], j.grammatical, j.novel_grammatical, j.deep_grammatical
            );
        }
    }
}

/// Bits per token of the grammar learned from n sentences after `rounds`
/// of inside–outside, on each file given (one sentence per line).
fn score(dir: &str, n: usize, rounds: usize, files: &[String]) {
    use q_lm::subst::Subst;
    let train = read(&format!("{dir}/train.txt"));
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt")).unwrap().lines().map(String::from).collect();
    let v = vocab.len() as f64 + 1.0;
    let mut m = Subst::train(&train[..n], &vocab);
    m.em(&train[..n], rounds, 1e-3);
    for f in files {
        let set = read(f);
        println!("{f}: {} sentences, {:.4} bits/token", set.len(), floored(&m, &set, v));
    }
}

/// QLM-LEFT-001: where substitutability goes wrong on a family. Every
/// substring is given its true type (the symbols of the generating grammar
/// that derive it; "none" if no constituent), and the learner's merges and
/// categories are read against it.
fn trace(dir: &str, n: usize) {
    use q_lm::family::{Family, Sym};
    use q_lm::subst::{Merge, Subst};
    use std::collections::BTreeMap;
    let f = Family::parse(&fs::read_to_string(format!("{dir}/family.txt")).expect("a family directory"));
    let train = read(&format!("{dir}/train.txt"));
    let negative = read(&format!("{dir}/negative.txt"));
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt")).unwrap().lines().map(String::from).collect();
    let mut log: Vec<Merge> = Vec::new();
    let mut m = Subst::train_logged(&train[..n], &vocab, Some(&mut log));
    m.em(&train[..n], 20, 1e-3);
    let words = |w: &[u32]| w.iter().map(|&t| m.word_list[t as usize].as_str()).collect::<Vec<_>>().join(" ");
    let mut sig_cache: HashMap<Vec<u32>, String> = HashMap::new();
    let mut sig = |w: &[u32]| -> String {
        sig_cache
            .entry(w.to_vec())
            .or_insert_with(|| {
                let s: Vec<String> = w.iter().map(|&t| m.word_list[t as usize].clone()).collect();
                let mut t: Vec<String> = f
                    .derivations(&s)
                    .keys()
                    .map(|y| match y {
                        Sym::Class(c) => c.clone(),
                        other => format!("{other:?}"),
                    })
                    .collect();
                t.sort();
                if t.is_empty() { "none".into() } else { t.join("+") }
            })
            .clone()
    };
    println!("{n} training sentences: {} categories, {} rules, {} unions\n", m.categories, m.size(), log.len());
    // Categories by the true types of their members.
    let mut by_cat: BTreeMap<u32, BTreeMap<String, Vec<Vec<u32>>>> = BTreeMap::new();
    for (w, &c) in &m.category_of {
        by_cat.entry(c).or_default().entry(sig(w)).or_default().push(w.clone());
    }
    let mut mixed: Vec<(u32, usize, &BTreeMap<String, Vec<Vec<u32>>>)> = by_cat
        .iter()
        .filter(|(_, t)| t.len() > 1)
        .map(|(&c, t)| (c, t.values().map(|v| v.len()).sum(), t))
        .collect();
    mixed.sort_by_key(|x| std::cmp::Reverse(x.1));
    println!("**Categories whose members have more than one true type: {} of {}.**\n", mixed.len(), by_cat.len());
    for (c, total, t) in mixed.iter().take(8) {
        println!("- category {c}, {total} members:");
        for (s, ws) in t.iter() {
            let mut ex: Vec<&Vec<u32>> = ws.iter().collect();
            ex.sort_by_key(|w| w.len());
            println!("  - {s} ({}): {}", ws.len(), ex.iter().take(4).map(|w| format!("`{}`", words(w))).collect::<Vec<_>>().join(", "));
        }
    }
    // Unions across true types, in the order made.
    let mut crossing: BTreeMap<(String, String), (usize, Option<&Merge>)> = BTreeMap::new();
    for mg in &log {
        let (x, y) = (sig(&mg.a), sig(&mg.b));
        if x != y {
            let k = if x < y { (x, y) } else { (y, x) };
            let e = crossing.entry(k).or_insert((0, None));
            e.0 += 1;
            e.1.get_or_insert(mg);
        }
    }
    println!("\n**Unions across true types: {} of {}.** By pair of types, with the first such union and the context that made it:\n", crossing.values().map(|v| v.0).sum::<usize>(), log.len());
    let mut cr: Vec<_> = crossing.iter().collect();
    cr.sort_by_key(|x| std::cmp::Reverse(x.1 .0));
    for ((x, y), (count, first)) in cr.iter().take(12) {
        let mg = first.unwrap();
        println!("- {x} with {y}: {count} unions; first `{}` with `{}` in `{} _ {}`", words(&mg.a), words(&mg.b), words(&mg.left), words(&mg.right));
    }
    // The most probable derivation of accepted ungrammatical sentences.
    println!("\n**Ungrammatical sentences the grammar derives**, most probable derivation, each node with its span's true type:\n");
    let mut shown = 0;
    let mut accepted = 0;
    for s in &negative {
        if m.probability(s) == 0.0 {
            continue;
        }
        accepted += 1;
        if shown >= 4 {
            continue;
        }
        shown += 1;
        let ws: Vec<u32> = s.iter().map(|w| m.word_id(w).unwrap()).collect();
        let k = ws.len();
        // Viterbi: best[i][j][cat] = (prob, split, left cat, right cat).
        let mut best: Vec<Vec<HashMap<u32, (f64, usize, u32, u32)>>> = vec![vec![HashMap::new(); k + 1]; k + 1];
        for i in 0..k {
            for &(a, p) in m.lexical.get(&ws[i]).into_iter().flatten() {
                best[i][i + 1].insert(a, (p, 0, u32::MAX, 0));
            }
        }
        for len in 2..=k {
            for i in 0..=k - len {
                let j = i + len;
                let mut cell: HashMap<u32, (f64, usize, u32, u32)> = HashMap::new();
                for mid in i + 1..j {
                    for (&b, &(pb, ..)) in &best[i][mid] {
                        for (&c, &(pc, ..)) in &best[mid][j] {
                            for &(a, p) in m.binary.get(&(b, c)).into_iter().flatten() {
                                let v = p * pb * pc;
                                if cell.get(&a).is_none_or(|x| x.0 < v) {
                                    cell.insert(a, (v, mid, b, c));
                                }
                            }
                        }
                    }
                }
                best[i][j] = cell;
            }
        }
        fn show(best: &[Vec<HashMap<u32, (f64, usize, u32, u32)>>], i: usize, j: usize, a: u32, depth: usize, out: &mut Vec<(usize, usize, usize, u32)>) {
            out.push((depth, i, j, a));
            let (_, mid, b, c) = best[i][j][&a];
            if b != u32::MAX {
                show(best, i, mid, b, depth + 1, out);
                show(best, mid, j, c, depth + 1, out);
            }
        }
        let mut nodes = Vec::new();
        show(&best, 0, k, m.start, 0, &mut nodes);
        println!("`{}`\n", s.join(" "));
        println!("```");
        for (d, i, j, a) in nodes {
            if j - i > 1 {
                println!("{}[{a}] {}   ({})", "  ".repeat(d), words(&ws[i..j]), sig(&ws[i..j]));
            }
        }
        println!("```\n");
    }
    println!("{accepted} of {} ungrammatical sentences derived.", negative.len());
}

/// QLM-EQUIV-001: fresh ungrammatical sentences, unseen by any analysis so
/// far. 300 from development (seed 501), 300 from confirmation (seed 502).
/// Two words of a sentence swapped, kept only if the judge rejects it.
fn negatives(dir: &str) {
    let judge = Judge::load(dir);
    for (src, out, seed) in [("dev", "negative-dev", 501u64), ("confirm", "negative-confirm", 502)] {
        let set = read(&format!("{dir}/{src}.txt"));
        let mut rng = Rng(seed);
        let mut neg: Vec<Sentence> = Vec::new();
        let mut seen: BTreeSet<Sentence> = BTreeSet::new();
        while neg.len() < SAMPLES {
            let mut s = set[(rng.draw() as usize) % set.len()].clone();
            let (a, b) = ((rng.draw() as usize) % s.len(), (rng.draw() as usize) % s.len());
            if s[a] == s[b] {
                continue;
            }
            s.swap(a, b);
            if judge.depth(&s).is_none() && seen.insert(s.clone()) {
                neg.push(s);
            }
        }
        write(&format!("{dir}/{out}.txt"), neg.iter().map(|s| s.join(" ")));
    }
    println!("{dir}: negative-dev.txt and negative-confirm.txt, {SAMPLES} each");
}

/// QLM-SEMANTIC-001: a world and its text, written as `data` writes a
/// language: 20,000 training texts, 2,000 development, 2,000 confirmation,
/// the held-out statements as deep.txt (and deep-seen.txt, for the
/// transformer scripts), and the fact tests as tests.tsv.
fn semantic_data(dir: &str, seed: u64, variant: &str) {
    use q_lm::semantic::{Rel, Statement, World};
    let w = match variant {
        "v3" => World::v3(seed),
        "by-person" => World::with_holdout(seed, false),
        _ => World::new(seed),
    };
    fs::create_dir_all(dir).unwrap();
    let mut r = Rng(seed * 1000 + 1);
    let train = w.corpus(20_000, &mut r);
    let dev: Vec<String> = (0..2_000).map(|_| w.line(&w.text(&mut r))).collect();
    let confirm: Vec<String> = (0..2_000).map(|_| w.line(&w.text(&mut r))).collect();
    write(&format!("{dir}/train.txt"), train.iter().cloned());
    for n in sizes(train.len()) {
        write(&format!("{dir}/train-{n}.txt"), train.iter().take(n).cloned());
    }
    write(&format!("{dir}/dev.txt"), dev.into_iter());
    write(&format!("{dir}/confirm.txt"), confirm.into_iter());
    // Every held-out statement, rendered.
    let mut held: Vec<String> = Vec::new();
    for c in 0..q_lm::semantic::COUNTRIES {
        let k = w.capital[c];
        for ph in 0..2 {
            for st in [Statement { rel: Rel::Capital, subject: c, object: k, phrasing: ph }, Statement { rel: Rel::Located, subject: k, object: c, phrasing: ph }] {
                if !w.allowed(&st) {
                    held.push(w.render(&st));
                }
            }
        }
    }
    for p in 0..q_lm::semantic::PEOPLE {
        let st = Statement { rel: Rel::LivesOn, subject: p, object: w.lives_on(p), phrasing: 0 };
        if !w.allowed(&st) {
            held.push(w.render(&st));
        }
    }
    write(&format!("{dir}/deep.txt"), held.iter().cloned());
    write(&format!("{dir}/deep-seen.txt"), held.iter().cloned());
    let words: BTreeSet<String> = train.iter().chain(held.iter()).flat_map(|l| l.split(' ').map(String::from)).collect();
    write(&format!("{dir}/vocab.txt"), words.iter().cloned());
    let tests = w.tests();
    write(&format!("{dir}/tests.tsv"), tests.iter().map(|(a, b, c, d)| format!("{a}\t{b}\t{c}\t{d}")));
    let types = [("city", &w.cities), ("country", &w.countries), ("continent", &w.continents)];
    write(&format!("{dir}/types.tsv"), types.iter().map(|(t, ns)| format!("{t}\t{}", ns.join(" "))));
    let mut facts = format!("world seed {seed}\n");
    for c in 0..q_lm::semantic::COUNTRIES {
        facts += &format!("{} capital {} continent {}\n", w.countries[c], w.cities[w.capital[c]], w.continents[w.continent[c]]);
    }
    for p in 0..q_lm::semantic::PEOPLE {
        facts += &format!("{} lives {} on {}\n", w.people[p], w.cities[w.lives[p]], w.continents[w.lives_on(p)]);
        if let Some(b) = &w.born {
            facts += &format!("{} born {}\n", w.people[p], w.cities[b[p]]);
        }
    }
    fs::write(format!("{dir}/world.txt"), facts).unwrap();
    let mut by: std::collections::BTreeMap<&str, usize> = Default::default();
    for t in &tests {
        *by.entry(t.0.as_str()).or_insert(0) += 1;
    }
    println!("world {seed}: {} training texts, {} words, {} held-out statements; tests {by:?}", train.len(), words.len(), held.len());
}

/// QLM-SEMANTIC-001: the fact tests, for the learned grammar (20 rounds) and
/// the Kneser–Ney shortcut baselines, trained on n texts.
fn facts(dir: &str, n: usize) {
    use q_lm::prefix::Prefix;
    use q_lm::subst::Subst;
    use std::collections::BTreeMap;
    let train = read(&format!("{dir}/train.txt"));
    let sub = &train[..n.min(train.len())];
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt")).unwrap().lines().map(String::from).collect();
    let types: HashMap<String, Vec<String>> = fs::read_to_string(format!("{dir}/types.tsv"))
        .unwrap()
        .lines()
        .map(|l| {
            let (t, ns) = l.split_once('\t').unwrap();
            (t.to_string(), ns.split(' ').map(String::from).collect())
        })
        .collect();
    let tests: Vec<Vec<String>> = fs::read_to_string(format!("{dir}/tests.tsv")).unwrap().lines().map(|l| l.split('\t').map(String::from).collect()).collect();
    // Scores each test with next(prefix) -> word -> probability.
    let score = |name: &str, next: &mut dyn FnMut(&[String]) -> HashMap<String, f64>| {
        let mut agg: BTreeMap<String, (usize, usize, f64, f64, f64, usize)> = BTreeMap::new();
        for t in &tests {
            let prefix: Vec<String> = t[1].split(' ').map(String::from).collect();
            let d = next(&prefix);
            let z: f64 = d.values().sum();
            let cands = &types[&t[3]];
            // The usual floor: 0.999 of the model, 0.001 uniform. A prefix
            // the model cannot continue gets only the floor.
            let u = 0.001 / (vocab.len() as f64 + 1.0);
            let p = |w: &String| u + if z > 0.0 { 0.999 * d.get(w).copied().unwrap_or(0.0) / z } else { 0.0 };
            let truth = p(&t[2]).max(1e-300);
            let top = cands.iter().map(p).fold(0.0, f64::max);
            let tied = cands.iter().filter(|w| p(w) == top).count();
            let false_mean = cands.iter().filter(|w| **w != t[2]).map(p).sum::<f64>() / (cands.len() - 1) as f64;
            let e = agg.entry(t[0].clone()).or_insert((0, 0, 0.0, 0.0, 0.0, 0));
            e.0 += 1;
            // Strict: the answer alone at the top. Tie-adjusted: 1/(number
            // tied) when the answer is among the tied top candidates.
            e.1 += (p(&t[2]) == top && tied == 1) as usize;
            e.4 += if p(&t[2]) == top { 1.0 / tied as f64 } else { 0.0 };
            // An abstention: the model gives the prefix probability 0 and
            // cannot continue it, so only the floor answers.
            e.5 += (z <= 0.0) as usize;
            e.2 -= truth.log2();
            e.3 += truth.log2() - false_mean.max(1e-300).log2();
        }
        for (test, (count, right, bits, contrast, adjusted, abstain)) in agg {
            println!(
                "| {name} | {test} | {count} | {abstain} | {:.1}% | {:.1}% | {:.2} | {:.2} |",
                100.0 * right as f64 / count as f64, 100.0 * adjusted / count as f64, bits / count as f64, contrast / count as f64
            );
        }
    };
    println!("{} training texts; every probability floored (0.999 model + 0.001 uniform)\n", sub.len());
    println!("| model | test | items | abstained (prefix underivable) | accuracy, strict | accuracy, tie-adjusted | bits on the answer | contrast, bits |");
    println!("|---|---|---:|---:|---:|---:|---:|---:|");
    for order in [2, 3] {
        let m = KneserNey::train(sub, &vocab, order, 0.75);
        let mut next = |prefix: &[String]| -> HashMap<String, f64> { vocab.iter().map(|w| (w.clone(), m.p(prefix, w))).collect() };
        score(&format!("Kneser–Ney {order}-gram (shortcut baseline)"), &mut next);
    }
    let t = Instant::now();
    let mut g = Subst::train(sub, &vocab);
    g.em(sub, 20, 1e-3);
    eprintln!("grammar: {} categories, {} rules, {:.1} s", g.categories, g.size(), t.elapsed().as_secs_f64());
    let pf = Prefix::new(&g);
    let mut next = |prefix: &[String]| -> HashMap<String, f64> {
        let mut r = pf.start();
        for w in prefix {
            match g.word_id(w) {
                Some(id) => pf.step(&mut r, id),
                None => return HashMap::new(),
            }
        }
        pf.next(&r).into_iter().collect()
    };
    score(&format!("grammar, 20 rounds ({} categories, {} rules)", g.categories, g.size()), &mut next);
}

/// QLM-SEMANTIC-001: the city-mate shortcut of the first design, tested at
/// the level of the learned categories. DIR is a world made with
/// `qlm semantic DIR SEED by-person`. For each held-out composition person:
/// does the learner put them in one category with their city-mate, and does
/// the grammar then give the city-mate's continent?
fn shortcut(dir: &str) {
    use q_lm::prefix::Prefix;
    use q_lm::subst::Subst;
    let train = read(&format!("{dir}/train.txt"));
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt")).unwrap().lines().map(String::from).collect();
    let world: Vec<Vec<String>> = fs::read_to_string(format!("{dir}/world.txt")).unwrap().lines().map(|l| l.split(' ').map(String::from).collect()).collect();
    let lives: HashMap<&str, (&str, &str)> = world.iter().filter(|w| w.len() == 5 && w[1] == "lives").map(|w| (w[0].as_str(), (w[2].as_str(), w[4].as_str()))).collect();
    let tests: Vec<Vec<String>> = fs::read_to_string(format!("{dir}/tests.tsv")).unwrap().lines().map(|l| l.split('\t').map(String::from).collect()).collect();
    let continents: Vec<String> = fs::read_to_string(format!("{dir}/types.tsv")).unwrap().lines().find(|l| l.starts_with("continent")).unwrap().split_once('\t').unwrap().1.split(' ').map(String::from).collect();
    let held: BTreeSet<&str> = tests.iter().filter(|t| t[0] == "composition" || t[0] == "new entity").map(|t| t[1].split(' ').next().unwrap()).collect();
    let mut log = Vec::new();
    let mut g = Subst::train_logged(&train, &vocab, Some(&mut log));
    g.em(&train, 20, 1e-3);
    let pf = Prefix::new(&g);
    println!("| person | city-mate | mate's lives-on in training | same category as mate | predicted | answer | right | others in the category with lives-on in training, by continent |");
    println!("|---|---|---|---|---|---|---|---|");
    let (mut same_right, mut same, mut diff_right, mut diff) = (0, 0, 0, 0);
    for t in tests.iter().filter(|t| t[0] == "composition") {
        let p = t[1].split(' ').next().unwrap();
        let (city, _) = lives[p];
        let mate = lives.iter().find(|(q, (c, _))| *q != &p && *c == city).map(|(q, _)| *q).unwrap();
        let cat = |w: &str| g.category_of.get(&vec![g.word_id(w).unwrap()]).copied();
        let together = cat(p).is_some() && cat(p) == cat(mate);
        let mut r = pf.start();
        for w in t[1].split(' ') {
            pf.step(&mut r, g.word_id(w).unwrap());
        }
        let next = pf.next(&r);
        let pred = continents.iter().max_by(|a, b| next.get(*a).unwrap_or(&0.0).partial_cmp(next.get(*b).unwrap_or(&0.0)).unwrap()).unwrap();
        let right = *pred == t[2];
        if together {
            same += 1;
            same_right += right as usize;
        } else {
            diff += 1;
            diff_right += right as usize;
        }
        // Everyone in P's category whose lives-on is in training, by their
        // continent.
        let mut others: std::collections::BTreeMap<&str, usize> = Default::default();
        for (q, (_, on)) in &lives {
            if *q != p && !held.contains(q) && cat(q).is_some() && cat(q) == cat(p) {
                *others.entry(on).or_insert(0) += 1;
            }
        }
        println!("| {p} | {mate} | {} | {together} | {pred} | {} | {right} | {others:?} |", !held.contains(mate), t[2]);
    }
    println!("\nIn one category with the city-mate: {same_right} of {same} right. Not: {diff_right} of {diff} right.");
}

/// LARQL-QLM-GROUP-001: the first 1,000 development sentences of a family,
/// every token labelled "word class slot depth" (one sentence per line,
/// tokens separated by tabs). The families are unambiguous, so each
/// sentence has exactly one labelled tree. Also writes the grammar
/// learner's most probable lexical category of each word (full training
/// size, 20 rounds).
fn roles(dir: &str) {
    use q_lm::family::{Family, Sym};
    use q_lm::subst::Subst;
    let f = Family::parse(&fs::read_to_string(format!("{dir}/family.txt")).unwrap());
    let mut by: HashMap<Vec<String>, Vec<(String, String, i32, usize)>> = HashMap::new();
    for t in f.labelled(&Sym::S, 1, -1, 0) {
        let words: Vec<String> = t.iter().map(|x| x.0.clone()).collect();
        assert!(by.insert(words, t).is_none(), "an ambiguous sentence");
    }
    let dev = read(&format!("{dir}/dev.txt"));
    write(
        &format!("{dir}/roles.txt"),
        dev.iter().take(1000).map(|s| by[s].iter().map(|(w, c, sl, d)| format!("{w} {c} {sl} {d}")).collect::<Vec<_>>().join("\t")),
    );
    let train = read(&format!("{dir}/train.txt"));
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt")).unwrap().lines().map(String::from).collect();
    let mut g = Subst::train(&train, &vocab);
    g.em(&train, 20, 1e-3);
    write(
        &format!("{dir}/lexical.txt"),
        vocab.iter().map(|w| {
            let best = g.word_id(w).and_then(|i| g.lexical.get(&i)).and_then(|cs| cs.iter().max_by(|a, b| a.1.partial_cmp(&b.1).unwrap())).map(|c| c.0 as i64).unwrap_or(-1);
            format!("{w} {best}")
        }),
    );
    println!("{dir}: roles.txt (1,000 sentences) and lexical.txt");
}

/// QLM-EQUIV-001: arms A (one shared context), B (at least k) and C
/// (overlap at least theta) on a language directory, at n training
/// sentences, each with 20 rounds of inside–outside. Within B and C, the
/// parameter is chosen by the shortest two-part description (training
/// sentences only), and every setting is reported. Ungrammatical sentences
/// are the fresh development negatives (negative-dev.txt).
fn equiv(dir: &str, n: usize) {
    use q_lm::subst::{MergeRule, Subst};
    let judge = Judge::load(dir);
    let train = read(&format!("{dir}/train.txt"));
    let n = n.min(train.len());
    let sub = &train[..n];
    let sub_set: BTreeSet<&Sentence> = sub.iter().collect();
    let dev = read(&format!("{dir}/dev.txt"));
    let deep_seen = read(&format!("{dir}/deep-seen.txt"));
    let neg = read(&format!("{dir}/negative-dev.txt"));
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt")).unwrap().lines().map(String::from).collect();
    let v = vocab.len() as f64 + 1.0;
    println!("## {dir}, {n} training sentences\n");
    println!("| arm | setting | categories | rules | description, bits | development | deeper, corpus words | deeper derivable | fresh ungrammatical derivable | grammatical samples | not in training | deeper samples | learned in |");
    println!("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|");
    let rules = [
        ("A", MergeRule::Single),
        ("B", MergeRule::AtLeast(2)),
        ("B", MergeRule::AtLeast(3)),
        ("B", MergeRule::AtLeast(5)),
        ("C", MergeRule::Overlap(0.1)),
        ("C", MergeRule::Overlap(0.25)),
        ("C", MergeRule::Overlap(0.5)),
        ("C'", MergeRule::Jaccard(0.05)),
        ("C'", MergeRule::Jaccard(0.1)),
        ("C'", MergeRule::Jaccard(0.25)),
        ("C'", MergeRule::Jaccard(0.5)),
    ];
    let mut best: HashMap<&str, (f64, String)> = HashMap::new();
    for (arm, rule) in rules {
        let t = Instant::now();
        let mut m = Subst::train_rule(sub, &vocab, rule);
        let structure = t.elapsed().as_secs_f64();
        // A canonical fingerprint of the partition and the rule set: each
        // category named by its sorted members, rules over those names, so
        // two runs agree only if their grammars are the same.
        let fingerprint = {
            use std::collections::hash_map::DefaultHasher;
            use std::hash::{Hash, Hasher};
            let mut members: std::collections::BTreeMap<u32, Vec<Vec<u32>>> = Default::default();
            for (w, &c) in &m.category_of {
                members.entry(c).or_default().push(w.clone());
            }
            let mut name: HashMap<u32, Vec<Vec<u32>>> = HashMap::new();
            for (c, mut ws) in members {
                ws.sort();
                name.insert(c, ws);
            }
            let mut cats: Vec<&Vec<Vec<u32>>> = name.values().collect();
            cats.sort();
            let mut rules: Vec<(Vec<Vec<u32>>, String)> = Vec::new();
            for (a, rs) in &m.rules {
                for (rhs, _) in rs {
                    let r = match rhs {
                        q_lm::subst::Rhs::Word(w) => format!("w{w}"),
                        q_lm::subst::Rhs::Pair(b, c) => format!("{:?}|{:?}", name.get(b).map(|v| &v[0]), name.get(c).map(|v| &v[0])),
                    };
                    rules.push((name[a].clone(), r));
                }
            }
            rules.sort();
            let mut h = DefaultHasher::new();
            cats.hash(&mut h);
            rules.hash(&mut h);
            h.finish()
        };
        eprintln!("{dir} {n} {arm} {rule:?}: {} categories, {} rules, fingerprint {fingerprint:016x}, structure in {structure:.1} s", m.categories, m.size());
        if m.size() > 60_000 {
            println!("| {arm} | {rule:?} | {} | {} | – | not estimated: over 60,000 rules | | | | | | | structure {structure:.1} s |", m.categories, m.size());
            continue;
        }
        m.em(sub, 20, 1e-3);
        let secs = t.elapsed().as_secs_f64();
        let (g, d, _) = m.description_length(sub);
        let count = |set: &[Sentence]| set.iter().filter(|s| m.probability(s) > 0.0).count();
        let mut rng = Rng(SAMPLE_SEED);
        let finished: Vec<Sentence> = (0..SAMPLES).filter_map(|_| m.sample(&mut rng, 200)).collect();
        let j = judge_all(&judge, &finished, &sub_set);
        let setting = format!("{rule:?}");
        println!(
            "| {arm} | {setting} | {} | {} | {:.0} | {:.4} | {:.4} | {} of {} | {} of {} | {} of {} | {} | {} | {secs:.1} s |",
            m.categories, m.size(), g + d, floored(&m, &dev, v), floored(&m, &deep_seen, v),
            count(&deep_seen), deep_seen.len(), count(&neg), neg.len(), j.grammatical, finished.len(), j.novel_grammatical, j.deep_grammatical
        );
        let e = best.entry(arm).or_insert((f64::INFINITY, String::new()));
        if g + d < e.0 {
            *e = (g + d, setting);
        }
    }
    let mut arms: Vec<_> = best.into_iter().collect();
    arms.sort_by(|a, b| a.0.cmp(b.0));
    println!("\nChosen by the shortest description: {}\n", arms.iter().map(|(a, (_, s))| format!("{a} {s}")).collect::<Vec<_>>().join("; "));
}

/// QLM-004: rule pruning by minimum description length. The grammar learned
/// from n sentences (with 5 rounds of inside–outside) loses every rule whose
/// expected count is below tau, then the categories that can no longer
/// finish or be reached; 5 more rounds re-estimate it. The tau chosen is the
/// one with the shortest two-part description of the training sentences:
/// nothing but the training sentences decides it.
fn mdl(dir: &str, n: usize) {
    let judge = Judge::load(dir);
    use q_lm::prefix::Prefix;
    use q_lm::subst::Subst;
    let train = read(&format!("{dir}/train.txt"));
    let dev = read(&format!("{dir}/dev.txt"));
    let deep = read(&format!("{dir}/deep.txt"));
    let deep_seen = read(&format!("{dir}/deep-seen.txt"));
    let negative = read(&format!("{dir}/negative.txt"));
    let vocab: Vec<String> = fs::read_to_string(format!("{dir}/vocab.txt")).unwrap().lines().map(String::from).collect();
    let v = vocab.len() as f64 + 1.0;
    let sub = &train[..n];
    let sub_set: BTreeSet<&Sentence> = sub.iter().collect();
    let t = Instant::now();
    let mut base = Subst::train(sub, &vocab);
    base.em(sub, 5, 1e-3);
    eprintln!("{n}: base grammar in {:.1} s", t.elapsed().as_secs_f64());
    println!("| expected count kept | categories | rules | grammar bits | data bits | total bits | training not derivable | development bits/token | development derivable | deeper, corpus words (first 100) bits/token | deeper derivable | deeper, corpus words derivable | ungrammatical derivable | P(finishes) | grammatical samples | not in training | deeper | ms per next-token distribution | pruned and re-estimated in |");
    println!("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|");
    for tau in [0.0, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0] {
        let t = Instant::now();
        let mut m = base.clone();
        m.prune(tau);
        if !m.rules.contains_key(&m.start) {
            println!("| {tau} | nothing left: the start category lost every rule |");
            break;
        }
        m.em(sub, 5, 1e-3);
        let secs = t.elapsed().as_secs_f64();
        let (g, d, missing) = m.description_length(sub);
        let derivable = |set: &[Sentence]| set.iter().filter(|s| m.probability(s) > 0.0).count();
        let (mut total, mut tokens, mut ok) = (0.0, 0usize, 0);
        for s in &dev {
            let p = m.probability(s);
            ok += (p > 0.0) as usize;
            let floor = (1.0 / v).powi(s.len() as i32 + 1);
            total -= (0.999 * p + 0.001 * floor).log2();
            tokens += s.len() + 1;
        }
        let mut rng = Rng(SAMPLE_SEED);
        let finished: Vec<Sentence> = (0..SAMPLES).filter_map(|_| m.sample(&mut rng, 200)).collect();
        let j = judge_all(&judge, &finished, &sub_set);
        // Next-token cost, as `qlm prefix`, on the first 50 development sentences.
        let pf = Prefix::new(&m);
        let (mut ns, mut count) = (0.0, 0);
        for s in &dev[..50] {
            let mut r = pf.start();
            for i in 0..=s.len() {
                let t = Instant::now();
                let _ = pf.next(&r);
                ns += t.elapsed().as_secs_f64();
                count += 1;
                if i < s.len() {
                    match m.word_id(&s[i]) {
                        Some(w) => pf.step(&mut r, w),
                        None => break,
                    }
                }
            }
        }
        println!(
            "| {tau} | {} | {} | {g:.0} | {d:.0} | {:.0} | {missing} | {:.4} | {ok} | {:.4} | {} of {} | {} of {} | {} of {} | {:.6} | {} of {} | {} | {} | {:.2} | {secs:.1} s |",
            m.categories, m.size(), g + d, total / tokens as f64, floored(&m, &deep_seen[..100], v),
            derivable(&deep), deep.len(), derivable(&deep_seen), deep_seen.len(), derivable(&negative), negative.len(),
            m.termination(), j.grammatical, finished.len(), j.novel_grammatical, j.deep_grammatical,
            1000.0 * ns / count as f64
        );
    }
}

fn judge(path: &str) {
    let sys = paraphrase();
    let samples = read(path);
    let ok = samples
        .iter()
        .filter(|s| analyse(&sys, s).is_some())
        .count();
    println!("{ok} of {} grammatical", samples.len());
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    match args.get(1).map(String::as_str) {
        Some("data") => data(args.get(2).map(String::as_str).unwrap_or("data")),
        Some("report") => report(args.get(2).map(String::as_str).unwrap_or("data")),
        Some("judge") => judge(&args[2]),
        Some("family") => family_data(&args[2], &args[3], args[4].parse().unwrap()),
        Some("compare") => compare(&args[2]),
        Some("score") => score(&args[2], args[3].parse().unwrap(), args[4].parse().unwrap(), &args[5..]),
        Some("semantic") => semantic_data(&args[2], args[3].parse().unwrap(), args.get(4).map(String::as_str).unwrap_or("v2")),
        Some("shortcut") => shortcut(&args[2]),
        Some("facts") => facts(&args[2], args.get(3).and_then(|x| x.parse().ok()).unwrap_or(usize::MAX)),
        Some("roles") => roles(&args[2]),
        Some("equiv") => equiv(&args[2], args.get(3).and_then(|x| x.parse().ok()).unwrap_or(usize::MAX)),
        Some("negatives") => negatives(&args[2]),
        Some("trace") => trace(&args[2], args.get(3).and_then(|x| x.parse().ok()).unwrap_or(usize::MAX).min(read(&format!("{}/train.txt", args[2])).len())),
        Some("em") => em_curve(args.get(2).map(String::as_str).unwrap_or("data"), args.get(3).and_then(|x| x.parse().ok()).unwrap_or(1000)),
        Some("mdl") => mdl(args.get(2).map(String::as_str).unwrap_or("data"), args.get(3).and_then(|x| x.parse().ok()).unwrap_or(1000)),
        Some("prefix") => prefix(args.get(2).map(String::as_str).unwrap_or("data"), args.get(3).and_then(|x| x.parse().ok()).unwrap_or(10_000)),
        Some("subst") => subst(
            args.get(2).map(String::as_str).unwrap_or("data"),
            args.get(3)
                .and_then(|x| x.parse().ok())
                .unwrap_or(usize::MAX),
        ),
        _ => eprintln!("usage: qlm data DIR | qlm report DIR | qlm judge FILE"),
    }
}
