from qrisp import QuantumArray, QuantumFloat, QuantumModulus, dot, q_divmod
import numpy as np
import math
import os
import time
import re

def hamming_code_gen(N, k):
    n = 2**k-k-1
    if (N != n+k):
        print("N = " + N + ", n = " + n + " doesn't match Hamming code scheme. Adjusting N.\n")
        N = n+k
    # create g & r; for g see https://michaeldipperstein.github.io/hamming.html, for r see Chen '23 (might be source of error)
    data_bits = np.identity(n)
    comb = math.comb(n,k)
    parity_bits = np.ones((n,comb), int)
    np.fill_diagonal(parity_bits, 0)
    parity_bits = parity_bits[:, np.random.permutation(parity_bits.shape[1])]
    g = np.zeros(shape=(n, N))
    empty_g_indices = list(range(0,N))
    for i in range(n):
        g_index = np.random.choice(empty_g_indices)
        g[:,g_index] = data_bits[:,i]
        empty_g_indices.remove(g_index)
    g_copy = g.copy()
    r = g_copy.T
    for i in range(N-n):
        g_index = np.random.choice(empty_g_indices)
        g[:,g_index] = parity_bits[:,i]
        empty_g_indices.remove(g_index)
    # create s; a scrambler matrix of 1s and 0s which is invertible
    s = np.round(np.random.rand(n, n))
    while ((np.linalg.det(s))**2 != 1):
        #np.linalg.det(s) == 0
           #(np.all([s[i][j].is_integer() for i in range(s.shape[0]) for j in range(s.shape[1])]))):
        s = np.round(np.random.rand(n, n))
    # create p; permutation matrix
    p = np.identity(N)
    p = p[:, np.random.permutation(p.shape[1])]
    return s,g,p,r

def keygen(n):
    k = math.floor(math.log2(n))+1
    N = n + k
    
    s_prime, g_prime, p_prime, r_prime = hamming_code_gen(N,k)
    
    s = QuantumArray(qtype = QuantumModulus(2), shape = (n,n))
    s.encode(np.reshape(s_prime, (n,n)))
    
    s_inv = QuantumArray(qtype = QuantumModulus(2), shape = (n,n))
    s_inv.encode(np.linalg.inv(np.reshape(s_prime, (n,n)))%2)
    
    g = QuantumArray(qtype = QuantumModulus(2), shape = (n,N))
    g.encode(np.reshape(g_prime, (n,N)))
    
    p = QuantumArray(qtype = QuantumModulus(2), shape = (N,N))
    p.encode(np.reshape(p_prime, (N,N)))
    
    p_inv = QuantumArray(qtype = QuantumModulus(2), shape = (N,N))
    p_inv.encode(np.linalg.inv(np.reshape(p_prime, (N,N))))
    
    r = QuantumArray(qtype = QuantumModulus(2), shape = (N,n))
    r.encode(np.reshape(r_prime, (N,n)))
    
    psi = s@g@p
    
    return psi, r, s_inv, p_inv

def encrypt(arr_bin_x1, arr_bin_x2, psi):
    
    q_bin_x1 = QuantumArray(qtype= QuantumModulus(2), shape = (1,4))
    q_bin_x1.encode(np.reshape(np.array(arr_bin_x1), (1,4)))
    
    q_bin_x2 = QuantumArray(qtype = QuantumModulus(2), shape = (1,4))
    q_bin_x2.encode(np.reshape(np.array(arr_bin_x2), (1,4)))
    
    cx1 = q_bin_x1@psi
    cx2 = q_bin_x2@psi

    return cx1, cx2

def decrypt(cres, bin_carry, r, s_inv, p_inv):
    
    decres = cres@p_inv@r@s_inv
    decres_bin = ''.join([str(x) for x in decres.most_likely()[0]])
    bin_carry = bin_carry + '0'
    return int(decres_bin,2) + int(bin_carry,2)

def read_array(file):
    pattern = r"\((.*?)\)"
    with open(file, 'r') as file:
        content = ''.join(file.read().split())
        match = re.findall(pattern, content)[0]
    try:
        np_array = np.array(eval(match))
    except Exception as e:
        print(f"Error converting text to numpy array: {e}")
    cres = QuantumArray(qtype=QuantumModulus(2), shape= (1,7))
    cres[:] = np.reshape(np_array, (1,7))
    return cres

def he_add(x1,x2, psi, r, s_inv, p_inv, cx_file='cx_data.txt', result_file='result_data.txt', cx_ready_file='cx_ready.txt', result_ready_file='result_ready.txt'):
    result = 0
    if x1 >= 2**4 or x2 >= 2**4:
        x11 = max(0, x1-2**4+1)
        x12 = x1-x11
        x21 = max(0, x2-2**4+1)
        x22 = x2-x21
        result = result + he_add(x11, x21, psi, r, s_inv, p_inv) + he_add(x12, x22, psi, r, s_inv, p_inv)        
    else:
    #turn input into binary
        bin_x1 = bin(x1)[2:].zfill(4)
        bin_x2 = bin(x2)[2:].zfill(4)
        bin_carry = format(x1 & x2, '08b')
        arr_bin_x1 = [int(x) for x in bin_x1]
        arr_bin_x2 = [int(x) for x in bin_x2]
        cx1, cx2 = encrypt(arr_bin_x1, arr_bin_x2, psi)
        #cres = cx1 + cx2
        with open(cx_file, 'a') as f:
            print(cx1, file=f)
            print(cx2, file=f)

        # Create a flag to notify the external program
        with open(cx_ready_file, 'w') as f:
            f.write('ready')
    
        # Wait for the result ready flag
        while not os.path.exists(result_ready_file):
            time.sleep(1)  # Check every second

        # Retrieve the addition result from the result file
        cres = read_array(result_file)
        result = result + decrypt(cres, bin_carry, r, s_inv, p_inv)

        os.remove(result_file)
        os.remove(result_ready_file)
    
    return result