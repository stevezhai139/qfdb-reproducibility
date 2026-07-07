#!/usr/bin/env python3
"""
QFDB S1 -- tally a Google Forms response export into responses.csv.

Forms -> Responses -> Download .csv gives one row per respondent. Each respondent
answered exactly ONE condition question, so exactly one of the 16 English pairing
strings appears in their row; each maps to a unique (condition, cell). We match by
SUBSTRING, so bilingual options ("Electronics + Gadget / ..ไทย..") still parse as long
as the English part is kept. Robust to column naming/order.

USE:  python3 qfdb_s1_tally.py forms_export.csv      # writes responses.csv
Then: python3 chsh_analysis.py responses.csv ; python3 qfdb_s1_nosignaling.py responses.csv
"""
import sys, csv, re
CONDS=["AB","ABp","ApB","ApBp"]; CELL={"pp":0,"pm":1,"mp":2,"mm":3}
OPT={  # English pairing -> (condition, cell). Electronics/Gift=+1,Furniture/Tool=-1 ; Gadget/Toy=+1,Decor/Hardware=-1
 "electronics + gadget":("AB","pp"),"electronics + decor":("AB","pm"),"furniture + gadget":("AB","mp"),"furniture + decor":("AB","mm"),
 "electronics + toy":("ABp","pp"),"electronics + hardware":("ABp","pm"),"furniture + toy":("ABp","mp"),"furniture + hardware":("ABp","mm"),
 "gift + gadget":("ApB","pp"),"gift + decor":("ApB","pm"),"tool + gadget":("ApB","mp"),"tool + decor":("ApB","mm"),
 "gift + toy":("ApBp","pp"),"gift + hardware":("ApBp","pm"),"tool + toy":("ApBp","mp"),"tool + hardware":("ApBp","mm"),
}
def norm(s): return re.sub(r"\s+"," ",s.strip().lower())
def find_pair(row):
    for v in row:
        nv=norm(v)
        for key,val in OPT.items():
            if key in nv: return val      # substring => bilingual-safe
    return None
def main():
    if len(sys.argv)<2: print(__doc__); sys.exit(0)
    counts={c:[0,0,0,0] for c in CONDS}; n=0; skip=0
    with open(sys.argv[1], newline="", encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            hit=find_pair(row)
            if hit: counts[hit[0]][CELL[hit[1]]]+=1; n+=1
            else: skip+=1
    with open("responses.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["condition","n_pp","n_pm","n_mp","n_mm"])
        for c in CONDS: w.writerow([c]+counts[c])
    print(f"  parsed {n} responses ({skip} rows with no pairing = header/non-consent/blank)")
    for c in CONDS: print(f"    {c:4s}: {counts[c]}  N={sum(counts[c])}")
    print("  -> wrote responses.csv")
if __name__=="__main__": main()
