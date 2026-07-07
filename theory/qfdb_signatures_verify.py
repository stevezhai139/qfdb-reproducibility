#!/usr/bin/env python3
"""
QFDB Theory Note 03 - operational signatures S1-S3: does each test actually
separate quantum from classical? Exact classical simulation (numpy).
Reproduce:  python3 qfdb_signatures_verify.py
"""
import numpy as np
np.set_printoptions(precision=4, suppress=True)
k0=np.array([1,0],complex); k1=np.array([0,1],complex)
plus=(k0+k1)/np.sqrt(2); minus=(k0-k1)/np.sqrt(2)
I2=np.eye(2,dtype=complex); Z=np.array([[1,0],[0,-1]],complex); X=np.array([[0,1],[1,0]],complex)
def kron(*o):
    r=o[0]
    for x in o[1:]: r=np.kron(r,x)
    return r
def proj(v):
    v=v.reshape(-1,1); return (v@v.conj().T)/(v.conj().T@v).real

# ---- S1: CHSH  (from D3 relationship=entanglement) ----
print("S1  Bell/CHSH   classical bound |S|<=2 ; Tsirelson 2*sqrt2 ~ 2.828")
bell=(kron(k0,k0)+kron(k1,k1))/np.sqrt(2)
A,Ap=Z,X; B=(Z+X)/np.sqrt(2); Bp=(Z-X)/np.sqrt(2)
def E(st,M,N): return float((st.conj()@kron(M,N)@st).real)
S=E(bell,A,B)+E(bell,A,Bp)+E(bell,Ap,B)-E(bell,Ap,Bp)
prod=kron(k0,k0)
Sc=E(prod,A,B)+E(prod,A,Bp)+E(prod,Ap,B)-E(prod,Ap,Bp)
print(f"   entangled (Bell)  : S = {S:.4f}   -> FIRES (>2)  non-classical correlation")
print(f"   product (classical): S = {Sc:.4f}   -> no fire (<=2)")

# ---- S2: query order effect + QQ equality (from D5 quantum logic) ----
print("\nS2  Order effect + QQ equality (Wang-Busemeyer parameter-free invariant)")
psi=np.cos(0.4)*k0+np.sin(0.4)*k1
Ay,An=proj(k0),proj(k1)        # query A: "= |0> ?"
By,Bn=proj(plus),proj(minus)   # query B: "= |+> ?"  (incompatible with A)
def pp(P1,P2,st):              # P(1st=yes, then 2nd=yes) = ||P2 P1 st||^2
    v=P2@P1@st; return float((v.conj()@v).real)
AyBy,AnBn=pp(Ay,By,psi),pp(An,Bn,psi)
ByAy,BnAn=pp(By,Ay,psi),pp(Bn,An,psi)
print(f"   incompatible : order effect P(AyBy)-P(ByAy) = {AyBy-ByAy:+.4f} (!=0)")
print(f"                  QQ = [P(AyBy)+P(AnBn)] - [P(ByAy)+P(BnAn)] = {(AyBy+AnBn)-(ByAy+BnAn):+.4f}  (==0 : quantum invariant)")
By2,Bn2=proj(k0),proj(k1)      # compatible (commuting) version
print(f"   compatible   : order effect = {pp(Ay,By2,psi)-pp(By2,Ay,psi):+.4f}  (==0 : classical, no order effect)")

# ---- S3: interference / law of total probability (from D8 phase) ----
print("\nS3  Interference: P(B) coherent vs classical total-probability via A")
PBdir=float((psi.conj()@By@psi).real)
pAy=float((psi.conj()@Ay@psi).real); pAn=float((psi.conj()@An@psi).real)
sAy=Ay@psi; sAy/=np.sqrt((sAy.conj()@sAy).real)
sAn=An@psi; sAn/=np.sqrt((sAn.conj()@sAn).real)
PBcla=pAy*float((sAy.conj()@By@sAy).real)+pAn*float((sAn.conj()@By@sAn).real)
print(f"   P(B) coherent           = {PBdir:.4f}")
print(f"   P(B) classical (via A)  = {PBcla:.4f}")
print(f"   interference term       = {PBdir-PBcla:+.4f}  (!=0 => phase/coherence present, non-classical)")
