# QFDB circuit twin — Phase 3 (Level-3 bridge)

The paper's constructions realized as **standard quantum circuits** (Qiskit,
`quantum_info` only — no Aer, no hardware required), cross-validated against
the NumPy formalism. Why this matters beyond the NumPy scripts: a circuit
**cannot clone states and cannot take non-unitary shortcuts** — if the
constructions compile to circuits and reproduce the paper's numbers, the
theory is *implementable as stated*, not merely computable.

Run: `pip install qiskit` then `python3 qfdb_circuits.py` — every number is
asserted; the script fails loudly on any mismatch.

| Circuit | Paper construct | Result (exact) |
|---|---|---|
| C1 (2 qubits) | Inter-schema entanglement, §3 + S1: (\|cc⟩+\|ss⟩)/√2 | CHSH **S = 2.8284** (= 2√2); product control 1.414; entanglement entropy **1.000 bit** |
| C2 (3 qubits) | Temporal shells + `AS OF` (Prop 3 + dynamics ¶) | coherence **0.500 → 0.000 → 0.500** with shells retained (fidelity 1.000000); destroy one shell → coherence 0.307 / fidelity 0.807 — **partially irreversible, matching the analytic formula ½·sin φ₁·\|a²−b²\| to 9 decimals** |
| C3 (1 qubit) | Superposed schema, §3 example: √0.7\|chain⟩+√0.3\|star⟩ | Born statistics **0.70 / 0.30**; 10,000 sampled queries: 0.706/0.294 |

## What C2 demonstrates that NumPy cannot
In the NumPy scripts nothing *prevents* keeping a hidden copy of the state —
uncompute correctness rests on the author's discipline. On a circuit,
no-cloning and unitarity are enforced by the model itself: the shells are
**entangled records, not copies**, and `AS OF` works exactly and only while
they are retained. Destroying one of two shells loses *exactly the
information that shell carried* (quantitatively: recovered coherence
½·sin φ₁·|a²−b²|) — a sharper, graded form of Prop 3's boundary:
**logging granularity is not just a safety switch, it is a dial.**

## Hardware path (Level 3 first contact, zero cost)
C1 and C3 run unchanged on IBM Quantum's free tier (1–2 qubits; expect noisy
S ≈ 2.2–2.6 for C1 — still above the classical bound). C2 needs 3 qubits with
two CNOTs each way — also free-tier feasible. This is the concrete route to
the program's founding goal: *a schema that genuinely occupies the
non-classical part of the space* — first by construction on circuits, then
on physical hardware.
