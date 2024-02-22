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
  def ntt_modulus(self):
    num_bits = int(math.ceil(math.log2(self.plaintext_coeff_modulus)))
    return number_theory.find_ntt_prime(num_bits, self.poly_mod_degree)
