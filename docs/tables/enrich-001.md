## data-sem1-v3 llama-20004-s1

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 1.00 | 0.96 | 1.00 |
| 2 | 1.00 | 1.00 | 1.00 |
| 3 | 1.00 | 1.00 | 1.00 |
| 4 | 1.00 | 1.00 | 1.00 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.10 | 0.00 |
| 3 | 0.73 | 0.00 |
| 4 | 0.88 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem1-v3 transformer-20004-s1

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.02 |
| 2 | 0.00 | 0.00 | 0.02 |
| 3 | 0.00 | 0.00 | 0.02 |
| 4 | 0.00 | 0.02 | 0.02 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 0.96 | 0.92 | 0.96 |
| 2 | 0.96 | 0.96 | 0.96 |
| 3 | 0.96 | 1.00 | 0.96 |
| 4 | 0.96 | 0.96 | 0.96 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.03 | 0.00 |
| 2 | 0.03 | 0.00 |
| 3 | 0.05 | 0.02 |
| 4 | 0.33 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem1-v3 llama-20004-s2

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 0.96 | 0.96 | 0.96 |
| 2 | 0.96 | 0.96 | 0.96 |
| 3 | 0.96 | 0.96 | 0.96 |
| 4 | 0.96 | 0.96 | 0.96 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.02 | 0.00 |
| 2 | 0.27 | 0.00 |
| 3 | 0.78 | 0.00 |
| 4 | 0.77 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem1-v3 transformer-20004-s2

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.02 |
| 2 | 0.00 | 0.02 | 0.02 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 1.00 | 0.96 | 1.00 |
| 2 | 1.00 | 0.92 | 1.00 |
| 3 | 1.00 | 1.00 | 1.00 |
| 4 | 1.00 | 1.00 | 1.00 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.02 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.02 | 0.00 |
| 3 | 0.08 | 0.02 |
| 4 | 0.62 | 0.02 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem1-v3 llama-20004-s3

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.02 | 0.02 |
| 3 | 0.00 | 0.02 | 0.02 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 0.92 | 0.92 | 0.92 |
| 2 | 0.92 | 0.92 | 0.92 |
| 3 | 0.92 | 0.92 | 0.92 |
| 4 | 0.92 | 0.92 | 0.92 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.02 | 0.02 |
| 2 | 0.33 | 0.02 |
| 3 | 0.83 | 0.00 |
| 4 | 0.87 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem1-v3 transformer-20004-s3

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.03 | 0.00 |
| 2 | 0.00 | 0.00 | 0.02 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 0.96 | 0.88 | 0.96 |
| 2 | 0.96 | 0.96 | 0.96 |
| 3 | 0.96 | 0.96 | 0.96 |
| 4 | 0.96 | 0.96 | 0.96 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.02 | 0.00 |
| 3 | 0.08 | 0.00 |
| 4 | 0.62 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem2-v3 llama-20004-s1

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.05 | 0.03 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 1.00 | 1.00 | 1.00 |
| 2 | 1.00 | 1.00 | 1.00 |
| 3 | 1.00 | 1.00 | 1.00 |
| 4 | 1.00 | 1.00 | 1.00 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.07 | 0.02 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.07 | 0.00 |
| 3 | 0.75 | 0.00 |
| 4 | 0.92 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem2-v3 transformer-20004-s1

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 0.96 | 1.00 | 0.96 |
| 2 | 0.96 | 1.00 | 0.96 |
| 3 | 0.96 | 0.96 | 0.96 |
| 4 | 0.96 | 0.96 | 0.96 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.05 | 0.00 |
| 4 | 0.72 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem2-v3 llama-20004-s2

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 0.96 | 0.96 | 0.96 |
| 2 | 0.96 | 0.96 | 0.96 |
| 3 | 0.96 | 0.96 | 0.96 |
| 4 | 0.96 | 0.96 | 0.96 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.13 | 0.00 |
| 3 | 0.70 | 0.00 |
| 4 | 0.83 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem2-v3 transformer-20004-s2

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.02 | 0.00 | 0.00 |
| 2 | 0.02 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 0.92 | 0.92 | 0.92 |
| 2 | 0.92 | 0.96 | 0.92 |
| 3 | 0.92 | 0.96 | 0.92 |
| 4 | 0.92 | 0.92 | 0.92 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.02 | 0.00 |
| 2 | 0.02 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.07 | 0.00 |
| 4 | 0.63 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem2-v3 llama-20004-s3

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 0.96 | 0.96 | 0.96 |
| 2 | 0.96 | 0.96 | 0.96 |
| 3 | 0.96 | 0.96 | 0.96 |
| 4 | 0.96 | 0.96 | 0.96 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.12 | 0.00 |
| 3 | 0.72 | 0.02 |
| 4 | 0.72 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem2-v3 transformer-20004-s3

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.02 | 0.02 |
| 2 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.02 | 0.02 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 0.96 | 0.92 | 0.96 |
| 2 | 0.96 | 0.92 | 0.96 |
| 3 | 0.96 | 0.96 | 0.96 |
| 4 | 0.96 | 0.96 | 0.96 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.02 | 0.00 |
| 4 | 0.65 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem3-v3 llama-20004-s1

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.05 | 0.05 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 1.00 | 1.00 | 1.00 |
| 2 | 1.00 | 1.00 | 1.00 |
| 3 | 1.00 | 1.00 | 1.00 |
| 4 | 1.00 | 1.00 | 1.00 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.07 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.20 | 0.00 |
| 3 | 0.82 | 0.00 |
| 4 | 0.77 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem3-v3 transformer-20004-s1

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 1.00 | 1.00 | 1.00 |
| 2 | 1.00 | 1.00 | 1.00 |
| 3 | 1.00 | 1.00 | 1.00 |
| 4 | 1.00 | 1.00 | 1.00 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.05 | 0.00 |
| 4 | 0.43 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem3-v3 llama-20004-s2

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 1.00 | 1.00 | 1.00 |
| 2 | 1.00 | 1.00 | 1.00 |
| 3 | 1.00 | 1.00 | 1.00 |
| 4 | 1.00 | 1.00 | 1.00 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.02 | 0.00 |
| 2 | 0.18 | 0.00 |
| 3 | 0.85 | 0.00 |
| 4 | 0.87 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem3-v3 transformer-20004-s2

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 1.00 | 1.00 | 1.00 |
| 2 | 1.00 | 0.96 | 1.00 |
| 3 | 1.00 | 1.00 | 1.00 |
| 4 | 1.00 | 1.00 | 1.00 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.05 | 0.00 |
| 4 | 0.57 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem3-v3 llama-20004-s3

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 1.00 | 1.00 | 1.00 |
| 2 | 1.00 | 1.00 | 1.00 |
| 3 | 1.00 | 1.00 | 1.00 |
| 4 | 1.00 | 1.00 | 1.00 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.02 | 0.00 |
| 2 | 0.18 | 0.00 |
| 3 | 0.73 | 0.00 |
| 4 | 0.65 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

## data-sem3-v3 transformer-20004-s3

**1. Patch only the feed-forward output at the country's position** (share where the donor's capital wins)

| block | chosen-on pairs | judged pairs | random, matched (judged) |
|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 |

Chosen block: 1.

**2. Remove it** (mean over the 24 prompts): accuracy on the recipient's own capital

| block | unablated | country position ablated | control: position 2 (`capital`) ablated |
|---:|---:|---:|---:|
| 1 | 1.00 | 1.00 | 1.00 |
| 2 | 1.00 | 1.00 | 1.00 |
| 3 | 1.00 | 1.00 | 1.00 |
| 4 | 1.00 | 1.00 | 1.00 |

**3. Restore it**: the recipient's country swapped for another; only the feed-forward output at the country position restored from the clean run (judged pairs). Share where the clean answer returns

| block | restored | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.02 |
| 3 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 |

**5. Follow-up (not in the plan): the feed-forward output at the last position** patched from the donor (judged pairs). Share where the donor's capital wins

| block | patched | random, matched |
|---:|---:|---:|
| 1 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 |
| 4 | 0.58 | 0.00 |

**4. Reuse across queries (version 3)**: the feed-forward output at P's position (position 1) patched from Q; read under both queries. 44 people admitted.

| block | lives in → Q's home | was born in → Q's birth city | both at once | random, matched: both |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| 3 | 0.00 | 0.00 | 0.00 | 0.00 |
| 4 | 0.00 | 0.00 | 0.00 | 0.00 |

