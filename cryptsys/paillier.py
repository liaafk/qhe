import random
import re
import os
import time
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

    with open(cx_file, 'a') as f:
        print(c1, file=f)
        print(c2, file=f)
        
    # Create a flag to notify the external program
    with open(cx_ready_file, 'w') as f:
        f.write('ready')

    return c1, c2

def read_result(file):
    with open(file, 'r') as file:
        for line in file:
            match = int(line)
            break
    return match

def decrypt(n, lamb, mu, result_file='result_data.txt', result_ready_file='result_ready.txt'):
    # Wait for the result ready flag
    while not os.path.exists(result_ready_file):
        time.sleep(1)  # Check every second

    # Retrieve the addition result from the result file
    res = read_result(result_file)
    temp = pow(res, lamb, n**2)
    temp = (temp - 1) // n
    m = (temp * mu) % n

    os.remove(result_file)
    os.remove(result_ready_file)

    return m