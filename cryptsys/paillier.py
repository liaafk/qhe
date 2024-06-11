import random
from Crypto.Util.number import GCD, getPrime, inverse
from qrisp import QuantumFloat
import requests
import json

url = "http://localhost:5000/process"
headers = {'Content-Type': 'application/json'}

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

def encrypt(m1, m2, n, g):
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

def he_add(num1, num2, n, g, lamb, mu):
    qnum1 = QuantumFloat(num1.bit_length())
    qnum1[:] = num1
    qnum2 = QuantumFloat(num2.bit_length())
    qnum2[:] = num2
    c1, c2 = encrypt(qnum1, qnum2, n, g)
    input_data = f"{c1}\n{c2}"
    response = requests.post(url, data=json.dumps(input_data), headers=headers)
    if response.status_code == 200:
        return decrypt(n, response, lamb, mu)

def decrypt(n, response, lamb, mu):
    res = int((response.json()['result'].split('\n'))[0])
    temp = pow(res, lamb, n**2)
    temp = (temp - 1) // n
    m = (temp * mu) % n

    return m