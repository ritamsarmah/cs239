#!/usr/bin/env python3

import simon
import time


def test_algorithm(tests, algorithm, verbose=True):
    if verbose:
        print(f"\nRunning tests for {algorithm.__name__}\n" + '-' * 50)
        print("    n\ttime (s)\toutput\n" + '-' * 50)

    passed = 0
    total_time = 0
    for (test_input, test_output) in tests:
        start = time.time()

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
    # Test case format: ((n, oracle), expected_output)
    tests = [
        ((2, lambda x: [0b11, 0b00, 0b11, 0b00][x]), 0b01)
        # ((3, lambda x: [0b000, 0b001, 0b010, 0b011, 0b100, 0b101, 0b110, 0b111][x]), 0b110)
    ]

    test_algorithm(tests, simon.Simon)
