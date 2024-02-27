"""Type definitions for BGV."""
from dataclasses import dataclass
import numpy as np

# A plaintext is a single polynomial. The values of this array are coefficients
# of a polynomial whose evaluations at a specific set of points are the
# contents of the message.
#
# The coefficients are elements of the field Z/tZ, where t is prime.
#
# The "specific set of points" are the powers of a primitive 2N-th root of
# unity determined by the NTT modulus in BGVParams. For simplicity, the modulus
# used for the NTT encodings of a plaintext and the plaintext coefficient
# modulus are the same in this implementation.
Plaintext = np.ndarray

# A secret key is a single polynomial whose coefficients come from Z/QZ, where
# Q is the ciphertext coefficient modulus from BGVParams. The coefficients are
# known to be uniformly random, sampled from the set {-1, 0, 1}.
SecretKey = np.ndarray

# A public key is a pair of polynomials with coefficients in Z/QZ.
PublicKey = tuple[np.ndarray, np.ndarray]

# A ciphertext is a pair of polynomials with coefficients in Z/QZ.
Ciphertext = tuple[np.ndarray, np.ndarray]


# Debug data for learning purposes: allows us to see intermediate noise values
# and assert the correctness of various steps of the implementation.
@dataclass
class DebugData:
    """Debug data for BGV operations."""

    pk_error_sample: np.ndarray
    secret_key: np.ndarray
