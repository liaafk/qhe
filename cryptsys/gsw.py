from sympy import isprime
from math import ceil, log2
from random import randint
import numpy as np
from scipy.linalg import block_diag
from qrisp import QuantumFloat, QuantumArray, semi_classic_matmul
import requests
import json

url = "http://localhost:5000/process"
headers = {'Content-Type': 'application/json'}

class GSWKeys:
    def __init__(self, k, q, t, A, B):
        self.n = k
        self.q = q
        self.l = ceil(log2(q))
        self.m = self.n * self.l
        self.SK = t
        #self.e = e
        self.A = A
        self.PK = B

def gen_prime(b):
    p = randint(2**(b-1), 2**b)
    while not isprime(p):
        p = randint(2**(b-1), 2**b)
    return p

def generateSophieGermainPrime(k):
    p = gen_prime(k-1)
    sp = 2*p + 1
    while not isprime(sp):
        p = gen_prime(k-1)
        sp = 2*p + 1
    return p

def keygen(k):
    q = generateSophieGermainPrime(k)
    l = ceil(log2(q))
    n = k
    m = n*l
    s = np.random.randint(q, size=n-1, dtype=np.int64)
    t = np.append(s, 1)
    t_q = QuantumArray(qtype = QuantumFloat(k+2), shape = (1, n))
    t_q.encode(np.reshape(t, (1,n)))
    #e = int(np.rint(np.random.normal(scale=1.0, size=m)))
    A = np.random.randint(q, size=(n-1, m), dtype=np.int64)
    B = np.vstack((-A, np.dot(s, A))) #% q
    B_q = QuantumArray(qtype = QuantumFloat(k+2, signed = True), shape = B.shape)
    B_q.encode(B)
    return GSWKeys(k, q, t_q, A, B_q)

def encrypt(keys, message):
    
    R = np.random.randint(2, size=(keys.m, keys.m), dtype=np.int64)
    g = 2**np.arange(keys.l)
    G = block_diag(*[g for null in range(keys.n)])
    return semi_classic_matmul(keys.PK, R) + message*G

def read_array(response):
    try:
        np_array = np.array(eval(response.json()['result']))
        return np_array
    except Exception as e:
        print(f"Error converting text to numpy array: {e}")

def decrypt(keys, response):

    # Retrieve the addition result from the result file
    cres = read_array(response)
    sk = keys.SK.most_likely()
    msg = np.dot(sk, cres) #% keys.q
    g = 2**np.arange(keys.l)
    G = block_diag(*[g for null in range(keys.n)])
    sg = np.dot(sk, G) #% keys.q
    div = int(float(np.rint((msg / sg))))
    modes = np.unique(div, return_counts=True)
    modes = sorted(zip(modes[0], modes[1]), key = lambda t: -t[1])
    best_num = 0
    best_dist = float('inf')
    for mu in modes:
        dist = (msg - mu*sg) #% keys.q
        dist = np.minimum(dist, keys.q - dist)
        dist = np.dot(dist, dist.T)
        if dist < best_dist:
            best_num = mu
            best_dist = dist
    
    return best_num

def he_add(num1, num2, keys):
    cx1 = encrypt(keys,num1)
    cx2 = encrypt(keys,num2)
    input_data = f"{cx1}\n{cx2}"
    response = requests.post(url, data=json.dumps(input_data), headers=headers)
    if response.status_code == 200:
        return decrypt(keys, response)
    
# Function to guess the secret key
def guess_secret_key(ciphertexts, plaintexts, q, n):
    l = ceil(log2(q))
    m = n * l

    for attempt in range(10):  # Number of attempts to guess the key
        print(attempt)
        s_guess = np.random.randint(q, size=n-1, dtype=np.int64)
        t_guess = np.append(s_guess, 1)
        #t_q_guess = QuantumArray(qtype=QuantumFloat(n+2), shape=(1, n))
        #t_q_guess.encode(np.reshape(t_guess, (1, n)))

        correct_guesses = 0
        for pt, ct in zip(plaintexts, ciphertexts):
            msg = np.dot(t_guess, ct)
            g = 2**np.arange(l)
            G = block_diag(*[g for _ in range(n)])
            sg = np.dot(t_guess, G)
            div = int(float(np.rint((msg / sg))))
            if div == pt:
                correct_guesses += 1

        if correct_guesses == len(plaintexts):
            return t_guess  # Return the guessed secret key if all guesses are correct

    return None

# Function to perform chosen plaintext attack and predict plaintext from ciphertext
def chosen_plaintext_attack_and_predict(keys, test_ciphertext):
    plaintexts = list(range(10))
    ciphertexts = []

    for pt in plaintexts:
        ct = encrypt(keys, pt)
        ciphertexts.append(ct)

    # Attempt to guess the secret key
    guessed_key = guess_secret_key(ciphertexts, plaintexts, keys.q, keys.n)
    if guessed_key is None:
        print("Failed to guess the secret key.")
        return None

    # Use the guessed key to decrypt the test ciphertext
    sk = guessed_key.most_likely()
    msg = np.dot(sk, test_ciphertext)
    g = 2**np.arange(keys.l)
    G = block_diag(*[g for _ in range(keys.n)])
    sg = np.dot(sk, G)
    div = int(float(np.rint((msg / sg))))
    modes = np.unique(div, return_counts=True)
    modes = sorted(zip(modes[0], modes[1]), key=lambda t: -t[1])
    best_num = 0
    best_dist = float('inf')
    for mu in modes:
        dist = np.minimum(msg - mu * sg, keys.q - (msg - mu * sg))
        dist = np.dot(dist, dist.T)
        if dist < best_dist:
            best_num = mu
            best_dist = dist

    return best_num