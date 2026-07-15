#!/usr/bin/env python3
"""
QFDB S1 — LLM-respondent pilot harness (Tier 2; SUPPLEMENT, not a substitute
for the pre-registered human study).

What this measures: non-classical structure (or its absence) in the
*model's* correspondence-judgment statistics. It cannot certify anything
about human cognition or about the schema-field itself.

Design (mirrors the paper's S1 elicitation):
  - one API call = one synthetic respondent (fresh context, no memory)
  - each respondent sees ONE setting pair (between-subjects) and ONE item,
    gives a forced-choice category from each side  -> coded +/-1, +/-1
  - neutral task wording: a product-categorisation task; no mention of
    physics, experiments, or the four-setting structure
  - violation is claimed only if the 95% bootstrap CI on S clears 2 AND the
    no-signaling (marginal-law) check passes -- same criterion as the paper

Endpoints: any OpenAI-compatible chat API (OpenAI, vLLM, ollama, llama.cpp).
  env: OPENAI_BASE_URL (default https://api.openai.com/v1), OPENAI_API_KEY
Reproducibility: prefer an open-weights model; log everything to JSONL.

Usage:
  python3 llm_respondent_harness.py --dry-run                 # self-test, no API
  python3 llm_respondent_harness.py --items items.jsonl \
      --model llama3.1:8b --temperature 0.7 --n-per-pair 100
  python3 llm_respondent_harness.py --analyse runs/log_*.jsonl # re-analyse logs

items.jsonl: {"id": ..., "text": "<product title/description>"} per line
(e.g., exported from the Amazon-Google benchmark; see make_items_example()).
"""
import argparse, glob, json, os, random, re, sys, time, urllib.request

# ---------- settings (EDIT + pre-register BEFORE any real run) ----------
SETTINGS = {
    "A":  ("Electronics", "Furniture"),    # store 1, way of categorising 1
    "A'": ("Gift", "Tool"),                # store 1, way of categorising 2
    "B":  ("Gadget", "Decor"),             # store 2, way of categorising 1
    "B'": ("Toy", "Hardware"),             # store 2, way of categorising 2
}
PAIRS = [("A", "B"), ("A", "B'"), ("A'", "B"), ("A'", "B'")]

PROMPT = """You are helping two online stores file the same product into their catalogues.

Product: {item}

Store 1 files every product under exactly one of: {l1} or {l2}.
Store 2 files every product under exactly one of: {r1} or {r2}.

Which category does this product belong to in each store? Answer with only:
Store 1: <category>
Store 2: <category>"""

# ---------- CHSH machinery (same criterion as the paper / Tier 1) ----------
def chsh(counts):
    """counts[pair] = list of (a,b) with a,b in {+1,-1}."""
    import numpy as np
    E = {}
    for p, obs in counts.items():
        arr = np.array(obs, float)
        E[p] = float(np.mean(arr[:, 0] * arr[:, 1])) if len(arr) else 0.0
    S = E[("A", "B")] + E[("A", "B'")] + E[("A'", "B")] - E[("A'", "B'")]
    # bootstrap CI over respondents within each pair
    rng = np.random.default_rng(42)
    Ss = []
    for _ in range(5000):
        s = 0.0
        for p, sign in ((("A", "B"), 1), (("A", "B'"), 1), (("A'", "B"), 1), (("A'", "B'"), -1)):
            arr = np.array(counts[p], float)
            idx = rng.integers(0, len(arr), len(arr))
            s += sign * float(np.mean(arr[idx, 0] * arr[idx, 1]))
        Ss.append(s)
    lo, hi = float(np.percentile(Ss, 2.5)), float(np.percentile(Ss, 97.5))
    # no-signaling: side-1 marginal under a given setting must not depend on
    # the distant setting (and symmetrically)
    ns = []
    for a_set in ("A", "A'"):
        m = [float(np.mean([o[0] for o in counts[(a_set, b)]])) for b in ("B", "B'")]
        ns.append(abs(m[0] - m[1]))
    for b_set in ("B", "B'"):
        m = [float(np.mean([o[1] for o in counts[(a, b_set)]])) for a in ("A", "A'")]
        ns.append(abs(m[0] - m[1]))
    return dict(E={f"{p[0]},{p[1]}": v for p, v in E.items()}, S=S, ci=[lo, hi],
                max_nosignaling_delta=max(ns))

# ---------- respondent backends ----------
def call_llm(prompt, model, temperature, base_url, api_key, timeout=60):
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps({"model": model, "temperature": temperature,
                         "messages": [{"role": "user", "content": prompt}],
                         "max_tokens": 40}).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)["choices"][0]["message"]["content"]

def dry_respondent(item, l_opts, r_opts, rng):
    """Self-test backend: classical stochastic judge (shared latent = item
    hash + noise). Must yield S <= 2 -- validates the analysis path."""
    lam = (hash(item) % 1000) / 1000.0
    pick = lambda opts, bias: opts[0] if rng.random() < 0.5 + 0.4 * (lam - 0.5) + bias else opts[1]
    return f"Store 1: {pick(l_opts, 0.05)}\nStore 2: {pick(r_opts, -0.05)}"

def code_reply(reply, l_opts, r_opts):
    """Map free-text reply -> (+/-1, +/-1); None if unparseable (logged, excluded)."""
    def side(opts, line_tag):
        m = re.search(line_tag + r"\s*:?\s*(.+)", reply, flags=re.I)
        seg = m.group(1) if m else reply
        hit = [o for o in opts if re.search(r"\b" + re.escape(o) + r"\b", seg, re.I)]
        if len(hit) != 1:
            hit = [o for o in opts if re.search(r"\b" + re.escape(o) + r"\b", reply, re.I)]
        return (1 if hit[0] == opts[0] else -1) if len(hit) == 1 else None
    a = side(l_opts, r"store\s*1"); b = side(r_opts, r"store\s*2")
    return (a, b) if (a is not None and b is not None) else None

# ---------- run ----------
def run(args):
    items = []
    if args.items:
        with open(args.items) as f:
            items = [json.loads(l)["text"] for l in f if l.strip()]
    if not items:
        items = make_items_example()
        print(f"[warn] no --items given; using {len(items)} built-in example items")
    rng = random.Random(args.seed)
    os.makedirs("runs", exist_ok=True)
    log_path = f"runs/log_{args.model.replace('/', '_').replace(':', '_')}_T{args.temperature}_{int(time.time())}.jsonl"
    counts = {p: [] for p in PAIRS}
    n_bad = 0
    with open(log_path, "w") as log:
        for pair in PAIRS:
            for i in range(args.n_per_pair):
                item = rng.choice(items)
                l_opts, r_opts = SETTINGS[pair[0]], SETTINGS[pair[1]]
                if rng.random() < 0.5:  # counterbalance option order
                    l_opts = l_opts[::-1]
                if rng.random() < 0.5:
                    r_opts = r_opts[::-1]
                prompt = PROMPT.format(item=item, l1=l_opts[0], l2=l_opts[1],
                                       r1=r_opts[0], r2=r_opts[1])
                if args.dry_run:
                    reply = dry_respondent(item, SETTINGS[pair[0]], SETTINGS[pair[1]], rng)
                else:
                    reply = call_llm(prompt, args.model, args.temperature,
                                     os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                                     os.environ.get("OPENAI_API_KEY", ""))
                coded = code_reply(reply, SETTINGS[pair[0]], SETTINGS[pair[1]])
                log.write(json.dumps(dict(pair=list(pair), item=item, prompt=prompt,
                                          reply=reply, coded=coded, model=args.model,
                                          temperature=args.temperature)) + "\n")
                if coded is None:
                    n_bad += 1
                    continue
                counts[pair].append(coded)
    res = chsh(counts)
    res.update(model=args.model, temperature=args.temperature,
               n_per_pair=args.n_per_pair, unparseable=n_bad,
               n_coded=sum(len(v) for v in counts.values()), log=log_path)
    print(json.dumps(res, indent=1))
    verdict(res)
    return res

def analyse(paths):
    counts = {p: [] for p in PAIRS}
    meta = {}
    for path in paths:
        for line in open(path):
            d = json.loads(line)
            if d.get("coded"):
                counts[tuple(d["pair"])].append(d["coded"])
            meta = dict(model=d.get("model"), temperature=d.get("temperature"))
    res = chsh(counts); res.update(meta)
    res["n_coded"] = sum(len(v) for v in counts.values())
    print(json.dumps(res, indent=1)); verdict(res)

def verdict(res):
    lo = res["ci"][0]; ns = res["max_nosignaling_delta"]
    if lo > 2 and ns < 0.10:
        print("[verdict] CI above 2 AND no-signaling passes -> non-classical structure "
              "in the MODEL'S judgment statistics (not humans, not the schema-field).")
    elif lo > 2:
        print("[verdict] CI above 2 but no-signaling FAILS -> signaling/contextual, "
              "the weaker reading; do not report as a Bell violation.")
    else:
        print("[verdict] S consistent with the classical bound (<= 2).")
    # parse-rate guard (prereg: >10% at smoke test = fix before stage 1)
    bad = res.get("unparseable", 0)
    n_ok = res.get("n_coded")
    if n_ok:
        rate = bad / max(1, bad + n_ok)
        flag = "  << FIX PARSING BEFORE REAL RUN (prereg threshold 10%)" if rate > 0.10 else ""
        print(f"[parse] unparseable = {bad}/{bad + n_ok} = {100*rate:.1f}%{flag}")
    # human-study sample-size implication (prereg formula, alpha=.05 one-sided, power .8)
    S = res["S"]; margin = S - 2.0
    if margin > 0.05:
        import math
        n_pair = math.ceil((2 * 2.487 / margin) ** 2)
        print(f"[human-n] if humans matched S={S:.2f}: ~{n_pair}/setting-pair "
              f"(~{4*n_pair} respondents total)")
    else:
        print("[human-n] S <= 2: no violation-based estimate; human-study prior "
              "stays at the Aerts-Sozzo default (S=2.42 -> ~124/pair, ~496 total)")

def make_items_example():
    return ["cordless drill with lithium battery", "walnut coffee table",
            "wireless earbuds with charging case", "desk lamp with usb port",
            "robot vacuum cleaner", "leather office chair", "smart doorbell camera",
            "espresso machine", "bookshelf speaker pair", "standing desk converter"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--items"); ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--n-per-pair", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--analyse", nargs="*")
    a = ap.parse_args()
    if a.analyse:
        analyse([p for g in a.analyse for p in glob.glob(g)])
    else:
        run(a)
