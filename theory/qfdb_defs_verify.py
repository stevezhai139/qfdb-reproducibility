#!/usr/bin/env python3
"""
QFDB Theory Note 02 - verification of the NEW formal claims (definition set D1-D8).
Exact classical simulation (numpy). Reproduce:  python3 qfdb_defs_verify.py
"""
import numpy as np
np.set_printoptions(precision=4, suppress=True)

k0=np.array([1,0],complex); k1=np.array([0,1],complex)
plus=(k0+k1)/np.sqrt(2); minus=(k0-k1)/np.sqrt(2); ki=(k0+1j*k1)/np.sqrt(2)
I2=np.eye(2,dtype=complex); Z=np.array([[1,0],[0,-1]],complex)

def proj(v):
    v=v.reshape(-1,1); return (v@v.conj().T)/(v.conj().T@v).real
def kron(*o):
    r=o[0]
    for x in o[1:]: r=np.kron(r,x)
    return r
def is_herm(M): return bool(np.allclose(M,M.conj().T))
def rank(P): return int(np.round(np.trace(P).real))
def rS(r): return np.einsum('ibjb->ij', r.reshape(2,2,2,2))

print("D5  QUERY ALGEBRA = orthomodular lattice (quantum logic), NOT Boolean")
PA=kron(proj(plus),I2); PB=kron(proj(k0),I2)   # two yes/no queries on artifact A
print("   queries commute? [P_+,P_0]=0 :", bool(np.allclose(PA@PB,PB@PA)))
print("   naive AND = P_+ . P_0 is a valid observable (Hermitian)? :", is_herm(PA@PB),
      "  <- product NOT closed for non-commuting queries")

def join(P,Q):
    M=np.hstack([P,Q]); U,s,_=np.linalg.svd(M); r=int(np.sum(s>1e-9))
    B=U[:,:r]; return B@B.conj().T
def meet(P,Q):
    n=P.shape[0]; I=np.eye(n,dtype=complex); return I-join(I-P,I-Q)

a,b,c=proj(k0),proj(plus),proj(ki)             # three distinct rays on ONE qubit
lhs=meet(a,join(b,c)); rhs=join(meet(a,b),meet(a,c))
print(f"   a^(bvc) rank={rank(lhs)}   (a^b)v(a^c) rank={rank(rhs)}   -> distributive law FAILS")

print("\nD6  HISTORY = Stinespring dilation; non-unitary update is irreversible WITHOUT the stored shell")
rhoS=proj((k0+k1)/np.sqrt(2))
print(f"   original coherence |0><1| = {rhoS[0,1].real:.3f}")
deph=0.5*(rhoS+Z@rhoS@Z)
print(f"   after dephasing channel    = {deph[0,1].real:.3f}   (information lost)")
CNOT=np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]],complex)
glob=CNOT@kron(rhoS,proj(k0))@CNOT.conj().T    # couple system to environment qubit
print("   channel == trace_E[ U (rho (x) |0>) U+ ] ? :", bool(np.allclose(rS(glob),deph)))
rec=CNOT@glob@CNOT.conj().T                    # keep shell, uncompute (drill-down)
print(f"   after drill-down (uncompute) = {rS(rec)[0,1].real:.3f}   (recovered: shell retained)")

print("\nD3/D7  relationship measure + update trade-off (re-confirm)")
bell=(kron(k0,k0)+kron(k1,k1))/np.sqrt(2); rho=proj(bell)
def neg(r):
    t=np.transpose(r.reshape(2,2,2,2),(0,3,2,1)).reshape(4,4); e=np.linalg.eigvalsh(t)
    return float(np.sum(np.abs(e[e<0])))
H=np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
ru=kron(H,I2)@rho@kron(H,I2).conj().T
KZ=kron(Z,I2); rc=0.5*(rho+KZ@rho@KZ.conj().T)
print(f"   Bell neg={neg(rho):.3f} | local-unitary neg={neg(ru):.3f} (invariant) | local-channel neg={neg(rc):.3f} (down)")
