## data-sem1-v3 llama-20004-s1

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.91 | 1.00 |
| A: entity from the state | 0.68 | 1.00 | **0.76** | 0.91 | 1.00 |
| B: relation from the state | 1.00 | 1.00 | **1.00** | 0.91 | 1.00 |
| C: both from the state | 0.68 | 1.00 | **0.76** | 0.91 | 1.00 |
| D: both from the state, edited graph | 0.68 | 1.00 | **0.59** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.65 | 1.00 | **0.68** | 0.82 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.25 | 1.00 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': -0.1, 'continent': 0.03, 'home': 0.02, 'birth': -0.08}.

## data-sem1-v3 transformer-20004-s1

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 1.00 | 1.00 |
| A: entity from the state | 0.26 | 1.00 | **0.68** | 1.00 | 1.00 |
| B: relation from the state | 1.00 | 0.97 | **0.97** | 0.97 | 1.00 |
| C: both from the state | 0.26 | 0.97 | **0.68** | 1.00 | 1.00 |
| D: both from the state, edited graph | 0.26 | 0.97 | **0.09** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.21 | 1.00 | **0.74** | 0.97 | 0.97 |
| E: both from the state, new birth facts (single-observation people) | 0.25 | 1.00 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation birth; cosine to each centroid {'capital': 0.11, 'continent': 0.07, 'home': 0.12, 'birth': 0.16}.

## data-sem1-v3 llama-20004-s1 READ2

Read after block 2, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.91 | 1.00 |
| A: entity from the state | 0.53 | 1.00 | **0.62** | 0.94 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.82** | 0.79 | 1.00 |
| C: both from the state | 0.41 | 0.82 | **0.44** | 0.94 | 1.00 |
| D: both from the state, edited graph | 0.41 | 0.82 | **0.32** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.56 | 1.00 | **0.62** | 0.82 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': 0.04, 'continent': 0.22, 'home': 0.11, 'birth': 0.05}.

## data-sem1-v3 transformer-20004-s1 READ3

Read after block 3, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 1.00 | 1.00 |
| A: entity from the state | 0.35 | 1.00 | **0.79** | 1.00 | 1.00 |
| B: relation from the state | 1.00 | 0.65 | **0.65** | 0.65 | 1.00 |
| C: both from the state | 0.29 | 0.65 | **0.85** | 1.00 | 1.00 |
| D: both from the state, edited graph | 0.29 | 0.65 | **0.09** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.29 | 1.00 | **0.76** | 0.97 | 0.97 |
| E: both from the state, new birth facts (single-observation people) | 0.25 | 0.25 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': -0.01, 'continent': 0.08, 'home': 0.11, 'birth': 0.11}.

## data-sem1-v3 llama-20004-s2

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.85 | 1.00 |
| A: entity from the state | 0.65 | 1.00 | **0.71** | 0.85 | 1.00 |
| B: relation from the state | 1.00 | 0.85 | **0.88** | 0.79 | 1.00 |
| C: both from the state | 0.56 | 0.85 | **0.65** | 0.85 | 1.00 |
| D: both from the state, edited graph | 0.56 | 0.85 | **0.44** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.62 | 1.00 | **0.74** | 0.71 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.25 | 1.00 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': -0.04, 'continent': 0.05, 'home': 0.13, 'birth': -0.03}.

## data-sem1-v3 transformer-20004-s2

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.62 | 1.00 | **0.85** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| C: both from the state | 0.62 | 1.00 | **0.85** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.62 | 1.00 | **0.24** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.47 | 1.00 | **0.79** | 0.94 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': 0.04, 'continent': 0.04, 'home': 0.05, 'birth': -0.01}.

## data-sem1-v3 llama-20004-s2 READ2

Read after block 2, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.85 | 1.00 |
| A: entity from the state | 0.59 | 1.00 | **0.68** | 0.85 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.82** | 0.71 | 1.00 |
| C: both from the state | 0.50 | 0.82 | **0.59** | 0.85 | 1.00 |
| D: both from the state, edited graph | 0.50 | 0.82 | **0.50** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.41 | 1.00 | **0.56** | 0.65 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.25 | 1.00 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation birth; cosine to each centroid {'capital': 0.1, 'continent': 0.07, 'home': 0.1, 'birth': 0.14}.

## data-sem1-v3 transformer-20004-s2 READ3

Read after block 3, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.32 | 1.00 | **0.74** | 1.00 | 1.00 |
| B: relation from the state | 1.00 | 0.88 | **0.88** | 0.85 | 1.00 |
| C: both from the state | 0.32 | 0.88 | **0.74** | 1.00 | 1.00 |
| D: both from the state, edited graph | 0.32 | 0.88 | **0.15** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.32 | 1.00 | **0.79** | 0.97 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.25 | 1.00 | **0.00** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': 0.02, 'continent': -0.09, 'home': 0.08, 'birth': 0.05}.

## data-sem1-v3 llama-20004-s3

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.71 | 1.00 |
| A: entity from the state | 1.00 | 1.00 | **1.00** | 0.71 | 1.00 |
| B: relation from the state | 1.00 | 0.91 | **0.91** | 0.71 | 1.00 |
| C: both from the state | 0.91 | 0.91 | **0.91** | 0.71 | 1.00 |
| D: both from the state, edited graph | 0.91 | 0.91 | **0.74** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.76 | 1.00 | **0.82** | 0.68 | 0.97 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': -0.09, 'continent': -0.14, 'home': 0.03, 'birth': -0.06}.

## data-sem1-v3 transformer-20004-s3

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.15 | 1.00 | **0.53** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.82** | 0.79 | 1.00 |
| C: both from the state | 0.12 | 0.82 | **0.50** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.12 | 0.82 | **0.00** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.24 | 1.00 | **0.76** | 0.97 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.00 | 1.00 | **0.00** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': 0.02, 'continent': 0.13, 'home': 0.0, 'birth': -0.02}.

## data-sem1-v3 llama-20004-s3 READ2

Read after block 2, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.71 | 1.00 |
| A: entity from the state | 0.79 | 1.00 | **0.88** | 0.71 | 1.00 |
| B: relation from the state | 1.00 | 0.85 | **0.85** | 0.71 | 1.00 |
| C: both from the state | 0.82 | 0.85 | **0.79** | 0.71 | 1.00 |
| D: both from the state, edited graph | 0.82 | 0.85 | **0.62** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.62 | 1.00 | **0.71** | 0.68 | 0.97 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': 0.01, 'continent': 0.02, 'home': 0.21, 'birth': 0.06}.

## data-sem1-v3 transformer-20004-s3 READ3

Read after block 3, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.35 | 1.00 | **0.74** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 0.85 | **0.88** | 0.85 | 1.00 |
| C: both from the state | 0.35 | 0.85 | **0.71** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.35 | 0.85 | **0.06** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.35 | 1.00 | **0.68** | 0.97 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': 0.08, 'continent': 0.14, 'home': 0.07, 'birth': 0.01}.

## data-sem2-v3 llama-20004-s1

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **0.97** | 0.97 | 1.00 |
| A: entity from the state | 0.82 | 1.00 | **0.91** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 1.00 | **0.97** | 0.97 | 1.00 |
| C: both from the state | 0.82 | 1.00 | **0.91** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.82 | 1.00 | **0.76** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.74 | 1.00 | **0.79** | 0.85 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': -0.18, 'continent': -0.18, 'home': -0.0, 'birth': -0.05}.

## data-sem2-v3 transformer-20004-s1

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **0.97** | 0.91 | 1.00 |
| A: entity from the state | 0.47 | 1.00 | **0.82** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.79** | 0.76 | 1.00 |
| C: both from the state | 0.38 | 0.82 | **0.74** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.38 | 0.82 | **0.12** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.41 | 1.00 | **0.76** | 0.88 | 0.97 |
| E: both from the state, new birth facts (single-observation people) | 0.25 | 1.00 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': 0.03, 'continent': 0.03, 'home': 0.1, 'birth': -0.0}.

## data-sem2-v3 llama-20004-s1 READ2

Read after block 2, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **0.97** | 0.97 | 1.00 |
| A: entity from the state | 0.50 | 1.00 | **0.56** | 0.94 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.79** | 0.85 | 1.00 |
| C: both from the state | 0.44 | 0.82 | **0.50** | 0.94 | 1.00 |
| D: both from the state, edited graph | 0.44 | 0.82 | **0.38** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.41 | 1.00 | **0.50** | 0.85 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 0.75 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation capital; cosine to each centroid {'capital': 0.2, 'continent': 0.1, 'home': -0.02, 'birth': 0.06}.

## data-sem2-v3 transformer-20004-s1 READ3

Read after block 3, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **0.97** | 0.91 | 1.00 |
| A: entity from the state | 0.41 | 1.00 | **0.82** | 0.91 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.82** | 0.76 | 1.00 |
| C: both from the state | 0.35 | 0.82 | **0.79** | 0.94 | 1.00 |
| D: both from the state, edited graph | 0.35 | 0.82 | **0.21** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.38 | 1.00 | **0.74** | 0.88 | 0.97 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 0.50 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation birth; cosine to each centroid {'capital': -0.01, 'continent': 0.09, 'home': 0.09, 'birth': 0.09}.

## data-sem2-v3 llama-20004-s2

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **0.97** | 0.88 | 1.00 |
| A: entity from the state | 0.94 | 1.00 | **0.94** | 0.88 | 1.00 |
| B: relation from the state | 1.00 | 0.97 | **0.94** | 0.85 | 1.00 |
| C: both from the state | 0.91 | 0.97 | **0.91** | 0.88 | 1.00 |
| D: both from the state, edited graph | 0.91 | 0.97 | **0.59** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.76 | 1.00 | **0.79** | 0.85 | 0.97 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation capital; cosine to each centroid {'capital': 0.26, 'continent': -0.13, 'home': 0.14, 'birth': -0.13}.

## data-sem2-v3 transformer-20004-s2

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **0.97** | 0.94 | 1.00 |
| A: entity from the state | 0.79 | 1.00 | **0.85** | 0.94 | 1.00 |
| B: relation from the state | 1.00 | 1.00 | **0.97** | 0.94 | 1.00 |
| C: both from the state | 0.79 | 1.00 | **0.85** | 0.94 | 1.00 |
| D: both from the state, edited graph | 0.79 | 1.00 | **0.29** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.59 | 1.00 | **0.76** | 0.91 | 0.97 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation birth; cosine to each centroid {'capital': 0.09, 'continent': 0.06, 'home': -0.02, 'birth': 0.11}.

## data-sem2-v3 llama-20004-s2 READ2

Read after block 2, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **0.97** | 0.88 | 1.00 |
| A: entity from the state | 0.88 | 1.00 | **0.94** | 0.88 | 1.00 |
| B: relation from the state | 1.00 | 0.91 | **0.88** | 0.82 | 1.00 |
| C: both from the state | 0.79 | 0.91 | **0.88** | 0.91 | 1.00 |
| D: both from the state, edited graph | 0.79 | 0.91 | **0.59** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.65 | 1.00 | **0.74** | 0.85 | 0.97 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation capital; cosine to each centroid {'capital': 0.13, 'continent': -0.03, 'home': 0.06, 'birth': -0.12}.

## data-sem2-v3 transformer-20004-s2 READ3

Read after block 3, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **0.97** | 0.94 | 1.00 |
| A: entity from the state | 0.35 | 1.00 | **0.79** | 0.94 | 1.00 |
| B: relation from the state | 1.00 | 0.91 | **0.91** | 0.88 | 1.00 |
| C: both from the state | 0.29 | 0.91 | **0.79** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.29 | 0.91 | **0.21** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.29 | 1.00 | **0.74** | 0.94 | 0.97 |
| E: both from the state, new birth facts (single-observation people) | 1.00 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation birth; cosine to each centroid {'capital': 0.05, 'continent': -0.01, 'home': -0.01, 'birth': 0.06}.

## data-sem2-v3 llama-20004-s3

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **0.97** | 0.85 | 1.00 |
| A: entity from the state | 0.91 | 1.00 | **0.94** | 0.85 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.79** | 0.71 | 1.00 |
| C: both from the state | 0.74 | 0.82 | **0.79** | 0.85 | 1.00 |
| D: both from the state, edited graph | 0.74 | 0.82 | **0.50** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.88 | 1.00 | **0.88** | 0.76 | 0.97 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': -0.16, 'continent': -0.0, 'home': 0.1, 'birth': -0.04}.

## data-sem2-v3 transformer-20004-s3

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **0.97** | 0.94 | 1.00 |
| A: entity from the state | 0.44 | 1.00 | **0.65** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.79** | 0.76 | 1.00 |
| C: both from the state | 0.32 | 0.82 | **0.65** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.32 | 0.82 | **0.03** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.24 | 1.00 | **0.59** | 0.82 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': 0.02, 'continent': 0.09, 'home': -0.01, 'birth': 0.0}.

## data-sem2-v3 llama-20004-s3 READ2

Read after block 2, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **0.97** | 0.85 | 1.00 |
| A: entity from the state | 0.68 | 1.00 | **0.76** | 0.82 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.79** | 0.71 | 1.00 |
| C: both from the state | 0.50 | 0.82 | **0.62** | 0.82 | 1.00 |
| D: both from the state, edited graph | 0.50 | 0.82 | **0.35** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.59 | 1.00 | **0.71** | 0.74 | 0.97 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': -0.07, 'continent': 0.13, 'home': 0.01, 'birth': -0.07}.

## data-sem2-v3 transformer-20004-s3 READ3

Read after block 3, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **0.97** | 0.94 | 1.00 |
| A: entity from the state | 0.53 | 1.00 | **0.71** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 0.97 | **0.94** | 0.91 | 1.00 |
| C: both from the state | 0.50 | 0.97 | **0.71** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.50 | 0.97 | **0.21** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.32 | 1.00 | **0.62** | 0.88 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': -0.01, 'continent': 0.15, 'home': 0.02, 'birth': 0.08}.

## data-sem3-v3 llama-20004-s1

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.76 | 1.00 |
| A: entity from the state | 0.62 | 1.00 | **0.68** | 0.79 | 1.00 |
| B: relation from the state | 1.00 | 1.00 | **1.00** | 0.76 | 1.00 |
| C: both from the state | 0.62 | 1.00 | **0.68** | 0.79 | 1.00 |
| D: both from the state, edited graph | 0.62 | 1.00 | **0.62** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.71 | 1.00 | **0.76** | 0.82 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.25 | 1.00 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': -0.15, 'continent': 0.01, 'home': 0.08, 'birth': 0.0}.

## data-sem3-v3 transformer-20004-s1

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.41 | 1.00 | **0.91** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 0.88 | **0.88** | 0.88 | 1.00 |
| C: both from the state | 0.35 | 0.88 | **0.85** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.35 | 0.88 | **0.03** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.24 | 1.00 | **0.94** | 0.97 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': -0.05, 'continent': 0.08, 'home': 0.12, 'birth': 0.03}.

## data-sem3-v3 llama-20004-s1 READ2

Read after block 2, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.76 | 1.00 |
| A: entity from the state | 0.44 | 1.00 | **0.62** | 0.79 | 1.00 |
| B: relation from the state | 1.00 | 0.91 | **0.91** | 0.74 | 1.00 |
| C: both from the state | 0.44 | 0.91 | **0.59** | 0.79 | 1.00 |
| D: both from the state, edited graph | 0.44 | 0.91 | **0.41** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.35 | 1.00 | **0.53** | 0.88 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': -0.12, 'continent': 0.3, 'home': -0.02, 'birth': -0.18}.

## data-sem3-v3 transformer-20004-s1 READ3

Read after block 3, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.26 | 1.00 | **0.94** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 0.59 | **0.59** | 0.56 | 1.00 |
| C: both from the state | 0.24 | 0.59 | **0.88** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.24 | 0.59 | **0.09** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.26 | 1.00 | **0.88** | 0.97 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.00 | 0.00 | **0.00** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation birth; cosine to each centroid {'capital': -0.04, 'continent': 0.01, 'home': 0.05, 'birth': 0.06}.

## data-sem3-v3 llama-20004-s2

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.94 | 1.00 |
| A: entity from the state | 0.88 | 1.00 | **0.91** | 0.91 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.82** | 0.79 | 1.00 |
| C: both from the state | 0.71 | 0.82 | **0.76** | 0.88 | 1.00 |
| D: both from the state, edited graph | 0.71 | 0.82 | **0.62** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 1.00 | 1.00 | **1.00** | 0.88 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.25 | 1.00 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': 0.02, 'continent': -0.18, 'home': 0.12, 'birth': 0.05}.

## data-sem3-v3 transformer-20004-s2

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 1.00 | 1.00 |
| A: entity from the state | 0.44 | 1.00 | **0.71** | 1.00 | 1.00 |
| B: relation from the state | 1.00 | 0.97 | **0.97** | 0.97 | 1.00 |
| C: both from the state | 0.44 | 0.97 | **0.71** | 1.00 | 1.00 |
| D: both from the state, edited graph | 0.44 | 0.97 | **0.12** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.15 | 1.00 | **0.65** | 1.00 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.00 | 1.00 | **0.00** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation capital; cosine to each centroid {'capital': 0.06, 'continent': 0.06, 'home': 0.04, 'birth': 0.06}.

## data-sem3-v3 llama-20004-s2 READ2

Read after block 2, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.94 | 1.00 |
| A: entity from the state | 0.65 | 1.00 | **0.76** | 0.94 | 1.00 |
| B: relation from the state | 1.00 | 0.79 | **0.79** | 0.79 | 1.00 |
| C: both from the state | 0.50 | 0.79 | **0.59** | 0.94 | 1.00 |
| D: both from the state, edited graph | 0.50 | 0.79 | **0.38** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.59 | 1.00 | **0.74** | 0.91 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation capital; cosine to each centroid {'capital': 0.13, 'continent': -0.05, 'home': -0.0, 'birth': 0.11}.

## data-sem3-v3 transformer-20004-s2 READ3

Read after block 3, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 1.00 | 1.00 |
| A: entity from the state | 0.35 | 1.00 | **0.82** | 1.00 | 1.00 |
| B: relation from the state | 1.00 | 0.88 | **0.91** | 0.91 | 1.00 |
| C: both from the state | 0.38 | 0.88 | **0.85** | 1.00 | 1.00 |
| D: both from the state, edited graph | 0.38 | 0.88 | **0.18** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.35 | 1.00 | **0.76** | 1.00 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 1.00 | 1.00 | **1.00** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation birth; cosine to each centroid {'capital': 0.03, 'continent': -0.03, 'home': 0.02, 'birth': 0.09}.

## data-sem3-v3 llama-20004-s3

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.85 | 1.00 |
| A: entity from the state | 0.88 | 1.00 | **0.88** | 0.85 | 1.00 |
| B: relation from the state | 1.00 | 0.97 | **0.97** | 0.82 | 1.00 |
| C: both from the state | 0.88 | 0.97 | **0.88** | 0.85 | 1.00 |
| D: both from the state, edited graph | 0.88 | 0.97 | **0.68** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.88 | 1.00 | **0.88** | 0.82 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.25 | 1.00 | **0.25** | 0.25 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation birth; cosine to each centroid {'capital': -0.04, 'continent': -0.12, 'home': -0.05, 'birth': -0.02}.

## data-sem3-v3 transformer-20004-s3

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.32 | 1.00 | **0.82** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 0.94 | **0.94** | 0.91 | 1.00 |
| C: both from the state | 0.32 | 0.94 | **0.79** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.32 | 0.94 | **0.15** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.24 | 1.00 | **0.68** | 0.97 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': 0.05, 'continent': 0.05, 'home': 0.06, 'birth': -0.07}.

## data-sem3-v3 llama-20004-s3 READ2

Read after block 2, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.85 | 1.00 |
| A: entity from the state | 0.44 | 1.00 | **0.53** | 0.85 | 1.00 |
| B: relation from the state | 1.00 | 0.88 | **0.88** | 0.76 | 1.00 |
| C: both from the state | 0.35 | 0.88 | **0.44** | 0.88 | 1.00 |
| D: both from the state, edited graph | 0.35 | 0.88 | **0.24** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.44 | 1.00 | **0.56** | 0.82 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': 0.01, 'continent': -0.1, 'home': 0.11, 'birth': -0.05}.

## data-sem3-v3 transformer-20004-s3 READ3

Read after block 3, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.38 | 1.00 | **0.65** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| C: both from the state | 0.38 | 1.00 | **0.65** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.38 | 1.00 | **0.12** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.26 | 1.00 | **0.65** | 0.97 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': 0.07, 'continent': 0.08, 'home': 0.05, 'birth': -0.02}.

