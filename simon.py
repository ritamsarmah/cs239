#!/usr/bin/env python3

import numpy as np
from pyquil import Program
from pyquil import get_qc
from pyquil.gates import *
from pyquil.quil import DefGate
from pyquil.api import local_forest_runtime
import time


#-----------------------------------------#
# Functions for classical piece of Simon
#-----------------------------------------#

def arr_to_int(arr):
    res = 0
    arr = list(arr)
    arr.reverse()
    for i in range(len(arr)):
        res += arr[i]*(2**i)
    return res

'''
    check all equations with the target and make sure they're satisfied
    Inputs:
        eqns: list of equations of form {0,1}^n
        tgt: eqn of form {0,1}^n
'''
def simon_check_eqns(eqns, tgt):
    for e in eqns:
        if np.dot(e, tgt)%2 != 0:
            return False
    return True

'''
    find all possible target equations.
        just generate all possible lists of 0,1 (of length n)
'''
def findall_tgts(n):
    input_seqs = [[]]
    #generation process: in a loop, take all outputs of prev loop and add "output + '0'", "output+'1'"
    # to the set of new outputs. Do this repeatedly until we have all 2^n strings of length n.
    for i in range(n):
        new_arrs = []
        for seq in input_seqs:
            new_arrs.append(seq + [0])
            new_arrs.append(seq + [1])
        input_seqs = new_arrs
    return input_seqs

# eqns is a nparray with all equations
def simon_eqns_solver(eqns, n):
    tgts = findall_tgts(n)
    for t in tgts[1:]:
        r = simon_check_eqns(eqns, t)
        if r:
            return arr_to_int(t)
    return arr_to_int([0, 0, 0])

#-----------------------------------------#
# Class for implementing (quantum) Simon
#-----------------------------------------#

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

        ### first, build the simon circuit.
        p = Program()
        ro = p.declare('ro', memory_type='BIT', memory_size=self.n)

        # Apply Hadamard to first n qubits
        p += [H(q) for q in range(self.n)]

        # Apply U_f to all qubits
        p += self._apply_uf(range(self.n * 2))

        # Apply Hadamard to first n qubits (ignoring n helper bits)
        p += [H(q) for q in range(self.n)]

        # Measure first n qubits (ignoring n helper bits)
        p += [MEASURE(q, ro[q]) for q in range(self.n)]

        # Run n - 1 times to collect equations
        num_runs = 4*(self.n - 1)+1
        p.wrap_in_numshots_loop(num_runs)


        ### now, run it...
        #with local_forest_runtime():
        qc = get_qc(f'{self.n * 2}q-qvm')  # n bits + n helper bits
        qc.compiler.client.timeout = 1000

        t1 = time.time()
        executable = qc.compile(p)
        cpl_time = time.time()-t1
        #print(f"exe created! compile time = {cpl_time}")

        t1 = time.time()
        result = qc.run(executable)
        run_time = (time.time()-t1) / num_runs
        #print(f"computation finished! avg runtime ={run_time}")
        #print(result)

        soln = simon_eqns_solver(result, self.n)
        #print(f"\nFinal Solution: {soln}")

        print(f"\t*** compilation time: {cpl_time}, avg trial runtime: {run_time}")
        return soln

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

       # Initializes U_f as a 2^(2n) by 2^(2n) matrix of zeros
        U_f = np.zeros((2 ** (self.n * 2),) * 2, dtype=int)

        # Apply definition of U_f = |x>|b + f(x)> to construct matrix
        for x in range(2 ** self.n):
            # Number of helper bits is equal to number of qubits
            for b in range(2 ** self.n):
                row = (x << self.n) ^ b
                col = (x << self.n) ^ (self.f(x) ^ b)
                U_f[row][col] = 1

        uf_definition = DefGate("U_f", U_f)
        gate = uf_definition.get_constructor()
        return [uf_definition, gate(*qubits)]
