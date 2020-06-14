#!/usr/bin/env python3

import numpy as np
from qiskit import *
from qiskit.quantum_info.operators import Operator
from qiskit import IBMQ


'''
* to create manual trivial / nontrivial circuits, just replace the U_f code with
    a function like the below:

def ntriv_4(circuit):
    """
    the simon function is:
        s = 0b1001
        f(x) = min(x, x^s)

    the U-F circuit is: {x1,x2,x3,x4,h1,h2,h3,h4} --> {x1,x2,x3,x4,f1+h1,f2+h2,f3+h3,f4+h4}
        f1 = 0
        f2 = x2
        f3 = x3
        f4 = x1+x4
    """
    circuit.barrier()
    #f2
    circuit.cx(1, 5)
    #f3
    circuit.cx(2, 6)
    #f4
    circuit.cx(0, 3)
    circuit.cx(3, 7)
    circuit.cx(0, 3)
    #circuit.draw('mpl')
    #barrier 2, for drawing...
    circuit.barrier()

def triv_4(circuit):
    """
    in this trivial example, the secret s=0.
    so f(x) = x.
    Thus, U_f = {x1,x2,x3,x4,h1,h2,h3,h4} --> {x1,x2,x3,x4,x1+h1,x2+h2,x3+h3,x4+h3}
    """
    circuit.barrier()
    circuit.cx(0,4)
    circuit.cx(1,5)
    circuit.cx(2,6)
    circuit.cx(3,7)
    circuit.barrier()
'''

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

#-----------------------------------------#
# Functions for classical piece of Simon
#-----------------------------------------#

'''
    check all equations with the target and make sure they're satisfied
    Inputs:
        eqns: list of equations of form {0,1}^n
        tgt: eqn of form {0,1}^n
'''
def simon_check_eqns(eqns, tgt):
    for e in eqns:
        int_and = (e&tgt)
        str_and = "{0:b}".format(int_and)
        sum_and = sum([int(i) for i in str_and])
        #print(f"{e}, {tgt}, {int_and}, {str_and}, {sum_and}")
        if sum_and%2 != 0:
            return False
    return True

# eqns is a nparray with all equations (each equation is just an int.)
def simon_eqns_solver(eqns, n):
    tgts = list(range(2**n))
    for t in tgts[1:]:
        if simon_check_eqns(eqns, t):
            return t
    return 0

#-----------------------------------------#
# Class for implementing (quantum) Simon
#-----------------------------------------#

class Simon:
    """
    Simon algorithm.

    Parameters
    ----------
    n : int
        The length of bit string input to f.
    f : lambda
        A function that take as input an int in range [0, 2^n]
        representing binary string {0,1}^n and outputs int {0,1}^n.
        Also, f satisfies the condition:
            for all x, y, [f(x) = f(y)] iff [(x+y) in {0^n, s}], for some bitstring s

    Examples
    ----------
    ```
    >>> f = lambda x: [0b000, 0b001, 0b010, 0b011, 0b100, 0b101, 0b110, 0b111][x]
    >>> Simon(3, f).run()
    110
    ```
    """

    def __init__(self, n, f, provider):
        self.n = n
        self.f = f
        self.uf = None
        self.provider = provider

        self.__construct()

    def __construct(self):
        """
        Construct program for Simon algorithm.
        """
        total_qubits = 2 * self.n

        # Load backend based on number of qubits needed. burlington has 5, melbourne has 15
        self.backend = self.provider.get_backend('ibmq_burlington' if total_qubits <= 5 else 'ibmq_16_melbourne')

        # Create a Quantum circuit with 2n qubits and n classical bits for measurement
        self.circuit = QuantumCircuit(total_qubits, self.n)

        # Apply Hadamard to operator qubits only
        for q in range(self.n):
            self.circuit.h(q)

        # Apply U_f to all qubits
        self.__apply_uf(list(range(total_qubits)))

        # Apply Hadamard to operator qubits only.
        for q in range(self.n):
            self.circuit.h(q)

        # Measure operator n qubits (ignoring helper bits)
        for q in range(self.n):
            self.circuit.measure(q, q)

        numshots = 4 * self.n
        transpiled = transpile(self.circuit, self.backend)
        self.qobj = assemble(transpiled, self.backend, shots=numshots, optimization_level=3)

    def run(self):
        """
        Run Simon algorithm.

        Returns
        -------
        result : int
            Return a single int, "s"

        """
        job = self.backend.run(self.qobj)

        try:
            result = job.result()
        except qiskit.providers.ibmq.job.exceptions.IBMQJobFailureError:
            print(job.error_message())
            return -1, 0

        counts = result.get_counts(self.circuit)

        #reverse all outputted bitstrings.
        rev_keys = [''.join(reversed(e)) for e in list(counts.keys())]
        equations = [int(e, 2) for e in rev_keys]
        #utilize classical (brute force) functionality to deduce s.
        s = simon_eqns_solver(equations, self.n)

        ## DEBUG
        #print(counts)
        #print('-----')
        #print(equations)
        #print('-----')
        #print(s)

        # return output of classical eqn solver: "s".
        return s, result.time_taken

    def __apply_uf(self, qubits):
        """
        Define U_f gate (if not defined) that encodes oracle function f and applies it to qubits.

        Parameters
        -------
        qubits : [int]
            Qubits to apply U_f to.

        """
        uf_size = 2 ** (self.n *2)
        f_size = 2 ** self.n
        if self.uf is None:
            # Initializes U_f as a 2^(2n) by 2^(2n) matrix of zeros
            U_f = np.zeros((uf_size,) * 2, dtype=int)

            # Apply definition of U_f = |x>|b + f(x)> to construct matrix
            for x in range(f_size):
                for b in range(f_size):
                    row = (x << self.n) ^ b
                    col = (x << self.n) ^ (self.f(x) ^ b)
                    U_f[row][col] = 1

            self.uf = Operator(U_f)

        self.circuit.append(self.uf, qubits[::-1])
