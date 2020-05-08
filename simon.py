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
    f : list
        A list of length 2^n representing a function: {0, 1}^n -> {0, 1}.
        The indices (converted to binary) represent the input strings, and list
        values are outputs corresponding to their respective index as input.

    Examples
    ----------
    ```
    >>> Simon(2, [1, 0, 1, 0]).run()
    0
    >>> Simon(2, [1, 1, 1, 1]).run()
    1
    ```
    """

    def __init__(self, n, f):
        self.n = n
        self.f = f

    def run(self):
        """
        Run Simon's algorithm.

        Returns
        -------
        result : str
            Returns s in {0,1}^n such that for all x, y: [f(x) = f(y)] iff [(x + y) in {0^n, s}]

        """
        p = Program()
        ro = p.declare('ro', memory_type='BIT', memory_size=self.n)

        # Apply Hadamard to first n qubits
        for q in range(self.n + 1):
            p += H(q)

        # Create U_f gate
        uf_definition = self._define_uf()
        U_f = uf_definition.get_constructor()

        # Apply U_f to all qubits (n qubits + n helper qubits = n * 2)
        p += uf_definition
        p += U_f(*range(0, self.n * 2))

        # Apply Hadamard to first n qubits (ignoring helper bits)
        for q in range(self.n):
            p += H(q)

        # Measure first n qubits (ignoring helper bits)
        for q in range(self.n):
            p += MEASURE(q, ro[q])

        # TODO: set number of iterations
        num_trials = 
        qc = get_qc(f'{self.n * 2}q-qvm')   # n bits + n helper bits
        executable = qc.compile(p)
        result = qc.run(executable, trials=)

        return int(np.count_nonzero(result) == 0)

    def _define_uf(self):
        """
        Define a U_f gate that encodes function f.

        Returns
        -------
        U_f : DefGate
            Quil defintion for U_f

        """

        # Initializes U_f as a 2^(2n) x 2^(2n) array of zeros
        U_f = np.zeros((2 ** (self.n * 2),) * 2, dtype=int)

        # Apply definition of U_f = |x>|b + f(x)> to construct matrix
        # using each input/output pair (x, fx respectively)
        for (x, fx) in enumerate(self.f):
            # Iterate over possible values for helper bit, b
            for b in range(2 ** self.n):
                row = (x << 1) ^ b
                col = (x << 1) ^ (fx ^ b)
                U_f[row][col] = 1

        return DefGate("U_f", U_f)
