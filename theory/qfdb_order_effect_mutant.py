import numpy as np

# ===== Steer container as a qubit =====
# A-basis = the attribute STORED at plane t: |vacc>, |~vacc>
ket_vacc  = np.array([1.0, 0.0])
ket_nvacc = np.array([0.0, 1.0])

# At plane t the steer is UNVACCINATED, and this is a CERTAIN stored fact:
#   state = |~vacc>
psi0 = ket_nvacc.copy()
rho0 = np.outer(psi0, psi0)

def proj(v):
    v = v / np.linalg.norm(v)
    return np.outer(v, v.conj())

PA_vacc  = proj(ket_vacc)    # query A = "vaccinated@t?"  -> yes
PA_nvacc = proj(ket_nvacc)   #                              -> no

def B_projectors(theta):
    # query B = "susceptible to the MUTANT strain, evaluated @t?"
    # the mutant did not exist at t -> B is a later-defined concept,
    # modeled as a basis ROTATED by theta from A (theta = how 'off-axis' the new concept is)
    bplus  = np.array([ np.cos(theta/2), np.sin(theta/2)])  # susceptible (yes)
    bminus = np.array([-np.sin(theta/2), np.cos(theta/2)])  # not (no)
    return proj(bplus), proj(bminus)

def p(rho, P):                       # Born probability
    return float(np.real(np.trace(rho @ P)))

def post(rho, P):                    # state after a 'yes' to projector P
    r = P @ rho @ P
    tr = np.real(np.trace(r))
    return r/tr if tr > 1e-12 else r

print("Steer @ plane t is UNVACCINATED with certainty (stored fact).")
print("Q_A = 'vaccinated@t?'   Q_B = 'susceptible-to-mutant@t?' (concept didn't exist at t)\n")
print(f"{'theta(deg)':>10} {'P(~vacc) Afirst':>16} {'P(~vacc) Bfirst':>16} {'order effect':>13} {'QQ':>8}")
for deg in [0, 30, 45, 60, 90]:
    th = np.deg2rad(deg)
    PB_s, PB_ns = B_projectors(th)

    # --- A asked first (read the stored fact) ---
    pA_no_first = p(rho0, PA_nvacc)              # = 1, it's certain

    # --- B asked first, THEN A ---
    pBs, pBns = p(rho0, PB_s), p(rho0, PB_ns)
    rBs, rBns = post(rho0, PB_s), post(rho0, PB_ns)
    pA_no_after_B = pBs*p(rBs, PA_nvacc) + pBns*p(rBns, PA_nvacc)

    order_eff = pA_no_first - pA_no_after_B      # how much asking B first disturbs the vaccine record

    # --- QQ equality (Wang-Busemeyer fingerprint) ---
    P_AB_Ayes_Bno = p(rho0,PA_vacc)*(p(post(rho0,PA_vacc),PB_ns) if p(rho0,PA_vacc)>1e-12 else 0.0)
    P_AB_Ano_Byes = p(rho0,PA_nvacc)*p(post(rho0,PA_nvacc),PB_s)
    P_BA_Bno_Ayes = pBns*p(rBns, PA_vacc)
    P_BA_Byes_Ano = pBs *p(rBs,  PA_nvacc)
    QQ = (P_AB_Ayes_Bno + P_AB_Ano_Byes) - (P_BA_Bno_Ayes + P_BA_Byes_Ano)

    print(f"{deg:>10} {pA_no_first:>16.3f} {pA_no_after_B:>16.3f} {order_eff:>13.3f} {QQ:>8.3f}")

print("\nReading:")
print(" theta=0  : B is just a relabel of the vaccine axis -> NO order effect -> CLASSICAL (substitutable)")
print(" theta>0  : asking the mutant-question FIRST turns the certain '~vacc' into uncertainty")
print("            -> order effect != 0, while QQ stays 0 (quantum fingerprint) -> NOT substitutable")

# ===== classical disturbance model tuned to the SAME order effect (paper, Face A) =====
# B-first fully disturbs A (matches P(~vacc)=0.500 at theta=90); mutant prevalence r free.
print("\nClassical disturbance model tuned to the same order effect (theta=90):")
print("   (A=yes := '~vacc' certain; B ~ Bernoulli(r); asking B first redraws A fair)")
for r in (0.6, 0.7, 0.8):
    AyBy, AnBn = 1.0*r, 0.0*(1-r)      # A first: A=yes w.p. 1, B independent
    ByAy, BnAn = r*0.5, (1-r)*0.5      # B first: A redrawn 50/50 after disturbance
    qq = (AyBy+AnBn) - (ByAy+BnAn)
    print(f"   prevalence r={r:.1f}  ->  QQ = {qq:+.2f}   (order effect matched at 0.500)")
print("   => classical QQ=0 only at the fine-tuned base rate r=0.5;")
print("      the quantum model above gives QQ=0 at EVERY theta, parameter-free.")
