#!/usr/bin/env python3
"""
QFDB Phase-3, circuit C4: coherent constraints — computational proof of Prop B
(theory notes 06/08).

Prop B (Coherent Constraint).  For a two-place predicate P on D_A x D_B with
non-empty satisfying set S, let |psi_P> = |S|^(-1/2) sum_{(x,y) in S} |x,y>
(the constraint held coherently, instead of enumerated as rows).  Then:
  (i)   |psi_P> is a product state  <=>  S is a combinatorial rectangle AxB
        <=>  P is logically equivalent to a conjunction P1(x) AND P2(y);
  (ii)  Schmidt rank(|psi_P>) = rank of the 0/1 incidence matrix chi_S;
  (iii) the entanglement spectrum of |psi_P> is the squared singular-value
        spectrum of chi_S / sqrt(|S|).

Consequence: the entanglement of a coherently-held constraint is a purely
RELATIONAL quantity — computable from the relation's incidence matrix before
any physics.  "Entanglement = constraint without extension" (note 06) is now
quantitative: non-decomposability of the predicate IS the entanglement.

What this script proves, mechanically:
  C4.1  Circuit demo (qiskit): DECLARE CONSTRAINT x=y COHERENT on a 2-value
        domain is exactly the Bell preparation H+CX. Querying x forces y with
        conditional probability 1, yet no row of the extension {(0,0),(1,1)}
        is ever stored — the two qubits hold the intension.
        Entropy = 1.000 bit — the same number circuit C1 measures.
  C4.2  Exhaustive proof of (i) at |D_A|=|D_B|=3: all 511 non-empty
        relations — product <=> rectangle, zero exceptions (49 rectangles).
  C4.3  (ii)+(iii) cross-validated on random relations through two
        independently-coded pipelines:
          physics    : state -> partial trace -> eigenvalues -> rank/entropy
          relational : 0/1 matrix -> matrix_rank / singular values
  C4.4  Worked constraints: x=y at d=2 and d=4; x<=y on 3x3; an injective
        functional dependency (a key held coherently is MAXIMALLY entangled);
        a rectangle control (zero entanglement).

Run:  python3 c4_coherent_constraints.py      Deps: numpy; qiskit for C4.1
"""
import math
import numpy as np

np.set_printoptions(precision=4, suppress=True)
OK = "✓"

# ------------------------------------------------------------- Prop B core
def psi_from_relation(chi: np.ndarray) -> np.ndarray:
    """Coefficient matrix M of the uniform coherent constraint |psi_P>."""
    s = int(chi.sum())
    assert s > 0, "empty satisfying set"
    return chi.astype(float) / math.sqrt(s)

def physics_pipeline(M: np.ndarray):
    """|psi> with coefficients M -> reduced state of side A -> spectrum.
    Returns (Schmidt rank, entanglement entropy in bits)."""
    rho_a = M @ M.conj().T                      # partial trace over side B
    evals = np.linalg.eigvalsh(rho_a)
    evals = evals[evals > 1e-12]
    return len(evals), float(-(evals * np.log2(evals)).sum())

def relational_pipeline(chi: np.ndarray):
    """0/1 incidence matrix only — no state ever built.
    Returns (matrix rank, entropy from singular values of chi/sqrt|S|)."""
    rank = int(np.linalg.matrix_rank(chi))
    sv = np.linalg.svd(chi / math.sqrt(chi.sum()), compute_uv=False)
    p = sv ** 2
    p = p[p > 1e-12]
    return rank, float(-(p * np.log2(p)).sum())

def is_rectangle(chi: np.ndarray) -> bool:
    """S = A x B for the row/column supports?"""
    rows = chi.any(axis=1).astype(chi.dtype)
    cols = chi.any(axis=0).astype(chi.dtype)
    return bool(np.array_equal(chi, np.outer(rows, cols)))

# ------------------------------------------------------------------- C4.1
def c4_1_declare_constraint_coherent():
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    print("C4.1  DECLARE CONSTRAINT x=y COHERENT  (2 qubits, circuit)")
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)                                  # = coherent 'x=y', d=2
    sv = Statevector.from_instruction(qc)
    # qiskit little-endian: index = 2*q1 + q0 ; take x = q0, y = q1
    M = sv.data.reshape(2, 2).T                  # M[x, y]
    expect = np.eye(2) / math.sqrt(2)
    assert np.allclose(M, expect), "coherent x=y should be I/sqrt2"
    print(f"    preparation H+CX = uniform superposition over satisfying set "
          f"of x=y   {OK}")

    # query x, verify the constraint enforces y — extension never stored
    for x in (0, 1):
        col = M[x, :]                            # post-measurement branch
        p_x = float(np.sum(np.abs(col) ** 2))
        cond = np.abs(col) ** 2 / p_x
        assert abs(p_x - 0.5) < 1e-12 and abs(cond[x] - 1.0) < 1e-12
        print(f"    query x -> {x} (p = {p_x:.2f}): constraint forces y = {x} "
              f"with conditional probability {cond[x]:.2f}   {OK}")

    # entanglement of the constraint — via BOTH pipelines
    r_phys, e_phys = physics_pipeline(M)
    r_rel, e_rel = relational_pipeline(np.eye(2, dtype=int))
    assert r_phys == r_rel == 2 and abs(e_phys - 1.0) < 1e-12 \
        and abs(e_rel - 1.0) < 1e-12
    print(f"    entanglement entropy = {e_phys:.3f} bit — the SAME number "
          f"circuit C1 measures:\n"
          f"    the Bell schema pair of C1 *is* the constraint x=y held "
          f"coherently   {OK}")
    print("    (no row of the extension {(0,0),(1,1)} exists anywhere in the\n"
          "     register — the state stores the intension; classical storage\n"
          "     must materialize the extension to answer the same query)\n")

# ------------------------------------------------------------------- C4.2
def c4_2_exhaustive_product_iff_rectangle():
    print("C4.2  Prop B(i) exhaustively at 3x3: product <=> rectangle")
    d = 3
    n_rect = 0
    for bits in range(1, 2 ** (d * d)):
        chi = np.array([(bits >> k) & 1 for k in range(d * d)],
                       dtype=int).reshape(d, d)
        rank, _ = physics_pipeline(psi_from_relation(chi))
        rect = is_rectangle(chi)
        assert (rank == 1) == rect, f"counterexample: {chi.tolist()}"
        n_rect += rect
    assert n_rect == 49                          # (2^3-1)^2 non-empty AxB
    print(f"    all 511 non-empty relations checked: product state <=> "
          f"rectangle, 0 exceptions\n"
          f"    (49 rectangles = separable constraints; the remaining 462 "
          f"are entangled)   {OK}\n")

# ------------------------------------------------------------------- C4.3
def c4_3_schmidt_rank_equals_matrix_rank():
    print("C4.3  Prop B(ii)+(iii): physics pipeline == relational pipeline")
    rng = np.random.default_rng(2026)
    trials = 0
    max_rank_seen = 0
    while trials < 400:
        da = int(rng.integers(2, 7))
        db = int(rng.integers(2, 8))
        chi = (rng.random((da, db)) < rng.uniform(0.15, 0.85)).astype(int)
        if chi.sum() == 0:
            continue
        r_phys, e_phys = physics_pipeline(psi_from_relation(chi))
        r_rel, e_rel = relational_pipeline(chi)
        assert r_phys == r_rel, (chi.tolist(), r_phys, r_rel)
        assert abs(e_phys - e_rel) < 1e-9, (chi.tolist(), e_phys, e_rel)
        max_rank_seen = max(max_rank_seen, r_phys)
        trials += 1
    print(f"    400 random relations (up to 6x7): Schmidt rank == "
          f"incidence-matrix rank in all cases,\n"
          f"    entropies agree to < 1e-9 (max rank seen: {max_rank_seen})   "
          f"{OK}\n")

# ------------------------------------------------------------------- C4.4
def c4_4_worked_constraints():
    print("C4.4  worked constraints (rank = relational quantity, "
          "entropy in bits)")
    rows = []

    # x = y, d = 2 and d = 4
    for d in (2, 4):
        r, e = relational_pipeline(np.eye(d, dtype=int))
        assert r == d and abs(e - math.log2(d)) < 1e-12
        rows.append((f"x=y  (d={d})", r, e, "maximal"))

    # x <= y on 3x3
    chi = np.triu(np.ones((3, 3), dtype=int))
    r, e = relational_pipeline(chi)
    assert r == 3 and 0.0 < e < math.log2(3)
    rows.append(("x<=y (3x3)", r, e, "entangled, sub-maximal"))

    # injective functional dependency y = f(x), d = 4 (a key, coherently)
    f = [2, 0, 3, 1]
    chi = np.zeros((4, 4), dtype=int)
    for x, y in enumerate(f):
        chi[x, y] = 1
    r, e = relational_pipeline(chi)
    assert r == 4 and abs(e - 2.0) < 1e-12
    rows.append(("key: y=f(x), f injective (d=4)", r, e,
                 "MAXIMAL — a key held coherently"))

    # rectangle control: x in {0,1} AND y in {1,2}
    chi = np.outer([1, 1, 0], [0, 1, 1]).astype(int)
    r, e = relational_pipeline(chi)
    assert r == 1 and e < 1e-12
    rows.append(("x∈{0,1} ∧ y∈{1,2}  (rectangle)", r, e, "separable"))

    for name, r, e, verdict in rows:
        e = abs(e)                               # avoid printing -0.0000
        print(f"    {name:<38} rank {r}   entropy {e:.4f}   -> {verdict}")
    print(f"    every value asserted   {OK}\n")

# -------------------------------------------------------------------- main
if __name__ == "__main__":
    print("=" * 72)
    print("QFDB C4 — coherent constraints: computational proof of Prop B")
    print("=" * 72 + "\n")
    c4_1_declare_constraint_coherent()
    c4_2_exhaustive_product_iff_rectangle()
    c4_3_schmidt_rank_equals_matrix_rank()
    c4_4_worked_constraints()
    print("PROP B VERIFIED — exhaustive at 3x3 (511/511), randomized up to")
    print("6x7 (400/400), two independently-coded pipelines agree to 1e-9.")
    print("Entanglement of a coherent constraint = rank structure of the")
    print("relation itself: the quantum quantity is already sitting in the")
    print("incidence matrix. (Prop B, theory note 08)")
