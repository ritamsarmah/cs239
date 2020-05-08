#!/usr/bin/env python3

import deutsch_jozsa
import time


def test_algorithm(tests, algorithm):
    start = time.time()

    if verbose:
        print(f"\nRunning tests for {algorithm.__name__}\n" + '-' * 40)

    for (test_num, (test_input, test_output)) in enumerate(tests):
        output = algorithm(*test_input).run()

        if verbose:
            print(f"[Test {test_num + 1}] Output: {output}")

        assert output == test_output, "Failed Test {}. Expected {}, but got {}.".format(test_num + 1, test_output, output)

    end = time.time()
    elapsed = end - start

    print('-' * 40 + f"\nRan {len(tests)} tests in {elapsed:.4f}s")


if __name__ == "__main__":
    tests = [
        ((1, lambda x: [0, 1][x]), 0),
        ((1, lambda x: [1, 0][x]), 0),
        ((1, lambda x: 0 ), 1),
        ((1, lambda x: 1 ), 1),
        ((2, lambda x: 1), 1),
        ((2, lambda x: [1, 0, 0, 1][x]), 0),
        ((3, lambda x: 1), 1),
    ]

    test_algorithm(tests, deutsch_jozsa.DeutschJozsa)
