#!/usr/bin/env python3

import numpy as np
from qiskit import *
from qiskit.quantum_info.operators import Operator


class Grover:
    """
    Grover's algorithm.

    Parameters
    ----------
    n : int
        The length of bit string input to f.
    f : lambda
        A function that take as input an int in range [0, 2^n]
        representing binary string {0,1}^n and outputs int {0,1}.
    max_iterations : int
        The number of iterations to re-run if the x found
        from running doesn't have f(x) = 1. We decide that f doesn't
        have an x s.t. f(x) = 1 if we reach this number of iterations.

    Examples
    ----------
    ```
    >>> Grover(2, lambda x: 0).run()
    0
    >>> Grover(2, lambda x: x == 0b10).run()
    1
    ```
    """

    def __init__(self, n, f, max_iterations=5):
        self.n = n
        self.f = f
        self.iteration = 0
        self.max_iterations = max_iterations

        self.zf = None
        self.z0 = None
        self.__construct()

    def __construct(self):
        """
        Construct program for Grover's algorithm.
        """
        # Create a Quantum circuit with n qubits and n classical bits for measurement
        self.circuit = QuantumCircuit(self.n, self.n)

        # Apply Hadamard to all qubits
        for q in range(self.n):
            self.circuit.h(q)

        # Calculate number of times to apply G to qubits
        k = int(np.floor(np.pi / 4 * np.sqrt(2 ** self.n)))

        # Apply G to all qubits
        self.__apply_g(list(range(self.n)), k)

        # Measure all qubits
        for q in range(self.n):
            self.circuit.measure(q, q)

    def run(self):
        """
        Run Grover's algorithm.

        Returns
        -------
        result : int
            Return 1 if there exists x in [0,1] such that f(x) = 1, and 0 otherwise.

        """
        simulator = Aer.get_backend('qasm_simulator')
        job = execute(self.circuit, simulator, shots=1)
        result = job.result()
        counts = result.get_counts(self.circuit)
        measurement = list(counts.keys())[0]

        # Convert measurement into int input for f
        x = int(measurement[::-1], 2)

        # Verify output on oracle, if f(x) == 1, we're done
        # Else we re-run if we've got more iterations left
        if self.f(x) == 1:
            return 1
        elif self.iteration < self.max_iterations:
            self.iteration += 1
            return self.run()
        else:
            return 0

    def __apply_g(self, qubits, k):
        """
        Applies G = -H × Z_0 × H × Z_f to qubits with k repetitions

        Parameters
        ----------
        qubits : [int]
            Qubits to apply G to.

        k : int
            Number of times to apply G to qubits.

        """
        # Apply G to qubits k times
        for _ in range(k):
            self.__apply_zf(qubits)

            for q in qubits:
                self.circuit.h(q)

            self.__apply_z0(qubits)

            for q in qubits:
                self.circuit.h(q)

    def __apply_zf(self, qubits):
        """
        Define Z_f gate (if not defined) and applies it to qubits.

        Parameters
        ----------
        qubits : [int]
            Qubits to apply Z_f to.

        """

        if self.zf is None:
            # Initializes Z_f as a 2^n by 2^n matrix of zeros
            Z_f = np.eye(2 ** self.n, dtype=int)

            # Apply definition of Z_f = (-1)^{f(x)} to construct matrix
            for x in range(2 ** self.n):
                Z_f[x][x] = (-1) ** self.f(x)

            # Multiply by -1 to account for leading minus in G
            Z_f *= -1

            self.zf = Operator(Z_f)

        self.circuit.append(self.zf, qubits[::-1])

    def __apply_z0(self, qubits):
        """
        Defines Z_0 gate (if not defined) and applies it to qubits.

        Parameters
        ----------
        qubits : [int]
            Qubits to apply Z_0 to.

        """

        if self.z0 is None:
            # Create Z_0 as identity, except with -1 in top-left corner
            Z_0 = np.eye(2 ** self.n)
            Z_0[0][0] = -1
            self.z0 = Operator(Z_0)

        self.circuit.append(self.z0, qubits[::-1])
