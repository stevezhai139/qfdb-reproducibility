#!/usr/bin/env python3
"""
QFDB Theory Note 01 - 2-qubit toy model: numerical verification.

WHAT THIS IS: an EXACT classical simulation of a 2-qubit quantum system using
numpy linear algebra (state vectors, density matrices, partial traces,
eigenvalues). For 2 qubits the Hilbert space is 4-dimensional, so every number
is exact - no approximation, no Monte-Carlo sampling, no quantum hardware.
The fact that it runs on a laptop is the point: we committed to the
classically-simulable sector. Real-hardware tests remain parked.

REPRODUCE:  python3 qfdb_toy_verify.py        (needs only numpy)
"""
import numpy as np
np.set_printoptions(precision=4, suppress=True)

# --- building blocks ---
I2 = np.eye(2, dtype=complex)
Z  = np.array([[1, 0], [0, -1]], complex)
X  = np.array([[0, 1], [1, 0]], complex)
H  = np.array([[1, 1], [1, -1]], complex) / np.sqrt(2)
k0 = np.array([1, 0], complex)
k1 = np.array([0, 1], complex)
plus = (k0 + k1) / np.sqrt(2)

def kron(*ops):
    r = ops[0]
    for o in ops[1:]:
        r = np.kron(r, o)
    return r

def dm(psi):                       # pure-state density matrix
    psi = np.asarray(psi, complex).reshape(-1, 1)
    return psi @ psi.conj().T

def rhoA(rho):                     # reduced state of A = trace out B
    return np.einsum('ibjb->ij', rho.reshape(2, 2, 2, 2))

def rhoB(rho):                     # reduced state of B = trace out A
    return np.einsum('aiaj->ij', rho.reshape(2, 2, 2, 2))

def S(rho):                        # von Neumann entropy in bits
    e = np.linalg.eigvalsh(rho)
    e = e[e > 1e-12]
    return float(-np.sum(e * np.log2(e)))

def negativity(rho):               # entanglement measure valid for mixed states
    pt = np.transpose(rho.reshape(2, 2, 2, 2), (0, 3, 2, 1)).reshape(4, 4)
    e = np.linalg.eigvalsh(pt)
    return float(np.sum(np.abs(e[e < 0])))

# --- CLAIM 1: relationship = entanglement spectrum ---
print("CLAIM 1  relationship emerges as entanglement   |psi> = cos t|00> + sin t|11>")
for t, lab in [(0, "product   "), (np.pi/8, "t=pi/8    "), (np.pi/4, "Bell (max)")]:
    psi = np.cos(t) * kron(k0, k0) + np.sin(t) * kron(k1, k1)
    print(f"   {lab}  S(rhoA)={S(rhoA(dm(psi))):.4f}   negativity={negativity(dm(psi)):.4f}")

# --- CLAIM 2: does relative phase modulate entanglement? ---
print("\nCLAIM 2  relative phase vs entanglement          |psi> = (|00> + e^{i phi}|11>)/sqrt2")
for phi in [0, np.pi/2, np.pi]:
    psi = (kron(k0, k0) + np.exp(1j*phi) * kron(k1, k1)) / np.sqrt(2)
    print(f"   phi={phi:5.3f}  S(rhoA)={S(rhoA(dm(psi))):.4f}   negativity={negativity(dm(psi)):.4f}  (constant => phase does NOT modulate entanglement)")
print("   where cos^2 actually lives = OVERLAP of two single-artifact states |<a|b>|^2:")
for phi in [0, np.pi/2, np.pi]:
    b = (k0 + np.exp(1j*phi) * k1) / np.sqrt(2)
    print(f"   phi={phi:5.3f}  |<a|b>|^2={abs(np.vdot(plus, b))**2:.4f}  (= query/relevance, not entanglement)")

# --- CLAIM 4: update A -> B? update A -> relationship? ---
print("\nCLAIM 4  local update of A   (start: Bell state)")
bell = (kron(k0, k0) + kron(k1, k1)) / np.sqrt(2)
rho = dm(bell)
print(f"   Bell            rhoB_diag={np.diag(rhoB(rho)).real}  S(rhoA)={S(rhoA(rho)):.4f}  neg={negativity(rho):.4f}")
ru = kron(H, I2) @ rho @ kron(H, I2).conj().T               # local unitary on A
print(f"   local unitary   rhoB_diag={np.diag(rhoB(ru)).real}  S(rhoA)={S(rhoA(ru)):.4f}  neg={negativity(ru):.4f}  (B & entanglement UNCHANGED)")
KZ = kron(Z, I2)
rc = 0.5 * (rho + KZ @ rho @ KZ.conj().T)                   # local dephasing CHANNEL on A
print(f"   dephase channel rhoB_diag={np.diag(rhoB(rc)).real}  S(rhoA)={S(rhoA(rc)):.4f}  neg={negativity(rc):.4f}  (B marginal SAME, but entanglement -> 0)")
print("   => S(rhoA)=1.0 yet neg=0 after channel: S(rhoA) is NOT a valid entanglement measure for mixed states.")

# --- query algebra: non-commutativity ---
print("\nQUERY    [Z, X] == 0 ?", np.allclose(Z @ X, X @ Z), " -> query ordering matters (genuine order effect)")
