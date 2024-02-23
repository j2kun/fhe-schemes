"""Routines for encoding and decoding messages as RLWE plaintexts for BGV.

In BGV the plaintext space is the ring of polynomials

    (Z/tZ)[x]/(x^N + 1)

where N is a power of 2 and t > 2 is a prime.
"""

import galois
import numpy as np
from vanilla_bgv import number_theory
from vanilla_bgv.params import BGVParams
from vanilla_bgv.types import Plaintext


def encode(message: list[int], params: BGVParams) -> np.ndarray:
    """Encode a message as a polynomial in the plaintext space."""
    prime_field = galois.GF(params.ntt_modulus)
    evaluation_points = prime_field(message)

    # Do an inverse ntt because the inputs ints are interpreted as evaluations of
    # the polynomial at the ntt evaluation points.
    return galois.intt(
        evaluation_points,
        size=params.poly_mod_degree,
        modulus=params.ntt_modulus,
    )


def decode(plaintext: Plaintext, params: BGVParams) -> list[int]:
    """Decode a message to a list of integers."""
    prime_field = galois.GF(params.ntt_modulus)
    return galois.ntt(
        plaintext,
        size=params.poly_mod_degree,
        modulus=params.ntt_modulus,
    ).tolist()
