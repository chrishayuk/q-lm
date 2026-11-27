## data-sem1-v3 llama-20004-s1

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.08 | 0.12 |
| 2 | 0.12 | 0.67 | 0.83 |
| 3 | 0.83 | 0.96 | 0.96 |
| 4 | 0.96 | 0.96 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.92 | 1.00 | 0.88 | 0.79 | 0.88 |
| 4 | 0.92 | 1.00 | 1.00 | 0.88 | 0.96 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.58 | 0.04 | 0.04 | 0.29 | 0.00 | 1.00 |
| 2 | 1.00 | 0.38 | 0.00 | 0.88 | 0.38 | 1.00 |
| 3 | 1.00 | 0.83 | 0.00 | 0.88 | 0.83 | 1.00 |
| 4 (last) | 1.00 | 0.96 | 0.00 | 0.92 | 0.92 | 1.00 |

## data-sem1-v3 transformer-20004-s1

Unintervened accuracy on `the capital of C is`: 0.96

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.08 | 0.08 |
| 2 | 0.08 | 0.17 | 0.17 |
| 3 | 0.17 | 0.58 | 0.88 |
| 4 | 0.88 | 0.88 | 0.96 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.88 | 0.96 | 0.92 | 0.38 | 0.96 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.83 | 0.04 | 0.00 | 0.58 | 0.00 | 0.96 |
| 2 | 0.83 | 0.00 | 0.00 | 0.75 | 0.04 | 0.96 |
| 3 | 1.00 | 0.08 | 0.00 | 0.83 | 0.12 | 0.96 |
| 4 (last) | 1.00 | 0.62 | 0.00 | 0.88 | 0.58 | 0.96 |

## data-sem1-v3 llama-20004-s2

Unintervened accuracy on `the capital of C is`: 0.96

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.08 | 0.17 |
| 2 | 0.17 | 0.25 | 0.58 |
| 3 | 0.58 | 0.75 | 0.83 |
| 4 | 0.83 | 0.92 | 0.96 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.67 | 0.96 | 0.83 | 0.83 | 0.83 |
| 4 | 0.83 | 0.96 | 0.96 | 0.83 | 0.96 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.54 | 0.08 | 0.00 | 0.33 | 0.12 | 0.96 |
| 2 | 0.96 | 0.67 | 0.04 | 0.42 | 0.67 | 0.96 |
| 3 | 1.00 | 0.92 | 0.04 | 0.54 | 0.96 | 0.96 |
| 4 (last) | 1.00 | 1.00 | 0.00 | 0.79 | 0.96 | 0.96 |

## data-sem1-v3 transformer-20004-s2

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.04 | 0.08 |
| 2 | 0.08 | 0.17 | 0.17 |
| 3 | 0.17 | 0.58 | 0.96 |
| 4 | 0.96 | 0.96 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.96 | 1.00 | 0.88 | 0.46 | 0.88 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.50 | 0.00 | 0.00 | 0.58 | 0.00 | 1.00 |
| 2 | 0.71 | 0.08 | 0.04 | 0.71 | 0.04 | 1.00 |
| 3 | 0.96 | 0.12 | 0.04 | 0.67 | 0.25 | 1.00 |
| 4 (last) | 1.00 | 0.83 | 0.00 | 0.83 | 0.83 | 1.00 |

## data-sem1-v3 llama-20004-s3

Unintervened accuracy on `the capital of C is`: 0.92

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.12 | 0.12 |
| 2 | 0.12 | 0.17 | 0.79 |
| 3 | 0.79 | 0.79 | 0.92 |
| 4 | 0.92 | 0.96 | 0.92 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.79 | 0.92 | 0.92 | 0.83 | 0.79 |
| 4 | 0.88 | 0.92 | 0.92 | 0.83 | 0.92 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.21 | 0.04 | 0.08 | 0.29 | 0.08 | 0.92 |
| 2 | 1.00 | 0.58 | 0.04 | 0.62 | 0.75 | 0.92 |
| 3 | 1.00 | 1.00 | 0.04 | 0.54 | 0.96 | 0.92 |
| 4 (last) | 1.00 | 0.92 | 0.00 | 0.88 | 0.88 | 0.92 |

## data-sem1-v3 transformer-20004-s3

Unintervened accuracy on `the capital of C is`: 0.96

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.04 | 0.04 |
| 2 | 0.04 | 0.12 | 0.17 |
| 3 | 0.17 | 0.54 | 0.83 |
| 4 | 0.83 | 0.96 | 0.96 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.88 | 0.96 | 0.96 | 0.71 | 0.92 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.54 | 0.00 | 0.04 | 0.71 | 0.00 | 0.96 |
| 2 | 0.83 | 0.00 | 0.00 | 0.83 | 0.04 | 0.96 |
| 3 | 1.00 | 0.08 | 0.00 | 0.83 | 0.17 | 0.96 |
| 4 (last) | 1.00 | 0.75 | 0.04 | 0.83 | 0.67 | 0.96 |

## data-sem2-v3 llama-20004-s1

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.17 | 0.04 |
| 2 | 0.04 | 0.46 | 0.92 |
| 3 | 0.92 | 0.92 | 1.00 |
| 4 | 1.00 | 1.00 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.92 | 1.00 | 1.00 | 0.79 | 0.88 |
| 4 | 0.96 | 1.00 | 1.00 | 0.92 | 1.00 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.62 | 0.04 | 0.04 | 0.17 | 0.04 | 1.00 |
| 2 | 1.00 | 0.25 | 0.04 | 0.92 | 0.21 | 1.00 |
| 3 | 1.00 | 0.88 | 0.00 | 0.88 | 0.96 | 1.00 |
| 4 (last) | 1.00 | 0.88 | 0.00 | 0.88 | 0.96 | 1.00 |

## data-sem2-v3 transformer-20004-s1

Unintervened accuracy on `the capital of C is`: 0.96

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.04 | 0.04 |
| 2 | 0.04 | 0.08 | 0.08 |
| 3 | 0.08 | 0.54 | 0.88 |
| 4 | 0.88 | 0.96 | 0.96 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.88 | 0.96 | 0.96 | 0.67 | 0.88 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.62 | 0.08 | 0.04 | 0.50 | 0.00 | 0.96 |
| 2 | 0.83 | 0.04 | 0.00 | 0.71 | 0.00 | 0.96 |
| 3 | 0.88 | 0.08 | 0.00 | 0.62 | 0.04 | 0.96 |
| 4 (last) | 1.00 | 0.75 | 0.00 | 0.92 | 0.75 | 0.96 |

## data-sem2-v3 llama-20004-s2

Unintervened accuracy on `the capital of C is`: 0.96

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.21 | 0.38 |
| 2 | 0.38 | 0.46 | 0.71 |
| 3 | 0.71 | 0.71 | 0.88 |
| 4 | 0.88 | 0.92 | 0.96 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.79 | 0.96 | 0.96 | 0.79 | 0.83 |
| 4 | 0.88 | 0.96 | 0.96 | 0.92 | 0.96 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.88 | 0.12 | 0.04 | 0.54 | 0.04 | 0.96 |
| 2 | 1.00 | 0.42 | 0.04 | 0.79 | 0.38 | 0.96 |
| 3 | 1.00 | 0.96 | 0.00 | 0.75 | 0.96 | 0.96 |
| 4 (last) | 1.00 | 0.96 | 0.00 | 0.88 | 0.96 | 0.96 |

## data-sem2-v3 transformer-20004-s2

Unintervened accuracy on `the capital of C is`: 0.92

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.04 | 0.08 |
| 2 | 0.08 | 0.17 | 0.12 |
| 3 | 0.12 | 0.71 | 0.83 |
| 4 | 0.83 | 0.88 | 0.92 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.88 | 0.92 | 0.92 | 0.62 | 0.88 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.67 | 0.00 | 0.00 | 0.50 | 0.04 | 0.92 |
| 2 | 0.75 | 0.00 | 0.00 | 0.71 | 0.00 | 0.92 |
| 3 | 0.96 | 0.33 | 0.04 | 0.67 | 0.25 | 0.92 |
| 4 (last) | 1.00 | 0.96 | 0.00 | 0.79 | 0.83 | 0.92 |

## data-sem2-v3 llama-20004-s3

Unintervened accuracy on `the capital of C is`: 0.96

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.08 | 0.33 |
| 2 | 0.33 | 0.62 | 0.83 |
| 3 | 0.83 | 0.83 | 0.92 |
| 4 | 0.92 | 0.96 | 0.96 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.83 | 0.96 | 0.92 | 0.88 | 0.88 |
| 4 | 0.92 | 0.96 | 0.96 | 0.96 | 0.96 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.96 | 0.00 | 0.00 | 0.79 | 0.00 | 0.96 |
| 2 | 1.00 | 0.17 | 0.00 | 0.96 | 0.17 | 0.96 |
| 3 | 1.00 | 0.67 | 0.00 | 0.88 | 0.79 | 0.96 |
| 4 (last) | 1.00 | 0.75 | 0.00 | 0.92 | 0.75 | 0.96 |

## data-sem2-v3 transformer-20004-s3

Unintervened accuracy on `the capital of C is`: 0.96

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.04 | 0.04 |
| 2 | 0.04 | 0.08 | 0.38 |
| 3 | 0.38 | 0.46 | 0.83 |
| 4 | 0.83 | 0.96 | 0.96 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.83 | 0.96 | 0.88 | 0.54 | 0.88 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.21 | 0.08 | 0.00 | 0.67 | 0.00 | 0.96 |
| 2 | 0.88 | 0.04 | 0.00 | 0.71 | 0.00 | 0.96 |
| 3 | 0.96 | 0.12 | 0.00 | 0.67 | 0.04 | 0.96 |
| 4 (last) | 1.00 | 0.83 | 0.00 | 0.71 | 0.96 | 0.96 |

## data-sem3-v3 llama-20004-s1

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.04 | 0.08 |
| 2 | 0.08 | 0.42 | 0.96 |
| 3 | 0.96 | 1.00 | 0.92 |
| 4 | 0.92 | 1.00 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.96 | 1.00 | 0.92 | 0.71 | 0.92 |
| 4 | 0.96 | 1.00 | 1.00 | 0.92 | 1.00 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.96 | 0.04 | 0.04 | 0.50 | 0.00 | 1.00 |
| 2 | 1.00 | 0.33 | 0.00 | 0.83 | 0.29 | 1.00 |
| 3 | 1.00 | 0.96 | 0.00 | 0.67 | 0.96 | 1.00 |
| 4 (last) | 1.00 | 0.88 | 0.00 | 0.88 | 0.92 | 1.00 |

## data-sem3-v3 transformer-20004-s1

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.04 | 0.04 |
| 2 | 0.04 | 0.04 | 0.08 |
| 3 | 0.08 | 0.54 | 0.75 |
| 4 | 0.75 | 0.96 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 1.00 | 1.00 | 0.83 | 0.46 | 0.83 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.71 | 0.08 | 0.00 | 0.38 | 0.04 | 1.00 |
| 2 | 0.83 | 0.00 | 0.00 | 0.71 | 0.04 | 1.00 |
| 3 | 1.00 | 0.29 | 0.00 | 0.67 | 0.25 | 1.00 |
| 4 (last) | 1.00 | 0.62 | 0.00 | 1.00 | 0.67 | 1.00 |

## data-sem3-v3 llama-20004-s2

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.33 | 0.42 |
| 2 | 0.42 | 0.46 | 0.75 |
| 3 | 0.75 | 0.83 | 0.96 |
| 4 | 0.96 | 1.00 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.92 | 1.00 | 0.96 | 0.83 | 0.92 |
| 4 | 1.00 | 1.00 | 1.00 | 0.96 | 1.00 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.92 | 0.08 | 0.04 | 0.46 | 0.08 | 1.00 |
| 2 | 1.00 | 0.58 | 0.00 | 0.62 | 0.58 | 1.00 |
| 3 | 1.00 | 0.88 | 0.00 | 0.79 | 0.92 | 1.00 |
| 4 (last) | 1.00 | 0.96 | 0.00 | 0.96 | 0.96 | 1.00 |

## data-sem3-v3 transformer-20004-s2

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.04 | 0.04 |
| 2 | 0.04 | 0.08 | 0.08 |
| 3 | 0.08 | 0.71 | 0.96 |
| 4 | 0.96 | 1.00 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 1.00 | 1.00 | 1.00 | 0.67 | 1.00 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.71 | 0.04 | 0.00 | 0.67 | 0.00 | 1.00 |
| 2 | 0.83 | 0.04 | 0.00 | 0.67 | 0.00 | 1.00 |
| 3 | 0.92 | 0.25 | 0.00 | 0.58 | 0.21 | 1.00 |
| 4 (last) | 1.00 | 0.62 | 0.00 | 0.96 | 0.71 | 1.00 |

## data-sem3-v3 llama-20004-s3

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.21 | 0.25 |
| 2 | 0.25 | 0.46 | 0.79 |
| 3 | 0.79 | 0.79 | 0.92 |
| 4 | 0.92 | 0.96 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 1.00 | 1.00 | 0.92 | 0.83 | 0.83 |
| 4 | 0.96 | 1.00 | 1.00 | 0.92 | 0.96 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.96 | 0.12 | 0.08 | 0.75 | 0.04 | 1.00 |
| 2 | 1.00 | 0.62 | 0.00 | 0.96 | 0.42 | 1.00 |
| 3 | 1.00 | 0.96 | 0.04 | 0.58 | 1.00 | 1.00 |
| 4 (last) | 1.00 | 0.88 | 0.00 | 0.92 | 0.79 | 1.00 |

## data-sem3-v3 transformer-20004-s3

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.04 | 0.04 |
| 2 | 0.04 | 0.21 | 0.21 |
| 3 | 0.21 | 0.50 | 0.79 |
| 4 | 0.79 | 0.88 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.92 | 1.00 | 0.92 | 0.67 | 0.92 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.54 | 0.04 | 0.04 | 0.75 | 0.04 | 1.00 |
| 2 | 0.88 | 0.04 | 0.00 | 0.83 | 0.08 | 1.00 |
| 3 | 1.00 | 0.12 | 0.00 | 0.79 | 0.17 | 1.00 |
| 4 (last) | 1.00 | 0.67 | 0.00 | 0.88 | 0.62 | 1.00 |

