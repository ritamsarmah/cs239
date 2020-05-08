
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
    this I could very easily see becoming hard to mannage. Maybe create sparse or something?
'''
def build_uf(n, fn_io):
    U = np.zeros((2**(2*n), 2**(2*n)))
    for x, fx in enumerate(fn_io):
        for b in range(2**n):
            row = (x << n) ^ b
            fout = b ^ fx
            col = (x << n) ^ fout
            U[row][col] = 1
            
    U_defn = DefGate("U-F", U)
    return U_defn

def build_simon(n, fn_io):
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

    #add U_f
    Uf_defn = build_uf(n, fn_io)
    p += Uf_defn
    Uf_cst = Uf_defn.get_constructor()
    p += Uf_cst(*[i for i in range(2*n)])

    #--------------#
    print("checkpt 2")
    print(p)

    #add H
    for i in range(n):
        p += H(i)

    return p
    

'''
    define a function f: (s = "101")
    
    101 / 000 (0) -> 110 (6)
    100 / 001 (1) -> 111 (7)
    111 / 010 (2) -> 000 (8)
    110 / 011 (3) -> 001 (9)
    100 (4) -> 111 (7)
    101 (5) -> 110 (6)
    110 (6) -> 001 (1)
    111 (7) -> 000 (0)
'''
def create_simon_f3():
    f = []
    for ind in range(4):
        f.append((ind + 6) % 8)
    f.extend([7, 6, 1, 0])
    print(f)
    return f


#-------------------------------------#
## main: build the simon circuit, and print it.
f3 = create_simon_f3()
print(f3)

n=3
p = build_simon(n, f3)

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
    - for "create_simon_f3", I got a timeout. Also the matrix was 64x64.
'''
