"""Reproduce data-ts's preprocessing for TinyStories stories: lowercase,
split into sentences at . ! ? followed by whitespace, punctuation as tokens, 2 to 40 tokens,
words outside data-ts/vocab.txt as <unk>.

    python3 -I tools/ts_prep.py PARQUET_DIR SPLIT FIRST LAST OUT    (stories FIRST..LAST-1)
Writes OUT (sentences) and OUT.story (story index per sentence).
"""
import glob, re, sys
import pyarrow.parquet as pq

pdir, split, first, last, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
vocab = set(open("data-ts/vocab.txt").read().split())
texts = []
for f in sorted(glob.glob(f"{pdir}/{split}-*.parquet")):
    texts += pq.read_table(f, columns=["text"]).column("text").to_pylist()
    if len(texts) >= last:
        break
TOK = re.compile(r"[a-z]+|[0-9]+|[^\sa-z0-9]")


def sentences(t):
    # a sentence ends at . ! or ? followed by whitespace (so `clean!" Kitty` does not split)
    for piece in re.split(r"(?<=[.!?])\s+", t.lower()):
        toks = TOK.findall(piece)
        if toks:
            yield toks


lines, ids = [], []
for k in range(first, last):
    for s in sentences(texts[k] or ""):
        if 2 <= len(s) <= 40:
            lines.append(" ".join(w if w in vocab else "<unk>" for w in s))
            ids.append(k)
open(out, "w").write("\n".join(lines) + "\n")
open(out + ".story", "w").write("\n".join(map(str, ids)) + "\n")
print(f"{out}: {len(lines)} sentences from stories {first} to {last - 1}")
