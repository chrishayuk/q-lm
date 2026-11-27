"""Q-LM v3.2: static programs learned from composed examples
(docs/qlm-v3-plan.md, revision 1).

Everything the runtime executes is now learned from train.txt:
- the knowledge (v3.1: frames, entities, relations, bindings);
- the program for each relation, found here.

For each learned relation R, the candidates are the sequences of 1 to
MAX_LEN other learned relations. A candidate's accuracy is the fraction of
R's fitting pairs (s, o) for which executing it from s gives o. The best
candidate is the most accurate, then the shortest. A tenth of R's subjects
are kept back: the program is accepted if it is right on at least ACCEPT
of them. R is then "derived": a query for an entity with no stored binding
executes R's program.

world.json is read to score, and for task B only to name the tests. No
program, rule or stop condition is supplied.

    python3 -I v3/program.py WORLD_DIR [WORLD_DIR ...]
"""
import itertools, json, pickle, sys, time
from collections import defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from runtime import STOP, Runtime
from learn import frame, learn

MAX_LEN = 5
ACCEPT = 0.9


def run_prog(rt, s, prog):
    state, _ = rt.run(s, lambda e, i: prog[i] if i < len(prog) else STOP, len(prog))
    return state


def best_prog(rt, target, rels, pairs):
    """pairs: [(s, o)]. Returns (program, fit accuracy, select accuracy, candidates tried)."""
    subjects = sorted({s for s, _ in pairs})
    sel = set(subjects[::10])
    fit = [(s, o) for s, o in pairs if s not in sel]
    chk = [(s, o) for s, o in pairs if s in sel]
    others = [r for r in rels if r != target]
    best, tried = (None, -1.0), 0
    for n in range(1, MAX_LEN + 1):
        for prog in itertools.product(others, repeat=n):
            tried += 1
            acc = sum(max((st := run_prog(rt, s, prog)), key=st.get) == o for s, o in fit) / max(len(fit), 1)
            if acc > best[1]:  # strictly better: a shorter program wins a tie
                best = (prog, acc)
        if best[1] == 1.0:
            break  # nothing longer can be more accurate
    prog = best[0]
    sel_acc = sum(max((st := run_prog(rt, s, prog)), key=st.get) == o for s, o in chk) / max(len(chk), 1)
    return prog, best[1], sel_acc, tried


def accept(found):
    """found: relation -> program (a sequence of relations). A program is rejected if
    its definition reaches itself through other programs (a cycle), or if it uses a
    rejected program. Returns (accepted, rejected)."""
    def reach(g):
        seen, todo = set(), [r for r in found[g] if r in found]
        while todo:
            r = todo.pop()
            if r not in seen:
                seen.add(r)
                todo += [x for x in found[r] if x in found]
        return seen
    closure = {g: reach(g) for g in found}
    cyclic = {g for g in found if g in closure[g]}
    rejected = {g for g in found if g in cyclic or closure[g] & cyclic}
    return {g: p for g, p in found.items() if g not in rejected}, rejected


def wording(m, g):
    fs = sorted(f for f, h in m["frames"].items() if h == g)
    return " / ".join(" ".join(f) for f in fs)


def main(d):
    world = json.load(open(f"{d}/world.json"))
    sentences = open(f"{d}/train.txt").read().splitlines()
    vocab = [w for w in open(f"{d}/vocab.txt").read().split() if w != "END"]
    tests = [l.rstrip("\n").split("\t") for l in open(f"{d}/tests.tsv")]
    t0 = time.time()
    m = learn(sentences)
    rt = Runtime(m["knowledge"])
    rels = sorted(set(m["frames"].values()))
    pairs = defaultdict(list)
    for (s, g), objs in m["knowledge"].items():
        pairs[g].append((s, max(objs, key=objs.get)))
    found, lines = {}, []
    for g in rels:
        prog, fit, sel, tried = best_prog(rt, g, rels, pairs[g])
        if sel >= ACCEPT:
            found[g] = prog
        lines.append([g, prog, f"(length {len(prog)}; fit {fit:.3f}, held-back tenth {sel:.3f}; {tried} candidates)"])

    # Safeguard 1, cycles: rejected explicitly, with everything that depends on them.
    programs, cyclic = accept(found)

    def expand(g):
        """A derived relation's program in primitive relations. Passes count primitive reads."""
        out = []
        for r in programs[g]:
            out += expand(r) if r in programs else [r]
        return out

    # Safeguard 2, subroutines verified after expansion: the expanded primitive program, run over a
    # knowledge base with every derived relation's stored bindings deleted, must still reproduce all
    # of the relation's training pairs. This is also the compression test: the stored composed
    # answers are deleted and recomputed.
    derived = set(programs)
    lean = Runtime({k: v for k, v in rt.k.items() if k[1] not in derived})
    verified = {}
    for g in sorted(derived):
        prog = expand(g)
        ok = sum(max((st := run_prog(lean, s, prog)), key=st.get, default=None) == o for s, o in pairs[g])
        verified[g] = ok / len(pairs[g])
    programs = {g: p for g, p in programs.items() if verified[g] >= ACCEPT}
    for row in lines:
        g = row[0]
        tag = "DERIVED" if g in programs else ("rejected: in or using a cycle" if g in cyclic else
              (f"rejected: expanded program reproduces {verified[g]:.3f}" if g in verified else "stored"))
        exp = f"; expanded to {len(expand(g))} primitive steps, reproduces {verified[g]:.3f} of its training pairs with them deleted" if g in programs else ""
        row[:] = [f"    {wording(m, g)}: {tag}; best program " + " → ".join(wording(m, r).split(" / ")[0] for r in row[1]) + f" {row[2]}{exp}"]
    secs = time.time() - t0
    full = pickle.dumps((m, programs))
    m_lean = dict(m, knowledge=lean.k)
    print(f"{d} ({world['task']}, {world['regime']}): learned {len(rels)} relations and their programs in {secs:.1f}s; "
          f"whole model {len(full)} bytes serialised; {len(pickle.dumps((m_lean, programs)))} with the derived relations' stored answers deleted")
    print("\n".join(r[0] for r in lines))

    # Safeguard 3, oracle isolation: a prompt is read only through the learned frames. A prompt
    # matches a two-slot frame ending "_ ." when it equals the frame's other words with one token
    # in the first slot; that token is the start. No task-specific parsing.
    two = [(f, g) for f, g in m["frames"].items() if f[-2:] == ("_", ".") and f.count("_") == 2]

    def read_prompt(words):
        for f, g in two:
            body = f[:-2]
            if len(body) == len(words) and all(a == b or a == "_" for a, b in zip(body, words)):
                return words[body.index("_")], g
        return None, None

    # Safeguard 4, abstention against lost mass: an unseen query or a relation with no program is an
    # abstention (the projection spreads it); a read that finds nothing during execution is an
    # execution miss, and is counted, not hidden.
    def answer(prompt, passes, tally):
        start, g = read_prompt(prompt.split())
        if g is None:
            tally["abstain: query wording never seen"] += 1
            return {}
        if (start, g) in lean.k:
            tally["read directly"] += 1
            return lean.k[(start, g)]
        if g not in programs:
            tally["abstain: no stored answer and no program"] += 1
            return {}
        prog = expand(g)
        missed = []
        def choose(e, i):
            if i < len(prog) and (e, prog[i]) not in lean.k:
                missed.append(e)
            return prog[i] if i < len(prog) else STOP
        state, _ = lean.run(start, choose, passes)
        tally["executed, with a read that found nothing" if missed else "executed"] += 1
        return state

    worst, rows, tallies = 0.0, [], []
    for passes in (1, 2, 3, 4, 8):
        by, tally = defaultdict(lambda: [0, 0]), defaultdict(int)
        for task, kind, prompt, ans, depth in tests:
            p = Runtime.project(answer(prompt, passes, tally), vocab)
            worst = max(worst, abs(sum(p.values()) - 1))
            by[f"{kind} d{depth}"][0] += max(p, key=p.get) == ans
            by[f"{kind} d{depth}"][1] += 1
        rows.append((passes, {k: v[0] / v[1] for k, v in sorted(by.items())}))
        tallies.append(dict(tally))
    print(f"  held-out tests, over the knowledge with derived answers deleted (gate worst |sum - 1| {worst:.1e})")
    print("    passes | " + " | ".join(rows[0][1]))
    for (passes, acc), tally in zip(rows, tallies):
        print(f"    {passes:>6} | " + " | ".join(f"{acc[k]:.3f}" for k in acc) + "   [" + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())) + "]")


if __name__ == "__main__":
    for d in sys.argv[1:]:
        main(d)
