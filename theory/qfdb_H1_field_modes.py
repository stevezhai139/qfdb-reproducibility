import numpy as np, math

# ============ H1: a schema is a FIELD (modes + second quantization), not a fixed system ============

# ---- Part 1: bosonic mode = a MULTI-VALUED attribute (occupation 0,1,2,... = bag cardinality) ----
N = 8                                              # truncate occupation
a = np.diag(np.sqrt(np.arange(1, N+1)), 1)         # annihilation  = DELETE
ad = a.conj().T                                    # creation      = INSERT
num = ad @ a                                        # number operator = CARDINALITY of the attribute
ccr = a @ ad - ad @ a
print("Part 1  bosonic mode = multi-valued attribute   (cardinality = occupation number)")
print(f"   [a, a^dag] diag (bulk) = {np.round(np.diag(ccr)[:5].real,3)}   (=1 away from truncation)")
print(f"   number-operator spectrum (possible cardinalities) = {np.round(np.diag(num).real[:6],3)}")
vac = np.zeros(N+1); vac[0] = 1
one = ad @ vac;  one = one/np.linalg.norm(one)
print(f"   INSERT (a^dag) on vacuum -> cardinality {int(round((one.conj()@num@one).real))}")

# ---- Part 2: fermionic mode = a SINGLE-VALUED attribute (0/1, Pauli = at most one value) ----
af  = np.array([[0,1],[0,0]], float)               # fermionic annihilation
afd = af.conj().T
car = af @ afd + afd @ af
print("\nPart 2  fermionic mode = single-valued attribute (Pauli exclusion = at most one value)")
print(f"   {{a, a^dag}} = I ? -> diag {np.round(np.diag(car),3)}")
print(f"   INSERT twice (a^dag a^dag) = zero matrix? -> {np.allclose(afd@afd,0)}  (cannot hold two values)")

# ---- Part 3: schema evolution = ADD a mode -> Fock factorization, history preserved ----
print("\nPart 3  ADD COLUMN = add a mode -> H (x) H_new ; existing datapoints untouched")
psi_old = np.zeros(N+1); psi_old[2] = 1.0          # old attribute holds cardinality 2
card_before = (psi_old.conj()@num@psi_old).real
new_vac = np.zeros(2); new_vac[0] = 1              # new attribute starts empty (vacuum)
psi_ext = np.kron(psi_old, new_vac)
num_ext = np.kron(num, np.eye(2))
card_after = (psi_ext.conj()@num_ext@psi_ext).real
print(f"   old-attribute cardinality  before add = {card_before:.0f}   after add = {card_after:.0f}   (preserved)")
print( "   => the field grows a mode; prior excitations sit in the untouched factor (Fock invariance)")

# ---- Part 4: the FIELD payoff a fixed system cannot even REPRESENT: indefinite cardinality ----
print("\nPart 4  superposition of CARDINALITIES (coherent state) -- field, not fixed system")
alpha = 1.0
coh = np.array([np.exp(-abs(alpha)**2/2)*alpha**n/np.sqrt(math.factorial(n)) for n in range(N+1)])
coh = coh/np.linalg.norm(coh)
mean_n = (coh.conj()@num@coh).real
var_n  = (coh.conj()@(num@num)@coh).real - mean_n**2
print(f"   coherent state |a=1>: <cardinality> = {mean_n:.3f}, variance = {var_n:.3f}")
print(f"   amplitudes over cardinality 0..4   = {np.round(coh[:5].real,3)}")
print( "   => a relation in superposition of HAVING 0,1,2,... tuples.")
print( "      A fixed-dimension 'system' cannot even represent a variable/superposed row-count.")
