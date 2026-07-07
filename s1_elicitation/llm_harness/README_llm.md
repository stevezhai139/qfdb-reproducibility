# LLM-respondent S1 pilot (Tier 2) — supplement, not a substitute

**What a result means here:** a CHSH violation (CI > 2 + no-signaling pass) certifies
non-classical structure in the **model's** correspondence-judgment statistics — nothing
about human cognition, and nothing about the schema-field itself (Level-2). The
pre-registered human study remains the decisive test; this pilot (1) exercises the full
S1 instrument end-to-end, (2) supplies an effect-size prior for the human power
analysis, (3) is a novel observation either way.

## Run
```bash
# self-test without any API (classical simulated judge; must give S <= 2):
python3 llm_respondent_harness.py --dry-run

# real run — local open-weights model via ollama/vLLM (preferred for reproducibility):
export OPENAI_BASE_URL=http://localhost:11434/v1  OPENAI_API_KEY=none
python3 llm_respondent_harness.py --model llama3.1:8b --temperature 0.7 --n-per-pair 100

# temperature sensitivity (report all, pre-register the grid):
for T in 0.3 0.7 1.0; do python3 llm_respondent_harness.py --model llama3.1:8b --temperature $T; done

# items from the real benchmark (recommended; export titles from Amazon-Google):
python3 llm_respondent_harness.py --items items_amazon_google.jsonl ...
```

## Method discipline (why each rule exists)
- **One call = one respondent** (fresh context) → between-subjects, no memory carryover.
- **One setting pair per call** → the model never sees the four-setting CHSH structure.
- **Neutral wording** (catalogue filing task; no physics vocabulary) → mitigates
  role-play/contamination from quantum-cognition literature in training data.
- **Option order counterbalanced** per call → removes position bias from marginals.
- **Temperature > 0** and a reported grid → response variability is a knob, so show
  sensitivity instead of picking one value.
- **Open-weights model as primary** (+ optional API model as secondary) → API drift
  breaks reproducibility; log model tag + full replies in `runs/*.jsonl`.
- **Same acceptance criterion as the paper:** violation iff 95% CI on S clears 2 AND
  the no-signaling deltas pass; if marginals shift with the distant setting, report as
  contextuality-with-signaling, not a Bell violation.
- **Pre-register SETTINGS + prompt + grid** (edit the header of the script, commit,
  hash) before the first real run — same ritual as `../s1_stored/PREREGISTRATION.md`.

## Caveats to carry into any write-up
Measures the model, not people; prompt-sensitive (report the exact prompt); model
version pinned; unparseable replies logged and excluded (report the rate); a null
result does not falsify the human hypothesis, and a violation does not confirm it.

*Note: `runs/log_gpt-4o-mini_T0.7_*.jsonl` in this folder is a `--dry-run` self-test artifact (simulated judge; the model tag is the unused default), not real model data.*
