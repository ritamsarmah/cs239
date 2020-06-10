#!/usr/bin/env python3


import bernstein_vazirani
import deutsch_jozsa
import grover
import simon
import time

from qiskit import IBMQ
from qiskit.providers.ibmq import least_busy

def test_algorithm(tests, algorithm, backend, verbose=True):
    if verbose:
        print(f"\n{algorithm.__name__} Tests\n" + '-' * 70)
        print("n\ttotal (s)\tcompile (s)\truntime (s)\toutput\n" + '-' * 70)

    passed = 0
    total_compile_time = 0
    total_run_time = 0

    for (test_num, (test_input, test_output)) in enumerate(tests):
        start_compile = time.time()
        instance = algorithm(*test_input, backend)
        end_compile = time.time()
        elapsed_compile = end_compile - start_compile
        total_compile_time += elapsed_compile

        output, elapsed_run = instance.run()
        total_run_time += elapsed_run

        if verbose:
            if output == test_output:
                print(
                    f"{test_input[0]}\t{elapsed_compile+elapsed_run:.4f}\t\t{elapsed_compile:.4f}\t\t{elapsed_run:.4f}\t\t{output}")
                passed += 1
            else:
                print(
                    f"{test_input[0]}\t{elapsed_compile+elapsed_run:.4f}\t\t{elapsed_compile:.4f}\t\t{elapsed_run:.4f}\t\t{output} (Expected: {test_output})")

    print('-' * 70 +
          f"\nTotal:\t{total_compile_time+total_run_time:.4f}\t\t{total_compile_time:.4f}\t\t{total_run_time:.4f}\t\tPassed {passed}/{len(tests)}")


if __name__ == "__main__":
    # Load least busy backend and use the same QC to run all tests
    provider = IBMQ.enable_account('58b3caece224fe45e9eebe211808f050207d41998913468ea773c2024c5cb8ea278daae70e9a8d0a0656f205a198109aff811c48ceb6f38e217e2c29ce831fd3')
    small_devices = provider.backends(filters=lambda x: x.configuration().n_qubits == 5 and not x.configuration().simulator)
    backend = least_busy(small_devices)
    print(f"Using backend: {backend}")

    # Test case format: ((n, oracle), expected_output)

    #function design: given x and s, deduce y s.t. x+y=s. Return min(x, y)
    #return a bitstring y, the same size as x
    def simon_fn(x, s):
        y = x ^ s #x ^ y = s <==> x ^ s = y
        return min(x, y)

    simon_tests = [
        ((1, lambda x: [0b0, 0b1][x]), 0b0),
        ((2, lambda x: [0b11, 0b00, 0b11, 0b00][x]), 0b10),
        ((2, lambda x: [0b10, 0b01, 0b01, 0b10][x]), 0b11),
        ((2, lambda x: [0b00, 0b01, 0b10, 0b11][x]), 0b00),
        ((3, lambda x: [0b000, 0b001, 0b010, 0b011, 0b010, 0b011, 0b000, 0b001][x]), 0b110),
        ((3, lambda x: [0b000, 0b001, 0b010, 0b011, 0b100, 0b101, 0b110, 0b111][x]), 0b000),
        ((4, lambda x: [0b0000, 0b0001, 0b0010, 0b0011, 0b0100, 0b0101, 0b0110, 0b0111, 0b1000, 0b1001, 0b1010, 0b1011, 0b1100, 0b1101, 0b1110, 0b1111][x]), 0b0000),
        ((4, lambda x: [0b0000, 0b0001, 0b0010, 0b0011, 0b0100, 0b0101, 0b0110, 0b0111,
                        0b0001, 0b0000, 0b0011, 0b0010, 0b0101, 0b0100, 0b0111, 0b0110][x]), 0b1001),

        ((5, lambda x: simon_fn(x, 0b10011)), 0b10011),
        ((5, lambda x: simon_fn(x, 0b10100)), 0b10100),
        ((6, lambda x: simon_fn(x, 0b100101)), 0b100101),
        ((6, lambda x: simon_fn(x, 0b110000)), 0b110000)
    ]

    test_algorithm(simon_tests, simon.Simon, backend)

    grover_tests = [
        ((1, lambda x: int(x == 0b1)), 1),
        ((1, lambda x: 0), 0),
        ((2, lambda x: int(x == 0b10)), 1),
        ((2, lambda x: 0), 0),
        ((3, lambda x: int(x == 0b101)), 1),
        ((3, lambda x: 0), 0),
        ((4, lambda x: int(x == 0b1101)), 1),
        ((4, lambda x: 0), 0),
        ((5, lambda x: int(x == 0b10101)), 1),
        ((5, lambda x: 0), 0),

        ((6, lambda x: int(x == 0b101010)), 1),
        ((6, lambda x: 0), 0),
        ((7, lambda x: int(x == 0b1010111)), 1),
        ((7, lambda x: 0), 0),
        ((8, lambda x: int(x == 0b10101)), 1),
        ((8, lambda x: 0), 0),

        ((9, lambda x: int(x == 0b101010011)), 1),
        ((9, lambda x: int(x == 0b101011111)), 1),
        ((10, lambda x: int(x == 0b1001010011)), 1),
        ((10, lambda x: int(x == 0b1)), 1)
    ]

    #  test_algorithm(grover_tests, grover.Grover, backend)

    dj_tests = [
        ((1, lambda x: x % 2), 0),
        ((1, lambda x: 0), 1),
        ((2, lambda x: x % 2), 0),
        ((2, lambda x: 0), 1),
        ((3, lambda x: x % 2), 0),
        ((3, lambda x: 0), 1),
        ((4, lambda x: x % 2), 0),
        ((4, lambda x: 0), 1),
        ((5, lambda x: x % 2), 0),
        ((5, lambda x: 0), 1),

        ((6, lambda x: x % 2), 0),
        ((6, lambda x: 0), 1),
        ((7, lambda x: x % 2), 0),
        ((7, lambda x: 0), 1),
        ((8, lambda x: x % 2), 0),
        ((8, lambda x: 0), 1),
        ((9, lambda x: x % 2), 0),
        ((9, lambda x: 0), 1),
        ((10, lambda x: x % 2), 0),
        ((10, lambda x: 0), 1),
        ((11, lambda x: x % 2), 0),
        ((11, lambda x: 0), 1)
    ]

    test_algorithm(dj_tests, deutsch_jozsa.DeutschJozsa, backend)


    #take integers as input, treat as binary strings and multiply
    #return 0 or 1
    def mult_bstrings(x, y):
        int_and = (x&y)
        str_and = "{0:b}".format(int_and)
        sum_and = sum([int(i) for i in str_and])
        return sum_and %2

    bv_tests = [
        # output format: ("a", "b")
        ((1, lambda x: [0, 1][x]), (1, 0)),
        ((1, lambda x: [1, 0][x]), (1, 1)),
        ((2, lambda x: 1), (0, 1)),
        ((2, lambda x: [1, 0, 0, 1][x]), (0b11, 1)),
        ((3, lambda x: 1), (0, 1)),
        ((3, lambda x: [1, 0, 1, 0, 0, 1, 0, 1][x]), (0b101, 1)),
        ((4, lambda x: 1), (0, 1)),
        ((4, lambda x: sum(
            [(8 & x != 0), (4 & x != 0), (1 & x != 0)]) % 2), (0b1101, 0)),
        ((5, lambda x: 1), (0, 1)),
        ((5, lambda x: sum(
            [(16 & x != 0), (4 & x != 0), (2 & x != 0)]) % 2), (0b10110, 0)),

        ((6, lambda x: mult_bstrings(0b1101 << 2, x)), (0b1101 << 2, 0)),
        ((6, lambda x: 1), (0, 1)),
        ((7, lambda x: mult_bstrings(0b1101 << 2, x)), (0b1101 << 2, 0)),
        ((7, lambda x: 1), (0, 1)),
        ((8, lambda x: mult_bstrings(0b1101 << 3, x)), (0b1101 << 3, 0)),
        ((8, lambda x: 1), (0, 1)),
        ((9, lambda x: mult_bstrings(0b1101 << 4, x)), (0b1101 << 4, 0)),
        ((9, lambda x: 1), (0, 1)),
        ((10, lambda x: mult_bstrings(0b1101 << 5, x)), (0b1101 << 5, 0)),
        ((10, lambda x: 1), (0, 1)),
        ((11, lambda x: mult_bstrings(0b1101 << 6, x)), (0b1101 << 6, 0)),
        ((11, lambda x: 1), (0, 1))
        #((12, lambda x: mult_bstrings(0b1101 << 7, x)), (0b1101 << 8, 0))
    ]

    test_algorithm(bv_tests, bernstein_vazirani.BernsteinVazirani, backend)
