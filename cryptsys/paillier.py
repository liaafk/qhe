import random
from Crypto.Util.number import GCD, getPrime, inverse
from qrisp import QuantumFloat

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

def encrypt(m1, m2, n, g, cx_file='cx_data.txt', cx_ready_file='cx_ready.txt'):
    while True:
        r = random.randint(1, n - 1)
        if GCD(n, r) == 1:
            break
    c1 = (q_pow(g, m1, n**2) * pow(r, n, n**2)) % (n**2)
    while True:
        r = random.randint(1, n - 1)
        if GCD(n, r) == 1:
            break
    c2 = (q_pow(g, m2, n**2) * pow(r, n, n**2)) % (n**2)

    return c1, c2

def decrypt(n, response, lamb, mu):
    res = int((response.json()['result'].split('\n'))[0])
    temp = pow(res, lamb, n**2)
    temp = (temp - 1) // n
    m = (temp * mu) % n

    return m