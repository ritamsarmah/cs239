#!/usr/bin/env python3

import grover
import time


def test_algorithm(tests, algorithm, verbose=True):
    if verbose:
        print(f"\nRunning tests for {algorithm.__name__}\n" + '-' * 50)
        print("    n\ttime (s)\toutput\n" + '-' * 50)

    passed = 0
    total_time = 0
    for (test_input, test_output) in tests:
        start = time.time()

    for (test_num, (test_input, test_output)) in enumerate(tests):
        output = algorithm(*test_input).run()
        
        end = time.time()
        elapsed = end - start
        total_time += elapsed

        if verbose:
            if output == test_output:
                print(f"(✓) {test_input[0]}\t{elapsed:.4f}\t\t{output}")
                passed += 1
            else:
                print(
                    f"(×) {test_input[0]}\t{elapsed:.4f}\t\t{output} (Expected: {test_output})\t")

    print('-' * 50 + f"\nPassed {passed}/{len(tests)} tests in {total_time:.4f}s")


if __name__ == "__main__":
    tests = [
        ((2, lambda x: [0, 0, 0, 1][x]), 0b01),
    ]

    test_algorithm(tests, grover.Grover)
