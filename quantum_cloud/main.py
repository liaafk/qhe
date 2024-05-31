import numpy as np
import re
from qrisp import QuantumArray, QuantumModulus, cx, QuantumFloat
from flask import Flask, request, jsonify

app = Flask(__name__)

def read_arrays(data):
    result_array = []
    pattern = r"\((.*?)\)"
    content = ''.join(data.split('\n'))
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

def read_qfs(data):
    matches = []
    for line in data.split('\n'):
        pattern = r"\{([^:]+):"
        matches.append(int(re.findall(pattern, line)[0]))
    return matches[0], matches[1]

def read_ints(data):
    matches = []
    for line in data.split('\n'):
        matches.append(int(float(line)))
    return matches[0], matches[1]

@app.route('/process', methods=['POST'])
def process_data():
    data = request.json
    app.logger.info(f'Received data: {data}')
    first_line = data.split('\n', 1)[0].strip()
    if first_line.startswith("{OutcomeArray"):
        cx1, cx2 = read_arrays(data)
        result_array = cx1 + cx2
        result = np.array2string(result_array, separator=',', formatter={'all': lambda x: str(x)})
    elif first_line.startswith("([["):
        cx1, cx2 = read_arrays(data)
        res = f"{(cx1+cx2).most_likely()}"
        result = f"{'('+','.join(res.split())+')'}"
    elif first_line.endswith(".0"):
        cx1, cx2 = read_ints(data)
        bits = max(cx1.bit_length(), cx2.bit_length())
        qcx1 = QuantumFloat(bits)
        qcx1[:] = cx1
        qcx2 = QuantumFloat(bits)
        qcx2[:] = cx2
        result = f"{(cx(qcx1,qcx2)[1]).get_ev()}" 
    else:
        cx1, cx2 = read_ints(data)
        result = f"{cx1 * cx2}"

    return jsonify({'result': result})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
