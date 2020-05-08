#!/usr/bin/env python3

import numpy as np
from pyquil import Program
from pyquil import get_qc
from pyquil.gates import *
from pyquil.quil import DefGate


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

    Examples
    ----------
    ```
    TODO: Add example
    >>> Grover(...).run()
    ```
    """

    def __init__(self, n, f):
        self.n = n
        self.f = f

    def run(self):
        """
        Run Grover's algorithm.

        Returns
        -------
        result : int
            Returns 1 if self.f is constant or 0 if self.f is balanced.

        """
        p = Program()
        ro = p.declare('ro', memory_type='BIT', memory_size=self.n)

        # Apply Hadamard to all qubits
        p += [H(q) for q in range(self.n)]

        # Apply G to all qubits
        k = int(np.floor(np.pi / 4 * np.sqrt(2 ** self.n)))
        p += self._apply_g(range(self.n), k)

        # Measure all qubits
        p += [MEASURE(q, ro[q]) for q in range(self.n)]

        # Get a QC with n bits
        qc = get_qc(f'{self.n}q-qvm')
        qc.compiler.client.timeout = 1000
        executable = qc.compile(p)

        result = qc.run(executable)

        print(result)
        # return int(np.count_nonzero(result) == 0)

    def _apply_g(self, qubits, k):
        """
        Applies G = -H × Z_0 × H × Z_f to qubits k repetitions

        Parameters
        ----------
        qubits : [int]
            Qubits to apply G to.

        k : int
            Number of times to apply G to qubits.

        Returns
        ----------
        G : list
            List of all applications of matrix G to qubits.
        """
        G = []

        # Construct G and apply k times
        for _ in range(k):
            G += self._apply_zf(qubits)
            G += [H(q) for q in qubits]
            G += self._apply_z0(qubits)
            G += [H(q) for q in qubits]

        return G

    def _apply_zf(self, qubits):
        """
        Creates Z_f gate and applies it to qubits.

        Parameters
        ----------
        qubits : [int]
            Qubits to apply Z_f to.

        Returns
        ----------
        [zf_definition, Z_f] : [DefGate, Callable]
            Quil definition for Z_f and the gate.

        """

        # Initializes Z_f as a 2^n by 2^n matrix of zeros
        Z_f = np.zeros((2 ** self.n,) * 2, dtype=int)

        # Apply definition of Z_f = (-1)^{f(x)}|x> to construct matrix
        for x in range(2 ** self.n):
            Z_f[x][x] = -1 ** self.f(x)

        print(Z_f)

        zf_definition = DefGate("Z_f", Z_f)
        gate = zf_definition.get_constructor()
        return [zf_definition, gate(*qubits)]

    def _apply_z0(self, qubits):
        """
        Creates Z_0 gate and applies it to qubits.

        Parameters
        ----------
        qubits : [int]
            Qubits to apply Z_0 to.

        Returns
        ----------
        [z0_definition, Z_0] : [DefGate, Callable]
            Quil definition for Z_0 and the gate.

        """

        # Create Z_0 as identity, except with -1 in top-left corner
        Z_0 = np.eye(2 ** self.n)
        Z_0[0][0] = -1

        z0_definition = DefGate("Z_0", Z_0)
        gate = z0_definition.get_constructor()
        return [z0_definition, gate(*qubits)]
