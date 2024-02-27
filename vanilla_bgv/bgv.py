"""The BGV homomorphic encryption scheme."""
import math
from typing import Optional

import numpy as np

from vanilla_bgv import encoding
from vanilla_bgv import types
from vanilla_bgv.number_theory import polymul
from vanilla_bgv.params import BGVParams


# None of these random samples are cryptographically secure!
def key_sample(size):
    """Sample from the secret key distribution."""
    return np.random.randint(
        -1, 2, size=size, dtype=np.int64
    )  # sampling from {-1, 0, 1}


def error_sample(params, size):
    """Sample from the error distribution."""
    return np.round(np.random.normal(0, params.error_stdev, size=size)).astype(np.int64)


def gen_keys(
    params: BGVParams,
) -> tuple[types.PublicKey, types.SecretKey, types.DebugData]:
    """Generate BGV public and secret keys."""
    N = params.poly_mod_degree
    t = params.plaintext_coeff_modulus

    sk = key_sample(N)
    sample = np.random.randint(0, params.ciphertext_coeff_modulus, N)
    error = error_sample(params, N)

    pk = (
        np.mod(polymul(sample, sk) + t * error, params.ciphertext_coeff_modulus),
        np.mod(-sample, params.ciphertext_coeff_modulus),
    )

    debug_data = types.DebugData(pk_error_sample=error, secret_key=sk)
    return (pk, sk, debug_data)


def encrypt(
    pt: types.Plaintext,
    pk: types.PublicKey,
    params: BGVParams,
    debug_data: Optional[types.DebugData] = None,
) -> types.Ciphertext:
    """Encrypt a plaintext."""
    N = params.poly_mod_degree
    u = key_sample(N)
    t = params.plaintext_coeff_modulus
    Q = params.ciphertext_coeff_modulus
    error = (error_sample(params, N), error_sample(params, N))
    a_0 = np.mod(pt + polymul(pk[0], u) + t * error[0], Q)
    a_1 = np.mod(polymul(pk[1], u) + t * error[1], Q)

    if debug_data:
        error_fresh = (
            polymul(u, debug_data.pk_error_sample)
            + polymul(error[1], debug_data.secret_key)
            + error[0]
        )
        initial_noise = np.max(np.abs(error_fresh))
        if initial_noise > 0:
            # If the noise is below this bound, the decryption will succeed
            # This is asserted here to help debug tests where the parameters
            # are incorrectly set so that the initial noise is too large.
            initial_noise_bound = Q / (2 * t) - 0.5
            initial_noise_bound_bits = math.log2(initial_noise_bound)
            initial_noise_bits = math.log2(initial_noise)
            print(
                f"{initial_noise_bits=} < {initial_noise_bound_bits=}"
            )
            assert initial_noise < initial_noise_bound, "Initial noise is too large!"

    return (a_0, a_1)


def decrypt(
    ct: types.Ciphertext,
    sk: types.SecretKey,
    params: BGVParams,
) -> types.Plaintext:
    """Decrypt a ciphertext."""
    return encoding.to_signed_half_range(
        encoding.to_signed_half_range(
            ct[0] + polymul(ct[1], sk), params.ciphertext_coeff_modulus
        ),
        params.plaintext_coeff_modulus,
    )
