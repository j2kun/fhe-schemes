import math
import galois
import numpy as np


def find_ntt_primes(num_bits: int, m: int, qty: int) -> list[int]:
    """Find the first qyt primes q_i satisfying q_i = 1 mod m.

    Args:
      num_bits: the number of bits required in the result.
      m: the modulus of the required equivalence.
      qty: the number of primes to return.

    Returns:
      The discovered primes, or raise a ValueError if none could be found.
    """
    # smallest k such that m*k + 1 has at least num_bits many bits.
    primes: list[int] = []
    k = int(math.ceil((2**num_bits - 1) / m))
    current = m * k + 1
    while len(primes) < qty:
        if galois.is_prime(current):
            primes.append(current)
        current += m
    return primes


def find_ntt_prime(num_bits: int, m: int) -> int:
    """Find the first prime q satisfying q = 1 mod m.

    Args:
      num_bits: the number of bits required in the result.
      m: the modulus of the required equivalence.

    Returns:
      The discovered prime, or raise a ValueError if none could be found.
    """
    return find_ntt_primes(num_bits, m, 1)[0]


def wrapping_convolve(a, b):
    """Implement a wrapping convolution using numpy.convolve.

    Numpy doesn't have a wrapping option, so this requires repeating
    the coefficients of at least one of the input arrays.

    Also note that, because the "valid" mode computes a convolution only when the
    windows fully overlap, the first and last values are the same and should
    correspond to the very last value in the output. Hence the final slicing step.
    """
    conv_result = np.convolve(a, np.tile(b, 2), mode="valid")
    return conv_result[1:]


def negacyclic_polymul_preimage_and_map_back_conv(p1, p2):
    """Multiply two polynomials modulo (x^N + 1).

    Same as negacyclic_polymul_preimage_and_map_back,
    but uses a convolution operation instead of an FFT.
    """
    p1_preprocessed = np.concatenate([p1, -p1])
    p2_preprocessed = np.concatenate([p2, -p2])
    product = wrapping_convolve(p1_preprocessed, p2_preprocessed)
    return (product[: p1.shape[0]] - product[p1.shape[0] :]) // 4


def polymul(p1, p2):
    """Compute the negacyclic polynomial product of p1 and p2."""
    return negacyclic_polymul_preimage_and_map_back_conv(p1, p2)


def inverse(n, modulus):
    """Compute the multiplicative inverse of n by the given modulus."""
    _, m, _ = galois.egcd(n, modulus)
    return m
