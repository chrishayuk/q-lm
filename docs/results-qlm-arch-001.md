# Results: QLM-ARCH-001, which part of the architecture carries depth

Reported against [qlm-arch-001-plan.md](qlm-arch-001-plan.md). Colmerauer's
language; three seeds per arm. "Deeper" is bits per token on the 300 deeper
sentences with corpus words; development is all 13,143 development
sentences.

| arm | training sentences | development, seeds 1 / 2 / 3 | deeper, seeds 1 / 2 / 3 | deeper, mean | seed range |
|---|---:|---|---|---:|---:|
| base | 1,000 | 1.0621 / 1.0692 / 1.0618 | 2.922 / 3.009 / 2.900 | 2.944 | 0.109 |
| rope | 1,000 | 1.0619 / 1.0722 / 1.0607 | 2.183 / 2.072 / 2.134 | **2.130** | 0.111 |
| rms | 1,000 | 1.0623 / 1.0691 / 1.0617 | 2.927 / 3.025 / 2.885 | 2.946 | 0.140 |
| swiglu | 1,000 | 1.0624 / 1.0672 / 1.0622 | 3.138 / 3.053 / 3.058 | 3.083 | 0.086 |
| tie | 1,000 | 1.0794 / 1.0783 / 1.0827 | 4.858 / 4.877 / 4.371 | 4.702 | 0.507 |
| all four | 1,000 | 1.0657 / 1.0649 / 1.0784 | 2.434 / 2.447 / 2.690 | 2.524 | 0.256 |
| base | 105,138 | 1.0376 / 1.0379 / 1.0380 | 4.962 / 4.806 / 3.972 | 4.580 | 0.990 |
| rope | 105,138 | 1.0376 / 1.0380 / 1.0379 | 2.680 / 2.367 / 2.308 | **2.452** | 0.371 |
| rms | 105,138 | 1.0376 / 1.0379 / 1.0379 | 5.039 / 4.753 / 4.921 | 4.904 | 0.286 |
| swiglu | 105,138 | 1.0375 / 1.0377 / 1.0378 | 5.420 / 4.684 / 4.351 | 4.819 | 1.069 |
| tie | 105,138 | 1.0464 / 1.0440 / 1.0450 | 4.345 / 3.638 / 3.557 | 3.846 | 0.789 |
| all four | 105,138 | 1.0461 / 1.0435 / 1.0439 | 2.414 / 2.423 / 2.531 | 2.456 | 0.117 |

## The plan's reading

**The reimplementation check passes.** The base arm reimplements the
custom transformer. On deeper sentences:

| training sentences | base arm, mean | custom transformer, mean (range) |
|---:|---:|---:|
| 1,000 | 2.944 | 2.894 (2.82 to 2.94) |
| 105,138 | 4.580 | 4.797 (4.67 to 4.93) |

Both differences are within the seed spreads. One base seed at full size
(3.97) is lower than any custom seed.

**Which change "carries depth".** The rule is that an arm's mean beats
base's by more than both arms' seed ranges combined.
- **Rotary positions:** they lower deeper bits from 4.580 to 2.452, a gap of
  2.13 against a combined range of 1.36. Rotary carries depth.
- **RMSNorm and the gated feed-forward:** both are slightly worse than
  base. They do not.
- **Tied embeddings:**
  - at full size, 3.846, a gap of 0.73 against a combined range of 1.78. It
    does not carry depth;
  - at 1,000 sentences they make depth much worse, 4.70 against 2.94;
  - at both sizes they cost corpus fit: 1.045 against 1.038.
- **The combined arm against Llama.** The combined arm gives 2.456 at full
  size. Llama, on the same 300 sentences, gives 2.41, 2.93 and 2.34 (mean
  2.56). This code path with all four changes reproduces Llama's depth
  behaviour.
- **Rotary alone is the best arm at both sizes.** The combined arm is a
  little worse than rotary alone: 2.524 against 2.130 at 1,000 sentences.
  The extra changes, tying above all, cost a little.

**With rotary positions, depth gets worse with more data much less:**
2.13 to 2.45, against base's 2.94 to 4.58.

## What it says, and what it does not

- **Positions are the main reason the custom transformer did badly at
  depth.** It was not sentence length: the length test in
  results-architectures.md ruled that out. A learned table of absolute
  positions has to learn separately what each word does at each position.
  Rotary positions make attention depend on relative position. An
  embedded clause then looks the same wherever it starts, which is what
  recursion asks for. This is an interpretation; the experiment shows only
  that rotary alone carries the difference.
- **For the comparison with the grammar:** on Colmerauer's language, the
  rotary arm is the strongest transformer yet at depth: 2.13 at 1,000
  sentences, against the converged grammar's 1.81 there on the first 100
  (results-architectures.md). The two are not yet on the same sentences;
  that comparison needs the rotary arm scored on the first 100 deeper
  sentences.
- **For the families:** Llama has rotary positions and still trails the
  grammar by 0.2 to 1.5 bits there (results-qlm005.md). So rotary positions
  do not close the gap on those languages.

## Next

- The rotary arm on the three families, to see whether it beats Llama there
  as it did here at 1,000 sentences.
- The rotary arm on the grammar's exact sentences.
