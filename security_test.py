from cryptsys import chen, gsw, paillier, qotp
import numpy as np
from qrisp import QuantumFloat

def main():
    print('Security test: Chen')
    success = 0
    psi, r, s_inv, p_inv = chen.keygen(4)
    
    # Encrypt a test plaintext
    for i in np.random.randint(100, size=10):
        bin_x1 = bin(i)[2:].zfill(4)
        bin_x2 = bin(0)[2:].zfill(4)  # Encrypting with zero for simplicity
        arr_bin_x1 = [int(x) for x in bin_x1]
        arr_bin_x2 = [int(x) for x in bin_x2]
        test_ciphertext1, _ = chen.encrypt(arr_bin_x1, arr_bin_x2, psi)
    
        # Perform the chosen plaintext attack and predict the plaintext
        guess = chen.chosen_plaintext_attack_and_predict(test_ciphertext1)
        if i == guess:
            success = success + 1
    print(f'Success rate: {success/10}')

    print('Security test: GSW')
    success = 0
    keys = gsw.keygen(3)
    print('keys generated')
    for i in np.random.randint(100, size=10):
        test_ciphertext = gsw.encrypt(keys, i)
        guess = gsw.chosen_plaintext_attack_and_predict(keys, test_ciphertext)
        if i == guess:
            success = success + 1
    print(f'Success rate: {success/10}')

    print('Security test: QOTP')
    success = 0
    for i in np.random.randint(100, size=10):
        q_i = QuantumFloat(i.bit_length())
        q_i[:] = i
        q_0 = QuantumFloat(i.bit_length())
        q_0[:] = 0
        _, _, _ = qotp.encrypt(q_i, q_0)
        guess = qotp.chosen_plaintext_attack_and_predict(keys, q_i)
        if i == guess:
            success = success + 1
    print(f'Success rate: {success/10}')

if __name__ == "__main__":
    main()