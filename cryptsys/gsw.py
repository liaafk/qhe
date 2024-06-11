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
    
    R = np.random.randint(2, size=(keys.m, keys.m), dtype=np.int64).astype(keys.datatype)
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