import math
import galois


def find_ntt_prime(num_bits: int, m: int) -> int:
    """Find the first prime q satisfying q = 1 mod m.

    Args:
      num_bits: the number of bits required in the result.
      m: the modulus of the required equivalence, should be a power of 2.

    Returns:
      The discovered prime, or raise a ValueError if none could be found.
    """
    # smallest k such that m*k + 1 has at least num_bits many bits.
    k = int(math.ceil((2**num_bits - 1) / m))
    current = m * k + 1
    while not galois.is_prime(current):
        current += m
    return current
