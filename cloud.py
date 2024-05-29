import numpy as np
import os
import re
import time
from qrisp import QuantumArray, QuantumModulus, cx, QuantumFloat

def read_arrays(file):
    result_array = []
    pattern = r"\((.*?)\)"
    with open(file, 'r') as file:
        content = ''.join(file.read().split())

    matches = re.findall(pattern, content)
    for match in matches:
        try:
            np_array = np.array(eval(match))
            result_array.append(np_array)
            dimensions = np_array.shape
        except Exception as e:
            print(f"Error converting text to numpy array: {e}")
        
    if dimensions == (1, 7):
        cx1 = QuantumArray(qtype=QuantumModulus(2), shape=dimensions)
        cx1[:] = np.reshape(np.array(list(result_array[0]), dtype=int), dimensions)
        cx2 = QuantumArray(qtype=QuantumModulus(2), shape=dimensions)
        cx2[:] = np.reshape(np.array(list(result_array[1]), dtype=int), dimensions)
        return cx1, cx2
    else:
        return result_array[0], result_array[1]

"""def read_arrays(file, shape, qtype=QuantumModulus(2)):
    result_array = []
    with open(file, 'r') as file:
        for line in file:
            # Find all occurrences of [ and ]
            brackets = [m.start() for m in re.finditer(r'\[|\]', line)]
            
            if len(brackets) >= 3 and brackets[-1] > brackets[1]:
                # Extract content between second [ and first ]
                content = line[brackets[1]+1:brackets[-2]]
            
            result_array.append(''.join(content.split(', ')))
    print(result_array)
    cx1 = QuantumArray(qtype=qtype, shape=shape)
    cx1[:] = np.reshape(np.array(list(result_array[0]), dtype=int), (1,7))
    cx2 = QuantumArray(qtype=qtype, shape=shape)
    cx2[:] = np.reshape(np.array(list(result_array[1]), dtype=int), (1,7))
    return cx1, cx2"""

def read_qfs(file):
    matches = []
    with open(file, 'r') as file:
        for line in file:
            pattern = r"\{([^:]+):"
            matches.append(int(re.findall(pattern, line)[0]))
    return matches[0], matches[1]

def read_ints(file):
    matches = []
    with open(file, 'r') as file:
        for line in file:
            matches.append(int(line))
    return matches[0], matches[1]

def write_array(file, q_array):
    with open(file, 'w') as f:
        if isinstance(q_array, QuantumArray): 
            print(q_array, file=f)
        else:
            f.write(np.array2string(q_array, separator=',', formatter={'all': lambda x: str(x)}))

def write_qfs(file, cx1, cx2):
    bits = max(cx1.bit_length(), cx2.bit_length())
    qcx1 = QuantumFloat(bits)
    qcx1[:] = cx1
    qcx2 = QuantumFloat(bits)
    qcx2[:] = cx2
    with open(file, 'a') as f:
        print(cx(qcx1,qcx2)[1], file=f)

def write_ints(file, cx1, cx2):
    with open(file, 'a') as f:
        print(cx1*cx2, file=f)

def main():
    input_file = 'cx_data.txt'
    output_file = 'result_data.txt'
    cx_ready_file = 'cx_ready.txt'
    result_ready_file = 'result_ready.txt'
    shape = (1, 7)  # Adjust shape as necessary for your specific use case

    # Wait for the cx_ready flag
    while not os.path.exists(cx_ready_file):
        time.sleep(1)  # Check every second

    with open(input_file, 'r') as file:
        first_line = file.readline().strip()
        if first_line.startswith("{OutcomeArray"):
            cx1, cx2 = read_arrays(input_file)
            write_array(output_file, cx1 + cx2)
        elif first_line.startswith("{"):
            cx1, cx2 = read_qfs(input_file)
            write_qfs(output_file, cx1, cx2)
        else:
            cx1, cx2 = read_ints(input_file)
            write_ints(output_file, cx1, cx2)
    # Create a flag to notify the main program
    with open(result_ready_file, 'w') as f:
        f.write('ready')
    
    os.remove(input_file)
    os.remove(cx_ready_file)

if __name__ == "__main__":
    main()