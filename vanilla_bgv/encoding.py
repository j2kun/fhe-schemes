"""Routines for encoding and decoding messages as RLWE plaintexts for BGV.

In BGV the plaintext space is the ring of polynomials

    (Z/tZ)[x]/(x^N + 1)

where N is a power of 2 and t > 2 is a prime.
"""

import galois
import numpy as np
from vanilla_bgv.params import BGVParams
from vanilla_bgv.types import Plaintext


def to_signed_half_range(x: np.ndarray, modulus: int) -> np.ndarray:
    """Map an integer to the signed half range of the modulus."""
    x = np.mod(x, modulus)
    return np.where(x >= modulus // 2, x - modulus, x)


def from_signed_half_range(x: np.ndarray, modulus: int) -> np.ndarray:
    """Map an integer from the signed half range of the modulus."""
    x = np.mod(x, modulus)
    return np.where(x < 0, x + modulus, x)


def encode(message: list[int], params: BGVParams) -> Plaintext:
    """Encode a message as a polynomial in the plaintext space."""
    prime_field = galois.GF(params.plaintext_coeff_modulus)
    evaluation_points = prime_field(message)

    # Do an inverse ntt because the inputs ints are interpreted as evaluations
    # of the polynomial at the ntt evaluation points. This is to ensure that
    # taking a product of the polynomials (in coefficient form) corresponds to
    # taking an entry-wise product of the underlying messages. Otherwise this
    # product would be equivalent to a convolution of the messages, which is
    # less useful.
    poly = np.array(
        galois.intt(
            evaluation_points,
            size=params.poly_mod_degree,
            modulus=params.plaintext_coeff_modulus,
        ),
        dtype=np.int64,
    )
    return to_signed_half_range(poly, params.plaintext_coeff_modulus)


def decode(plaintext: Plaintext, params: BGVParams) -> list[int]:
    """Decode a message to a list of integers."""
    prime_field = galois.GF(params.plaintext_coeff_modulus)
    coefficients = prime_field(
        from_signed_half_range(plaintext, params.plaintext_coeff_modulus)
    )
    return galois.ntt(
        coefficients,
        size=params.poly_mod_degree,
        modulus=params.plaintext_coeff_modulus,
    ).tolist()
