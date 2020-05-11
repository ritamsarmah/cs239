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

        self.p = None
        self.zf_definition = None
        self.z0_definition = None
        self._construct()

    def _construct(self):
        """
        Construct program for Grover's algorithm.
        """
        self.p = Program()
        ro = self.p.declare('ro', memory_type='BIT', memory_size=self.n)

        # Apply Hadamard to all qubits
        self.p += [H(q) for q in range(self.n)]

        # Calculate number of times to apply G to qubits
        k = int(np.floor(np.pi / 4 * np.sqrt(2 ** self.n)))

        # Apply G to all qubits
        self.p += self._apply_g(range(self.n), k)

        # Measure all qubits
        self.p += [MEASURE(q, ro[q]) for q in range(self.n)]

    def run(self):
        """
        Run Grover's algorithm.

        Returns
        -------
        result : int
            Returns 1 if self.f is constant or 0 if self.f is balanced.

        """

        # Get a QC with n bits
        qc = get_qc(f'{self.n}q-qvm')
        qc.compiler.client.timeout = 1000
        executable = qc.compile(self.p)

        result = qc.run(executable)

        # Convert measurement to bits
        x = int("".join(map(str, result.flatten())), 2)

        # Verify output on oracle, if f(x) == 1, we're done
        # Else we re-run if we've got more iterations left
        if self.f(x) == 1:
            return 1
        elif self.iteration < self.max_iterations:
            self.iteration += 1
            return self.run()
        else:
            return 0

    def _apply_g(self, qubits, k):
        """
        Applies G = -H × Z_0 × H × Z_f to qubits with k repetitions

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

        # Apply G to qubits k times
        for _ in range(k):
            G += [self._apply_zf(qubits)]
            G += [H(q) for q in qubits]
            G += [self._apply_z0(qubits)]
            G += [H(q) for q in qubits]

        return G

    def _apply_zf(self, qubits):
        """
        Define Z_f gate (if not defined) and applies it to qubits.

        Parameters
        ----------
        qubits : [int]
            Qubits to apply Z_f to.

        Returns
        ----------
        Z_f : Gate
            Z_f gate applied to qubits

        """

        if self.zf_definition is None:
            # Initializes Z_f as a 2^n by 2^n matrix of zeros
            Z_f = np.eye(2 ** self.n, dtype=int)

            # Apply definition of Z_f = (-1)^{f(x)} to construct matrix
            for x in range(2 ** self.n):
                Z_f[x][x] = (-1) ** self.f(x)

            # Multiply by -1 to account for leading minus in G
            Z_f *= -1

            self.zf_definition = DefGate("Z_f", Z_f)
            self.p += self.zf_definition

        Z_f = self.zf_definition.get_constructor()
        return Z_f(*qubits)

    def _apply_z0(self, qubits):
        """
        Defines Z_0 gate (if not defined) and applies it to qubits.

        Parameters
        ----------
        qubits : [int]
            Qubits to apply Z_0 to.

        Returns
        ----------
        Z_0 : Gate
            Z_0 gate applied to qubits

        """

        if self.z0_definition is None:
            # Create Z_0 as identity, except with -1 in top-left corner
            Z_0 = np.eye(2 ** self.n)
            Z_0[0][0] = -1

            self.z0_definition = DefGate("Z_0", Z_0)
            self.p += self.z0_definition

        Z_0 = self.z0_definition.get_constructor()
        return Z_0(*qubits)
