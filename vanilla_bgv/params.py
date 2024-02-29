"""Parameter containers."""

from dataclasses import dataclass, field
import math

from vanilla_bgv import number_theory


@dataclass
class BGVParams:
    """Parameters for the BGV scheme.

    BGV Parameters correspond to:

    - A polynomial degree N, corresponding to the degree of X^N + 1
      in the polynomial ring used for RLWE ciphertexts. This parameters
      corresponds directly to the cryptographic security of the scheme.
    - A plaintext modulus t, a prime corresponding to the maximum size of a
      message input to the encryption.
    - A chain of moduli Q_0 dividing Q_1 dividing ... dividing Q_L, used for
      modulus switching. This parameter affects how (multiplicatively) deep the
      FHE circuits may be before bootstrapping is required. Making the number
      of moduli and their bit size larger increases the possible depth, at the
      expense of performance. Q_L = Q is the starting modulus of the ciphertext
      space. Increasing Q also reduces the security of the scheme, so
      increasing it must come with an increase in the polynomial degree N.

    Because the plaintext modulus, ciphertext modulus, and polynomial degree
    must be related according to some number theoretic properties, the user
    specifies the number of bits of the plaintext and ciphertext moduli, and
    the concrete parameter values are selected automatically.
    """

    poly_mod_degree: int  # referred to as N, a power of 2
    plaintext_coeff_modulus_num_bits: int  # ceil(log2(t))
    ciphertext_coeff_modulus_num_bits: int  # ceil(log2(Q))
    modulus_chain_length: int  # L + 1

    # TODO: pick a better default for error_stdev
    error_stdev: int = 1  # referred to as sigma_err

    # params below are initalized during post_init

    # referred to as t, a prime
    plaintext_coeff_modulus: int = 0

    # Q_0, ..., Q_L = Q, each Q_i divides Q_{i+1}
    ciphertext_moduli: list[int] = field(default_factory=list)

    # the primes used to construct ciphertext_moduli
    ciphertext_moduli_primes: list[int] = field(default_factory=list)

    @property
    def ciphertext_coeff_modulus(self):
        return self.ciphertext_moduli[-1]

    def __post_init__(self):
        self.plaintext_coeff_modulus = number_theory.find_ntt_prime(
            self.plaintext_coeff_modulus_num_bits, 2 * self.poly_mod_degree
        )

        self.ciphertext_moduli_primes = number_theory.find_ntt_primes(
            self.ciphertext_coeff_modulus_num_bits,
            2 * self.poly_mod_degree,
            qty=self.modulus_chain_length,
        )

        self.ciphertext_moduli = []
        q_i = 1
        for i in range(self.modulus_chain_length):
            q_i *= self.ciphertext_moduli_primes[i]
            self.ciphertext_moduli.append(q_i)

        # required to apply CRT decomposition of the plaintext
        assert self.plaintext_coeff_modulus % (2 * self.poly_mod_degree) == 1

        # required for modulus switching, computing various quantities in RNS
        for q_i in self.ciphertext_moduli:
            assert q_i > self.plaintext_coeff_modulus
            assert math.gcd(self.plaintext_coeff_modulus, q_i) == 1

        print(self)
