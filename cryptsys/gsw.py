from sympy import isprime
from math import floor, ceil, log2
from random import randint
import numpy as np
from scipy.linalg import block_diag
from scipy.stats import mode
from qrisp import QuantumFloat, QuantumArray, semi_classic_matmul

class GSWKeys:
    def __init__(self, k, q, t, A, B, datatype):
        self.n = k
        self.q = q
        self.l = ceil(log2(q))
        self.m = self.n * self.l
        self.SK = t
        #self.e = e
        self.A = A
        self.PK = B 
        self.datatype = datatype

def gen_prime(b):
    """ Returns a prime p with b bits """
    p = randint(2**(b-1), 2**b)
    while not isprime(p):
        p = randint(2**(b-1), 2**b)
    return p

def generateSophieGermainPrime(k):
    """ Return a Sophie Germain prime p with k bits """
    p = gen_prime(k-1)
    sp = 2*p + 1
    while not isprime(sp):
        p = gen_prime(k-1)
        sp = 2*p + 1
    return p

def generateSafePrime(k):
    """ Return a safe prime p with k bits """
    p = gen_prime(k-1)
    sp = 2*p + 1
    while not isprime(sp):
        p = gen_prime(k-1)
        sp = 2*p + 1
    return sp

def keygen(k):
    if k > 29:
        datatype = 'object'
    else:
        datatype = np.int64
    # pick a random Sophie Germain prime [q] in the range 2**.2**k
    # and get its bit length [l]
    q = generateSophieGermainPrime(k)
    l = ceil(log2(q))
    print(" "*12 + "q = %d" % q)
    #
    # the gadget matrix [G] is an n×m matrix (n rows, m = n×l columns)
    #
    # the secret vector [s] is an (n-1)-dimensional vector,
    # the secret key [t] is -s 1, an n-dimensional vector‖
    #
    # the error vector [e] is an m-dimensional vector
    #
    # the matrix [A] is an (n-1)×m matrix (n-1 rows, m = n×l columns)
    #
    # the public key [B] is ( A )
    # ( sA+e )
    #
    n = k
    m = n*l
    s = np.random.randint(q, size=n-1, dtype=np.int64).astype(datatype)
    t = np.append(s, 1)
    t_q = QuantumArray(qtype = QuantumFloat(k+2), shape = (1, n)) #QuantumArray(qtype = QuantumModulus(q), shape = (1, n))
    t_q.encode(np.reshape(t, (1,n)))
    #e = np.rint(np.random.normal(scale=1.0, size=m)).astype(int).astype(datatype)
    A = np.random.randint(q, size=(n-1, m), dtype=np.int64).astype(datatype)
    B = np.vstack((-A, np.dot(s, A))) #% q
    B_q = QuantumArray(qtype = QuantumFloat(k+2, signed = True), shape = B.shape)
    B_q.encode(B)
    return GSWKeys(k, q, t_q, A, B_q, datatype)

def buildGadget(l, n):
    # the secret vector [s] is an (n-1)-dimensional vector,
    # the secret key [t] is -s 1, an n-dimensional vector‖
    #
    # the error vector [e] is an m-dimensional vector
    #
    # the matrix [A] is an (n-1)×m matrix (n-1 rows, m = n×l columns)
    #
    # the public key [B] is ( A ) which is an n×m matrix
    # ( sA+e )
    #
    g = 2**np.arange(l)
    G = block_diag(*[g for null in range(n)])
    return G

def encrypt(keys, message):
    #
    # the gadget matrix [G] is an n×m matrix (n rows, m = n×l columns)
    #
    # the matrix R is an m×m matrix (n×l rows, n×l columns)
    #
    # the ciphertext is (n×m) (m×m) *> an n×m matrix⋅
    #
    R = np.random.randint(2, size=(keys.m, keys.m), dtype=np.int64).astype(keys.datatype)
    #R_q = QuantumArray(qtype = QuantumModulus(keys.q), shape=(keys.m, keys.m))
    #R_q.encode(R)
    G = buildGadget(keys.l, keys.n)
    return semi_classic_matmul(keys.PK, R) + message*G

def decrypt(keys, ciphertext):
    sk = keys.SK.most_likely()
    msg = np.dot(sk, ciphertext) #% keys.q
    g = buildGadget(keys.l, keys.n)
    sg = np.dot(sk, g) #% keys.q
    div = np.rint((msg / sg).astype(float)).astype(np.int64)
    modes = np.unique(div, return_counts=True)
    modes = sorted(zip(modes[0], modes[1]), key = lambda t: -t[1])
    best_num = 0
    best_dist = float('inf')
    for mu,count in modes:
        dist = (msg - mu*sg) #% keys.q
        dist = np.minimum(dist, keys.q - dist)
        # dist = np.linalg.norm(dist)
        dist = np.dot(dist, dist.T)
        if dist < best_dist:
            best_num = mu
            best_dist = dist
    return best_num