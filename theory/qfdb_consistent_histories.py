import numpy as np
from numpy import pi, exp, sqrt

# ===== calf -> steer -> ox as consistent histories =====
# Hilbert space: |calf>, |steer>, |ox|  (qutrit = the entity's lifecycle stage)
calf   = np.array([1,0,0], dtype=complex)
steer    = np.array([0,1,0], dtype=complex)
ox = np.array([0,0,1], dtype=complex)

def proj(v):
    v = v/np.linalg.norm(v); return np.outer(v, v.conj())

# 3-point quantum Fourier transform = a clean "aging" dynamics that spreads the stage
w = exp(2j*pi/3)
F = (1/sqrt(3))*np.array([[1,1,1],[1,w,w**2],[1,w**2,w**4]], dtype=complex)

P_steer    = proj(steer)              # intermediate alternative: "passed through STEER"
P_notsteer = np.eye(3) - P_steer      #                           "did NOT pass through steer"
P_ox = proj(ox)           # final query: "is it OX now?"

def decoherence_functional(phi, gamma):
    # t1: animal recorded as |calf>.  U1: calf-life -> mid-life.  U2: mid-life -> now (with phase phi).
    psi0 = calf
    rho0 = np.outer(psi0, psi0.conj())
    U1   = F
    U2   = F.conj().T @ np.diag([1, exp(1j*phi), 1])   # relative phase on the steer branch
    def C(Pm):                  # chain operator for an intermediate alternative
        return P_ox @ U2 @ Pm @ U1
    names = [('steer',P_steer), ('notsteer',P_notsteer)]
    D = {}
    for n1,P1 in names:
        for n2,P2 in names:
            D[(n1,n2)] = np.trace(C(P1) @ rho0 @ C(P2).conj().T)
    # gamma = how much the intermediate steer-stage is LOGGED (measured) -> dephases off-diagonal
    off = (1-gamma)
    P_coh = (D[('steer','steer')] + D[('notsteer','notsteer')] + off*(D[('steer','notsteer')]+D[('notsteer','steer')])).real
    return D, P_coh

print("DECOHERENCE FUNCTIONAL  D(alpha,beta)  over histories {through-steer , not-through-steer}\n")
for gamma,label in [(0.0,"gamma=0  (steer-stage NOT logged -> QFDB)"),
                    (1.0,"gamma=1  (steer-stage LOGGED every step -> classical temporal DB)")]:
    D,_ = decoherence_functional(phi=pi/2, gamma=gamma)
    Dm = np.array([[D[('steer','steer')], (1-gamma)*D[('steer','notsteer')]],
                   [(1-gamma)*D[('notsteer','steer')], D[('notsteer','notsteer')]]])
    print(label)
    print("   [[ %6.3f%+6.3fj , %6.3f%+6.3fj ]"%(Dm[0,0].real,Dm[0,0].imag,Dm[0,1].real,Dm[0,1].imag))
    print("    [ %6.3f%+6.3fj , %6.3f%+6.3fj ]]"%(Dm[1,0].real,Dm[1,0].imag,Dm[1,1].real,Dm[1,1].imag))
    offmag = abs((1-gamma)*D[('steer','notsteer')])
    print("   |off-diagonal| = %.3f  -> %s\n"%(offmag, "0  => CLASSICAL (substitutable)" if offmag<1e-9 else "!=0 => QUANTUM (NOT substitutable)"))

print("P(ox now) vs phase phi  --  coherent (unlogged) vs classical (logged):")
print(f"{'phi(deg)':>8} {'P_coherent':>12} {'P_classical':>12} {'difference':>11}")
for deg in [0,60,90,120,180]:
    phi = np.deg2rad(deg)
    _,Pc = decoherence_functional(phi, gamma=0.0)
    _,Pd = decoherence_functional(phi, gamma=1.0)
    print(f"{deg:>8} {Pc:>12.3f} {Pd:>12.3f} {Pc-Pd:>11.3f}")
print("\n=> classical P(ox) is phase-BLIND (flat). Coherent P(ox) MOVES with the unlogged")
print("   steer-stage's phase. The gap = the off-diagonal of D = the witness of 'not substitutable'.")
