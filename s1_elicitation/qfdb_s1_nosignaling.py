#!/usr/bin/env python3
"""
QFDB S1 -- No-signaling / marginal-law check (companion to chsh_analysis.py).

WHY: a CLEAN Bell/CHSH test requires NO-SIGNALING -- the marginal distribution of
one schema's outcome must not depend on which setting the OTHER schema is measured
under. If it does, an S>2 is CONTEXTUALITY (still non-classical, but weaker) rather
than clean nonlocal entanglement. Reviewers will ask for this; we report it.

Four checks (party A = schema 1, settings A/A'; party B = schema 2, settings B/B'):
  (1) <A>  : AB  vs AB'   -- A's marginal must not depend on B's setting
  (2) <A'> : A'B vs A'B'
  (3) <B>  : AB  vs A'B   -- B's marginal must not depend on A's setting
  (4) <B'> : AB' vs A'B'
Each delta should be ~0; we give a bootstrap 95% CI and flag any that excludes 0.

USE:
  python3 qfdb_s1_nosignaling.py --demo quantum     # zero-marginal => should PASS
  python3 qfdb_s1_nosignaling.py --demo classical   # should PASS
  python3 qfdb_s1_nosignaling.py --demo signaling   # built to FAIL (checker sanity)
  python3 qfdb_s1_nosignaling.py responses.csv      # your real data
"""
import sys, numpy as np
import chsh_analysis as ch

# counts order (n_pp,n_pm,n_mp,n_mm) = (++,+-,-+,--) for (A,B). first option each side = +1.
def mA(c):                              # marginal mean of party A (=+1 in pp,pm)
    c=np.asarray(c,float); return (c[0]+c[1]-c[2]-c[3])/c.sum()
def mB(c):                              # marginal mean of party B (=+1 in pp,mp)
    c=np.asarray(c,float); return (c[0]-c[1]+c[2]-c[3])/c.sum()
def outA(c): c=np.asarray(c,int); return np.repeat([1,1,-1,-1], c)   # per-respondent A outcome
def outB(c): c=np.asarray(c,int); return np.repeat([1,-1,1,-1], c)   # per-respondent B outcome

def boot_diff(s1, s2, B=3000, seed=0):  # CI for mean(s1)-mean(s2), independent samples
    rng=np.random.default_rng(seed); d=np.empty(B)
    for i in range(B):
        d[i]=s1[rng.integers(0,len(s1),len(s1))].mean()-s2[rng.integers(0,len(s2),len(s2))].mean()
    return float(np.percentile(d,2.5)), float(np.percentile(d,97.5))

CHECKS=[("<A>  AB  vs AB' ","AB","ABp",outA,mA),
        ("<A'> A'B vs A'B'","ApB","ApBp",outA,mA),
        ("<B>  AB  vs A'B ","AB","ApB",outB,mB),
        ("<B'> AB' vs A'B'","ABp","ApBp",outB,mB)]

def report(counts):
    print("  no-signaling checks (delta marginal ~0; CI excluding 0 = marginal-law broken):")
    broken=0
    for label,c1,c2,outf,mf in CHECKS:
        d=mf(counts[c1])-mf(counts[c2]); lo,hi=boot_diff(outf(counts[c1]),outf(counts[c2]))
        flag="" if (lo<=0<=hi) else "   <-- BROKEN"
        broken+=0 if flag=="" else 1
        print(f"    {label}   delta={d:+.3f}  95%CI [{lo:+.3f}, {hi:+.3f}]{flag}")
    print()
    if broken==0:
        print("  >>> NO-SIGNALING HOLDS (all 4 marginals stable across the other setting).")
        print("      Clean Bell test: an S>2 here is genuine nonlocal-type entanglement")
        print("      (no common-cause / shared-latent model can reproduce it).")
    else:
        print(f"  >>> {broken}/4 marginal(s) depend on the other setting -- NO-SIGNALING VIOLATED.")
        print("      Honest reading: an S>2 here is CONTEXTUALITY (still non-classical, still")
        print("      beats common-cause) but NOT clean nonlocal entanglement. Report the case.")

def gen_signaling(n=200, seed=1):       # make B-marginal depend on A's setting -> trips checks 3&4
    q=ch.gen_quantum(n,seed); out=dict(q)
    for k in ("ApB","ApBp"):
        c=list(q[k]); sh=int(0.18*sum(c))
        c[0]+=sh; c[2]+=sh; c[1]=max(0,c[1]-sh); c[3]=max(0,c[3]-sh)
        out[k]=tuple(int(x) for x in c)
    return out

if __name__=="__main__":
    if len(sys.argv)>=3 and sys.argv[1]=="--demo":
        k=sys.argv[2]
        counts = ch.gen_quantum() if k=="quantum" else ch.gen_classical() if k=="classical" else gen_signaling()
        print(f"[synthetic {k} data]")
    elif len(sys.argv)==2:
        counts=ch.load_csv(sys.argv[1]); print(f"[your data: {sys.argv[1]}]")
    else:
        print(__doc__); sys.exit(0)
    report(counts)
