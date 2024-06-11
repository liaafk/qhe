from qrisp import QuantumFloat, x, z, mcx
import numpy as np
import requests
import json

url = "http://localhost:5000/process"
headers = {'Content-Type': 'application/json'}

def bit_carry(j,k,carry):
    for i in range(len(carry.reg)):
        mcx([j.reg[i], k.reg[i]], carry.reg[i])
    carry.exp_shift(1)

def encrypt(j, k):
    a_list = []
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
    
    return a_list, c_list, d_list

def he_add(num1,num2):
    bits = max(num1.bit_length(), num2.bit_length())
    qnum1 = QuantumFloat(bits)
    qnum1[:] = num1
    qnum2 = QuantumFloat(bits)
    qnum2[:] = num2
    carry = QuantumFloat(bits)
    carry[:] = 0
    bit_carry(qnum1, qnum2, carry)
    a_list, c_list, d_list = encrypt(qnum1, qnum2)
    input_data = f"{qnum1.get_ev()}\n{qnum2.get_ev()}"
    response = requests.post(url, data=json.dumps(input_data), headers=headers)
    if response.status_code == 200:
        return decrypt(carry, response, a_list, c_list, d_list)


def read_result(response):
    match = int(float((response.json()['result'].split('\n'))[-1]))
    cres = QuantumFloat(match.bit_length())
    cres[:] = match
    return cres

def decrypt(carry, response, a_list, c_list, d_list):
    res = read_result(response)
    for i in range(len(res.reg)):
        if a_list[i] != c_list[i]:
            x(res.reg[i])
        if d_list[i] == 1:
            z(res.reg[i])

    return carry + res