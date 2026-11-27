## data-sem1 transformer-20004-s1

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.97 | 0.97 | 0.03 |
| 2 | 0.97 | 0.20 | 0.20 | 0.01 |
| 3 | 0.20 | 0.03 | 0.03 | 0.00 |
| 4 | 0.03 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.08) | 0.00 (w 0.11) | 0.00 (w 0.71) | 0.00 (w 0.75) |
| 2 | 0.00 (w 0.10) | 0.00 (w 0.11) | 0.06 (w 0.82) | 0.06 (w 0.77) |
| 3 | 0.00 (w 0.07) | 0.04 (w 0.64) | 0.01 (w 0.13) | 0.00 (w 0.07) |
| 4 | 0.00 (w 0.51) | 0.00 (w 0.10) | 0.00 (w 0.16) | 0.00 (w 0.84) |

Top three heads [(2, 2), (2, 3), (3, 1)] patched together: 0.78. Three other heads [(2, 1), (1, 2), (3, 0)]: 0.01.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.75. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (2, 2) | 4/24 | 11/24 | 1/24 | 1/24 |
| (2, 3) | 3/24 | 11/24 | 4/24 | 4/24 |
| (3, 1) | 2/24 | 12/24 | 1/24 | 2/24 |

## data-sem1 llama-20004-s1

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.03 | 0.03 | 0.02 |
| 2 | 0.03 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.35) | 0.00 (w 0.21) | 0.00 (w 0.37) | 0.11 (w 0.68) |
| 2 | 0.01 (w 0.85) | 0.00 (w 0.14) | 0.00 (w 0.38) | 0.00 (w 0.26) |
| 3 | 0.00 (w 0.08) | 0.00 (w 0.14) | 0.00 (w 0.20) | 0.00 (w 0.14) |
| 4 | 0.00 (w 0.15) | 0.00 (w 0.16) | 0.00 (w 0.09) | 0.00 (w 0.04) |

Top three heads [(1, 3), (2, 0), (1, 0)] patched together: 0.84. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.00.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.84. Other heads restored: 0.00.

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
| 2 | 0.95 | 0.08 | 0.08 | 0.03 |
| 3 | 0.08 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.10) | 0.00 (w 0.54) | 0.00 (w 0.54) | 0.00 (w 0.28) |
| 2 | 0.06 (w 0.92) | 0.00 (w 0.03) | 0.02 (w 0.87) | 0.00 (w 0.31) |
| 3 | 0.00 (w 0.13) | 0.00 (w 0.20) | 0.00 (w 0.21) | 0.01 (w 0.36) |
| 4 | 0.00 (w 0.47) | 0.00 (w 0.24) | 0.00 (w 0.04) | 0.01 (w 0.32) |

Top three heads [(2, 0), (2, 2), (3, 3)] patched together: 0.73. Three other heads [(2, 3), (1, 2), (3, 0)]: 0.00.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.71. Other heads restored: 0.01.

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
| 1 | 1.00 | 0.40 | 0.40 | 0.03 |
| 2 | 0.40 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.19) | 0.00 (w 0.26) | 0.12 (w 0.91) | 0.01 (w 0.34) |
| 2 | 0.00 (w 0.89) | 0.00 (w 0.54) | 0.02 (w 0.65) | 0.01 (w 0.90) |
| 3 | 0.00 (w 0.18) | 0.00 (w 0.15) | 0.00 (w 0.18) | 0.00 (w 0.14) |
| 4 | 0.00 (w 0.17) | 0.00 (w 0.20) | 0.00 (w 0.23) | 0.00 (w 0.03) |

Top three heads [(1, 2), (2, 2), (1, 3)] patched together: 0.66. Three other heads [(3, 0), (2, 0), (3, 1)]: 0.00.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.65. Other heads restored: 0.03.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 2) | 10/24 | 8/24 | 1/24 | 10/24 |
| (2, 2) | 0/24 | 11/24 | 4/24 | 7/24 |
| (1, 3) | 1/24 | 3/24 | 6/24 | 11/24 |

## data-sem1 transformer-20004-s3

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.99 | 0.99 | 0.00 |
| 2 | 0.99 | 0.62 | 0.62 | 0.00 |
| 3 | 0.62 | 0.07 | 0.07 | 0.00 |
| 4 | 0.07 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.02) | 0.00 (w 0.44) | 0.00 (w 0.25) | 0.00 (w 0.10) |
| 2 | 0.05 (w 0.73) | 0.00 (w 0.27) | 0.00 (w 0.13) | 0.01 (w 0.65) |
| 3 | 0.01 (w 0.56) | 0.00 (w 0.69) | 0.00 (w 0.30) | 0.00 (w 0.11) |
| 4 | 0.00 (w 0.05) | 0.00 (w 0.52) | 0.00 (w 0.19) | 0.02 (w 0.87) |

Top three heads [(2, 0), (4, 3), (2, 3)] patched together: 0.38. Three other heads [(2, 2), (1, 2), (3, 0)]: 0.03.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.36. Other heads restored: 0.03.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (2, 0) | 5/24 | 13/24 | 1/24 | 1/24 |
| (4, 3) | 2/24 | 12/24 | 1/24 | 3/24 |
| (2, 3) | 4/24 | 2/24 | 3/24 | 6/24 |

## data-sem1 llama-20004-s3

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.19 | 0.19 | 0.01 |
| 2 | 0.19 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.56) | 0.13 (w 0.81) | 0.00 (w 0.38) | 0.00 (w 0.03) |
| 2 | 0.00 (w 0.83) | 0.00 (w 0.59) | 0.00 (w 0.43) | 0.00 (w 0.78) |
| 3 | 0.00 (w 0.27) | 0.00 (w 0.28) | 0.00 (w 0.42) | 0.00 (w 0.31) |
| 4 | 0.00 (w 0.14) | 0.00 (w 0.20) | 0.00 (w 0.05) | 0.00 (w 0.07) |

Top three heads [(1, 1), (1, 0), (1, 2)] patched together: 0.71. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.00.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.74. Other heads restored: 0.00.

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

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.08) | 0.00 (w 0.10) | 0.01 (w 0.91) | 0.00 (w 0.43) |
| 2 | 0.00 (w 0.69) | 0.00 (w 0.28) | 0.01 (w 0.38) | 0.00 (w 0.44) |
| 3 | 0.00 (w 0.05) | 0.01 (w 0.23) | 0.01 (w 0.60) | 0.00 (w 0.24) |
| 4 | 0.00 (w 0.44) | 0.00 (w 0.90) | 0.00 (w 0.74) | 0.00 (w 0.65) |

Top three heads [(1, 2), (2, 2), (3, 1)] patched together: 0.16. Three other heads [(2, 3), (1, 3), (3, 0)]: 0.00.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.15. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 2) | 3/24 | 14/24 | 2/24 | 2/24 |
| (2, 2) | 2/24 | 8/24 | 1/24 | 3/24 |
| (3, 1) | 1/24 | 3/24 | 1/24 | 2/24 |

## data-sem2 llama-20004-s1

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.01 | 0.01 | 0.02 |
| 2 | 0.01 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.08 (w 0.63) | 0.00 (w 0.16) | 0.02 (w 0.53) | 0.04 (w 0.67) |
| 2 | 0.01 (w 0.88) | 0.00 (w 0.17) | 0.00 (w 0.17) | 0.00 (w 0.10) |
| 3 | 0.00 (w 0.27) | 0.00 (w 0.22) | 0.00 (w 0.26) | 0.00 (w 0.21) |
| 4 | 0.00 (w 0.09) | 0.00 (w 0.13) | 0.00 (w 0.05) | 0.00 (w 0.10) |

Top three heads [(1, 0), (1, 3), (1, 2)] patched together: 0.96. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.00.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.97. Other heads restored: 0.00.

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
| 1 | 0.97 | 0.97 | 0.97 | 0.01 |
| 2 | 0.97 | 0.23 | 0.23 | 0.01 |
| 3 | 0.23 | 0.00 | 0.00 | 0.01 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.04) | 0.00 (w 0.53) | 0.00 (w 0.23) | 0.00 (w 0.32) |
| 2 | 0.07 (w 0.84) | 0.00 (w 0.26) | 0.11 (w 0.89) | 0.00 (w 0.17) |
| 3 | 0.00 (w 0.03) | 0.02 (w 0.46) | 0.06 (w 0.68) | 0.00 (w 0.17) |
| 4 | 0.00 (w 0.16) | 0.00 (w 0.42) | 0.00 (w 0.02) | 0.01 (w 0.47) |

Top three heads [(2, 2), (2, 0), (3, 2)] patched together: 0.75. Three other heads [(2, 3), (1, 2), (3, 0)]: 0.00.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.76. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (2, 2) | 2/24 | 13/24 | 1/24 | 3/24 |
| (2, 0) | 8/24 | 13/24 | 2/24 | 3/24 |
| (3, 2) | 3/24 | 10/24 | 1/24 | 1/24 |

## data-sem2 llama-20004-s2

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.06 | 0.06 | 0.01 |
| 2 | 0.06 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.12) | 0.00 (w 0.20) | 0.42 (w 0.99) | 0.00 (w 0.40) |
| 2 | 0.00 (w 0.82) | 0.00 (w 0.25) | 0.00 (w 0.63) | 0.00 (w 0.47) |
| 3 | 0.00 (w 0.22) | 0.00 (w 0.40) | 0.00 (w 0.26) | 0.00 (w 0.34) |
| 4 | 0.00 (w 0.18) | 0.00 (w 0.25) | 0.00 (w 0.15) | 0.00 (w 0.02) |

Top three heads [(1, 2), (1, 0), (1, 1)] patched together: 0.63. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.00.

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
| 1 | 1.00 | 0.95 | 0.95 | 0.04 |
| 2 | 0.95 | 0.85 | 0.85 | 0.01 |
| 3 | 0.85 | 0.03 | 0.03 | 0.01 |
| 4 | 0.03 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.17) | 0.02 (w 0.70) | 0.00 (w 0.51) | 0.00 (w 0.08) |
| 2 | 0.00 (w 0.33) | 0.00 (w 0.18) | 0.00 (w 0.13) | 0.00 (w 0.70) |
| 3 | 0.03 (w 0.61) | 0.02 (w 0.67) | 0.00 (w 0.03) | 0.03 (w 0.78) |
| 4 | 0.02 (w 0.36) | 0.00 (w 0.40) | 0.00 (w 0.11) | 0.01 (w 0.63) |

Top three heads [(3, 0), (3, 3), (1, 1)] patched together: 0.42. Three other heads [(2, 2), (1, 3), (2, 3)]: 0.00.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.41. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (3, 0) | 1/24 | 10/24 | 1/24 | 1/24 |
| (3, 3) | 3/24 | 15/24 | 2/24 | 1/24 |
| (1, 1) | 0/24 | 3/24 | 4/24 | 4/24 |

## data-sem2 llama-20004-s3

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.60 | 0.60 | 0.03 |
| 2 | 0.60 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.23) | 0.01 (w 0.57) | 0.00 (w 0.47) | 0.00 (w 0.20) |
| 2 | 0.00 (w 0.90) | 0.01 (w 0.94) | 0.00 (w 0.71) | 0.00 (w 0.77) |
| 3 | 0.00 (w 0.16) | 0.00 (w 0.15) | 0.00 (w 0.19) | 0.00 (w 0.23) |
| 4 | 0.00 (w 0.01) | 0.00 (w 0.08) | 0.00 (w 0.16) | 0.00 (w 0.10) |

Top three heads [(1, 1), (2, 1), (1, 0)] patched together: 0.31. Three other heads [(3, 0), (2, 0), (3, 1)]: 0.01.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.34. Other heads restored: 0.01.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 1) | 4/24 | 3/24 | 3/24 | 7/24 |
| (2, 1) | 1/24 | 8/24 | 1/24 | 6/24 |
| (1, 0) | 1/24 | 1/24 | 1/24 | 3/24 |

## data-sem3 transformer-20004-s1

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.93 | 0.93 | 0.02 |
| 2 | 0.93 | 0.53 | 0.53 | 0.01 |
| 3 | 0.53 | 0.01 | 0.01 | 0.00 |
| 4 | 0.01 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.06) | 0.00 (w 0.13) | 0.03 (w 0.85) | 0.00 (w 0.55) |
| 2 | 0.00 (w 0.08) | 0.00 (w 0.26) | 0.00 (w 0.03) | 0.04 (w 0.82) |
| 3 | 0.00 (w 0.31) | 0.09 (w 0.82) | 0.00 (w 0.06) | 0.00 (w 0.29) |
| 4 | 0.00 (w 0.26) | 0.01 (w 0.61) | 0.00 (w 0.27) | 0.00 (w 0.02) |

Top three heads [(3, 1), (2, 3), (1, 2)] patched together: 0.91. Three other heads [(2, 2), (1, 3), (3, 0)]: 0.00.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.93. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (3, 1) | 1/24 | 14/24 | 1/24 | 1/24 |
| (2, 3) | 7/24 | 16/24 | 3/24 | 4/24 |
| (1, 2) | 3/24 | 11/24 | 1/24 | 5/24 |

## data-sem3 llama-20004-s1

Machinery check: patching a prompt with its own state leaves the answer: 23 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 0.97 | 0.54 | 0.54 | 0.03 |
| 2 | 0.54 | 0.01 | 0.01 | 0.01 |
| 3 | 0.01 | 0.01 | 0.01 | 0.01 |
| 4 | 0.01 | 0.01 | 0.01 | 0.01 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.09 (w 0.78) | 0.01 (w 0.11) | 0.01 (w 0.26) | 0.01 (w 0.29) |
| 2 | 0.03 (w 0.98) | 0.01 (w 0.59) | 0.01 (w 0.44) | 0.02 (w 0.78) |
| 3 | 0.01 (w 0.20) | 0.01 (w 0.16) | 0.01 (w 0.31) | 0.01 (w 0.28) |
| 4 | 0.01 (w 0.04) | 0.01 (w 0.17) | 0.01 (w 0.06) | 0.01 (w 0.11) |

Top three heads [(1, 0), (2, 0), (2, 3)] patched together: 0.81. Three other heads [(3, 0), (1, 3), (3, 1)]: 0.01.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.84. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 0) | 3/24 | 4/24 | 2/24 | 2/24 |
| (2, 0) | 6/24 | 16/24 | 1/24 | 2/24 |
| (2, 3) | 2/24 | 9/24 | 3/24 | 7/24 |

## data-sem3 transformer-20004-s2

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.93 | 0.93 | 0.02 |
| 2 | 0.93 | 0.33 | 0.33 | 0.03 |
| 3 | 0.33 | 0.01 | 0.01 | 0.00 |
| 4 | 0.01 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.06) | 0.00 (w 0.59) | 0.00 (w 0.53) | 0.00 (w 0.44) |
| 2 | 0.02 (w 0.73) | 0.00 (w 0.07) | 0.02 (w 0.61) | 0.00 (w 0.40) |
| 3 | 0.00 (w 0.12) | 0.00 (w 0.44) | 0.00 (w 0.52) | 0.02 (w 0.49) |
| 4 | 0.01 (w 0.29) | 0.00 (w 0.08) | 0.00 (w 0.21) | 0.00 (w 0.64) |

Top three heads [(2, 0), (2, 2), (3, 3)] patched together: 0.36. Three other heads [(2, 3), (1, 2), (3, 0)]: 0.01.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.33. Other heads restored: 0.01.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (2, 0) | 4/24 | 14/24 | 2/24 | 4/24 |
| (2, 2) | 5/24 | 5/24 | 2/24 | 5/24 |
| (3, 3) | 1/24 | 8/24 | 1/24 | 1/24 |

## data-sem3 llama-20004-s2

Machinery check: patching a prompt with its own state leaves the answer: 24 of 24.

**1. Where in the block the hand-off closes** (country position; share where the donor's capital wins)

| block | at its input | after attention | after the feed-forward (block output) | random, matched (input) |
|---:|---:|---:|---:|---:|
| 1 | 1.00 | 0.05 | 0.05 | 0.02 |
| 2 | 0.05 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.37) | 0.00 (w 0.22) | 0.40 (w 0.99) | 0.00 (w 0.02) |
| 2 | 0.01 (w 0.94) | 0.00 (w 0.51) | 0.00 (w 0.36) | 0.00 (w 0.78) |
| 3 | 0.00 (w 0.11) | 0.00 (w 0.08) | 0.00 (w 0.12) | 0.00 (w 0.26) |
| 4 | 0.00 (w 0.19) | 0.00 (w 0.17) | 0.00 (w 0.17) | 0.00 (w 0.05) |

Top three heads [(1, 2), (2, 0), (1, 0)] patched together: 0.96. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.00.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.97. Other heads restored: 0.00.

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
| 1 | 1.00 | 1.00 | 1.00 | 0.02 |
| 2 | 1.00 | 0.88 | 0.88 | 0.01 |
| 3 | 0.88 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.00 (w 0.16) | 0.00 (w 0.25) | 0.00 (w 0.34) | 0.00 (w 0.11) |
| 2 | 0.00 (w 0.56) | 0.00 (w 0.09) | 0.00 (w 0.50) | 0.00 (w 0.52) |
| 3 | 0.00 (w 0.59) | 0.00 (w 0.80) | 0.00 (w 0.07) | 0.00 (w 0.64) |
| 4 | 0.00 (w 0.28) | 0.00 (w 0.07) | 0.00 (w 0.46) | 0.00 (w 0.72) |

Top three heads [(1, 0), (1, 1), (1, 2)] patched together: 0.00. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.08.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.00. Other heads restored: 0.07.

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
| 1 | 1.00 | 0.03 | 0.03 | 0.01 |
| 2 | 0.03 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

**2. Heads** (last position; patching one head's output from the donor: share where the donor's capital wins; attention weight from the last position to the country)

| block | head 0 | head 1 | head 2 | head 3 |
|---:|---:|---:|---:|---:|
| 1 | 0.03 (w 0.79) | 0.02 (w 0.80) | 0.00 (w 0.16) | 0.00 (w 0.59) |
| 2 | 0.00 (w 0.80) | 0.00 (w 0.70) | 0.00 (w 0.18) | 0.00 (w 0.69) |
| 3 | 0.00 (w 0.25) | 0.00 (w 0.38) | 0.00 (w 0.20) | 0.00 (w 0.28) |
| 4 | 0.00 (w 0.05) | 0.00 (w 0.20) | 0.00 (w 0.09) | 0.00 (w 0.08) |

Top three heads [(1, 0), (1, 1), (1, 2)] patched together: 0.67. Three other heads [(3, 0), (2, 1), (3, 1)]: 0.00.

**3. Restoration**: recipient corrupted to another country; only the top heads' outputs at the last position restored from the clean run. Share where the clean answer returns

Top heads restored: 0.70. Other heads restored: 0.00.

**4. What the top heads carry** (their output at the last position, read through the output head: is the prompt's country, or its capital, the top of its type?)

| head (block, head) | country decodable | capital decodable | other head: country | other head: capital |
|---|---:|---:|---:|---:|
| (1, 0) | 3/24 | 4/24 | 3/24 | 7/24 |
| (1, 1) | 3/24 | 11/24 | 2/24 | 8/24 |
| (1, 2) | 1/24 | 2/24 | 3/24 | 5/24 |

