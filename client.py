from cryptsys import chen, gsw, paillier, qotp
from qrisp import QuantumFloat, QuantumModulus

def main():
  
    # Get two integers from user
    num1 = int(input("Enter first number: "))
    num2 = int(input("Enter second number: "))
    cs = input("Enter preferred cryptosystem: ")

    if cs == "chen":
        psi, r, s_inv, p_inv = chen.keygen(4)
        result = chen.he_add(num1, num2, psi, r, s_inv, p_inv)
    
    if cs == "qotp":
        bits = max(num1.bit_length(), num2.bit_length())
        qnum1 = QuantumFloat(bits)
        qnum1[:] = num1
        qnum2 = QuantumFloat(bits)
        qnum2[:] = num2
        carry = QuantumFloat(bits)
        carry[:] = 0
        qotp.bit_carry(qnum1, qnum2, carry)
        a_list, c_list, d_list = qotp.encrypt(qnum1, qnum2)
        result = qotp.decrypt(carry, a_list, c_list, d_list)

    if cs == "paillier":
        (n, g), (lamb, mu) = paillier.keygen()
        qnum1 = QuantumFloat(num1.bit_length())
        qnum1[:] = num1
        qnum2 = QuantumFloat(num2.bit_length())
        qnum2[:] = num2
        c1, c2 = paillier.encrypt(qnum1, qnum2, n, g)
        result = paillier.decrypt(n, lamb, mu)
    
    if cs == "gsw":
        keys = gsw.keygen(3)
        cx1 = gsw.encrypt(keys,num1)
        cx2 = gsw.encrypt(keys,num2)
        gsw.write_file(cx1, cx2)
        result = gsw.decrypt(keys)
    
    print(f"Sum of encrypted numbers: {result}")

if __name__ == "__main__":
    main()