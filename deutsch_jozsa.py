#!/usr/bin/env python3

import numpy as np
from qiskit import *
from qiskit.quantum_info.operators import Operator

class DeutschJozsa:
    """
    Deutsch Jozsa algorithm.

    Parameters
    ----------
    n : int
        The length of bit string input to f.
    f : lambda
        A function that take as input an int in range [0, 2^n]
        representing binary string {0,1}^n and outputs int {0,1}.

    Examples
    ----------
    ```
    >>> DeutschJozsa(2, lambda x: [1, 0, 1, 0][x]).run()
    0
    >>> DeutschJozsa(2, lambda x: 1).run()
    1
    ```
    """

    def __init__(self, n, f):
        self.n = n
        self.f = f
        self.uf = None

        self.__construct()

    def __construct(self):
        """
        Construct program for Deutsch-Jozsa algorithm.
        """
        # Create a Quantum circuit with n+1 qubits and n classical bits for measurement
        self.circuit = QuantumCircuit(self.n + 1, self.n)

        # Set helper bit (at index n) to 1
        self.circuit.x(self.n)

        # Apply Hadamard to all qubits
        for q in range(self.n + 1):
            self.circuit.h(q)

        # Apply U_f to all qubits
        self.__apply_uf(list(range(self.n + 1)))

        # Apply Hadamard to first n qubits (ignoring helper bit)
        for q in range(self.n):
            self.circuit.h(q)

        # Measure first n qubits (ignoring helper bit)
        for q in range(self.n):
            self.circuit.measure(q, q)

    def run(self):
        """
        Run Deutsch-Jozsa algorithm.

        Returns
        -------
        result : (int, int)
            Returns tuple of ints, equivalent to bit strings a and b.

        """
        simulator = Aer.get_backend('qasm_simulator')
        job = execute(self.circuit, simulator, shots=1)
        result = job.result()
        counts = result.get_counts(self.circuit)
        measurement = list(counts.keys())[0]

        # If output is all zeros, function is constant.
        # The expression is cast to an int (False = 0 => balanced, True = 1 => constant)
        return int(measurement == '0' * self.n)

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

        self.circuit.unitary(self.uf, qubits[::-1], label='u_f')
