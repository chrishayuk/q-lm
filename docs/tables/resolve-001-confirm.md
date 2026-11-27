## data-sem4-v3 llama-20004-s1

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.17 | 0.17 |
| 2 | 0.17 | 0.54 | 0.92 |
| 3 | 0.92 | 0.88 | 0.96 |
| 4 | 0.96 | 0.96 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.92 | 1.00 | 0.96 | 0.75 | 0.88 |
| 4 | 0.96 | 1.00 | 1.00 | 0.96 | 1.00 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.46 | 0.08 | 0.04 | 0.29 | 0.17 | 1.00 |
| 2 | 1.00 | 0.42 | 0.00 | 0.96 | 0.46 | 1.00 |
| 3 | 1.00 | 0.96 | 0.08 | 0.71 | 0.92 | 1.00 |
| 4 (last) | 1.00 | 0.88 | 0.00 | 0.88 | 0.92 | 1.00 |

## data-sem4-v3 transformer-20004-s1

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.04 | 0.04 |
| 2 | 0.04 | 0.29 | 0.12 |
| 3 | 0.12 | 0.58 | 0.92 |
| 4 | 0.92 | 1.00 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 1.00 | 1.00 | 0.92 | 0.62 | 0.88 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.88 | 0.04 | 0.00 | 0.54 | 0.08 | 1.00 |
| 2 | 0.67 | 0.00 | 0.00 | 0.67 | 0.12 | 1.00 |
| 3 | 0.96 | 0.08 | 0.00 | 0.54 | 0.17 | 1.00 |
| 4 (last) | 1.00 | 0.71 | 0.00 | 0.92 | 0.75 | 1.00 |

## data-sem4-v3 llama-20004-s2

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.12 | 0.17 |
| 2 | 0.17 | 0.29 | 0.71 |
| 3 | 0.71 | 0.71 | 1.00 |
| 4 | 1.00 | 1.00 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.96 | 1.00 | 1.00 | 0.88 | 1.00 |
| 4 | 1.00 | 1.00 | 1.00 | 0.96 | 1.00 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.62 | 0.00 | 0.00 | 0.38 | 0.08 | 1.00 |
| 2 | 1.00 | 0.58 | 0.00 | 0.71 | 0.54 | 1.00 |
| 3 | 1.00 | 1.00 | 0.00 | 0.58 | 1.00 | 1.00 |
| 4 (last) | 1.00 | 1.00 | 0.00 | 0.79 | 1.00 | 1.00 |

## data-sem4-v3 transformer-20004-s2

Unintervened accuracy on `the capital of C is`: 0.88

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.04 | 0.04 |
| 2 | 0.04 | 0.12 | 0.12 |
| 3 | 0.12 | 0.50 | 0.92 |
| 4 | 0.92 | 0.92 | 0.88 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.88 | 0.88 | 0.79 | 0.71 | 0.79 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.58 | 0.08 | 0.00 | 0.50 | 0.04 | 0.88 |
| 2 | 0.67 | 0.04 | 0.00 | 0.67 | 0.04 | 0.88 |
| 3 | 0.96 | 0.00 | 0.00 | 0.79 | 0.25 | 0.88 |
| 4 (last) | 1.00 | 0.92 | 0.00 | 0.83 | 0.83 | 0.88 |

## data-sem4-v3 llama-20004-s3

Unintervened accuracy on `the capital of C is`: 0.92

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.17 | 0.21 |
| 2 | 0.21 | 0.42 | 0.79 |
| 3 | 0.79 | 0.79 | 0.96 |
| 4 | 0.96 | 0.96 | 0.92 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.79 | 0.92 | 0.92 | 0.88 | 0.88 |
| 4 | 0.88 | 0.92 | 0.92 | 0.79 | 0.88 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.96 | 0.00 | 0.00 | 0.79 | 0.08 | 0.92 |
| 2 | 1.00 | 0.29 | 0.00 | 0.79 | 0.33 | 0.92 |
| 3 | 1.00 | 0.88 | 0.00 | 0.71 | 0.92 | 0.92 |
| 4 (last) | 1.00 | 0.88 | 0.00 | 0.75 | 0.83 | 0.92 |

## data-sem4-v3 transformer-20004-s3

Unintervened accuracy on `the capital of C is`: 0.92

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.08 | 0.08 |
| 2 | 0.08 | 0.21 | 0.38 |
| 3 | 0.38 | 0.46 | 0.92 |
| 4 | 0.92 | 0.92 | 0.92 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.88 | 0.92 | 0.88 | 0.71 | 0.83 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.58 | 0.04 | 0.00 | 0.67 | 0.04 | 0.92 |
| 2 | 0.79 | 0.08 | 0.00 | 0.83 | 0.04 | 0.92 |
| 3 | 0.96 | 0.12 | 0.00 | 0.67 | 0.17 | 0.92 |
| 4 (last) | 1.00 | 0.67 | 0.04 | 0.92 | 0.62 | 0.92 |

## data-sem5-v3 llama-20004-s1

Unintervened accuracy on `the capital of C is`: 0.96

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.17 | 0.25 |
| 2 | 0.25 | 0.29 | 0.54 |
| 3 | 0.54 | 0.50 | 0.88 |
| 4 | 0.88 | 0.83 | 0.96 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.83 | 0.96 | 0.71 | 0.54 | 0.79 |
| 4 | 0.88 | 0.96 | 0.96 | 0.92 | 0.96 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.12 | 0.04 | 0.04 | 0.12 | 0.08 | 0.96 |
| 2 | 1.00 | 0.46 | 0.00 | 0.83 | 0.50 | 0.96 |
| 3 | 1.00 | 0.92 | 0.00 | 0.62 | 0.92 | 0.96 |
| 4 (last) | 1.00 | 1.00 | 0.00 | 0.71 | 1.00 | 0.96 |

## data-sem5-v3 transformer-20004-s1

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.08 | 0.08 |
| 2 | 0.08 | 0.04 | 0.04 |
| 3 | 0.04 | 0.71 | 0.88 |
| 4 | 0.88 | 0.96 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 1.00 | 1.00 | 1.00 | 0.79 | 0.92 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.71 | 0.00 | 0.04 | 0.62 | 0.08 | 1.00 |
| 2 | 0.88 | 0.00 | 0.04 | 0.71 | 0.04 | 1.00 |
| 3 | 0.96 | 0.08 | 0.04 | 0.79 | 0.08 | 1.00 |
| 4 (last) | 1.00 | 0.62 | 0.00 | 0.88 | 0.58 | 1.00 |

## data-sem5-v3 llama-20004-s2

Unintervened accuracy on `the capital of C is`: 0.92

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.29 | 0.29 |
| 2 | 0.29 | 0.50 | 0.83 |
| 3 | 0.83 | 0.79 | 0.92 |
| 4 | 0.92 | 0.96 | 0.92 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.79 | 0.92 | 0.83 | 0.71 | 0.83 |
| 4 | 0.79 | 0.92 | 0.92 | 0.83 | 0.83 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.83 | 0.00 | 0.00 | 0.75 | 0.04 | 0.92 |
| 2 | 1.00 | 0.25 | 0.00 | 0.83 | 0.38 | 0.92 |
| 3 | 1.00 | 0.88 | 0.00 | 0.79 | 0.92 | 0.92 |
| 4 (last) | 1.00 | 0.96 | 0.00 | 0.88 | 0.88 | 0.92 |

## data-sem5-v3 transformer-20004-s2

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.08 | 0.04 |
| 2 | 0.04 | 0.25 | 0.33 |
| 3 | 0.33 | 0.79 | 1.00 |
| 4 | 1.00 | 0.96 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 1.00 | 1.00 | 0.92 | 0.75 | 0.92 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.33 | 0.00 | 0.00 | 0.42 | 0.00 | 1.00 |
| 2 | 0.67 | 0.00 | 0.00 | 0.71 | 0.08 | 1.00 |
| 3 | 1.00 | 0.17 | 0.00 | 0.67 | 0.21 | 1.00 |
| 4 (last) | 1.00 | 0.83 | 0.00 | 0.96 | 0.75 | 1.00 |

## data-sem5-v3 llama-20004-s3

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.21 | 0.12 |
| 2 | 0.12 | 0.25 | 0.75 |
| 3 | 0.75 | 0.75 | 0.92 |
| 4 | 0.92 | 0.96 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.88 | 1.00 | 0.92 | 0.88 | 0.92 |
| 4 | 0.96 | 1.00 | 1.00 | 0.92 | 1.00 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.38 | 0.04 | 0.04 | 0.21 | 0.08 | 1.00 |
| 2 | 1.00 | 0.58 | 0.00 | 0.62 | 0.50 | 1.00 |
| 3 | 1.00 | 0.96 | 0.00 | 0.58 | 1.00 | 1.00 |
| 4 (last) | 1.00 | 0.96 | 0.00 | 0.83 | 1.00 | 1.00 |

## data-sem5-v3 transformer-20004-s3

Unintervened accuracy on `the capital of C is`: 0.96

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.04 | 0.04 |
| 2 | 0.04 | 0.04 | 0.25 |
| 3 | 0.25 | 0.67 | 0.83 |
| 4 | 0.83 | 0.92 | 0.96 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.88 | 0.96 | 0.96 | 0.88 | 0.92 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.38 | 0.00 | 0.00 | 0.79 | 0.08 | 0.96 |
| 2 | 0.92 | 0.00 | 0.00 | 0.92 | 0.04 | 0.96 |
| 3 | 1.00 | 0.00 | 0.00 | 0.92 | 0.04 | 0.96 |
| 4 (last) | 1.00 | 0.92 | 0.00 | 0.88 | 0.83 | 0.96 |

## data-sem6-v3 llama-20004-s1

Unintervened accuracy on `the capital of C is`: 0.96

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.04 | 0.12 |
| 2 | 0.12 | 0.25 | 0.62 |
| 3 | 0.62 | 0.79 | 0.83 |
| 4 | 0.83 | 0.96 | 0.96 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.83 | 0.96 | 0.88 | 0.75 | 0.88 |
| 4 | 0.92 | 0.96 | 0.96 | 0.88 | 0.96 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.33 | 0.04 | 0.04 | 0.12 | 0.08 | 0.96 |
| 2 | 1.00 | 0.33 | 0.04 | 0.71 | 0.38 | 0.96 |
| 3 | 1.00 | 0.92 | 0.08 | 0.58 | 0.88 | 0.96 |
| 4 (last) | 1.00 | 0.83 | 0.00 | 0.92 | 0.96 | 0.96 |

## data-sem6-v3 transformer-20004-s1

Unintervened accuracy on `the capital of C is`: 0.92

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.08 | 0.00 |
| 2 | 0.00 | 0.25 | 0.17 |
| 3 | 0.17 | 0.58 | 0.83 |
| 4 | 0.83 | 0.92 | 0.92 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.88 | 0.92 | 0.88 | 0.67 | 0.79 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.33 | 0.00 | 0.04 | 0.42 | 0.04 | 0.92 |
| 2 | 0.67 | 0.00 | 0.00 | 0.58 | 0.04 | 0.92 |
| 3 | 0.92 | 0.12 | 0.04 | 0.58 | 0.29 | 0.92 |
| 4 (last) | 1.00 | 0.62 | 0.00 | 0.88 | 0.79 | 0.92 |

## data-sem6-v3 llama-20004-s2

Unintervened accuracy on `the capital of C is`: 0.96

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.33 | 0.46 |
| 2 | 0.46 | 0.54 | 0.79 |
| 3 | 0.79 | 0.79 | 0.92 |
| 4 | 0.92 | 0.92 | 0.96 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.83 | 0.96 | 0.92 | 0.83 | 0.75 |
| 4 | 0.92 | 0.96 | 0.96 | 0.88 | 0.96 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.67 | 0.08 | 0.00 | 0.54 | 0.17 | 0.96 |
| 2 | 1.00 | 0.67 | 0.00 | 0.58 | 0.71 | 0.96 |
| 3 | 1.00 | 0.88 | 0.04 | 0.67 | 0.83 | 0.96 |
| 4 (last) | 1.00 | 0.96 | 0.00 | 0.79 | 0.96 | 0.96 |

## data-sem6-v3 transformer-20004-s2

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.12 | 0.12 |
| 2 | 0.12 | 0.38 | 0.46 |
| 3 | 0.46 | 0.75 | 0.88 |
| 4 | 0.88 | 0.92 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.96 | 1.00 | 0.96 | 0.71 | 0.88 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.50 | 0.04 | 0.08 | 0.67 | 0.12 | 1.00 |
| 2 | 0.92 | 0.00 | 0.00 | 0.96 | 0.17 | 1.00 |
| 3 | 1.00 | 0.17 | 0.00 | 0.88 | 0.25 | 1.00 |
| 4 (last) | 1.00 | 0.67 | 0.00 | 0.92 | 0.75 | 1.00 |

## data-sem6-v3 llama-20004-s3

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.08 | 0.21 |
| 2 | 0.21 | 0.42 | 0.88 |
| 3 | 0.88 | 0.96 | 1.00 |
| 4 | 1.00 | 1.00 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.92 | 1.00 | 0.96 | 0.79 | 0.96 |
| 4 | 0.96 | 1.00 | 0.96 | 0.83 | 0.92 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.42 | 0.00 | 0.00 | 0.17 | 0.21 | 1.00 |
| 2 | 1.00 | 0.42 | 0.00 | 0.75 | 0.46 | 1.00 |
| 3 | 1.00 | 0.88 | 0.00 | 0.58 | 0.96 | 1.00 |
| 4 (last) | 1.00 | 0.83 | 0.00 | 0.92 | 0.92 | 1.00 |

## data-sem6-v3 transformer-20004-s3

Unintervened accuracy on `the capital of C is`: 1.00

**A0. Where the answer first appears** at the answer position (logit lens; share of the 24 with the true capital top)

| block | before attention | after attention | after the feed-forward |
|---:|---:|---:|---:|
| 1 | 0.04 | 0.08 | 0.04 |
| 2 | 0.04 | 0.17 | 0.25 |
| 3 | 0.25 | 0.50 | 0.71 |
| 4 | 0.71 | 0.88 | 1.00 |

**A. Retrieval or amplification** (answer position)

| block | removal: own-capital accuracy | removal at position 2 | the feed-forward's output alone names the true capital | the same, its input with all city directions removed | the same, a random subspace removed |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.92 | 1.00 | 1.00 | 0.67 | 0.88 |

**B. An external table in place of the feed-forward** (answer position; share of the 24 prompts giving the table's city)

| block | true table | edited table (a different city for every country) | random vector, matched: gives the edited city | random vector, matched: true city survives | another city's vector gives that city | the prompt's own output (trivial upper bound) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.58 | 0.00 | 0.00 | 0.54 | 0.08 | 1.00 |
| 2 | 0.75 | 0.08 | 0.00 | 0.88 | 0.12 | 1.00 |
| 3 | 1.00 | 0.04 | 0.04 | 0.79 | 0.33 | 1.00 |
| 4 (last) | 1.00 | 0.83 | 0.00 | 0.92 | 0.83 | 1.00 |

