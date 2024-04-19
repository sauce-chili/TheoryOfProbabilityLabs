from functools import reduce
from math import sqrt, pi, exp

from core.formulas.combinatorics import (
    combinations_without_rep as C,
    permutations_with_rep as rP
)


def bernoulli(p: float, n: int, min_successes: int, max_successes: int | None = None) -> float:
    if max_successes is None:
        max_successes = min_successes

    result = 0.0
    q = 1 - p
    for count_of_successes in range(min_successes, max_successes + 1):
        result += C(count_of_successes, n) * (p ** count_of_successes) * (q ** (n - count_of_successes))

    return result


def polynomial_distribution(n: int, m: list[float], p: list[float]) -> float:
    if len(m) != len(p):
        raise ValueError("Sizes of m and p must be equal")
    return rP(n, m) * reduce(lambda x, y: x * y, (p[i] ** m[i] for i in range(len(m))))


def local_moivre_laplace(x: float, n: int, p: float) -> float:
    return gauss(x) / sqrt(n * p * (1 - p))


def gauss(x: float) -> float:
    return (1 / sqrt(2 * pi)) * exp(-((x ** 2) / 2))
