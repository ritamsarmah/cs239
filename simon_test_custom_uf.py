
'''
Simon Circuit:

       _    ____    _
|0> --|H|--|    |--|H|
|0> --|H|--|    |--|H|
...    _   |    |   _
|0> --|H|--|    |--|H| (n* inputs)
           | Uf |
|0> -------|    |-----
|0> -------|    |-----
...        |    |
|0> -------|____|----- (n* helpers)

'''

'''
  Simon circuit components
  0. helper qubits of size n
  1. collective hadamard
  2. create and add the U_f circuit.
  3. hadamard & measure all the non-helpers.

'''

from pyquil import Program, get_qc
from pyquil.gates import *
from pyquil.api import local_forest_runtime
import numpy as np
from pyquil.quil import DefGate

'''
    Here, build a custom_uf (with gates) for sanity check.
    hand-compiled function: f:{x, y, z, a, b, c} -> x, y, z, f{x, y, z} + {a, b, c}
    fn:
    - c = 1 + z
    - b = y + z
    - a = 1 + yz

    this function has s = 100
'''
def add_custom_uf(p):
    # c = 1+z
    p += CNOT(2, 5)
    p += X(5)
    # b = y+z
    p += CNOT(1, 2)
    p += CNOT(2, 4)
    p += CNOT(1, 2)
    # a = 1+ yz
    p += CCNOT(1, 2, 3)
    p += X(3)

    return p

def build_simon(n):
    #first, we need to get correct size for "n"
    p = Program()
    if n > 8:
        raise ValueError("Too many qubits!")

    #add hadamards
    for i in range(n):
        p += H(i)

    #--------------#
    print("checkpt 1")
    print(p)

    #add custom U_f
    p = add_custom_uf(p)

    #--------------#
    print("checkpt 2")
    print(p)

    #add H
    for i in range(n):
        p += H(i)

    return p


#-------------------------------------#
n=3
p = build_simon(n)

print("\nfinal output...")
print(p)

#-------------------------------------#
## next: try to run the simon circuit.
with local_forest_runtime():
    qc = get_qc('9q-square-qvm')
    result = qc.run_and_measure(p, trials=10)
    for i in range(n):
        print(result[i])

'''
    - here are the results for the custom U_f.
    - as mentioned, "s = 100" for this problem. Thus, the results give correct equations.
q1: [0 0 0 0 0 0 0 0 0 0]
q2: [0 1 0 0 1 0 1 0 0 1]
q3: [0 0 1 0 0 1 1 0 1 0]
'''
