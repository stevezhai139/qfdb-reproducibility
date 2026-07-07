#!/usr/bin/env python3
"""
QFDB S1 -- Power analysis: how many respondents per condition to detect S>2?

Decision rule (matches chsh_analysis.py): declare a violation iff the 95% CI lower
bound on S exceeds 2. We simulate the elicitation at a range of per-condition sizes n
and 'true' effects S_true (via visibility v: E_k = v*E_Tsirelson, so S_true=v*2sqrt2),
and report POWER = P(CI-lower > 2). Lower bound uses the normal approx
S - 1.96*SE, SE = sqrt(sum (1-E_k^2)/n) -- validated against the bootstrap below.
Outputs: a power table, the smallest n reaching 80% power per effect, fig_s1_power.pdf.
"""
import numpy as np
import chsh_analysis as ch
TS=1/np.sqrt(2); SIGN=np.array([1,1,1,-1]); ETS=np.array([TS,TS,TS,-TS])
def probs(E): return np.array([(1+E)/4,(1-E)/4,(1-E)/4,(1+E)/4])
def power(v,n,R=3000,seed=0):
    rng=np.random.default_rng(seed); P=[probs(e) for e in v*ETS]; hits=0
    for _ in range(R):
        Eh=np.empty(4); var=0.0
        for j in range(4):
            c=rng.multinomial(n,P[j]); e=(c[0]-c[1]-c[2]+c[3])/n; Eh[j]=e; var+=(1-e*e)/n
        if (SIGN*Eh).sum()-1.96*np.sqrt(var) > 2: hits+=1
    return hits/R

EFFECTS=[2.20,2.40,2.60,2.828]; NGRID=[15,20,25,30,40,50,60,80,100,120]
def vof(S): return S/(2*np.sqrt(2))

def main():
    print("=== VALIDATION: analytic 95% lower bound vs chsh_analysis bootstrap (quantum, n=50) ===")
    cq=ch.gen_quantum(50,seed=3); Es={k:ch.E_of(cq[k]) for k in ch.CONDS}; S=ch.chsh(Es)
    var=sum((1-ch.E_of(cq[k])**2)/sum(cq[k]) for k in ch.CONDS)
    blo,bhi=ch.bootstrap_ci(cq); alo=S-1.96*np.sqrt(var)
    print(f"  S={S:+.3f}  analytic lo={alo:+.3f}   bootstrap lo={blo:+.3f}  (agree => power rule faithful)\n")
    print("=== POWER = P(95% CI lower bound > 2), {} sims/cell ===".format(3000))
    hdr="  n/cond | "+" ".join(f"S~{e:4.2f}" for e in EFFECTS); print(hdr); print("  "+"-"*(len(hdr)-2))
    grid={e:[] for e in EFFECTS}
    for n in NGRID:
        row=[]
        for e in EFFECTS:
            p=power(vof(e),n,seed=n); grid[e].append(p); row.append(f"{p:5.2f} ")
        print(f"  {n:5d}  | "+" ".join(row))
    print("\n=== smallest n/condition for >=80% power ( x4 = total respondents ) ===")
    for e in EFFECTS:
        hit=[n for n,p in zip(NGRID,grid[e]) if p>=0.8]
        if hit: print(f"  S_true~{e:4.2f}:  n>={hit[0]:3d} / condition   (total ~{4*hit[0]})")
        else:   print(f"  S_true~{e:4.2f}:  >120 / condition (effect too weak for this grid)")
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        plt.figure(figsize=(5.2,3.6))
        for e in EFFECTS: plt.plot(NGRID,grid[e],marker="o",label=f"S_true~{e:.2f}")
        plt.axhline(0.8,ls="--",c="grey",lw=1); plt.text(NGRID[-1],0.81,"80%",ha="right",fontsize=8,color="grey")
        plt.xlabel("respondents per condition (n)"); plt.ylabel("power: P(CI lower > 2)")
        plt.title("QFDB S1 power: detecting S>2 vs sample size"); plt.legend(fontsize=8); plt.tight_layout()
        plt.savefig("fig_s1_power.pdf"); print("\n  figure -> fig_s1_power.pdf")
    except Exception as ex:
        print("  (figure skipped:", ex, ")")

if __name__=="__main__": main()
