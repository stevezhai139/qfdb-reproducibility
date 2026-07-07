import numpy as np, itertools

Z = np.array([[1,0],[0,-1]], float); X = np.array([[0,1],[1,0]], float)
def M(t): return np.cos(t)*Z + np.sin(t)*X          # a +-1 query at "angle" t
def kron(*o):
    r=np.array([[1.0]])
    for m in o: r=np.kron(r,m)
    return r

# CHSH settings (two facets per schema): A,A' on schema-1 ; B,B' on schema-2
a, ap, b, bp = 0.0, np.pi/2, np.pi/4, -np.pi/4
def E(rho,tA,tB): return float(np.real(np.trace(rho@kron(M(tA),M(tB)))))
def CHSH(rho):    return E(rho,a,b)+E(rho,a,bp)+E(rho,ap,b)-E(rho,ap,bp)

def negativity(rho):                                # D3 measure; >0 => entangled
    r=rho.reshape(2,2,2,2).transpose(0,3,2,1).reshape(4,4)
    ev=np.linalg.eigvalsh(r); return float(sum(abs(e) for e in ev if e<0))

# ---------- Part 1: COMMON CAUSE (shared domain / embeddings = the classical story) ----------
det_max=0.0
for a0,a1,b0,b1 in itertools.product([-1,1],repeat=4):
    det_max=max(det_max, abs(a0*b0+a0*b1+a1*b0-a1*b1))
rng=np.random.default_rng(0); mix_max=0.0
for _ in range(200000):
    a0,a1,b0,b1=rng.choice([-1,1],4)
    mix_max=max(mix_max, abs(a0*b0+a0*b1+a1*b0-a1*b1))

# ---------- Part 2: JOINT PREPARATION (schema integration = 'schema Bell state') ----------
phi=np.array([1,0,0,1],float)/np.sqrt(2)            # (|s1,s1> + |s2,s2>)/sqrt2
rho_bell=np.outer(phi,phi)

print("=== H5  two schemas: classical correlation  vs  genuine entanglement ===\n")
print("Part 1  COMMON CAUSE  (two schemas describe one domain via shared embeddings)")
print(f"   max|S| deterministic shared-latent = {det_max:.3f}")
print(f"   max|S| 200k random mixtures        = {mix_max:.3f}")
print( "   => classical schema correlation CAPPED at 2  (this is the Uprety / FK / embedding regime)\n")

print("Part 2  JOINT PREPARATION (schema integration as a non-factorizable state)")
print(f"   CHSH S    = {CHSH(rho_bell):.3f}   (Tsirelson bound 2.828)")
print(f"   negativity= {negativity(rho_bell):.3f}  (>0 => entangled)")
print( "   => S>2  => NOT reproducible by ANY common-cause model => genuine entanglement\n")

print("Part 3  Werner sweep   p = 'how non-separable the integration prepares the pair'")
print(f"   {'p':>6} {'negativity':>11} {'CHSH S':>8}   verdict")
for p in [1.0,0.85,0.7071,0.6,0.5,1/3,0.2]:
    rho=p*rho_bell+(1-p)*np.eye(4)/4
    S=CHSH(rho); neg=negativity(rho)
    v=("VIOLATES (entanglement earned)" if S>2.0001 else
       "entangled but no violation"      if neg>1e-6 else
       "separable / classical")
    print(f"   {p:>6.3f} {neg:>11.3f} {S:>8.3f}   {v}")
print("\nDiscriminator: negativity>0 is necessary (formal entanglement);")
print("S>2 is the DEBATE-FREE witness. Note the gap 1/3<p<0.707: entangled yet S<=2.")
