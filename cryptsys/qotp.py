from qrisp import QuantumFloat, QuantumSession, x, z, cx, mcx
import numpy as np
import math
import os
import time
import re

def bit_carry(j,k,carry):
    for i in range(len(carry.reg)):
        mcx([j.reg[i], k.reg[i]], carry.reg[i])
    carry.exp_shift(1)

def encrypt(j, k, cx_file='cx_data.txt', cx_ready_file='cx_ready.txt'):
    a_list = []
    b_list = []
    c_list = []
    d_list = []

    for q1,q2 in zip(j.reg, k.reg):
        a,b,c,d = np.random.randint(2, size = 4)
        a_list.append(a)
        c_list.append(c)
        d_list.append(d)
        if(a == 1):
            x(q1)
        if(b == 1):
            z(q1)
        if(c == 1):
            x(q2)
        if(d == 1):
            z(q2)
    
    with open(cx_file, 'a') as f:
        print(j, file=f)
        print(k, file=f)
        
    # Create a flag to notify the external program
    with open(cx_ready_file, 'w') as f:
        f.write('ready')
    return a_list, c_list, d_list

def add(j,k):
    return 

def read_result(file):
    with open(file, 'r') as file:
        pattern = r"\{([^:]+):"
        for line in file:
            pass
        match = int(re.findall(pattern, line)[0])
    cres = QuantumFloat(match.bit_length())
    cres[:] = match

    return cres

def decrypt(carry, a_list, c_list, d_list, result_file='result_data.txt', result_ready_file='result_ready.txt'):
    # Wait for the result ready flag
    while not os.path.exists(result_ready_file):
        time.sleep(1)  # Check every second

    # Retrieve the addition result from the result file
    res = read_result(result_file)
    for i in range(len(res.reg)):
        if a_list[i] != c_list[i]:
            x(res.reg[i])
        if d_list[i] == 1:
            z(res.reg[i])
    print(res)
    print(carry)
    os.remove(result_file)
    os.remove(result_ready_file)

    return carry + res