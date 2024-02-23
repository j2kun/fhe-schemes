"""Parameter containers."""

from dataclasses import dataclass
from functools import cached_property
import math
from vanilla_bgv import number_theory


@dataclass(frozen=True)
class BGVParams:
    """Parameters for the BGV scheme."""

    poly_mod_degree: int  # referred to as N, a power of 2
    plaintext_coeff_modulus: int  # referred to as t, a prime

    @cached_property
    def encoding_ntt_modulus(self):
        """Find a prime q = 1 (mod 2N), the NTT modulus for plaintext encoding."""
        num_bits = int(math.ceil(math.log2(self.plaintext_coeff_modulus)))
        return number_theory.find_ntt_prime(num_bits, 2 * self.poly_mod_degree)
