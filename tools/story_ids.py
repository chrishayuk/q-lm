"""Recover story boundaries for data-ts (the sentences themselves are unchanged).

data-ts was built from TinyStories stories split at . ! ?, lowercased, with
punctuation as tokens, keeping 2 to 40 tokens; story boundaries were not
kept. Each data sentence is aligned to the raw stories by its character
stream without whitespace, in order, and given the index of the story it
starts in. Writes FILE.story (one story index per line) next to each file.

    .venv-gpt2/bin/python -I tools/story_ids.py PARQUET_DIR data-ts train.txt:train dev.txt:validation
"""
import glob, sys
import pyarrow.parquet as pq

pdir, ddir = sys.argv[1], sys.argv[2]
for spec in sys.argv[3:]:
    fname, split = spec.split(":")
    files = sorted(glob.glob(f"{pdir}/{split}-*.parquet"))
    sents = [l.split() for l in open(f"{ddir}/{fname}").read().splitlines()]
    need = sum(len("".join(s)) for s in sents)
    # Concatenate stories (whitespace removed, lowercased) until there is enough text.
    stream, owner, n_chars = [], [], 0
    for f in files:
        for t in pq.read_table(f, columns=["text"]).column("text").to_pylist():
            c = "".join((t or "").lower().split())
            stream.append(c)
            owner.append(len(owner))
            n_chars += len(c)
            if n_chars > need * 1.5 + 10_000:
                break
        if n_chars > need * 1.5 + 10_000:
            break
    starts, pos = [], 0
    for c in stream:
        starts.append(pos)
        pos += len(c)
    text = "".join(stream)
    import bisect
    ids, ptr, misses, skipped = [], 0, 0, 0
    for s in sents:
        key = "".join(s)
        j = text.find(key, ptr, ptr + 20_000)
        if j < 0:
            misses += 1
            ids.append(ids[-1] if ids else 0)
            continue
        skipped += j - ptr
        ids.append(bisect.bisect_right(starts, j) - 1)
        ptr = j + len(key)
    open(f"{ddir}/{fname}.story", "w").write("\n".join(map(str, ids)) + "\n")
    print(f"{fname}: {len(sents)} sentences, {misses} not found, {len(set(ids))} stories, "
          f"{skipped} characters skipped between sentences (filtered sentences, whitespace-free)")
