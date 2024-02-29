import numpy as np
from hypothesis import given
from hypothesis import strategies as st
from vanilla_bgv.number_theory import find_ntt_prime, find_ntt_primes, polymul, inverse
import galois
import numpy as np


def test_find_ntt_prime():
    num_bits = 4
    m = 8
    assert find_ntt_prime(num_bits, m) == 17


@given(
    st.integers(min_value=4, max_value=128),
    st.integers(min_value=5, max_value=32),
)
def test_find_ntt_prime_satisfies_modulus_req(num_bits, log2_m):
    m = 2**log2_m
    actual = find_ntt_prime(num_bits, m)
    assert actual % m == 1


@given(
    st.integers(min_value=4, max_value=128),
    st.integers(min_value=5, max_value=32),
)
def test_find_ntt_primes_all_distinct(num_bits, log2_m):
    m = 2**log2_m
    actual = find_ntt_primes(num_bits, m, qty=5)
    assert len(set(actual)) == len(actual)


def _np_polymul_mod(poly1, poly2, poly_mod):
    # Reversing the list order because numpy polymul interprets the polynomial
    # with higher-order coefficients first, whereas our code does the opposite
    np_mul = np.polymul(list(reversed(poly1)), list(reversed(poly2)))
    (_, np_poly_mod) = np.polydiv(np_mul, poly_mod)
    np_pad = np.pad(
        np_poly_mod,
        (len(poly1) - len(np_poly_mod), 0),
        "constant",
        constant_values=(0, 0),
    )
    return np.array(list(reversed(np_pad)), dtype=np.int32)


def _np_negacyclic_polymul(poly1, poly2):
    # a reference implementation for negacyclic polynomial multiplication
    # poly_mod represents the polynomial to divide by: x^N + 1, N = len(a)
    poly_mod = np.zeros(len(poly1) + 1, np.uint32)
    poly_mod[0] = 1
    poly_mod[len(poly1)] = 1
    return _np_polymul_mod(poly1, poly2, poly_mod)


N = 16


@given(
    st.lists(st.integers(min_value=-100, max_value=100), min_size=N, max_size=N),
    st.lists(st.integers(min_value=-100, max_value=100), min_size=N, max_size=N),
)
def test_negacyclic_polymul(p1, p2):
    p1 = np.array(p1)
    p2 = np.array(p2)
    expected = _np_negacyclic_polymul(p1, p2)
    actual = polymul(p1, p2)
    np.testing.assert_array_equal(expected, actual)


@given(st.integers(min_value=7, max_value=16))
def test_multiplicative_inverse(num_bits):
    prime = galois.random_prime(bits=num_bits, seed=1)
    for x in range(1, prime):
        actual = inverse(x, prime)
        assert (actual * x) % prime == 1
