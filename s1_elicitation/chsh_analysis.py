#!/usr/bin/env python3
"""
QFDB signature S1 (Bell/CHSH) — analysis you run yourself.

WHAT IT DOES: takes joint yes/no judgments from a 2x2 "measurement setting"
elicitation and computes the CHSH number S. Classical bound |S| <= 2; quantum
(Tsirelson) up to 2*sqrt(2) ~ 2.828. S > 2 (significantly) = the correlations
admit NO single classical joint distribution = non-classical structure.

USE IT THREE WAYS:
  python3 chsh_analysis.py --demo classical   # synthetic data that should NOT violate
  python3 chsh_analysis.py --demo quantum     # synthetic data that SHOULD violate
  python3 chsh_analysis.py responses.csv      # YOUR real data

INPUT CSV (4 rows, one per setting pair). Coding: first option of each side = +1.
  condition,n_pp,n_pm,n_mp,n_mm
  AB,40,8,7,45
  ABp,...
  ApB,...
  ApBp,...
"""
import sys, csv, numpy as np

CONDS = ["AB", "ABp", "ApB", "ApBp"]   # A-B, A-B', A'-B, A'-B'

# ---- core computation (this is the whole method, in 4 lines) ----
def E_of(counts):
    # correlation for one condition: E = <outcomeA * outcomeB>
    # outcomes (A,B): pp=(+,+)->+1  pm=(+,-)->-1  mp=(-,+)->-1  mm=(-,-)->+1
    n = np.asarray(counts, float); N = n.sum()
    return (n[0] - n[1] - n[2] + n[3]) / N

def chsh(Es):
    # one term carries the minus sign (standard CHSH combination)
    return Es["AB"] + Es["ABp"] + Es["ApB"] - Es["ApBp"]

# ---- significance: bootstrap respondents within each condition ----
def bootstrap_ci(counts, B=4000, seed=0):
    rng = np.random.default_rng(seed)
    samp = {}
    for k, v in counts.items():
        prod = np.repeat([1, -1, -1, 1], np.asarray(v, int))   # per-respondent A*B product
        samp[k] = prod
    Ss = np.empty(B)
    for i in range(B):
        Es = {k: s[rng.integers(0, len(s), len(s))].mean() for k, s in samp.items()}
        Ss[i] = chsh(Es)
    return np.percentile(Ss, 2.5), np.percentile(Ss, 97.5)

# ---- synthetic data so you can watch the computation before collecting ----
def gen_quantum(n=200, seed=1):
    rng = np.random.default_rng(seed)
    Et = {"AB": 1/np.sqrt(2), "ABp": 1/np.sqrt(2), "ApB": 1/np.sqrt(2), "ApBp": -1/np.sqrt(2)}
    out = {}
    for k, E in Et.items():
        p = [(1+E)/4, (1-E)/4, (1-E)/4, (1+E)/4]   # zero marginals, correlation E
        out[k] = tuple(int(x) for x in rng.multinomial(n, p))
    return out

def gen_classical(n=200, seed=1, corr=0.92):
    # every respondent has DEFINITE values for all four settings (a local hidden
    # variable model) -> a valid joint distribution exists -> S <= 2 guaranteed.
    rng = np.random.default_rng(seed)
    out = {k: [0, 0, 0, 0] for k in CONDS}
    idx = {(1,1):0, (1,-1):1, (-1,1):2, (-1,-1):3}
    for _ in range(n):
        u = rng.choice([-1, 1])
        val = {s: (u if rng.random() < corr else -u) for s in ["a","ap","b","bp"]}
        for k,(x,y) in {"AB":("a","b"),"ABp":("a","bp"),"ApB":("ap","b"),"ApBp":("ap","bp")}.items():
            out[k][idx[(val[x], val[y])]] += 1
    return {k: tuple(v) for k, v in out.items()}

def load_csv(path):
    d = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            d[row["condition"].strip()] = (int(row["n_pp"]), int(row["n_pm"]), int(row["n_mp"]), int(row["n_mm"]))
    return d

def report(counts):
    Es = {k: E_of(counts[k]) for k in CONDS}
    for k in CONDS:
        print(f"  E({k:4s}) = {Es[k]:+.3f}   (from counts {counts[k]}, N={sum(counts[k])})")
    S = chsh(Es)
    lo, hi = bootstrap_ci(counts)
    print(f"\n  CHSH  S = {S:+.3f}   95% CI [{lo:+.3f}, {hi:+.3f}]")
    print(f"  classical bound = 2.000 ; Tsirelson = {2*np.sqrt(2):.3f}")
    if lo > 2:   print("  >>> VIOLATION: S significantly > 2  => NON-CLASSICAL structure")
    elif S > 2:  print("  >>> S > 2 but CI touches 2 — need more respondents")
    else:        print("  >>> no violation (S <= 2): consistent with a classical model")

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--demo":
        counts = gen_quantum() if sys.argv[2] == "quantum" else gen_classical()
        print(f"[synthetic {sys.argv[2]} data]")
    elif len(sys.argv) == 2:
        counts = load_csv(sys.argv[1]); print(f"[your data: {sys.argv[1]}]")
    else:
        print(__doc__); sys.exit(0)
    report(counts)
