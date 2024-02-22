"""Parameter containers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BGVParams:
  """Parameters for the BGV scheme."""

  poly_mod_degree: int  # referred to as N, a power of 2
  plaintext_coeff_modulus: int  # referred to as t, a prime
