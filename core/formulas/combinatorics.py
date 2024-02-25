from math import factorial
from functools import reduce


def permutation_with_rep(*k) -> int:
    kp = reduce(lambda x, y: x * y, map(factorial, k))
    return factorial(sum(k)) // kp


def permutation_without_rep(n: int) -> int:
    return factorial(n)


def permutations_with_rep(n, m: list) -> int:
    if n != sum(m):
        raise ValueError("The sum m1 + m2 + ... + mk should be equal to n")
    mul_of_fact = reduce(lambda x, y: x * y, map(factorial, m))
    return factorial(n) // mul_of_fact


def accommodations_with_rep(m: int, n: int) -> int:
    return int(n ** m)


def placement_without_rep(k: int, n: int) -> int:
    if k <= n:
        ValueError("Number n must be greater than k")
    return factorial(n) // factorial(n - k)


def combinations_without_rep(m: int, n: int) -> int:
    if m > n:
        raise ValueError("Number n must be greater than m")

    return factorial(n) // (factorial(n - m) * factorial(m))


def combinations_with_rep(k: int, n: int) -> int:
    return combinations_without_rep(k, n + k - 1)
