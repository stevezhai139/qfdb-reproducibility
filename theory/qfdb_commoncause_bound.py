#!/usr/bin/env python3
"""
Layer-A formal backbone for #1/#5: ANY common-cause (shared-latent) model of two
schemas obeys the CHSH bound |S| <= 2. So embedding-based schema correlation
(= a shared-latent model) can never be genuine entanglement; only a non-common-cause
(quantum-like) source can exceed 2. Bell violation is therefore the sole discriminator.
Exact, classical simulation.
"""
import numpy as np, itertools
# A common-cause model: each unit has a hidden state lambda fixing definite outcomes for
# ALL four settings: a(A),a(A') for schema1 ; b(B),b(B') for schema2, each in {+1,-1}.
# A deterministic strategy = (aA,aAp,bB,bBp) in {+/-1}^4 ; any model = a distribution over these.
strat=list(itertools.product([1,-1],repeat=4))
def Sval(s):
    aA,aAp,bB,bBp=s
    return aA*bB + aA*bBp + aAp*bB - aAp*bBp   # CHSH combination
vals=np.array([Sval(s) for s in strat])

print("=== deterministic common-cause strategies (all 16) ===")
print("  S values:", sorted(set(vals.tolist())))
print(f"  max S = {vals.max()}   min S = {vals.min()}   => every deterministic LHV in [-2, 2]")

print("\n=== any MIXTURE (noisy / contextual shared-latent) is a convex combo => still bounded ===")
rng=np.random.default_rng(0); worst=0.0
for _ in range(200000):
    p=rng.random(16); p/=p.sum()
    worst=max(worst, abs(float(p@vals)))
print(f"  max |S| over 200k random common-cause mixtures = {worst:.4f}   (<= 2, always)")

print("\n=== proof (2 lines) ===")
print("  S = E[ a(A)(b(B)+b(B')) + a(A')(b(B)-b(B')) ];  b(B)+b(B') and b(B)-b(B') in {0,+/-2},")
print("  one is 0 -> bracket = +/-2 -> |S| <= E[2] = 2.   QED  (Bell/CHSH classical bound)")

print("\n=== contrast: a genuine entangled (non-common-cause) quantum state ===")
print(f"  reaches S = 2*sqrt(2) = {2*np.sqrt(2):.4f}  > 2   (no shared-latent model reproduces this)")
print("\nCONCLUSION: embedding/common-cause schema correlation is capped at 2;")
print("            S1 > 2 on real correspondences is the ONLY witness of genuine entanglement.")
