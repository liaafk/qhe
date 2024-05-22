from qrisp import QuantumFloat, QuantumSession, x, z, cx, mcx
import numpy as np
import math

def bit_carry(j,k,carry):
    for i in range(len(carry.reg)):
        mcx([j.reg[i], k.reg[i]], carry.reg[i])
    carry.exp_shift(1)

def encrypt(j, k):
    a_list = []
    b_list = []
    c_list = []
    d_list = []

    for q1,q2 in zip(j.reg, k.reg):
        a,b,c,d = np.random.randint(2, size = 4)
        a_list.append(a)
        b_list.append(b)
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
        
    return j, k, a_list, b_list, c_list, d_list

def add(j,k):
    return cx(j,k)[1]

def decrypt(carry, res, a_list, c_list, d_list):
    for i in range(len(res.reg)):
        if a_list[i] != c_list[i]:
            x(res.reg[i])
        if d_list[i] == 1:
            z(res.reg[i])
    return carry + res