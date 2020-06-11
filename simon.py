#!/usr/bin/env python3

import numpy as np
from qiskit import *
from qiskit.quantum_info.operators import Operator
from qiskit import IBMQ


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
        self.backend = backend

        self.__construct()

    def __construct(self):
        """
        Construct program for Simon algorithm.
        """
        # Create a Quantum circuit with 2n qubits and n classical bits for measurement
        self.circuit = QuantumCircuit(2*self.n, self.n)

        # Apply Hadamard to operator qubits only
        for q in range(self.n):
            self.circuit.h(q)

        # Apply U_f to all qubits
        self.__apply_uf(list(range(2*self.n)))

        # Apply Hadamard to operator qubits only.
        for q in range(self.n):
            self.circuit.h(q)

        # Measure operator n qubits (ignoring helper bits)
        for q in range(self.n):
            self.circuit.measure(q, q)

    def run(self):
        """
        Run Simon algorithm.

        Returns
        -------
        result : int
            Return a single int, "s"

        """
        numshots = 4 * self.n
        job = execute(self.circuit, self.backend, shots=numshots)
        result = job.result()
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
