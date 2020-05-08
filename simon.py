#!/usr/bin/env python3

import numpy as np
from pyquil import Program
from pyquil import get_qc
from pyquil.gates import *
from pyquil.quil import DefGate


class Simon:
    """
    Simon's algorithm.

    Parameters
    ----------
    n : int
        The length of bit string input to f.
    f : lambda
        A function that take as input an int in range [0, 2^n]
        representing binary string {0,1}^n and outputs int {0,1}^n.

    Examples
    ----------
    ```
    >>> f = lambda x: [0b000, 0b001, 0b010, 0b011, 0b100, 0b101, 0b110, 0b111][x]
    >>> Simon(3, f).run()
    110
    ```
    """

    def __init__(self, n, f):
        self.n = n
        self.f = f

    def run(self):
        """
        Run Simon's algorithm.

        Returns
        ----------
        result : int
            Returns s in {0,1}^n such that
            for all x, y: [f(x) = f(y)] iff [(x + y) in {0^n, s}]

        """
        p = Program()
        ro = p.declare('ro', memory_type='BIT', memory_size=self.n)

        # Apply Hadamard to first n qubits
        p += [H(q) for q in range(self.n)]

        # Apply U_f to all qubits
        p += self._apply_uf(range(0, self.n * 2))

        # Apply Hadamard to first n qubits (ignoring n helper bits)
        p += [H(q) for q in range(self.n)]

        # Measure first n qubits (ignoring n helper bits)
        p += [MEASURE(q, ro[q]) for q in range(self.n)]

        # Run n - 1 times to collect equations
        p.wrap_in_numshots_loop(self.n - 1)

        qc = get_qc(f'{self.n * 2}q-qvm')  # n bits + n helper bits
        qc.compiler.client.timeout = 1000
        executable = qc.compile(p)
        result = qc.run(executable)

        print(result)
        return np.linalg.solve(result, np.zeros(self.n - 1))

    def _apply_uf(self, qubits):
        """
        Creates a U_f gate that encodes oracle function f and applies it to qubits.

        Parameters
        ----------
        qubits : [int]
            Qubits to apply U_f to.

        Returns
        ----------
        [uf_definition, U_f] : [DefGate, Callable]
            Quil definition for U_f and the gate.

        """

        # Initializes U_f as a 2^(n+1) by 2^(n+1) matrix of zeros
        U_f = np.zeros((2 ** (self.n + 1),) * 2, dtype=int)

        # Apply definition of U_f = |x>|b + f(x)> to construct matrix
        for x in range(2 ** self.n):
            for b in [0, 1]:
                row = (x << 1) ^ b
                col = (x << 1) ^ (self.f(x) ^ b)
                U_f[row][col] = 1

        uf_definition = DefGate("U_f", U_f)
        gate = uf_definition.get_constructor()
        return [uf_definition, gate(*qubits)]
