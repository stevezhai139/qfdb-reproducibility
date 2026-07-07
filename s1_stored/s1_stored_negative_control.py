#!/usr/bin/env python3
"""
QFDB S1 stored-data negative control (pre-registered: see PREREGISTRATION.md).

Prediction: stored two-store correlations are common-cause => S <= 2 on every
benchmark pair, even under adversarial setting search; the constructed Bell
state reaches 2*sqrt(2) ~ 2.828 in the same pipeline (positive control).

Usage:  python3 s1_stored_negative_control.py <path-to-ditto-Structured-dir> [out_dir]
Data :  git clone --depth 1 --filter=blob:none --sparse https://github.com/megagonlabs/ditto
        cd ditto && git sparse-checkout set data/er_magellan/Structured
"""
import sys, os, re, json, hashlib
import numpy as np

RNG_SEED = 42
N_BOOT = 10_000
STOP = set("with the and for from this that have has are was were will your you our new all can "
           "per pack set of in on to a an by or & - --".split())

# ---------------- ditto format ----------------
def parse_record(chunk):
    """'COL f VAL v COL f2 VAL v2 ...' -> dict f->v (strings, stripped)."""
    parts = re.split(r"COL\s+", chunk.strip())
    rec = {}
    for p in parts:
        if not p.strip():
            continue
        m = re.match(r"(\S+)\s+VAL\s*(.*)", p.strip(), flags=re.S)
        if m:
            rec[m.group(1).strip()] = m.group(2).strip()
    return rec

def load_split(path):
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")
            if len(cols) != 3:
                continue
            l, r, y = cols
            if y.strip() == "1":
                items.append((parse_record(l), parse_record(r)))
    return items

def load_dataset(root, name):
    d = os.path.join(root, name)
    train = load_split(os.path.join(d, "train.txt"))
    heldout = load_split(os.path.join(d, "valid.txt")) + load_split(os.path.join(d, "test.txt"))
    return train, heldout

# ---------------- rule library (per side, from own-side TRAIN only) ----------------
def text_field(recs):
    """Main text field = first key of the first record (ditto preserves order)."""
    for r in recs:
        if r:
            return next(iter(r.keys()))
    return None

def numeric_fields(recs):
    out = {}
    for r in recs[:200]:
        for k, v in r.items():
            try:
                if v != "":
                    float(v)
                    out[k] = out.get(k, 0) + 1
            except ValueError:
                pass
    return [k for k, c in out.items() if c >= 10]

def tokens_top(recs, field, k=8):
    freq = {}
    for r in recs:
        for t in re.findall(r"[a-zA-Z]{4,}", r.get(field, "").lower()):
            if t not in STOP:
                freq[t] = freq.get(t, 0) + 1
    return [t for t, _ in sorted(freq.items(), key=lambda x: -x[1])[:k]]

def build_rules(train_side):
    """Return list of (name, fn(record)->+/-1). Missing value -> -1 (frozen)."""
    rules = []
    tf = text_field(train_side)
    for nf in numeric_fields(train_side):
        vals = []
        for r in train_side:
            try:
                vals.append(float(r.get(nf, "")))
            except ValueError:
                pass
        if len(vals) < 10:
            continue
        med = float(np.median(vals))
        def mk(nf=nf, med=med):
            def fn(r):
                try:
                    return 1 if float(r.get(nf, "")) > med else -1
                except ValueError:
                    return -1
            return fn
        rules.append((f"num:{nf}>{med:.4g}", mk()))
    if tf:
        lens = [len(r.get(tf, "")) for r in train_side]
        medl = float(np.median(lens))
        rules.append((f"len:{tf}>{medl:.0f}",
                      lambda r, tf=tf, medl=medl: 1 if len(r.get(tf, "")) > medl else -1))
        for t in tokens_top(train_side, tf):
            rules.append((f"tok:{t}",
                          lambda r, tf=tf, t=t: 1 if t in r.get(tf, "").lower() else -1))
    return rules

# ---------------- CHSH machinery (shared with self-tests) ----------------
def chsh_S(a1, a2, b1, b2):
    """responses: +/-1 arrays over the SAME items."""
    E = lambda x, y: float(np.mean(x * y))
    return E(a1, b1) + E(a1, b2) + E(a2, b1) - E(a2, b2)

def boot_ci(a1, a2, b1, b2, n=N_BOOT, seed=RNG_SEED):
    rng = np.random.default_rng(seed)
    N = len(a1)
    idx = rng.integers(0, N, size=(n, N))
    Ss = (np.mean(a1[idx] * b1[idx], axis=1) + np.mean(a1[idx] * b2[idx], axis=1)
          + np.mean(a2[idx] * b1[idx], axis=1) - np.mean(a2[idx] * b2[idx], axis=1))
    return float(np.percentile(Ss, 2.5)), float(np.percentile(Ss, 97.5))

def responses(rule, side_recs):
    return np.array([rule(r) for r in side_recs], dtype=float)

# ---------------- self-tests (positive controls; must pass first) ----------------
def self_tests():
    # 1) Bell state, CHSH-optimal settings -> 2.828
    k0 = np.array([1, 0], complex); k1 = np.array([0, 1], complex)
    bell = (np.kron(k0, k0) + np.kron(k1, k1)) / np.sqrt(2)
    Z = np.array([[1, 0], [0, -1]], complex); X = np.array([[0, 1], [1, 0]], complex)
    A, Ap = Z, X; B = (Z + X) / np.sqrt(2); Bp = (Z - X) / np.sqrt(2)
    Ee = lambda M, N: float((bell.conj() @ np.kron(M, N) @ bell).real)
    S_bell = Ee(A, B) + Ee(A, Bp) + Ee(Ap, B) - Ee(Ap, Bp)
    assert abs(S_bell - 2 * np.sqrt(2)) < 1e-9, S_bell
    # 2) engineered classical items attain exactly 2 (bound sharp, not exceeded)
    rng = np.random.default_rng(0)
    lam = rng.integers(0, 2, 4000) * 2 - 1          # shared latent per item
    a1 = lam.astype(float); a2 = lam.astype(float)  # A = A' = lambda
    b1 = lam.astype(float); b2 = -lam.astype(float) # B = lambda, B' = -lambda
    S_cls = chsh_S(a1, a2, b1, b2)
    assert abs(S_cls - 2.0) < 1e-12, S_cls
    # 3) product state -> S <= 2 (independent responses -> S ~ 0)
    p1 = (rng.integers(0, 2, 4000) * 2 - 1).astype(float)
    p2 = (rng.integers(0, 2, 4000) * 2 - 1).astype(float)
    S_prod = chsh_S(p1, p1, p2, p2)
    assert abs(S_prod) <= 2.0
    print(f"[self-test] Bell 2.8284 OK | engineered classical S=2.000 attained OK | product |S|={abs(S_prod):.3f}<=2 OK")
    return S_bell

# ---------------- analyses A/B/C per dataset ----------------
def analyse(root, name):
    train, held = load_dataset(root, name)
    trL = [l for l, _ in train]; trR = [r for _, r in train]
    hL = [l for l, _ in held];  hR = [r for _, r in held]
    rulesL = build_rules(trL); rulesR = build_rules(trR)
    if len(rulesL) < 2 or len(rulesR) < 2 or len(held) < 30:
        return None
    RL = {n: responses(f, hL) for n, f in rulesL}
    RR = {n: responses(f, hR) for n, f in rulesR}
    RLt = {n: responses(f, trL) for n, f in rulesL}
    RRt = {n: responses(f, trR) for n, f in rulesR}
    namesL = list(RL); namesR = list(RR)

    # A. natural: first numeric rule (fallback len) + top-1 token rule, mirrored
    def pick_natural(names):
        num = next((n for n in names if n.startswith("num:")), None) or \
              next((n for n in names if n.startswith("len:")), None)
        tok = next((n for n in names if n.startswith("tok:")), None)
        return num, tok
    A_, Ap_ = pick_natural(namesL); B_, Bp_ = pick_natural(namesR)
    nat = None
    if all(x is not None for x in (A_, Ap_, B_, Bp_)):
        S = chsh_S(RL[A_], RL[Ap_], RR[B_], RR[Bp_])
        lo, hi = boot_ci(RL[A_], RL[Ap_], RR[B_], RR[Bp_])
        nat = dict(S=S, ci=[lo, hi], settings=[A_, Ap_, B_, Bp_])

    # B. adversarial: maximize |S| on TRAIN, evaluate argmax on held-out
    best = (0.0, None)
    for i, a1 in enumerate(namesL):
        for a2 in namesL:
            if a2 == a1:
                continue
            for b1 in namesR:
                for b2 in namesR:
                    if b2 == b1:
                        continue
                    S = chsh_S(RLt[a1], RLt[a2], RRt[b1], RRt[b2])
                    if abs(S) > abs(best[0]):
                        best = (S, (a1, a2, b1, b2))
    (a1, a2, b1, b2) = best[1]
    S_tr = best[0]
    S_ev = chsh_S(RL[a1], RL[a2], RR[b1], RR[b2])
    lo, hi = boot_ci(RL[a1], RL[a2], RR[b1], RR[b2])

    # C. between-subjects dry run: 4 disjoint groups, one setting pair each
    rng = np.random.default_rng(RNG_SEED)
    perm = rng.permutation(len(hL)); grp = np.array_split(perm, 4)
    pairs = [(a1, b1), (a1, b2), (a2, b1), (a2, b2)]
    Es, margL, margR = [], {}, {}
    for g, (an, bn) in zip(grp, pairs):
        x, y = RL[an][g], RR[bn][g]
        Es.append(float(np.mean(x * y)))
        margL.setdefault(an, {})[bn] = float(np.mean(x))
        margR.setdefault(bn, {})[an] = float(np.mean(y))
    S_bs = Es[0] + Es[1] + Es[2] - Es[3]
    ns = []
    for an, d in margL.items():
        if len(d) == 2:
            ns.append(abs(list(d.values())[0] - list(d.values())[1]))
    for bn, d in margR.items():
        if len(d) == 2:
            ns.append(abs(list(d.values())[0] - list(d.values())[1]))
    return dict(dataset=name, n_train=len(train), n_heldout=len(held),
                natural=nat,
                adversarial=dict(S_train=S_tr, S_heldout=S_ev, ci=[lo, hi],
                                 settings=[a1, a2, b1, b2]),
                between_subjects=dict(S=S_bs, max_nosignaling_delta=(max(ns) if ns else None)))

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__) or ".", "results")
    os.makedirs(out_dir, exist_ok=True)
    prereg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PREREGISTRATION.md")
    if os.path.exists(prereg):
        h = hashlib.sha256(open(prereg, "rb").read()).hexdigest()[:16]
        print(f"[prereg] PREREGISTRATION.md sha256[:16] = {h}")
    S_bell = self_tests()
    datasets = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    results, violations = [], 0
    for name in datasets:
        r = analyse(root, name)
        if r is None:
            print(f"{name:<22} skipped (too small / too few rules)")
            continue
        results.append(r)
        adv = r["adversarial"]; lo, hi = adv["ci"]
        viol = lo > 2.0
        violations += int(viol)
        natS = f"{r['natural']['S']:+.3f}" if r["natural"] else "  n/a"
        print(f"{name:<22} n={r['n_heldout']:<5} S_nat={natS}  "
              f"S_adv(train)={adv['S_train']:+.3f}  S_adv(heldout)={adv['S_heldout']:+.3f} "
              f"CI[{lo:+.3f},{hi:+.3f}]  NSdelta={r['between_subjects']['max_nosignaling_delta']:.3f}  "
              f"{'** CI>2 **' if viol else '<=2 OK'}")
    summary = dict(prediction="S <= 2 on all stored-data pairs",
                   positive_control_bell=S_bell, n_datasets=len(results),
                   n_violations_CIabove2=violations, results=results)
    out = os.path.join(out_dir, "s1_stored_results.json")
    json.dump(summary, open(out, "w"), indent=1)
    print(f"\n[verdict] {len(results)} datasets, CI-above-2 violations: {violations} "
          f"(prediction {'VERIFIED' if violations == 0 else 'FALSIFIED - investigate'})  |  Bell control: {S_bell:.4f}")
    print(f"[out] {out}")

if __name__ == "__main__":
    main()
