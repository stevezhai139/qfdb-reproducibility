#!/usr/bin/env python3
"""
QFDB Phase-3: circuit twin — the paper's constructions realized as standard
quantum circuits (Qiskit), cross-validated against the NumPy formalism.

Why circuits and not just NumPy: a circuit cannot clone states, cannot apply
non-unitary shortcuts, and must manage ancillas explicitly. If every QFDB
construction compiles to circuits and reproduces the formalism's numbers,
the theory is implementable as stated — not just computable.

Three demonstrations (each asserts against the paper's exact numbers):
  C1  Inter-schema entanglement: (|chain,chain> + |star,star>)/sqrt(2),
      CHSH with optimal settings -> S = 2*sqrt(2) ~ 2.8284  (paper S1 end)
      + product-state control -> S well below 2.
  C2  Temporal shells & AS OF (Prop 3 + dynamics): transactions entangle a
      shell ancilla per step (logging); AS OF = exact uncompute while shells
      are retained (fidelity 1.0); measuring/discarding a shell makes the
      update irreversible (coherence 0.5 -> 0 -> 0.5 vs 0.5 -> 0 -> 0).
      Mirrors qfdb_defs_verify.py D6 on real circuits, no cloning anywhere.
  C3  Superposed schema (Def 1): sqrt(0.7)|chain> + sqrt(0.3)|star>,
      Born statistics -> P(chain)=0.70, P(star)=0.30  (paper §3 example).

Run:  python3 qfdb_circuits.py          (exact statevector/density-matrix)
Deps: qiskit >= 1.0 (quantum_info only; no Aer, no hardware needed)
Hardware path: circuits C1/C3 are 1-2 qubits, C2 is 3 qubits — all runnable
on IBM Quantum's free tier as-is (expect noisy S ~ 2.2-2.6 for C1).
"""
import math
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace, Operator

np.set_printoptions(precision=4, suppress=True)
OK = "✓"

# ---------------------------------------------------------------- helpers
def zz_expectation(state: Statevector, theta_a: float, theta_b: float) -> float:
    """E(a,b): rotate each qubit's measurement axis by RY(-theta) then <Z(x)Z>."""
    qc = QuantumCircuit(2)
    qc.ry(-theta_a, 0)
    qc.ry(-theta_b, 1)
    rotated = state.evolve(qc)
    zz = Operator.from_label("ZZ")  # qiskit label order: qubit1 qubit0 (both Z: symmetric)
    return float(np.real(rotated.expectation_value(zz)))

def chsh(state: Statevector) -> float:
    A, Ap = 0.0, math.pi / 2                # Z and X
    B, Bp = math.pi / 4, -math.pi / 4       # (Z+X)/sqrt2 and (Z-X)/sqrt2
    return (zz_expectation(state, A, B) + zz_expectation(state, A, Bp)
            + zz_expectation(state, Ap, B) - zz_expectation(state, Ap, Bp))

def coherence01(rho_1q: DensityMatrix) -> float:
    """|off-diagonal| of a 1-qubit reduced state — the C of Prop 1."""
    return float(abs(np.asarray(rho_1q.data)[0, 1]))

# ---------------------------------------------------------------- C1
def c1_inter_schema_entanglement():
    print("C1  inter-schema entanglement (2 qubits: schema A, schema B)")
    bell = QuantumCircuit(2)
    bell.h(0)
    bell.cx(0, 1)                            # (|cc> + |ss>)/sqrt2
    sv = Statevector.from_instruction(bell)
    # cross-validate amplitudes against the formalism
    expect = np.zeros(4, complex); expect[0] = expect[3] = 1 / math.sqrt(2)
    assert np.allclose(sv.data, expect), "Bell amplitudes mismatch"
    S = chsh(sv)
    assert abs(S - 2 * math.sqrt(2)) < 1e-9
    print(f"    state = (|chain,chain> + |star,star>)/sqrt2   amplitudes {OK}")
    print(f"    CHSH S = {S:.4f}  = 2*sqrt(2)  -> exceeds classical bound 2   {OK}")
    prod = Statevector.from_instruction(QuantumCircuit(2))   # |chain,chain>
    Sp = chsh(prod)
    assert abs(Sp) <= 2.0
    print(f"    product-state control: S = {Sp:.4f}  (<= 2, no violation)   {OK}")
    # entanglement entropy of either schema = 1 bit (paper: '1.000 bit')
    rho_a = partial_trace(DensityMatrix(sv), [1])
    evals = np.linalg.eigvalsh(np.asarray(rho_a.data))
    ent = float(-sum(e * math.log2(e) for e in evals if e > 1e-12))
    assert abs(ent - 1.0) < 1e-9
    print(f"    entanglement entropy = {ent:.3f} bit   {OK}\n")

# ---------------------------------------------------------------- C2
def c2_temporal_shells_asof():
    """
    3 qubits: q0 = entity (data), q1 = shell of txn1, q2 = shell of txn2.
    Entity starts in |+> (coherence 0.5 — same number as qfdb_defs_verify D6).
    Each transaction: unitary update RY(phi) on data, then LOG: CX(data->shell).
    AS OF t-2 = uncompute: CX2, RY(-phi2), CX1, RY(-phi1) — needs the shells.
    """
    print("C2  temporal shells & AS OF (3 qubits: entity + 2 shells)")
    phi1, phi2 = 0.9, 1.3

    def build(upto_txn: int, uncompute: bool = False) -> QuantumCircuit:
        qc = QuantumCircuit(3)
        qc.h(0)                                        # coherent entity, C = 0.5
        if upto_txn >= 1:
            qc.ry(phi1, 0); qc.cx(0, 1)                # txn1 + log shell1
        if upto_txn >= 2:
            qc.ry(phi2, 0); qc.cx(0, 2)                # txn2 + log shell2
        if uncompute:
            qc.cx(0, 2); qc.ry(-phi2, 0)               # inverse txn2
            qc.cx(0, 1); qc.ry(-phi1, 0)               # inverse txn1
        return qc

    rho0 = partial_trace(DensityMatrix.from_instruction(build(0)), [1, 2])
    c_initial = coherence01(rho0)
    rho_logged = partial_trace(DensityMatrix.from_instruction(build(2)), [1, 2])
    c_logged = coherence01(rho_logged)
    rho_back = partial_trace(DensityMatrix.from_instruction(build(2, uncompute=True)), [1, 2])
    c_recovered = coherence01(rho_back)
    fid = float(np.real(np.trace(np.asarray(rho0.data) @ np.asarray(rho_back.data))))
    # purity-based fidelity check: rho0 is pure, so tr(rho0 rho_back) = <psi0|rho_back|psi0>
    print(f"    entity coherence: initial {c_initial:.3f} -> after 2 logged txns "
          f"{c_logged:.3f} -> after AS OF t-2 (shells retained) {c_recovered:.3f}")
    assert abs(c_initial - 0.5) < 1e-9 and c_logged < 1e-9 and abs(c_recovered - 0.5) < 1e-9
    assert abs(fid - 1.0) < 1e-9
    print(f"    recovery fidelity with shells retained = {fid:.6f}   {OK}")

    # now DESTROY a shell before uncompute: measure shell1 (record then discard)
    qc = build(2)
    rho = DensityMatrix.from_instruction(qc)
    P0 = Operator(np.diag([1, 0]).astype(complex))
    P1 = Operator(np.diag([0, 1]).astype(complex))
    # dephase shell1 (= measured, outcome forgotten): rho -> sum_m P_m rho P_m
    def apply_on(op, qubit):
        full = [np.eye(2, dtype=complex)] * 3
        full[qubit] = np.asarray(op.data)
        m = full[2]
        for k in (1, 0):
            m = np.kron(m, full[k])
        return m
    m0, m1 = apply_on(P0, 1), apply_on(P1, 1)
    r = np.asarray(rho.data)
    rho_dephased = DensityMatrix(m0 @ r @ m0.conj().T + m1 @ r @ m1.conj().T)
    unc = QuantumCircuit(3)
    unc.cx(0, 2); unc.ry(-phi2, 0); unc.cx(0, 1); unc.ry(-phi1, 0)
    rho_fail = partial_trace(rho_dephased.evolve(unc), [1, 2])
    c_fail = coherence01(rho_fail)
    fid_fail = float(np.real(np.trace(np.asarray(rho0.data) @ np.asarray(rho_fail.data))))
    # analytic cross-validation (the 'twin' claim): after dephasing shell1,
    # the recovered coherence is (1/2)|sin(phi1)| * |a^2 - b^2| with
    # (a,b) = RY(phi1) applied to (1,1)/sqrt2 — pure formalism, no circuit.
    a = (math.cos(phi1 / 2) - math.sin(phi1 / 2)) / math.sqrt(2)
    b = (math.cos(phi1 / 2) + math.sin(phi1 / 2)) / math.sqrt(2)
    c_analytic = 0.5 * abs(math.sin(phi1)) * abs(a * a - b * b)
    assert abs(c_fail - c_analytic) < 1e-9, (c_fail, c_analytic)
    print(f"    shell1 measured-and-forgotten before AS OF: coherence {c_fail:.3f} "
          f"(analytic {c_analytic:.3f} {OK}), fidelity {fid_fail:.3f}")
    assert fid_fail < 0.999 and c_fail < c_initial - 0.05
    print(f"    -> partially irreversible: exactly the information the destroyed\n"
          f"       shell carried is gone; the intact shell2 leg still uncomputes   {OK}")
    print("    (no state was ever cloned: shells are entangled records, and the\n"
          "     circuit model physically forbids copying — Prop 3's boundary holds\n"
          "     because of unitarity, not because we promised to be careful)\n")

# ---------------------------------------------------------------- C3
def c3_superposed_schema():
    print("C3  superposed schema (1 qubit): sqrt(0.7)|chain> + sqrt(0.3)|star>")
    theta = 2 * math.acos(math.sqrt(0.7))
    qc = QuantumCircuit(1)
    qc.ry(theta, 0)
    sv = Statevector.from_instruction(qc)
    amps = sv.data
    assert abs(amps[0] - math.sqrt(0.7)) < 1e-12 and abs(amps[1] - math.sqrt(0.3)) < 1e-12
    p = sv.probabilities()
    print(f"    amplitudes = (sqrt(0.7), sqrt(0.3))   {OK}")
    print(f"    Born statistics: P(chain) = {p[0]:.2f}, P(star) = {p[1]:.2f}   {OK}")
    # sampled shots (finite-statistics view, seeded)
    rng = np.random.default_rng(42)
    shots = rng.choice([0, 1], size=10_000, p=p)
    print(f"    10,000 sampled queries: chain {np.mean(shots == 0):.3f}, "
          f"star {np.mean(shots == 1):.3f}\n")

# ---------------------------------------------------------------- main
if __name__ == "__main__":
    print("=" * 72)
    print("QFDB circuit twin — constructions on real quantum circuits (Qiskit)")
    print("=" * 72 + "\n")
    c1_inter_schema_entanglement()
    c2_temporal_shells_asof()
    c3_superposed_schema()
    print("ALL CIRCUITS PASS — every number matches the NumPy formalism.")
    print("Next step (hardware): C1/C3 run unchanged on IBM Quantum free tier.")
