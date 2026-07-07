# S1 stored-data negative control — pre-registration
**Date frozen:** 2026-07-07 (before any evaluation run)
**Prediction (from the paper, Level-2 honesty):** stored-data correlations across two independently built stores are common-cause; therefore **S ≤ 2 on every benchmark pair**, including under adversarial setting search. The constructed entangled state reaches 2√2 ≈ 2.828 in the same pipeline (positive control).

## Data
Magellan/ditto entity-matching benchmarks (7 two-store pairs): Amazon-Google (primary; the paper's "two marketplaces, same products"), Walmart-Amazon, DBLP-ACM, DBLP-GoogleScholar, iTunes-Amazon, Fodors-Zagats, Beer.
Items = ground-truth **matched** record pairs (label = 1) only. Splits: rules/statistics derived on TRAIN only; evaluation on VALID∪TEST (held out). Fetch: `git clone --depth 1 --filter=blob:none --sparse https://github.com/megagonlabs/ditto && git sparse-checkout set data/er_magellan/Structured`.

## Measurement (locality by construction)
Each side's response for an item is a deterministic ±1 function of **that side's record and that side's setting only** (never the other side's record or setting). A "setting" = a binary categorisation rule from the mechanical library below; missing value → −1 (frozen convention).

Rule library per side (derived from own-side TRAIN split only, no hand-picking):
1. `num:<field>` — numeric field > own-side train median (price, year, ABV where present)
2. `len` — main text field length > own-side train median
3. `tok:<t>` — main text field contains token *t*, for the top-8 most frequent alphabetic tokens (length ≥ 4, stopwords removed) of own-side train titles

## Analyses (both reported, no cherry-picking)
- **A. Natural settings, same-items:** A = price/num rule, A′ = top-1 token rule (mirrored on side B). All four E(·,·) on the same held-out items; S = E(A,B)+E(A,B′)+E(A′,B)−E(A′,B′); 95% bootstrap CI (10,000 resamples over items).
- **B. Adversarial settings:** exhaustive search over all ordered rule pairs (A,A′)×(B,B′), A≠A′, B≠B′, maximizing |S| on TRAIN; the argmax is then evaluated once on held-out items with bootstrap CI. This is the strongest classical attempt to break the bound.
- **C. Between-subjects dry run:** held-out items randomly partitioned into four disjoint groups (seed 42), one per setting pair (mimics the human protocol); report S and the no-signaling deltas (max marginal shift of one side across the other side's settings) with bootstrap CIs.

## Positive controls / self-tests (must pass before real data is read)
1. Bell state + CHSH-optimal settings in the same S-computation code → S = 2.828 ± 0.001.
2. Synthetic classical items engineered for perfect rule correlations (E = +1,+1,+1,−1) → S = 2.000 exactly (bound attained, not exceeded → instrument is sharp).
3. Product state → S ≤ 2.

## Decision criterion (mirrors the paper's S1 criterion)
A dataset counts as a **violation** only if the 95% bootstrap CI on S lies entirely above 2 **and** the no-signaling deltas are consistent with 0 (analysis C). Anything else confirms the classical-sector prediction. All seven datasets are reported regardless of outcome.

## Framing commitment
Results are reported as a **verified classical-sector prediction** (the theory says stored/common-cause data cannot exceed 2; we verify the pipeline end-to-end and measure the margin), never as a "failed violation".
