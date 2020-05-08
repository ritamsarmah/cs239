import numpy as np
from pyquil import Program, get_qc
from pyquil.gates import *
from pyquil.api import local_forest_runtime
from pyquil.quil import DefGate

def deutsch_jozsa(f, n):
    p = Program()

    # initialize first n qubits to 0, helper qubit to 1
    zeros = [0]*n
    zeros.append(1)

    # apply H to all qubits
    for q in range(len(zeros)):
        p += H(q)

    # create Uf gate
    uf_def, Uf = Uf_gate(f, n)

    # apply Uf to all qubits
    p += uf_def
    p += Uf(*range(n+1))

    # apply H to all but helper qubit
    for q in range(len(zeros)-1):
        p += H(q)

    with local_forest_runtime():
        qvm = get_qc(f'{n+1}q-qvm')
        results = qvm.run_and_measure(p, trials=10)
        print(results)

def Uf_gate(f, n):
    size = 2**(n+1)
    uf = np.zeros((size, size), dtype=int)

    for x in range (2**n):
        fx = f(x)
        x0 = bin(x) + '0'
        x1 = bin(x) + '1'
        
        if fx == 0:
            h0 = x0
            h1 = x1
        else:
            h0 = x1
            h1 = x0

        uf[int(h0,2)][int(x0,2)] = 1
        uf[int(h1,2)][int(x1,2)] = 1

    uf_def = DefGate("Uf", uf)
    Uf = uf_def.get_constructor()
    return uf_def, Uf

def fa(bin):
    return 1

deutsch_jozsa(fa, 1)
