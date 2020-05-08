#!/usr/bin/env python3

import numpy as np
from pyquil import Program
from pyquil import get_qc
from pyquil.gates import *
from pyquil.quil import DefGate


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

    def run(self):
        """
        Run Deutsch–Jozsa algorithm.

        Returns
        -------
        result : int
            Returns 1 if self.f is constant or 0 if self.f is balanced.

        """
        p = Program()
        ro = p.declare('ro', memory_type='BIT', memory_size=self.n)

        # Initialize helper bit (at index n) to 1
        p += X(self.n)

        # Apply Hadamard to all qubits
        for q in range(self.n + 1):
            p += H(q)

        # Create U_f gate
        uf_definition = self._define_uf()
        U_f = uf_definition.get_constructor()

        # Apply U_f to all qubits
        p += uf_definition
        p += U_f(*range(0, self.n + 1))

        # Apply Hadamard to first n qubits (ignoring helper bit)
        for q in range(self.n):
            p += H(q)

        # Measure first n qubits (ignoring helper bit)
        for q in range(self.n):
            p += MEASURE(q, ro[q])

        qc = get_qc(f'{self.n + 1}q-qvm')  # n bits + 1 helper bit
        executable = qc.compile(p)
        result = qc.run(executable)

        # Count number of non-zeros, and if there are none it's constant.
        # The expression is cast to an int (False = 0 => balanced, True = 1 => constant)
        return int(np.count_nonzero(result) == 0)

    def _define_uf(self):
        """
        Define a U_f gate that encodes function f.

        Returns
        -------
        U_f : DefGate
            Quil definition for U_f

        """

        # Initializes U_f as a 2^(n+1) by 2^(n+1) matrix of zeros
        U_f = np.zeros((2 ** (self.n + 1),) * 2, dtype=int)

        # Apply definition of U_f = |x>|b + f(x)> to construct matrix
        # using each input/output pair (x, fx respectively)
        for x in range(2 ** self.n):
            for b in [0, 1]:
                row = (x << 1) ^ b
                col = (x << 1) ^ (self.f(x) ^ b)
                U_f[row][col] = 1

        return DefGate("U_f", U_f)
