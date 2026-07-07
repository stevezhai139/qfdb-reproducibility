# S1 — Bell/CHSH elicitation toolkit

The S1 human-subjects study (a CHSH test of inter-schema correspondence judgments)
is **pending IRB approval**. **No human-subject data is included here.**

These are the **pre-registered analysis instruments**, validated on synthetic and
held-out data:

- `chsh_analysis.py` — CHSH S + 95% bootstrap CI (decision rule: CI-lower > 2)
- `qfdb_s1_power.py` — power analysis (respondents/condition to detect S>2)
- `qfdb_s1_nosignaling.py` — no-signaling / marginal-law check
- `qfdb_s1_tally.py` — convert a survey export → responses.csv
- `PROTOCOL_google_form.md` — the exact elicitation instrument (items, settings, randomization)

Demo (synthetic):
```bash
python3 chsh_analysis.py --demo quantum     # violates (S>2)
python3 chsh_analysis.py --demo classical   # does not
python3 qfdb_s1_nosignaling.py --demo signaling
python3 qfdb_s1_power.py
```
