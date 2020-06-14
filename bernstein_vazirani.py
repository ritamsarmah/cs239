#!/usr/bin/env python3

import numpy as np
from qiskit import *
from qiskit.quantum_info.operators import Operator
from qiskit import IBMQ, transpile, assemble

'''
Additional code for manually compiled U_f tests:

def bv_obtain_gates(a):
    n = len(a)
    gates = []
    for i, v in enumerate(a):
        if v=='1':
            #if the ith number in 'a' is 1, then create cnot gate from qb i-->helper.
            gates.append((i, n))
    return n, gates

def build_circuit(circuit, a, b):
    n, gates = bv_obtain_gates(a)
    circuit.barrier()
    for g in gates:
        circuit.cx(g[0], g[1])
    if int(b)==1:
        circuit.x(n)
    circuit.barrier()

## example of a trivial U_f circuit:
def triv_4(circuit):
    a, b = '0011', '1'
    build_circuit(circuit, a, b)

## example of a nontrivial circuit:
def ntriv_4(circuit):
    a, b = '1111', '1'
    build_circuit(circuit, a, b)
'''

class BernsteinVazirani:
    """
    Bernstein Vazirani algorithm.

    Parameters
    ----------
    n : int
        The length of bit string input to f.
    f : lambda
        A function that take as input an int in range [0, 2^n]
        representing binary string {0,1}^n and outputs int {0,1}.
        * note: f should have the form y = a*x+b, where...
            - a is a bitstring of length n
            - b is a single bit

    Return Value
    ----------
    (a, b)

    Examples
    ----------
    ```
    >>> BernsteinVazirani(2, lambda x: [1, 0, 1, 0][x]).run()
    (0b01, 1)
    >>> BernsteinVazirani(2, lambda x: 1).run()
    (0,1)
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
        Construct program for B-V algorithm.
        """
        total_qubits = self.n + 1

        # Load backend based on number of qubits needed. burlington has 5, melbourne has 15
        self.backend = self.provider.get_backend(
            'ibmq_burlington' if total_qubits <= 5 else 'ibmq_16_melbourne')

        # Create a Quantum circuit with n+1 qubits and n classical bits for measurement
        self.circuit = QuantumCircuit(total_qubits, self.n)

        # Set helper bit (at index n) to 1
        self.circuit.x(self.n)

        # Apply Hadamard to all qubits
        for q in range(total_qubits):
            self.circuit.h(q)

        # Apply U_f to all qubits
        self.__apply_uf(list(range(total_qubits)))

        # Apply Hadamard to first n qubits (ignoring helper bit)
        for q in range(self.n):
            self.circuit.h(q)

        # Measure first n qubits (ignoring helper bit)
        for q in range(self.n):
            self.circuit.measure(q, q)

        transpiled = transpile(self.circuit, self.backend)
        self.qobj = assemble(transpiled, self.backend, shots=1024, optimization_level=3)

    def run(self):
        """
        Run B-V algorithm.

        Returns
        -------
        result : (int, int)
            Returns tuple of ints, equivalent to bit strings a and b.

        """
        job = self.backend.run(self.qobj)

        try:
            result = job.result()
        except qiskit.providers.ibmq.job.exceptions.IBMQJobFailureError:
            print(job.error_message())
            return -1, 0

        counts = result.get_counts(self.circuit)
        measurement = max(counts, key=lambda key: counts[key])

        # Get a by converting measurement to integer
        a = int(measurement[::-1], 2)

        # Get b by calling function
        b = self.f(0)

        return (a, b), result.time_taken

    def __apply_uf(self, qubits):
        """
        Define U_f gate (if not defined) that encodes oracle function f and applies it to qubits.

        Parameters
        -------
        qubits : [int]
            Qubits to apply U_f to.

        """

        if self.uf is None:
            # Initializes U_f as a 2^(n+1) by 2^(n+1) matrix of zeros
            U_f = np.zeros((2 ** (self.n + 1),) * 2, dtype=int)

            # Apply definition of U_f = |x>|b + f(x)> to construct matrix
            for x in range(2 ** self.n):
                for b in [0, 1]:
                    row = (x << 1) ^ b
                    col = (x << 1) ^ (self.f(x) ^ b)
                    U_f[row][col] = 1

            self.uf = Operator(U_f)

        self.circuit.append(self.uf, qubits[::-1])
