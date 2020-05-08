#!/usr/bin/env python3

import deutsch_jozsa
import time


def test_algorithm(tests, algorithm, verbose=True):
    start = time.time()

    if verbose:
        print(f"\nRunning tests for {algorithm.__name__}")
    for (test_num, (test_input, test_output)) in enumerate(tests):
        if verbose:
            print(
                f"----------------------------------------------------------------------\nTest {test_num + 1}: {test_input}")

        output = algorithm(*test_input).run()

        if verbose:
            print(f"Result: {output}")

        assert output == test_output, f"Failed Test {test_num + 1}. Expected {test_output}, but got {output}"

    end = time.time()
    elapsed = end - start

    print(
        f"----------------------------------------------------------------------\nRan {len(tests)} tests in {elapsed}s\n\nOK")


if __name__ == "__main__":
    tests = [
        ((1, [0, 0]), 1),
        ((1, [0, 1]), 0),
        ((1, [1, 0]), 0),
        ((1, [1, 1]), 1),
        ((2, [1, 1, 1, 1]), 1),
        ((2, [1, 0, 0, 1]), 0),
        ((3, [1] * (2**3)), 1),
    ]

    test_algorithm(tests, deutsch_jozsa.DeutschJozsa)
