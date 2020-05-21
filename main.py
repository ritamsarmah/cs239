#!/usr/bin/env python3


import bernstein_vazirani
#  import deutsch_jozsa
# import grover
# import simon
import time


def test_algorithm(tests, algorithm, verbose=True):
    if verbose:
        print(f"\nRunning tests for {algorithm.__name__}\n" + '-' * 70)
        print("n\ttotal (s)\tcompile (s)\truntime (s)\toutput\n" + '-' * 70)

    passed = 0
    total_compile_time = 0
    total_run_time = 0

    for (test_num, (test_input, test_output)) in enumerate(tests):
        start_compile = time.time()
        instance = algorithm(*test_input)
        end_compile = time.time()
        elapsed_compile = end_compile - start_compile
        total_compile_time += elapsed_compile

        start_run = time.time()
        output = instance.run()
        end_run = time.time()
        elapsed_run = end_run - start_run
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
    # Test case format: ((n, oracle), expected_output)

    simon_tests = [
        ((1, lambda x: [0b0, 0b1][x]), 0b0),
        ((2, lambda x: [0b11, 0b00, 0b11, 0b00][x]), 0b10),
        ((2, lambda x: [0b10, 0b01, 0b01, 0b10][x]), 0b11)
        #((2, lambda x: [0b00, 0b01, 0b10, 0b11][x]), 0b00),
        #((3, lambda x: [0b000, 0b001, 0b010, 0b011, 0b010, 0b011, 0b000, 0b001][x]), 0b110),
        #((3, lambda x: [0b000, 0b001, 0b010, 0b011, 0b100, 0b101, 0b110, 0b111][x]), 0b000)
        # (this test crashes everything.)
        #((4, lambda x: [0b0000, 0b0001, 0b0010, 0b0011, 0b0100, 0b0101, 0b0110, 0b0111, 0b1000, 0b1001, 0b1010, 0b1011, 0b1100, 0b1101, 0b1110, 0b1111][x]), 0b000)
    ]

    # test_algorithm(simon_tests, simon.Simon)

    grover_tests = [
        ((1, lambda x: x == 0b1), 1),
        ((1, lambda x: 0), 0),
        ((2, lambda x: x == 0b10), 1),
        ((2, lambda x: 0), 0),
        ((3, lambda x: x == 0b101), 1),
        ((3, lambda x: 0), 0),
        ((4, lambda x: x == 0b1101), 1),
        ((4, lambda x: 0), 0),
        ((5, lambda x: x == 0b10101), 1),
        ((5, lambda x: 0), 0)
    ]

    # test_algorithm(grover_tests, grover.Grover)

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
        ((5, lambda x: 0), 1)
    ]

    #  test_algorithm(dj_tests, deutsch_jozsa.DeutschJozsa)

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
            [(16 & x != 0), (4 & x != 0), (2 & x != 0)]) % 2), (0b10110, 0))
    ]

    test_algorithm(bv_tests, bernstein_vazirani.BernsteinVazirani)
