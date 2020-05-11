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
        ((2, lambda x: [0b11, 0b00, 0b11, 0b00][x]), 0b10),
        ((2, lambda x: [0b10, 0b01, 0b01, 0b10][x]), 0b11),
        ((2, lambda x: [0b00, 0b01, 0b10, 0b11][x]), 0b00),
        ((3, lambda x: [0b000, 0b001, 0b010, 0b011, 0b010, 0b011, 0b000, 0b001][x]), 0b110)
        ((3, lambda x: [0b000, 0b001, 0b010, 0b011, 0b100, 0b101, 0b110, 0b111][x]), 0b000)
        # (this test crashes everything.)
        #((4, lambda x: [0b0000, 0b0001, 0b0010, 0b0011, 0b0100, 0b0101, 0b0110, 0b0111, 0b1000, 0b1001, 0b1010, 0b1011, 0b1100, 0b1101, 0b1110, 0b1111][x]), 0b000)

    ]

    test_algorithm(tests, simon.Simon)

'''
finally got good results for this example:
    [0b000, 0b001, 0b010, 0b011, 0b010, 0b011, 0b000, 0b001], s = 0b110

    - resulting equations are correct.
    - compile time: 88.390 s
    - average runtime (per trial) = 2.647 s

example: identity(2)
    - compile time: 3.037
    - avg runtime: 0.184

example: identity(3)
    - compile time: 89.780
    - avg. runtime: 2.611

example: identity(4)
    == ran out of heap memory.




'''
