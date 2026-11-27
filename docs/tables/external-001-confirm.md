## data-sem4-v3 llama-20004-s1

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.76 | 1.00 | **0.82** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 0.97 | **0.97** | 0.94 | 1.00 |
| C: both from the state | 0.74 | 0.97 | **0.82** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.74 | 0.97 | **0.47** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.71 | 1.00 | **0.82** | 1.00 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': -0.12, 'continent': 0.04, 'home': -0.09, 'birth': 0.02}.

## data-sem4-v3 transformer-20004-s1

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 1.00 | 1.00 |
| A: entity from the state | 0.35 | 1.00 | **0.82** | 1.00 | 1.00 |
| B: relation from the state | 1.00 | 0.97 | **0.97** | 0.97 | 1.00 |
| C: both from the state | 0.32 | 0.97 | **0.82** | 1.00 | 1.00 |
| D: both from the state, edited graph | 0.32 | 0.97 | **0.18** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.29 | 1.00 | **0.82** | 0.97 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': 0.1, 'continent': 0.06, 'home': 0.21, 'birth': 0.17}.

## data-sem4-v3 llama-20004-s2

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.91 | 1.00 |
| A: entity from the state | 0.82 | 1.00 | **0.97** | 0.91 | 1.00 |
| B: relation from the state | 1.00 | 0.97 | **0.97** | 0.91 | 1.00 |
| C: both from the state | 0.82 | 0.97 | **0.94** | 0.91 | 1.00 |
| D: both from the state, edited graph | 0.82 | 0.97 | **0.68** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.74 | 1.00 | **0.85** | 0.91 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.25 | 1.00 | **0.00** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': -0.03, 'continent': -0.0, 'home': 0.1, 'birth': -0.08}.

## data-sem4-v3 transformer-20004-s2

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.38 | 1.00 | **0.53** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| C: both from the state | 0.38 | 1.00 | **0.53** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.38 | 1.00 | **0.18** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.53 | 1.00 | **0.65** | 0.94 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.00 | 1.00 | **0.00** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': -0.04, 'continent': 0.08, 'home': -0.01, 'birth': 0.06}.

## data-sem4-v3 llama-20004-s3

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.88 | 1.00 | **0.88** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 0.94 | **0.94** | 0.94 | 1.00 |
| C: both from the state | 0.85 | 0.94 | **0.85** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.85 | 0.94 | **0.65** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.85 | 1.00 | **0.88** | 0.97 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': -0.07, 'continent': -0.01, 'home': 0.07, 'birth': -0.21}.

## data-sem4-v3 transformer-20004-s3

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.29 | 1.00 | **0.68** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.82** | 0.82 | 1.00 |
| C: both from the state | 0.26 | 0.82 | **0.68** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.26 | 0.82 | **0.06** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.41 | 1.00 | **0.82** | 1.00 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': -0.08, 'continent': 0.1, 'home': -0.04, 'birth': 0.04}.

## data-sem5-v3 llama-20004-s1

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.91 | 1.00 |
| A: entity from the state | 0.82 | 1.00 | **0.97** | 0.91 | 1.00 |
| B: relation from the state | 1.00 | 0.97 | **0.97** | 0.88 | 1.00 |
| C: both from the state | 0.79 | 0.97 | **0.97** | 0.91 | 1.00 |
| D: both from the state, edited graph | 0.79 | 0.97 | **0.68** | 0.03 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.65 | 1.00 | **0.82** | 0.82 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 1.00 | 1.00 | **1.00** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation capital; cosine to each centroid {'capital': 0.03, 'continent': 0.02, 'home': -0.11, 'birth': -0.11}.

## data-sem5-v3 transformer-20004-s1

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 1.00 | 1.00 |
| A: entity from the state | 0.32 | 1.00 | **0.71** | 1.00 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.82** | 0.82 | 1.00 |
| C: both from the state | 0.29 | 0.82 | **0.74** | 1.00 | 1.00 |
| D: both from the state, edited graph | 0.29 | 0.82 | **0.06** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.21 | 1.00 | **0.68** | 0.97 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation birth; cosine to each centroid {'capital': -0.0, 'continent': 0.08, 'home': 0.14, 'birth': 0.15}.

## data-sem5-v3 llama-20004-s2

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.88 | 1.00 |
| A: entity from the state | 0.91 | 1.00 | **0.91** | 0.88 | 1.00 |
| B: relation from the state | 1.00 | 0.97 | **0.97** | 0.85 | 1.00 |
| C: both from the state | 0.88 | 0.97 | **0.91** | 0.88 | 1.00 |
| D: both from the state, edited graph | 0.88 | 0.97 | **0.79** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.91 | 1.00 | **0.91** | 0.88 | 0.94 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': 0.2, 'continent': -0.05, 'home': 0.32, 'birth': -0.08}.

## data-sem5-v3 transformer-20004-s2

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.94 | 1.00 |
| A: entity from the state | 0.59 | 1.00 | **0.76** | 0.94 | 1.00 |
| B: relation from the state | 1.00 | 1.00 | **1.00** | 0.94 | 1.00 |
| C: both from the state | 0.59 | 1.00 | **0.76** | 0.94 | 1.00 |
| D: both from the state, edited graph | 0.59 | 1.00 | **0.24** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.62 | 1.00 | **0.79** | 0.94 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.50 | 1.00 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation birth; cosine to each centroid {'capital': 0.02, 'continent': 0.05, 'home': 0.03, 'birth': 0.06}.

## data-sem5-v3 llama-20004-s3

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.82 | 1.00 |
| A: entity from the state | 0.82 | 1.00 | **0.85** | 0.82 | 1.00 |
| B: relation from the state | 1.00 | 0.76 | **0.76** | 0.71 | 1.00 |
| C: both from the state | 0.68 | 0.76 | **0.62** | 0.82 | 1.00 |
| D: both from the state, edited graph | 0.68 | 0.76 | **0.47** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.82 | 1.00 | **0.82** | 0.76 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': -0.07, 'continent': -0.13, 'home': 0.1, 'birth': -0.08}.

## data-sem5-v3 transformer-20004-s3

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.35 | 1.00 | **0.79** | 0.97 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.82** | 0.79 | 1.00 |
| C: both from the state | 0.26 | 0.82 | **0.68** | 0.97 | 1.00 |
| D: both from the state, edited graph | 0.26 | 0.82 | **0.09** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.38 | 1.00 | **0.79** | 0.94 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.50** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': 0.1, 'continent': 0.1, 'home': -0.01, 'birth': 0.04}.

## data-sem6-v3 llama-20004-s1

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.76 | 1.00 |
| A: entity from the state | 0.62 | 1.00 | **0.65** | 0.71 | 1.00 |
| B: relation from the state | 1.00 | 1.00 | **1.00** | 0.76 | 1.00 |
| C: both from the state | 0.62 | 1.00 | **0.65** | 0.71 | 1.00 |
| D: both from the state, edited graph | 0.62 | 1.00 | **0.56** | 0.06 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.56 | 1.00 | **0.65** | 0.68 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation capital; cosine to each centroid {'capital': 0.1, 'continent': 0.02, 'home': -0.01, 'birth': 0.08}.

## data-sem6-v3 transformer-20004-s1

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 1.00 | 1.00 |
| A: entity from the state | 0.53 | 1.00 | **0.74** | 1.00 | 1.00 |
| B: relation from the state | 1.00 | 1.00 | **1.00** | 1.00 | 1.00 |
| C: both from the state | 0.53 | 1.00 | **0.74** | 1.00 | 1.00 |
| D: both from the state, edited graph | 0.53 | 1.00 | **0.18** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.29 | 1.00 | **0.82** | 0.94 | 0.97 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation birth; cosine to each centroid {'capital': 0.01, 'continent': 0.06, 'home': 0.07, 'birth': 0.1}.

## data-sem6-v3 llama-20004-s2

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.91 | 1.00 |
| A: entity from the state | 0.91 | 1.00 | **0.94** | 0.91 | 1.00 |
| B: relation from the state | 1.00 | 0.82 | **0.88** | 0.79 | 1.00 |
| C: both from the state | 0.79 | 0.82 | **0.91** | 0.91 | 1.00 |
| D: both from the state, edited graph | 0.79 | 0.82 | **0.53** | 0.03 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.79 | 1.00 | **0.88** | 0.79 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.25 | 1.00 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': -0.17, 'continent': -0.13, 'home': 0.15, 'birth': -0.11}.

## data-sem6-v3 transformer-20004-s2

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 1.00 | 1.00 |
| A: entity from the state | 0.79 | 1.00 | **0.88** | 1.00 | 1.00 |
| B: relation from the state | 1.00 | 0.91 | **0.91** | 0.91 | 1.00 |
| C: both from the state | 0.71 | 0.91 | **0.85** | 1.00 | 1.00 |
| D: both from the state, edited graph | 0.71 | 0.91 | **0.06** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.74 | 1.00 | **0.88** | 0.94 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation birth; cosine to each centroid {'capital': 0.01, 'continent': -0.01, 'home': -0.06, 'birth': 0.05}.

## data-sem6-v3 llama-20004-s3

Read after block 1, inject at block 3. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.91 | 1.00 |
| A: entity from the state | 0.82 | 1.00 | **0.82** | 0.91 | 1.00 |
| B: relation from the state | 1.00 | 1.00 | **1.00** | 0.91 | 1.00 |
| C: both from the state | 0.82 | 1.00 | **0.82** | 0.91 | 1.00 |
| D: both from the state, edited graph | 0.82 | 1.00 | **0.68** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.65 | 1.00 | **0.68** | 0.88 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.75 | 1.00 | **0.75** | 0.25 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation home; cosine to each centroid {'capital': -0.06, 'continent': -0.18, 'home': -0.04, 'birth': -0.09}.

## data-sem6-v3 transformer-20004-s3

Read after block 2, inject at block 4. Known entities: 24 countries, 44 people; held out: 6 countries, 11 people; 4 single-observation people.

| arm | entity decoded | relation decoded | model gives the graph's answer | random injection gives it | provider disabled gives it |
|---|---:|---:|---:|---:|---:|
| oracle (true graph) | 1.00 | 1.00 | **1.00** | 0.97 | 1.00 |
| A: entity from the state | 0.35 | 1.00 | **0.74** | 1.00 | 1.00 |
| B: relation from the state | 1.00 | 0.94 | **0.94** | 0.91 | 1.00 |
| C: both from the state | 0.29 | 0.94 | **0.68** | 1.00 | 1.00 |
| D: both from the state, edited graph | 0.29 | 0.94 | **0.21** | 0.00 | 0.00 |
| paraphrase control: arm C on wording 2 (where the centroids were fitted; not counted) | 0.35 | 1.00 | **0.62** | 0.91 | 1.00 |
| E: both from the state, new birth facts (single-observation people) | 0.25 | 1.00 | **0.25** | 0.00 | 0.00 |

A prompt the provider should not answer (`the`): nearest relation continent; cosine to each centroid {'capital': 0.05, 'continent': 0.07, 'home': -0.06, 'birth': 0.03}.

