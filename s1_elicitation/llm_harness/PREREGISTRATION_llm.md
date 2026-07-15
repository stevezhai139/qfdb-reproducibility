# Tier-2 LLM-respondent S1 pilot — pre-registration
**Date frozen:** 2026-07-15, before any real (non-dry-run) call.
**Purpose (two, both outcome-neutral):** (1) exercise the full S1 elicitation instrument end-to-end on a judgment-generating system; (2) obtain an effect-size prior that calibrates the human study's sample size (n per setting pair = (2·2.487/(S−2))² at one-sided α=.05, power .8: S=2.6→69/pair; S=2.4→155/pair; S=2.2→619/pair).
**What a result can and cannot mean:** any violation certifies non-classical structure in the *model's* judgment statistics only — not human cognition, not the schema-field (Level-2 untouched). A null does not falsify the human hypothesis.

## Frozen design (hashes lock the artifacts)
- **Instrument:** `llm_respondent_harness.py` — SETTINGS + PROMPT frozen at sha256[:16] = `ff791789968dc84e` (Store-1: {Electronics,Furniture}/{Gift,Tool}; Store-2: {Gadget,Decor}/{Toy,Hardware}; neutral catalogue-filing wording, no physics vocabulary). Any change to SETTINGS/PROMPT after this date = new prereg version, disclosed.
- **Items:** `items_amazon_google.jsonl` (400 real product titles from the Amazon–Google benchmark), sha256[:16] = `051eb1d4fc447ba4`.
- **Respondent model (primary):** `llama3.1:8b` via ollama (open-weights; record `ollama list` digest in the run log). Other models, if any, are secondary robustness checks, reported separately.
- **Protocol:** one API call = one respondent (fresh context, memoryless); one setting pair per call (between-subjects); option order counterbalanced per call; unparseable replies logged and excluded (rate reported; if >10% at smoke test → fix parsing/prompt *before* stage 1 and note it).

## Two-stage plan with one interim look (mirrors the paper's design)
- **Smoke test:** 20 calls at T=0.7 — parse-rate check only; results discarded.
- **Stage 1 (interim look):** T=0.7, n=100/pair (400 calls). Look at S ± CI and no-signaling deltas only.
- **Stage 2 (full):** T ∈ {0.3, 0.7, 1.0}, n=400/pair (4,800 calls) — run regardless of stage-1 outcome unless the instrument is broken (parse rate >10%); stage-1 data are *not* pooled into stage 2 (fresh seed).
- **Acceptance criterion (same as the paper):** violation iff the 95% bootstrap CI on S lies above 2 **and** max no-signaling delta is small (pre-set threshold 0.10); if CI>2 with NS delta ≥0.10 → report as contextuality-with-signaling, not a Bell violation.

## Expected outcomes — all three informative, none predicted
(a) S ≤ 2: classical-consistent judgment statistics; human-study prior stays at the Aerts–Sozzo default. (b) CI > 2 with NS failure: marginal-selectivity structure (the Dzhafarov-style outcome) — directly informative, since humans in the same one-judge-sees-both-settings design face the identical threat; sharpens the human protocol. (c) CI > 2 with NS pass: non-classical structure in the model's judgment statistics — a novel observation warranting its own write-up.

## Reporting commitments
All stages and all temperatures reported, no pooling across prereg versions, raw JSONL logs kept in `runs/` and pushed to the repository, parse rates disclosed, model digest recorded. Results feed the journal/follow-on version and the human-study power analysis — not the CIDR submission (already under review).
