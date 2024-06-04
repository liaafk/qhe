from cryptsys import chen, gsw, paillier, qotp

def main():
  
    # Get two integers from user
    num1 = int(input("Enter first number: "))
    num2 = int(input("Enter second number: "))
    cs = input("Enter preferred cryptosystem: ")

    if cs == "chen":
        psi, r, s_inv, p_inv = chen.keygen(4)
        result = chen.he_add(num1, num2, psi, r, s_inv, p_inv)
    
    if cs == "qotp":
        result = qotp.he_add(num1, num2)

    if cs == "paillier":
        (n, g), (lamb, mu) = paillier.keygen()
        result = paillier.he_add(num1, num2, n, g, lamb, mu)
    
    if cs == "gsw":
        keys = gsw.keygen(3)
        result = gsw.he_add(num1, num2, keys)
    
    else:
        print(f"Not a supported cryptosystem. Try again with chen, gsw, paillier, or qotp.")
        return -1
    
    print(f"Sum of encrypted numbers: {result}")

if __name__ == "__main__":
    main()