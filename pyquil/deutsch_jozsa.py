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

        self.uf_definition = None
        self._construct()

    def _construct(self):
        """
        Construct program for Deutsch-Jozsa algorithm.
        """
        self.p = Program()
        ro = self.p.declare('ro', memory_type='BIT', memory_size=self.n)

        # Set helper bit (at index n) to 1
        self.p += X(self.n)

        # Apply Hadamard to all qubits
        self.p += [H(q) for q in range(self.n + 1)]

        # Apply U_f to all qubits
        self.p += self._apply_uf(range(self.n + 1))

        # Apply Hadamard to first n qubits (ignoring helper bit)
        self.p += [H(q) for q in range(self.n)]

        # Measure first n qubits (ignoring helper bit)
        self.p += [MEASURE(q, ro[q]) for q in range(self.n)]

        # Get a QC with n bits + 1 helper bit
        self.qc = get_qc(f'{self.n + 1}q-qvm')
        self.qc.compiler.client.timeout = 1000
        self.executable = self.qc.compile(self.p)

    def run(self):
        """
        Run Deutsch–Jozsa algorithm.

        Returns
        -------
        result : int
            Returns 1 if self.f is constant or 0 if self.f is balanced.

        """
        
        result = self.qc.run(self.executable)

        # Count number of non-zeros, and if there are none it's constant.
        # The expression is cast to an int (False = 0 => balanced, True = 1 => constant)
        return int(np.count_nonzero(result) == 0)

    def _apply_uf(self, qubits):
        """
        Define U_f gate (if not defined) that encodes oracle function f and applies it to qubits.

        Parameters
        -------
        qubits : [int]
            Qubits to apply U_f to.

        Returns
        -------
        U_f : Gate
            Z_f gate applied to qubits.

        """

        if self.uf_definition is None:
            # Initializes U_f as a 2^(n+1) by 2^(n+1) matrix of zeros
            U_f = np.zeros((2 ** (self.n + 1),) * 2, dtype=int)

            # Apply definition of U_f = |x>|b + f(x)> to construct matrix
            for x in range(2 ** self.n):
                for b in [0, 1]:
                    row = (x << 1) ^ b
                    col = (x << 1) ^ (self.f(x) ^ b)
                    U_f[row][col] = 1

            self.uf_definition = DefGate("U_f", U_f)
            self.p += self.uf_definition

        U_f = self.uf_definition.get_constructor()
        return U_f(*qubits)
