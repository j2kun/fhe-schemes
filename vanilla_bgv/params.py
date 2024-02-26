"""Parameter containers."""
import math
from dataclasses import dataclass

from vanilla_bgv import number_theory


@dataclass
class BGVParams:
    """Parameters for the BGV scheme."""

    poly_mod_degree: int  # referred to as N, a power of 2
    plaintext_coeff_modulus_num_bits: int  # ceil(log2(t))
    ciphertext_coeff_modulus: int  # referred to as Q

    # TODO: pick a better default for error_stdev
    error_stdev: int = 1  # referred to as sigma_err

    # params below are initalized during post_init
    plaintext_coeff_modulus: int = 0  # referred to as t, a prime

    def __post_init__(self):
        self.plaintext_coeff_modulus = number_theory.find_ntt_prime(
            self.plaintext_coeff_modulus_num_bits, 2 * self.poly_mod_degree
        )

        # required to apply CRT decomposition of the plaintext
        assert self.plaintext_coeff_modulus % (2 * self.poly_mod_degree) == 1

        # required for modulus switching, computing various quantities in RNS
        assert self.ciphertext_coeff_modulus > self.plaintext_coeff_modulus
        assert (
            math.gcd(self.plaintext_coeff_modulus, self.ciphertext_coeff_modulus) == 1
        )
