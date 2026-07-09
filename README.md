> **Reviewers:** [`QFDB_companion.pdf`](QFDB_companion.pdf) is the supplementary material for the CIDR 2027 submission -- full proofs, worked-example algebra, S1 power analysis, and the complete pre-registered negative-control methods and results.

# QFDB — Reproducibility Repository

Companion code for the paper:

> **Database Schemas as Quantum Fields: Relational and Document Models as a Classical Sector**
> Arun Reungsilpkolkarn, School of Information Technology and Innovation, Bangkok University (2026).

Every numerical claim in the paper is reproduced by a script here. **All computations run classically on a laptop** (the *classically simulable regime*); **no quantum hardware is required**. We claim a faithful representational account, not a speedup.

---

## Requirements

- Python ≥ 3.10
- `numpy`, `scipy`, `pandas`, `matplotlib`

```bash
pip install -r requirements.txt
```

---

## Reproducing the paper's numbers

Each row is independently runnable. Outputs below were verified on the reference machine.

| Paper claim | Script | Key expected output (verified) |
|---|---|---|
| **Common-cause bound** — any shared-latent (LHV) model of two schemas obeys \|S\|≤2; only a non-common-cause source reaches Tsirelson 2√2 | `theory/qfdb_commoncause_bound.py` | deterministic LHV: `max S = 2`; 200k random mixtures: `max|S| = 1.45`; entangled: `S = 2.8284 > 2` |
| **Falsifiable signatures S1/S2/S3** fire as designed | `theory/qfdb_signatures_verify.py` | S1: Bell `S=2.8284` fires, product `S=1.4142` no-fire · S2: `QQ = 0.0000` (parameter-free invariant) · S3: interference term `+0.359 ≠ 0` |
| **2-qubit toy: structure vs state** (non-classicality lives in coherence/negativity, not structure) | `theory/qfdb_toy_verify.py` | product `negativity=0`; Bell `negativity=0.5`; phase does **not** modulate entanglement; dephasing channel sends entanglement→0 while the marginal is unchanged |
| **Definition set D1–D8** (non-distributive query logic; coherence recovered after drill-down) | `theory/qfdb_defs_verify.py` | distributive law **FAILS** (rank 1 vs 0); coherence recovered `= 0.5`; Bell negativity `0.5` invariant under local unitary, →0 under local channel |
| **Face A — incompatible query / order effect** (QQ=0 at every θ; a tuned classical model departs) | `theory/qfdb_order_effect_mutant.py` | θ-sweep of `P(vaccinated@t)`; `QQ = 0.000` parameter-free |
| **Face B — unlogged history / decoherence** (logging granularity = order-safety boundary) | `theory/qfdb_consistent_histories.py` | logged: present probability fixed; unlogged: phase-dependent swing |
| **S2 calibration on real surveys** (mean order effect 0.087, QQ +0.001, n.s.) | `s2_calibration/qfdb_s2_pipeline.py` | requires the question-order survey data (Wang et al. 2014; see `data/`) |
| Field-mode / two-schema entanglement constructions | `theory/qfdb_H1_field_modes.py`, `theory/qfdb_H5_two_schema.py` | mode occupation & 1.000-bit entanglement of the paired-schema state |

```bash
# example
python3 theory/qfdb_commoncause_bound.py
python3 theory/qfdb_signatures_verify.py
```

---

## S1 elicitation toolkit (the decisive Bell test on real data)

The S1 human-subjects study (a CHSH/Bell test of inter-schema correspondence judgments) is **pending IRB approval**; no human data is collected until then. These scripts are the **pre-registered analysis instrument**, validated on synthetic and held-out data.

| Script | Purpose |
|---|---|
| `s1_elicitation/chsh_analysis.py` | compute CHSH `S` + 95% bootstrap CI from elicited responses (decision rule: CI-lower > 2) |
| `s1_elicitation/qfdb_s1_power.py` | power analysis — respondents per condition needed to detect `S>2` |
| `s1_elicitation/qfdb_s1_nosignaling.py` | no-signaling / marginal-law check (clean nonlocal entanglement vs contextuality) |
| `s1_elicitation/qfdb_s1_tally.py` | convert a survey response export → `responses.csv` for the above |

```bash
python3 s1_elicitation/chsh_analysis.py --demo quantum     # synthetic data that violates
python3 s1_elicitation/chsh_analysis.py --demo classical   # synthetic data that does not
```

---

## Suggested repository layout

```
qfdb-reproducibility/
├── README.md
├── requirements.txt
├── theory/            # reproduces every theoretical number (run standalone)
├── s1_elicitation/    # CHSH analysis + power + no-signaling + tally  (keep together; they import chsh_analysis)
├── s2_calibration/    # order-effect / QQ pipeline on real survey data
└── data/              # survey data for S2 + pointers (no S1 human data until IRB)
```
*(The four `s1_elicitation/` scripts import `chsh_analysis.py`, so keep them in one directory.)*

---

## Data availability

- **S2:** question-order survey data (Wang et al., *PNAS* 2014) — see `data/` and `DATA_SOURCES.md`.
- **S1:** protocol + instrument only; **no human-subject data is included** (study pending IRB approval).

## Scope

This code establishes **Level 1** (the representational account) in the classically simulable regime. It does **not** claim that real databases are non-classical (Level 2, empirical, open) nor implement a quantum-field database (Level 3, future). See the paper, §Scope.

## License

Released under the MIT License (code). See `LICENSE`.

## Citation

```bibtex
@misc{reungsilpkolkarn2026qfdb,
  title  = {Database Schemas as Quantum Fields: Relational and Document Models as a Classical Sector},
  author = {Reungsilpkolkarn, Arun},
  year   = {2026},
  note   = {School of Information Technology and Innovation, Bangkok University}
}
```

## Reference environments
Every number reproduces digit-for-digit (incl. bootstrap CIs; fixed PCG64 seed) on:
- MacBook Pro, Apple M4, 24 GB RAM, 512 GB internal SSD + 1 TB Thunderbolt external SSD, macOS Tahoe 26.x, NumPy 2.2.6
- Debian Linux (aarch64), Python 3.10, NumPy 2.2.6

NumPy-only (LLM harness: stdlib-only); no GPU or quantum hardware; the full negative-control run takes < 1 minute.
