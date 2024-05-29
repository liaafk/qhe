import time
import matplotlib.pyplot as plt
import random
from qrisp import QuantumFloat
from cryptsys import chen, gsw, paillier, qotp

def chen_add(num1, num2):
    psi, r, s_inv, p_inv = chen.keygen(4)
    return chen.he_add(num1,num2, psi, r, s_inv, p_inv)
    
def gsw_add(num1, num2):
    keys = gsw.keygen(2)
    ca = gsw.encrypt(keys, num1)
    cb = gsw.encrypt(keys, num2)
    ca_cb = ca.most_likely() + cb.most_likely()
    return gsw.decrypt(keys, ca_cb)

def qotp_add(num1, num2, i):
    add_1 = QuantumFloat(i)
    add_2 = QuantumFloat(i)
    carry = QuantumFloat(i)
    add_1[:] = num1
    add_2[:] = num2
    carry[:] = 0
    qotp.bit_carry(add_1,add_2,carry)
    enc_add_1, enc_add_2, key_a, key_b, key_c, key_d = qotp.encrypt(add_1, add_2)
    enc_result = qotp.add(enc_add_1, enc_add_2)
    return qotp.decrypt(carry, enc_result, key_a, key_c, key_d)

def paillier_add(num1, num2, i):
    (n, g), (lamb, mu) = paillier.keygen()
    m1 = QuantumFloat(i)
    m1[:] = num1
    m2 = QuantumFloat(i)
    m2[:] =num2

    c1 = paillier.encrypt(m1, n, g)
    c2 = paillier.encrypt(m2, n, g)

    c3 = c1 * c2
    return paillier.decrypt(c3, n, g, lamb, mu)
    
def run_and_time(algorithm, num1, num2, i):
    if algorithm == 'chen':
        start = time.time()
        print(chen_add(num1, num2))
        end = time.time()
    elif algorithm == 'gsw':
        start = time.time()
        print(gsw_add(num1, num2))
        end = time.time()
    elif algorithm == 'qotp':
        start = time.time()
        print(qotp_add(num1, num2, i))
        end = time.time()
    elif algorithm == 'paillier':
        start = time.time()
        print(paillier_add(num1, num2, i))
        end = time.time()
    return end-start

def generate_input_pairs(num_iterations):
    list1, list2 = [], []
    for i in range(1, num_iterations + 1):
        # Calculate range boundaries
        lower_bound = 2**i - 1
        upper_bound = 2**i
    
        # Generate random integers within the range
        num1 = random.randint(lower_bound, upper_bound - 1)
        num2 = random.randint(lower_bound, upper_bound - 1)
    
        # Append numbers to respective lists
        list1.append(num1)
        list2.append(num2)
    return list1, list2
  

def main():
    # Define a range of input sizes to test
    nums1, nums2 = generate_input_pairs(1)

    # Initialize lists to store runtimes for each algorithm
    chen_times = []
    gsw_times = []
    qotp_times = []
    paillier_times = []

  # Measure and store runtimes for each input size
    for i in range(1, len(nums1)+1):
        chen_times.append(run_and_time('chen', nums1[i-1], nums2[i-1], i))
        gsw_times.append(run_and_time('gsw', nums1[i-1], nums2[i-1], i))
        qotp_times.append(run_and_time('qotp', nums1[i-1], nums2[i-1], i))
        paillier_times.append(run_and_time('paillier', nums1[i-1], nums2[i-1], i))

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(range(1,len(nums1)+1), chen_times, label='Chen')
    plt.plot(range(1,len(nums1)+1), gsw_times, label='GSW')
    plt.plot(range(1,len(nums1)+1), qotp_times, label='Quantum OTP')
    plt.plot(range(1,len(nums1)+1), paillier_times, label='Paillier')

    # Add labels and title
    plt.xlabel("Input Size")
    plt.ylabel("Runtime (seconds)")
    plt.title("Comparison of Algorithm Runtimes")

    # Add legend
    plt.legend()

    # Show the plot
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()