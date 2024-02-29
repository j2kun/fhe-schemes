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
            initial_noise_bound = debug_data.error_bound(params)
            initial_noise_bound_bits = math.log2(initial_noise_bound)
            initial_noise_bits = math.log2(initial_noise)
            print(f"{initial_noise_bits=} < {initial_noise_bound_bits=}")
            assert initial_noise < initial_noise_bound, "Initial noise is too large!"

    return types.Ciphertext(
        polynomials=(a_0, a_1),
        # every ciphertext starts at the highest modulus in the chain,
        # and is lowered to smaller moduli during modulus switching.
        modulus_index=params.modulus_chain_length - 1,
    )


def decrypt(
    ct: types.Ciphertext,
    sk: types.SecretKey,
    params: BGVParams,
) -> types.Plaintext:
    """Decrypt a ciphertext."""
    polys = ct.polynomials
    return encoding.to_signed_half_range(
        encoding.to_signed_half_range(
            polys[0] + polymul(polys[1], sk), params.ciphertext_coeff_modulus
        ),
        params.plaintext_coeff_modulus,
    )


def extract_error_magnitude(
    ct: types.Ciphertext,
    pt: types.Plaintext,
    sk: types.SecretKey,
    params: BGVParams,
) -> types.Plaintext:
    """Decrypt the ciphertext and extract the error part."""
    # Using the notation from https://eprint.iacr.org/2021/204, p6 equation (1)
    # compute m' = [m]_t + tv_fresh mod Q_L (here Q_L = Q is the ciphertext
    # modulus), then subtract off [m]_t and divide by t
    polys = ct.polynomials
    m_prime = encoding.to_signed_half_range(
        polys[0] + polymul(polys[1], sk), params.ciphertext_coeff_modulus
    )
    error_times_t = m_prime - pt
    rescaled_error = error_times_t // params.plaintext_coeff_modulus
    return np.max(np.abs(rescaled_error))


def add(
    ct1: types.Ciphertext,
    ct2: types.Ciphertext,
    params: BGVParams,
) -> types.Ciphertext:
    """Add two ciphertexts."""
    if ct1.modulus_index != ct2.modulus_index:
        raise ValueError(
            "Expected input ciphertexts to have the same "
            f"moduli, but found {ct1.modulus_index=} != "
            f"{ct2.modulus_index=}"
        )

    polys1 = ct1.polynomials
    polys2 = ct2.polynomials
    added_polys = (
        np.mod(polys1[0] + polys2[0], params.ciphertext_coeff_modulus),
        np.mod(polys1[1] + polys2[1], params.ciphertext_coeff_modulus),
    )
    return types.Ciphertext(
        polynomials=added_polys,
        modulus_index=ct1.modulus_index,
    )
