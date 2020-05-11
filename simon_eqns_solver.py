
import numpy as np

## helper function: convert list of numbers to integer (binary)
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

if __name__ == "__main__":
    #do some checks: 1. generate targets.
    print(findall_tgts(2))
    print("\n")
    print(findall_tgts(3))
    print("\n")
    print(findall_tgts(4))
    print("\n--------------------------------------\n")

    #2. check the equations:
    a = np.array([[1, 1, 0], [1, 1, 1], [1, 1, 1], [0, 0, 0], [0, 0, 1], [0, 0, 1], [1, 1, 0], [1, 1, 0]])
    b = np.array([1, 1, 0])
    b0 = np.array([0, 0, 0])
    b1 = np.array([0, 0, 1])
    b2 = np.array([1, 0, 1])
    print(simon_check_eqns(a, b))
    print(simon_check_eqns(a, b0))
    print(simon_check_eqns(a, b1))
    print(simon_check_eqns(a, b2))

    print("\n--------------------------------------\n")
    print("testing a malfunctioning case... should =2")
    err1 = np.array([[0, 1],[0, 1], [0, 0]])
    berr = np.array([1,0])
    print(simon_check_eqns(err1, berr))
    print(f"check the array to int translator...{berr}")
    print(arr_to_int(berr))
    print(simon_eqns_solver(err1, 2))


    #3. see if we can generate the right one:
    print("\n--------------------------------------\n")
    print(simon_eqns_solver(a, 3))
