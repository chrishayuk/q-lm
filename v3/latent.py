"""Q-LM v3, latent routing conditions: the node's kind is never stated.

From train.txt only (v3.1 learns the knowledge):
1. LINKS and ATTRIBUTES. A learned relation is a link if its objects are
   subjects of other facts (entity to entity), and an attribute otherwise
   (entity to a value, here "X has a bell .").
2. LABELS FROM COMPUTATION. For each relation Q with composed pairs
   (s, o), every walk from s over links (other than Q), of 1 to MAX_WALK
   steps, that ends at o is enumerated. A walk that gives one node two
   different actions is dropped. The shortest remaining walk, if it is the
   only one of its length, labels each node on it with the action it needed (the link it followed) and o
   with STOP. Nodes are grouped by the computation they require, not by
   their contexts.
3. CONDITION. A Bernoulli naive Bayes over each node's attribute values
   predicts its action (counts with add-one smoothing; no gradient). It is
   the routing and stopping policy for any node, labelled or not.

Accepted if right on at least ACCEPT of a held-back tenth of Q's subjects.

Control, DISTRIBUTIONAL: the nodes clustered by their attribute values
alone (k-means, k = 6, the true number of kinds, supplied), each cluster
given the majority action of its labelled nodes.

world.json is read only to score.

    python3 -I v3/latent.py WORLD_DIR [WORLD_DIR ...]
"""
import itertools, json, math, random, sys, time
from collections import Counter, defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from runtime import STOP, Runtime
from learn import learn
from program import ACCEPT, wording

MAX_WALK = 5
CAP = 32
LABELS = __import__("os").environ.get("LABELS", "shortest")  # "shortest" (first version) or "em"
EM_ROUNDS = 10


def top(d):
    return max(d, key=d.get) if d else None


def main(d):
    world = json.load(open(f"{d}/world.json"))
    sentences = open(f"{d}/train.txt").read().splitlines()
    vocab = [w for w in open(f"{d}/vocab.txt").read().split() if w != "END"]
    tests = [l.rstrip("\n").split("\t") for l in open(f"{d}/tests.tsv")]
    t0 = time.time()
    m = learn(sentences)
    k = m["knowledge"]
    rels = sorted(set(m["frames"].values()))
    subjects = {s for s, _ in k}
    objs = defaultdict(set)
    pairs = defaultdict(list)
    for (s, g), os_ in k.items():
        objs[g] |= set(os_)
        pairs[g].append((s, top(os_)))
    links = [g for g in rels if len(objs[g] & subjects) > 0.5 * len(objs[g])]
    attrs = [g for g in rels if g not in links]
    feats = lambda e: {(a, v) for a in attrs for v in k.get((e, a), {})}
    allf = sorted({f for e in subjects for f in feats(e)})
    out = [f"{d} ({world['task']}, {world['regime']}): links " + ", ".join(wording(m, g) for g in links)
           + "; attributes " + (", ".join(wording(m, g) for g in attrs) or "none")]
    two = [(f, g) for f, g in m["frames"].items() if f[-2:] == ("_", ".") and f.count("_") == 2]

    def read_prompt(words):  # prompts are read only through the learned frames
        for f, g in two:
            body = f[:-2]
            if len(body) == len(words) and all(a == b or a == "_" for a, b in zip(body, words)):
                return words[body.index("_")], g
        return None, None
    tables = {}
    for q in links:
        subs = sorted({s for s, _ in pairs[q]})
        sel = set(subs[::10])
        steps = [g for g in links if g != q]
        labels, unique, ambiguous, walk_len, candidates = defaultdict(Counter), 0, 0, {}, []
        for s, o in pairs[q]:
            if s in sel:
                continue
            found = []
            for n in range(1, MAX_WALK + 1):
                for acts in itertools.product(steps, repeat=n):
                    e, path, ok = s, [], True
                    for a in acts:
                        nxt = top(k.get((e, a), {}))
                        if nxt is None:
                            ok = False
                            break
                        path.append((e, a))
                        e = nxt
                    if ok and e == o:
                        path.append((o, STOP))
                        given = {}
                        if all(given.setdefault(x, a) == a for x, a in path):
                            found.append(path)
            candidates.append((s, found))
            shortest = [f for f in found if found and len(f) == min(map(len, found))]
            if len(shortest) == 1:  # the shortest consistent walk, if it is the only one of its length
                unique += 1
                walk_len[s] = {len(shortest[0]) - 1: 1.0}
                for x, a in shortest[0]:
                    labels[x][a] += 1
            elif shortest:
                ambiguous += 1
        if not labels:
            continue

        def fit(weighted):
            """weighted: [(node, action, weight)] -> naive Bayes counts."""
            n_a, n_af = Counter(), defaultdict(Counter)
            for x, a, w in weighted:
                n_a[a] += w
                for f in feats(x):
                    n_af[a][f] += w
            return n_a, n_af

        def make_post(n_a, n_af):
            acts = sorted(n_a, key=str)
            n = sum(n_a.values())

            def nb_post(e):
                """The posterior over actions for entity e (log-space, normalised)."""
                fe = feats(e)
                sc = {}
                for a in acts:
                    x = math.log(n_a[a] / n)
                    for f in allf:
                        p = (n_af[a][f] + 1) / (n_a[a] + 2)
                        x += math.log(p if f in fe else 1 - p)
                    sc[a] = x
                mx = max(sc.values())
                z = sum(math.exp(v - mx) for v in sc.values())
                return {a: math.exp(v - mx) / z for a, v in sc.items()}
            return nb_post

        if LABELS == "em":
            # EM over every consistent walk of every example: equal weights first, then each walk
            # weighted by the product of its actions' posteriors (its final STOP included).
            cands = [(s_, ws) for s_, ws in candidates if ws]
            weights = [[1 / len(ws)] * len(ws) for _, ws in cands]
            for _ in range(EM_ROUNDS):
                nb_post = make_post(*fit([(x, a, w) for (_, ws), wt in zip(cands, weights) for path, w in zip(ws, wt) for x, a in path]))
                cache = {}
                pp = lambda x: cache.setdefault(x, nb_post(x))
                weights = []
                for _, ws in cands:
                    sc = [math.prod(pp(x).get(a, 1e-12) for x, a in path) for path in ws]
                    z = sum(sc)
                    weights.append([v / z for v in sc])
            labels = defaultdict(Counter)
            walk_len = {}
            for (s_, ws), wt in zip(cands, weights):
                walk_len[s_] = defaultdict(float)
                for path, w in zip(ws, wt):
                    walk_len[s_][len(path) - 1] += w
                    for x, a in path:
                        labels[x][a] += w
            unique = sum(max(wt) > 0.99 for wt in weights)
            ambiguous = len(cands) - unique
            nb_post = make_post(*fit([(x, a, w) for (_, ws), wt in zip(cands, weights) for path, w in zip(ws, wt) for x, a in path]))
        node_label = {x: c.most_common(1)[0][0] for x, c in labels.items()}
        if LABELS != "em":
            nb_post = make_post(*fit([(x, a, 1.0) for x, a in node_label.items()]))

        def nb(e):
            return top(nb_post(e))
        policy = {e: nb(e) for e in subjects}
        kq = {key: v for key, v in k.items() if key[1] != q}
        rt = Runtime(kq)

        def run_policy(start, pol, passes):
            return rt.run(start, lambda e, i: pol.get(e, STOP), passes)[0]
        chk = [(s, o) for s, o in pairs[q] if s in sel]
        sel_acc = sum(top(run_policy(s, policy, CAP)) == o for s, o in chk) / max(len(chk), 1)
        line = (f"  {wording(m, q)}: {'POLICY' if sel_acc >= ACCEPT else 'no policy'}; {unique} training examples with one "
                f"consistent walk, {ambiguous} with several; {len(node_label)} nodes labelled by computation; held-back tenth {sel_acc:.3f}")
        out.append(line)
        tables[q] = (sel_acc, policy, node_label, run_policy, line, nb_post, kq, walk_len)
    if not tables:
        print("\n".join(out)); return None
    # The relation best explained by a policy is reported in full, accepted or not.
    q = max(tables, key=lambda g: tables[g][0])
    sel_acc, policy, node_label, run_policy, _, nb_post, kq, walk_len = tables[q]
    ctx = {"world": world, "m": m, "q": q, "kq": kq, "nb_post": nb_post, "read_prompt": read_prompt, "tests": tests,
           "vocab": vocab, "subjects": subjects, "pairs": pairs[q], "node_label": node_label, "feats": feats, "accepted": sel_acc >= ACCEPT,
           "walk_len": walk_len, "attrs": attrs}
    out.append(f"  reported in full: {wording(m, q)} ({'ACCEPTED' if sel_acc >= ACCEPT else 'NOT accepted'})")
    if True:
        # How the computation-formed groups relate to the hidden kinds (scoring only).
        if "kind" in world:
            rule = {kd: "STOP" for kd in world["terminal"]} | world["rule"]
            name = lambda a: "STOP" if a is STOP else wording(m, a).split(" / ")[0][2:-4]
            right = sum(name(policy[v]) == rule[world["kind"][v]] for v in world["kind"] if v in policy)
            grouped = defaultdict(Counter)
            for v in world["kind"]:
                grouped[name(policy[v])][world["kind"][v]] += 1
            out.append(f"    every node's predicted action against its hidden kind's: {right} of {len(world['kind'])} ({right / len(world['kind']):.3f})")
            out.append("    groups formed by computation: " + "; ".join(f"{a} ← " + ", ".join(f"{kd} {c}" for kd, c in g.most_common()) for a, g in sorted(g_ for g_ in grouped.items())))
        # Control: distributional clusters (k-means on attribute values), majority action per cluster.
        rng = random.Random(0)
        nodes = sorted(subjects)
        X = {e: [1.0 if f in feats(e) else 0.0 for f in allf] for e in nodes}
        best_km = None
        for _ in range(10):  # restarts; the lowest within-cluster sum of squares is kept
            cent = [X[e][:] for e in rng.sample(nodes, 6)]
            for _ in range(30):
                assign = {e: min(range(6), key=lambda j: sum((a - b) ** 2 for a, b in zip(X[e], cent[j]))) for e in nodes}
                for j in range(6):
                    mem = [X[e] for e in nodes if assign[e] == j]
                    if mem:
                        cent[j] = [sum(c) / len(mem) for c in zip(*mem)]
            sse = sum(sum((a - b) ** 2 for a, b in zip(X[e], cent[assign[e]])) for e in nodes)
            if best_km is None or sse < best_km[0]:
                best_km = (sse, assign)
        assign = best_km[1]
        maj = {j: Counter(node_label[e] for e in nodes if assign[e] == j and e in node_label).most_common(1) for j in range(6)}
        dpolicy = {e: (maj[assign[e]][0][0] if maj[assign[e]] else STOP) for e in nodes}
        policies = [("computation-formed condition", policy), ("CONTROL distributional clusters (k-means, k = 6, 10 restarts)", dpolicy)]
        if "signatures" in world:  # CEILING, scoring only: Bayes-optimal kind from the true signatures and noise rates
            from worlds import PROPS
            P_SIG, P_NOISE = world["noise"]
            rule = {kd: "STOP" for kd in world["terminal"]} | world["rule"]
            act_of = {("STOP" if a is STOP else wording(m, a).split(" / ")[0][2:-4]): a for a in set(node_label.values())}
            prior = Counter(world["kind"].values())

            def bayes_post(e):
                """Exact posterior over actions: kinds summed by action, with the generator's
                rule that a node showing nothing is given one random signature property."""
                ps = {f[1] for f in feats(e)}
                post = defaultdict(float)
                for kd, sg in world["signatures"].items():
                    pr = lambda p: P_SIG if p in sg else P_NOISE
                    lik = math.prod(pr(p) if p in ps else 1 - pr(p) for p in PROPS)
                    if len(ps) == 1 and next(iter(ps)) in sg:
                        lik += math.prod(1 - pr(p) for p in PROPS) / len(sg)
                    post[act_of.get(rule[kd], STOP)] += prior[kd] * lik
                z = sum(post.values())
                return {a: v / z for a, v in post.items()}
            ctx["bayes_post"] = bayes_post
            policies.append(("REFERENCE Bayes posterior over actions (true signatures; scoring only)", {e: top(bayes_post(e)) for e in nodes}))
        for label, pol in policies:
            rows, worst = [], 0.0
            for passes in (1, 2, 3, 4, 8, CAP):
                by = defaultdict(lambda: [0, 0])
                for task, kind, prompt, ans, depth in tests:
                    start, g = read_prompt(prompt.split())
                    p = Runtime.project(run_policy(start, pol, passes) if g == q else {}, vocab)
                    worst = max(worst, abs(sum(p.values()) - 1))
                    by[f"{kind} d{depth}"][0] += top(p) == ans
                    by[f"{kind} d{depth}"][1] += 1
                rows.append((passes, {kk: v[0] / v[1] for kk, v in sorted(by.items())}))
            out.append(f"  held-out tests, {label} (gate worst |sum - 1| {worst:.1e})")
            out.append("    passes | " + " | ".join(rows[0][1]))
            for passes, acc in rows:
                out.append(f"    {passes:>6} | " + " | ".join(f"{acc[kk]:.3f}" for kk in acc))
    out.insert(1, f"  learned in {time.time() - t0:.1f}s")
    print("\n".join(out))
    return ctx


if __name__ == "__main__":
    for d in sys.argv[1:]:
        main(d)
