import random
import numpy as np

from hypothesis import given, settings
from hypothesis import strategies as st

from vanilla_bgv import bgv
from vanilla_bgv import encoding


ERROR_FREE_TEST_PARAMS = bgv.BGVParams(
    poly_mod_degree=16,
    plaintext_coeff_modulus_num_bits=16,
    ciphertext_coeff_modulus=2659 * 2663,
    error_stdev=0,
)

@given(st.integers())
@settings(deadline=None)
def test_encrypt_decrypt_noise_free(seed):
    random.seed(seed)
    pk, sk, debug_data = bgv.gen_keys(ERROR_FREE_TEST_PARAMS)
    plaintext = np.arange(ERROR_FREE_TEST_PARAMS.poly_mod_degree)
    ct = bgv.encrypt(plaintext, pk=pk, params=ERROR_FREE_TEST_PARAMS, debug_data=debug_data)
    decrypted = bgv.decrypt(ct, sk=sk, params=ERROR_FREE_TEST_PARAMS)
    np.testing.assert_allclose(decrypted, plaintext, 1e-05)


def test_encrypt_decrypt_noise_free_with_encoding():
    random.seed(1)
    pk, sk, debug_data = bgv.gen_keys(ERROR_FREE_TEST_PARAMS)
    message = [1, 2, 3, 4]
    plaintext = encoding.encode(message, ERROR_FREE_TEST_PARAMS)
    ct = bgv.encrypt(plaintext, pk=pk, params=ERROR_FREE_TEST_PARAMS, debug_data=debug_data)
    decrypted = bgv.decrypt(ct, sk=sk, params=ERROR_FREE_TEST_PARAMS)
    actual = encoding.decode(decrypted, ERROR_FREE_TEST_PARAMS)
    assert message == actual[: len(message)], actual


@given(st.integers())
@settings(deadline=None)
def test_encrypt_decrypt_with_small_noise(seed):
    random.seed(seed)
    params = bgv.BGVParams(
        poly_mod_degree=16,
        plaintext_coeff_modulus_num_bits=16,
        ciphertext_coeff_modulus=2659 * 2663,
        error_stdev=5,
    )
    pk, sk, debug_data = bgv.gen_keys(params)
    message = [1, 2, 3, 4]
    plaintext = encoding.encode(message, params)
    ct = bgv.encrypt(plaintext, pk=pk, params=params, debug_data=debug_data)
    decrypted = bgv.decrypt(ct, sk=sk, params=params)
    actual = encoding.decode(decrypted, params)
    assert message == actual[: len(message)], actual


def test_encrypt_decrypt_with_large_noise():
    random.seed(1)
    params = bgv.BGVParams(
        poly_mod_degree=2048,
        plaintext_coeff_modulus_num_bits=32,
        ciphertext_coeff_modulus=242744763933053,   # a 48-bit prime
        error_stdev=2**7,
    )
    pk, sk, debug_data = bgv.gen_keys(params)
    message = [1, 2, 3, 4]
    plaintext = encoding.encode(message, params)
    ct = bgv.encrypt(plaintext, pk=pk, params=params, debug_data=debug_data)
    decrypted = bgv.decrypt(ct, sk=sk, params=params)
    actual = encoding.decode(decrypted, params)
    assert message == actual[: len(message)], actual
