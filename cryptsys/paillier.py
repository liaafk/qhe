import random

from Crypto.Util.number import GCD, getPrime, inverse
from qrisp import QuantumFloat, q_divmod, qRange

def keygen():
    p = getPrime(8)
    q = getPrime(8)
    assert GCD(p * q, (p - 1) * (q - 1)) == 1, "GCD != 1"

    n = p * q
    phi = (p - 1) * (q - 1)
    lamb = phi
    g = n + 1
    mu = inverse(phi, n)

    return (n, g), (lamb, mu)

def q_pow(x, y, z):
    exp = 1
    while (y > 0).most_likely():
        exp = exp * x
        y = y - 1
    return exp%z

def encrypt(m, n, g):
    while True:
        r = random.randint(1, n - 1)
        if GCD(n, r) == 1:
            break
    c = (q_pow(g, m, n**2) * pow(r, n, n**2)) % (n**2)

    return c

def decrypt(c, n, g, lamb, mu):
    temp = pow(c, lamb, n**2)
    temp = (temp - 1) // n
    m = (temp * mu) % n

    return m