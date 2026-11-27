## data-sem1 transformer-20004-s1

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.97 | 0.97 | 0.01 |
| 2 | 0.97 | 0.20 | 0.20 | 0.02 |
| 3 | 0.20 | 0.03 | 0.03 | 0.00 |
| 4 | 0.03 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.08) | 0.00 (w 0.11) | 0.00 (w 0.71) | 0.00 (w 0.75) |
| 2 | 0.00 (w 0.10) | 0.00 (w 0.11) | 0.05 (w 0.82) | 0.02 (w 0.77) |
| 3 | 0.00 (w 0.07) | 0.03 (w 0.64) | 0.00 (w 0.13) | 0.00 (w 0.07) |
| 4 | 0.00 (w 0.51) | 0.00 (w 0.10) | 0.00 (w 0.16) | 0.00 (w 0.84) |

Top three heads [(2, 2), (3, 1), (2, 3)] patched together: 0.78. Three other heads [(2, 1), (1, 2), (3, 0)]: 0.02.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (2,2) | 0.07 | +6.71 |
| (3,1) | 0.05 | +5.49 |
| (2,3) | 0.10 | +5.54 |
| (2,2), (3,1) | 0.47 | +12.77 |
| (2,2), (2,3) | 0.38 | +12.55 |
| (3,1), (2,3) | 0.25 | +11.06 |
| (2,2), (3,1), (2,3) | 0.78 | +18.39 |

Sum of the single heads' changes: +17.74 bits; all three together: +18.39 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.70. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (2, 2) | 4/24 | 11/24 | 1/24 | 1/24 |
| (3, 1) | 2/24 | 12/24 | 4/24 | 4/24 |
| (2, 3) | 3/24 | 11/24 | 1/24 | 2/24 |

## data-sem1 llama-20004-s1

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.03 | 0.03 | 0.00 |
| 2 | 0.03 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.35) | 0.00 (w 0.21) | 0.00 (w 0.37) | 0.12 (w 0.68) |
| 2 | 0.02 (w 0.85) | 0.00 (w 0.14) | 0.00 (w 0.38) | 0.00 (w 0.26) |
| 3 | 0.00 (w 0.08) | 0.00 (w 0.14) | 0.00 (w 0.20) | 0.00 (w 0.14) |
| 4 | 0.00 (w 0.15) | 0.00 (w 0.16) | 0.00 (w 0.09) | 0.00 (w 0.04) |

Top three heads [(1, 3), (2, 0), (1, 0)] patched together: 0.87. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.00.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (1,3) | 0.10 | +8.13 |
| (2,0) | 0.00 | +2.77 |
| (1,0) | 0.00 | +2.88 |
| (1,3), (2,0) | 0.33 | +13.87 |
| (1,3), (1,0) | 0.52 | +15.72 |
| (2,0), (1,0) | 0.03 | +6.67 |
| (1,3), (2,0), (1,0) | 0.87 | +21.72 |

Sum of the single heads' changes: +13.77 bits; all three together: +21.72 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.82. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 3) | 1/24 | 3/24 | 2/24 | 6/24 |
| (2, 0) | 5/24 | 6/24 | 3/24 | 3/24 |
| (1, 0) | 2/24 | 4/24 | 4/24 | 4/24 |

## data-sem1 transformer-20004-s2

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.95 | 0.95 | 0.00 |
| 2 | 0.95 | 0.08 | 0.08 | 0.00 |
| 3 | 0.08 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.10) | 0.00 (w 0.54) | 0.00 (w 0.54) | 0.00 (w 0.28) |
| 2 | 0.05 (w 0.92) | 0.00 (w 0.03) | 0.02 (w 0.87) | 0.00 (w 0.31) |
| 3 | 0.00 (w 0.13) | 0.00 (w 0.20) | 0.00 (w 0.21) | 0.02 (w 0.36) |
| 4 | 0.00 (w 0.47) | 0.00 (w 0.24) | 0.00 (w 0.04) | 0.02 (w 0.32) |

Top three heads [(2, 0), (2, 2), (3, 3)] patched together: 0.70. Three other heads [(2, 3), (1, 2), (3, 0)]: 0.00.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (2,0) | 0.07 | +7.33 |
| (2,2) | 0.02 | +5.61 |
| (3,3) | 0.00 | +2.60 |
| (2,0), (2,2) | 0.52 | +13.91 |
| (2,0), (3,3) | 0.20 | +10.06 |
| (2,2), (3,3) | 0.12 | +8.24 |
| (2,0), (2,2), (3,3) | 0.70 | +16.46 |

Sum of the single heads' changes: +15.54 bits; all three together: +16.46 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.72. Other heads restored: 0.02.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (2, 0) | 7/24 | 13/24 | 1/24 | 6/24 |
| (2, 2) | 2/24 | 7/24 | 4/24 | 6/24 |
| (3, 3) | 1/24 | 6/24 | 5/24 | 1/24 |

## data-sem1 llama-20004-s2

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.40 | 0.40 | 0.02 |
| 2 | 0.40 | 0.00 | 0.00 | 0.02 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.19) | 0.00 (w 0.26) | 0.10 (w 0.91) | 0.00 (w 0.34) |
| 2 | 0.00 (w 0.89) | 0.00 (w 0.54) | 0.00 (w 0.65) | 0.02 (w 0.90) |
| 3 | 0.00 (w 0.18) | 0.00 (w 0.15) | 0.00 (w 0.18) | 0.00 (w 0.14) |
| 4 | 0.00 (w 0.17) | 0.00 (w 0.20) | 0.00 (w 0.23) | 0.00 (w 0.03) |

Top three heads [(1, 2), (2, 3), (1, 0)] patched together: 0.58. Three other heads [(3, 0), (2, 0), (3, 1)]: 0.00.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (1,2) | 0.15 | +9.44 |
| (2,3) | 0.00 | +1.98 |
| (1,0) | 0.00 | +0.12 |
| (1,2), (2,3) | 0.45 | +14.23 |
| (1,2), (1,0) | 0.20 | +10.66 |
| (2,3), (1,0) | 0.00 | +2.53 |
| (1,2), (2,3), (1,0) | 0.58 | +15.61 |

Sum of the single heads' changes: +11.54 bits; all three together: +15.61 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.53. Other heads restored: 0.02.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 2) | 10/24 | 8/24 | 1/24 | 10/24 |
| (2, 3) | 0/24 | 12/24 | 4/24 | 7/24 |
| (1, 0) | 2/24 | 1/24 | 6/24 | 11/24 |

## data-sem1 transformer-20004-s3

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.99 | 0.99 | 0.00 |
| 2 | 0.99 | 0.62 | 0.62 | 0.01 |
| 3 | 0.62 | 0.07 | 0.07 | 0.01 |
| 4 | 0.07 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.02) | 0.00 (w 0.44) | 0.00 (w 0.25) | 0.00 (w 0.10) |
| 2 | 0.05 (w 0.73) | 0.00 (w 0.27) | 0.00 (w 0.13) | 0.00 (w 0.65) |
| 3 | 0.00 (w 0.56) | 0.00 (w 0.69) | 0.00 (w 0.30) | 0.00 (w 0.11) |
| 4 | 0.00 (w 0.05) | 0.00 (w 0.52) | 0.00 (w 0.19) | 0.00 (w 0.87) |

Top three heads [(2, 0), (1, 0), (1, 1)] patched together: 0.08. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.18.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (2,0) | 0.05 | +4.54 |
| (1,0) | 0.00 | +0.02 |
| (1,1) | 0.00 | +1.10 |
| (2,0), (1,0) | 0.05 | +4.57 |
| (2,0), (1,1) | 0.08 | +5.58 |
| (1,0), (1,1) | 0.00 | +1.12 |
| (2,0), (1,0), (1,1) | 0.08 | +5.61 |

Sum of the single heads' changes: +5.66 bits; all three together: +5.61 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.05. Other heads restored: 0.07.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (2, 0) | 5/24 | 13/24 | 3/24 | 6/24 |
| (1, 0) | 1/24 | 1/24 | 1/24 | 2/24 |
| (1, 1) | 2/24 | 3/24 | 3/24 | 7/24 |

## data-sem1 llama-20004-s3

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.19 | 0.19 | 0.01 |
| 2 | 0.19 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.56) | 0.13 (w 0.81) | 0.00 (w 0.38) | 0.00 (w 0.03) |
| 2 | 0.00 (w 0.83) | 0.00 (w 0.59) | 0.00 (w 0.43) | 0.00 (w 0.78) |
| 3 | 0.00 (w 0.27) | 0.00 (w 0.28) | 0.00 (w 0.42) | 0.00 (w 0.31) |
| 4 | 0.00 (w 0.14) | 0.00 (w 0.20) | 0.00 (w 0.05) | 0.00 (w 0.07) |

Top three heads [(1, 1), (1, 0), (1, 2)] patched together: 0.73. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.00.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (1,1) | 0.13 | +7.83 |
| (1,0) | 0.00 | +2.53 |
| (1,2) | 0.00 | +1.37 |
| (1,1), (1,0) | 0.45 | +14.27 |
| (1,1), (1,2) | 0.33 | +11.51 |
| (1,0), (1,2) | 0.02 | +5.32 |
| (1,1), (1,0), (1,2) | 0.73 | +18.40 |

Sum of the single heads' changes: +11.74 bits; all three together: +18.40 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.72. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 1) | 1/24 | 12/24 | 1/24 | 6/24 |
| (1, 0) | 3/24 | 5/24 | 2/24 | 10/24 |
| (1, 2) | 2/24 | 3/24 | 1/24 | 6/24 |

## data-sem2 transformer-20004-s1

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.97 | 0.97 | 0.03 |
| 2 | 0.97 | 0.42 | 0.42 | 0.00 |
| 3 | 0.42 | 0.03 | 0.03 | 0.00 |
| 4 | 0.03 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.08) | 0.00 (w 0.10) | 0.00 (w 0.91) | 0.00 (w 0.43) |
| 2 | 0.00 (w 0.69) | 0.00 (w 0.28) | 0.02 (w 0.38) | 0.00 (w 0.44) |
| 3 | 0.00 (w 0.05) | 0.02 (w 0.23) | 0.02 (w 0.60) | 0.00 (w 0.24) |
| 4 | 0.00 (w 0.44) | 0.00 (w 0.90) | 0.00 (w 0.74) | 0.00 (w 0.65) |

Top three heads [(2, 2), (3, 1), (3, 2)] patched together: 0.05. Three other heads [(2, 1), (1, 2), (2, 3)]: 0.08.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (2,2) | 0.00 | +2.00 |
| (3,1) | 0.00 | +1.05 |
| (3,2) | 0.00 | +3.43 |
| (2,2), (3,1) | 0.00 | +3.15 |
| (2,2), (3,2) | 0.03 | +5.63 |
| (3,1), (3,2) | 0.00 | +4.77 |
| (2,2), (3,1), (3,2) | 0.05 | +7.05 |

Sum of the single heads' changes: +6.48 bits; all three together: +7.05 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.05. Other heads restored: 0.05.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (2, 2) | 2/24 | 8/24 | 3/24 | 3/24 |
| (3, 1) | 1/24 | 3/24 | 3/24 | 14/24 |
| (3, 2) | 3/24 | 9/24 | 2/24 | 2/24 |

## data-sem2 llama-20004-s1

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.01 | 0.01 | 0.02 |
| 2 | 0.01 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.10 (w 0.63) | 0.00 (w 0.16) | 0.02 (w 0.53) | 0.07 (w 0.67) |
| 2 | 0.02 (w 0.88) | 0.00 (w 0.17) | 0.00 (w 0.17) | 0.00 (w 0.10) |
| 3 | 0.00 (w 0.27) | 0.00 (w 0.22) | 0.00 (w 0.26) | 0.00 (w 0.21) |
| 4 | 0.00 (w 0.09) | 0.00 (w 0.13) | 0.00 (w 0.05) | 0.00 (w 0.10) |

Top three heads [(1, 0), (1, 3), (1, 2)] patched together: 0.97. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.00.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (1,0) | 0.07 | +6.83 |
| (1,3) | 0.02 | +5.77 |
| (1,2) | 0.02 | +4.11 |
| (1,0), (1,3) | 0.55 | +15.59 |
| (1,0), (1,2) | 0.52 | +14.22 |
| (1,3), (1,2) | 0.37 | +12.72 |
| (1,0), (1,3), (1,2) | 0.97 | +22.82 |

Sum of the single heads' changes: +16.70 bits; all three together: +22.82 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.98. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 0) | 4/24 | 5/24 | 2/24 | 1/24 |
| (1, 3) | 3/24 | 3/24 | 1/24 | 3/24 |
| (1, 2) | 3/24 | 5/24 | 1/24 | 4/24 |

## data-sem2 transformer-20004-s2

Machinery check: patching a prompt with its own state leaves the answer: 23 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 0.97 | 0.97 | 0.97 | 0.04 |
| 2 | 0.97 | 0.23 | 0.23 | 0.02 |
| 3 | 0.23 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.04) | 0.00 (w 0.53) | 0.00 (w 0.23) | 0.00 (w 0.32) |
| 2 | 0.07 (w 0.84) | 0.00 (w 0.26) | 0.10 (w 0.89) | 0.00 (w 0.17) |
| 3 | 0.00 (w 0.03) | 0.03 (w 0.46) | 0.08 (w 0.68) | 0.00 (w 0.17) |
| 4 | 0.00 (w 0.16) | 0.00 (w 0.42) | 0.00 (w 0.02) | 0.02 (w 0.47) |

Top three heads [(2, 2), (3, 2), (2, 0)] patched together: 0.72. Three other heads [(2, 3), (1, 2), (3, 0)]: 0.00.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (2,2) | 0.12 | +7.03 |
| (3,2) | 0.03 | +3.89 |
| (2,0) | 0.07 | +5.57 |
| (2,2), (3,2) | 0.27 | +11.23 |
| (2,2), (2,0) | 0.57 | +13.24 |
| (3,2), (2,0) | 0.17 | +9.48 |
| (2,2), (3,2), (2,0) | 0.72 | +17.38 |

Sum of the single heads' changes: +16.49 bits; all three together: +17.38 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.77. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (2, 2) | 2/24 | 13/24 | 1/24 | 3/24 |
| (3, 2) | 3/24 | 10/24 | 2/24 | 3/24 |
| (2, 0) | 8/24 | 13/24 | 1/24 | 1/24 |

## data-sem2 llama-20004-s2

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.06 | 0.06 | 0.01 |
| 2 | 0.06 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.12) | 0.00 (w 0.20) | 0.42 (w 0.99) | 0.00 (w 0.40) |
| 2 | 0.00 (w 0.82) | 0.00 (w 0.25) | 0.00 (w 0.63) | 0.00 (w 0.47) |
| 3 | 0.00 (w 0.22) | 0.00 (w 0.40) | 0.00 (w 0.26) | 0.00 (w 0.34) |
| 4 | 0.00 (w 0.18) | 0.00 (w 0.25) | 0.00 (w 0.15) | 0.00 (w 0.02) |

Top three heads [(1, 2), (1, 0), (1, 1)] patched together: 0.65. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.00.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (1,2) | 0.43 | +13.33 |
| (1,0) | 0.00 | +0.11 |
| (1,1) | 0.00 | +0.83 |
| (1,2), (1,0) | 0.52 | +14.24 |
| (1,2), (1,1) | 0.60 | +16.24 |
| (1,0), (1,1) | 0.00 | +1.06 |
| (1,2), (1,0), (1,1) | 0.65 | +17.19 |

Sum of the single heads' changes: +14.27 bits; all three together: +17.19 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.68. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 2) | 3/24 | 7/24 | 2/24 | 1/24 |
| (1, 0) | 1/24 | 0/24 | 1/24 | 6/24 |
| (1, 1) | 2/24 | 3/24 | 3/24 | 3/24 |

## data-sem2 transformer-20004-s3

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.95 | 0.95 | 0.02 |
| 2 | 0.95 | 0.85 | 0.85 | 0.02 |
| 3 | 0.85 | 0.03 | 0.03 | 0.00 |
| 4 | 0.03 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.17) | 0.02 (w 0.70) | 0.00 (w 0.51) | 0.00 (w 0.08) |
| 2 | 0.00 (w 0.33) | 0.00 (w 0.18) | 0.00 (w 0.13) | 0.00 (w 0.70) |
| 3 | 0.03 (w 0.61) | 0.02 (w 0.67) | 0.00 (w 0.03) | 0.02 (w 0.78) |
| 4 | 0.00 (w 0.36) | 0.00 (w 0.40) | 0.00 (w 0.11) | 0.02 (w 0.63) |

Top three heads [(3, 0), (1, 1), (3, 1)] patched together: 0.17. Three other heads [(2, 2), (1, 3), (2, 3)]: 0.00.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (3,0) | 0.02 | +4.68 |
| (1,1) | 0.02 | +2.21 |
| (3,1) | 0.02 | +3.05 |
| (3,0), (1,1) | 0.07 | +7.12 |
| (3,0), (3,1) | 0.08 | +8.11 |
| (1,1), (3,1) | 0.05 | +5.36 |
| (3,0), (1,1), (3,1) | 0.17 | +10.58 |

Sum of the single heads' changes: +9.94 bits; all three together: +10.58 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.12. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (3, 0) | 1/24 | 10/24 | 1/24 | 1/24 |
| (1, 1) | 0/24 | 3/24 | 2/24 | 1/24 |
| (3, 1) | 5/24 | 7/24 | 4/24 | 4/24 |

## data-sem2 llama-20004-s3

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.60 | 0.60 | 0.01 |
| 2 | 0.60 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.23) | 0.02 (w 0.57) | 0.00 (w 0.47) | 0.00 (w 0.20) |
| 2 | 0.00 (w 0.90) | 0.00 (w 0.94) | 0.00 (w 0.71) | 0.00 (w 0.77) |
| 3 | 0.00 (w 0.16) | 0.00 (w 0.15) | 0.00 (w 0.19) | 0.00 (w 0.23) |
| 4 | 0.00 (w 0.01) | 0.00 (w 0.08) | 0.00 (w 0.16) | 0.00 (w 0.10) |

Top three heads [(1, 1), (1, 0), (1, 2)] patched together: 0.17. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.03.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (1,1) | 0.00 | +4.74 |
| (1,0) | 0.00 | +0.41 |
| (1,2) | 0.00 | +1.98 |
| (1,1), (1,0) | 0.00 | +5.86 |
| (1,1), (1,2) | 0.08 | +8.98 |
| (1,0), (1,2) | 0.00 | +2.64 |
| (1,1), (1,0), (1,2) | 0.17 | +10.43 |

Sum of the single heads' changes: +7.13 bits; all three together: +10.43 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.15. Other heads restored: 0.05.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 1) | 4/24 | 3/24 | 3/24 | 7/24 |
| (1, 0) | 1/24 | 1/24 | 1/24 | 8/24 |
| (1, 2) | 2/24 | 5/24 | 1/24 | 3/24 |

## data-sem3 transformer-20004-s1

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.93 | 0.93 | 0.02 |
| 2 | 0.93 | 0.53 | 0.53 | 0.00 |
| 3 | 0.53 | 0.01 | 0.01 | 0.00 |
| 4 | 0.01 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.06) | 0.00 (w 0.13) | 0.00 (w 0.85) | 0.00 (w 0.55) |
| 2 | 0.00 (w 0.08) | 0.00 (w 0.26) | 0.00 (w 0.03) | 0.05 (w 0.82) |
| 3 | 0.00 (w 0.31) | 0.08 (w 0.82) | 0.00 (w 0.06) | 0.00 (w 0.29) |
| 4 | 0.00 (w 0.26) | 0.02 (w 0.61) | 0.00 (w 0.27) | 0.00 (w 0.02) |

Top three heads [(3, 1), (2, 3), (4, 1)] patched together: 0.78. Three other heads [(2, 1), (1, 2), (2, 2)]: 0.05.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (3,1) | 0.10 | +8.66 |
| (2,3) | 0.03 | +5.92 |
| (4,1) | 0.00 | +2.42 |
| (3,1), (2,3) | 0.57 | +15.92 |
| (3,1), (4,1) | 0.23 | +11.11 |
| (2,3), (4,1) | 0.08 | +8.64 |
| (3,1), (2,3), (4,1) | 0.78 | +18.37 |

Sum of the single heads' changes: +17.00 bits; all three together: +18.37 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.85. Other heads restored: 0.07.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (3, 1) | 1/24 | 14/24 | 1/24 | 3/24 |
| (2, 3) | 7/24 | 16/24 | 3/24 | 11/24 |
| (4, 1) | 3/24 | 10/24 | 1/24 | 1/24 |

## data-sem3 llama-20004-s1

Machinery check: patching a prompt with its own state leaves the answer: 23 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 0.97 | 0.54 | 0.54 | 0.02 |
| 2 | 0.54 | 0.01 | 0.01 | 0.00 |
| 3 | 0.01 | 0.01 | 0.01 | 0.01 |
| 4 | 0.01 | 0.01 | 0.01 | 0.01 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.12 (w 0.78) | 0.02 (w 0.11) | 0.02 (w 0.26) | 0.02 (w 0.29) |
| 2 | 0.03 (w 0.98) | 0.02 (w 0.59) | 0.02 (w 0.44) | 0.02 (w 0.78) |
| 3 | 0.02 (w 0.20) | 0.02 (w 0.16) | 0.02 (w 0.31) | 0.02 (w 0.28) |
| 4 | 0.02 (w 0.04) | 0.02 (w 0.17) | 0.02 (w 0.06) | 0.02 (w 0.11) |

Top three heads [(1, 0), (2, 0), (1, 1)] patched together: 0.63. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.00.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (1,0) | 0.07 | +6.25 |
| (2,0) | 0.03 | +4.20 |
| (1,1) | 0.00 | +0.22 |
| (1,0), (2,0) | 0.57 | +16.21 |
| (1,0), (1,1) | 0.08 | +6.92 |
| (2,0), (1,1) | 0.03 | +4.83 |
| (1,0), (2,0), (1,1) | 0.63 | +17.11 |

Sum of the single heads' changes: +10.67 bits; all three together: +17.11 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.73. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 0) | 3/24 | 4/24 | 2/24 | 2/24 |
| (2, 0) | 6/24 | 16/24 | 5/24 | 7/24 |
| (1, 1) | 2/24 | 1/24 | 3/24 | 7/24 |

## data-sem3 transformer-20004-s2

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.93 | 0.93 | 0.03 |
| 2 | 0.93 | 0.33 | 0.33 | 0.00 |
| 3 | 0.33 | 0.01 | 0.01 | 0.00 |
| 4 | 0.01 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.06) | 0.00 (w 0.59) | 0.00 (w 0.53) | 0.00 (w 0.44) |
| 2 | 0.02 (w 0.73) | 0.00 (w 0.07) | 0.03 (w 0.61) | 0.00 (w 0.40) |
| 3 | 0.00 (w 0.12) | 0.00 (w 0.44) | 0.00 (w 0.52) | 0.00 (w 0.49) |
| 4 | 0.02 (w 0.29) | 0.00 (w 0.08) | 0.00 (w 0.21) | 0.00 (w 0.64) |

Top three heads [(2, 2), (2, 0), (4, 0)] patched together: 0.20. Three other heads [(2, 3), (1, 2), (3, 0)]: 0.02.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (2,2) | 0.00 | +3.07 |
| (2,0) | 0.02 | +5.39 |
| (4,0) | 0.00 | +1.54 |
| (2,2), (2,0) | 0.08 | +8.87 |
| (2,2), (4,0) | 0.00 | +4.64 |
| (2,0), (4,0) | 0.03 | +6.81 |
| (2,2), (2,0), (4,0) | 0.20 | +10.31 |

Sum of the single heads' changes: +9.99 bits; all three together: +10.31 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.17. Other heads restored: 0.02.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (2, 2) | 5/24 | 5/24 | 2/24 | 4/24 |
| (2, 0) | 4/24 | 14/24 | 2/24 | 5/24 |
| (4, 0) | 1/24 | 8/24 | 1/24 | 1/24 |

## data-sem3 llama-20004-s2

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.05 | 0.05 | 0.01 |
| 2 | 0.05 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.37) | 0.00 (w 0.22) | 0.42 (w 0.99) | 0.00 (w 0.02) |
| 2 | 0.02 (w 0.94) | 0.00 (w 0.51) | 0.00 (w 0.36) | 0.00 (w 0.78) |
| 3 | 0.00 (w 0.11) | 0.00 (w 0.08) | 0.00 (w 0.12) | 0.00 (w 0.26) |
| 4 | 0.00 (w 0.19) | 0.00 (w 0.17) | 0.00 (w 0.17) | 0.00 (w 0.05) |

Top three heads [(1, 2), (2, 0), (1, 0)] patched together: 0.95. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.00.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (1,2) | 0.38 | +13.76 |
| (2,0) | 0.00 | +2.24 |
| (1,0) | 0.00 | +1.41 |
| (1,2), (2,0) | 0.85 | +20.08 |
| (1,2), (1,0) | 0.68 | +17.71 |
| (2,0), (1,0) | 0.03 | +4.68 |
| (1,2), (2,0), (1,0) | 0.95 | +23.19 |

Sum of the single heads' changes: +17.41 bits; all three together: +23.19 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.98. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 2) | 6/24 | 5/24 | 3/24 | 6/24 |
| (2, 0) | 5/24 | 8/24 | 0/24 | 3/24 |
| (1, 0) | 1/24 | 2/24 | 4/24 | 13/24 |

## data-sem3 transformer-20004-s3

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 1.00 | 1.00 | 0.01 |
| 2 | 1.00 | 0.88 | 0.88 | 0.01 |
| 3 | 0.88 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.16) | 0.00 (w 0.25) | 0.00 (w 0.34) | 0.00 (w 0.11) |
| 2 | 0.00 (w 0.56) | 0.00 (w 0.09) | 0.00 (w 0.50) | 0.00 (w 0.52) |
| 3 | 0.00 (w 0.59) | 0.00 (w 0.80) | 0.00 (w 0.07) | 0.00 (w 0.64) |
| 4 | 0.00 (w 0.28) | 0.00 (w 0.07) | 0.00 (w 0.46) | 0.00 (w 0.72) |

Top three heads [(1, 0), (1, 1), (1, 2)] patched together: 0.00. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.05.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (1,0) | 0.00 | +0.13 |
| (1,1) | 0.00 | +0.36 |
| (1,2) | 0.00 | +0.68 |
| (1,0), (1,1) | 0.00 | +0.50 |
| (1,0), (1,2) | 0.00 | +0.83 |
| (1,1), (1,2) | 0.00 | +1.08 |
| (1,0), (1,1), (1,2) | 0.00 | +1.24 |

Sum of the single heads' changes: +1.18 bits; all three together: +1.24 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.00. Other heads restored: 0.08.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 0) | 1/24 | 2/24 | 0/24 | 10/24 |
| (1, 1) | 2/24 | 1/24 | 1/24 | 1/24 |
| (1, 2) | 1/24 | 3/24 | 3/24 | 12/24 |

## data-sem3 llama-20004-s3

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.03 | 0.03 | 0.02 |
| 2 | 0.03 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (chosen on the first 60 pairs; the per-head table is over those 60; together and restoration are judged on the other 60. Last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.03 (w 0.79) | 0.00 (w 0.80) | 0.00 (w 0.16) | 0.00 (w 0.59) |
| 2 | 0.00 (w 0.80) | 0.00 (w 0.70) | 0.00 (w 0.18) | 0.00 (w 0.69) |
| 3 | 0.00 (w 0.25) | 0.00 (w 0.38) | 0.00 (w 0.20) | 0.00 (w 0.28) |
| 4 | 0.00 (w 0.05) | 0.00 (w 0.20) | 0.00 (w 0.09) | 0.00 (w 0.08) |

Top three heads [(1, 0), (1, 1), (1, 2)] patched together: 0.68. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.00.

**2b. Interactions of the three heads** (judged pairs): share where the donor's capital wins; mean change in log2 P(donor's capital) − log2 P(own capital)

| heads | share | change, bits |
|---|---:|---:|
| (1,0) | 0.03 | +4.97 |
| (1,1) | 0.03 | +4.92 |
| (1,2) | 0.00 | +0.29 |
| (1,0), (1,1) | 0.57 | +16.63 |
| (1,0), (1,2) | 0.05 | +5.94 |
| (1,1), (1,2) | 0.05 | +6.05 |
| (1,0), (1,1), (1,2) | 0.68 | +18.25 |

Sum of the single heads' changes: +10.18 bits; all three together: +18.25 bits.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.70. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 0) | 3/24 | 4/24 | 3/24 | 7/24 |
| (1, 1) | 3/24 | 11/24 | 2/24 | 8/24 |
| (1, 2) | 1/24 | 2/24 | 3/24 | 5/24 |

