import math
import random
from hypothesis import given, settings
from hypothesis import strategies as st
import numpy as np
from vanilla_bgv import bgv
from vanilla_bgv import encoding


ERROR_FREE_TEST_PARAMS = bgv.BGVParams(
    poly_mod_degree=16,
    plaintext_coeff_modulus_num_bits=8,
    ciphertext_coeff_modulus_num_bits=16,
    modulus_chain_length=2,
    error_stdev=0,
)


@given(st.integers())
@settings(deadline=None)
def test_encrypt_decrypt_noise_free(seed):
    random.seed(seed)
    pk, sk, debug_data = bgv.gen_keys(ERROR_FREE_TEST_PARAMS)
    plaintext = np.arange(ERROR_FREE_TEST_PARAMS.poly_mod_degree)
    ct = bgv.encrypt(
        plaintext, pk=pk, params=ERROR_FREE_TEST_PARAMS, debug_data=debug_data
    )
    decrypted = bgv.decrypt(ct, sk=sk, params=ERROR_FREE_TEST_PARAMS)
    np.testing.assert_allclose(decrypted, plaintext, 1e-05)


def test_encrypt_decrypt_noise_free_with_encoding():
    random.seed(1)
    pk, sk, debug_data = bgv.gen_keys(ERROR_FREE_TEST_PARAMS)
    message = [1, 2, 3, 4]
    plaintext = encoding.encode(message, ERROR_FREE_TEST_PARAMS)
    ct = bgv.encrypt(
        plaintext, pk=pk, params=ERROR_FREE_TEST_PARAMS, debug_data=debug_data
    )
    decrypted = bgv.decrypt(ct, sk=sk, params=ERROR_FREE_TEST_PARAMS)
    actual = encoding.decode(decrypted, ERROR_FREE_TEST_PARAMS)
    assert message == actual[: len(message)], actual


def test_switch_modulus():
    # Just encrypt, modulus switch, and decrypt
    random.seed(1)
    params = ERROR_FREE_TEST_PARAMS
    pk, sk, debug_data = bgv.gen_keys(params)
    message = [1, 2, 3, 4]
    plaintext = encoding.encode(message, params)
    ct = bgv.encrypt(
        plaintext, pk=pk, params=params, debug_data=debug_data
    )
    # import ipdb; ipdb.set_trace()
    ct = bgv.switch_modulus(ct, params)
    decrypted = bgv.decrypt(ct, sk=sk, params=params)
    actual = encoding.decode(decrypted, params)
    assert message == actual[: len(message)], actual


@given(st.integers())
@settings(deadline=None)
def test_encrypt_decrypt_with_small_noise(seed):
    random.seed(seed)
    params = bgv.BGVParams(
        poly_mod_degree=16,
        plaintext_coeff_modulus_num_bits=8,
        ciphertext_coeff_modulus_num_bits=16,
        modulus_chain_length=2,
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
        ciphertext_coeff_modulus_num_bits=48,
        modulus_chain_length=1,
        error_stdev=2**7,
    )
    pk, sk, debug_data = bgv.gen_keys(params)
    message = [1, 2, 3, 4]
    plaintext = encoding.encode(message, params)
    ct = bgv.encrypt(plaintext, pk=pk, params=params, debug_data=debug_data)
    decrypted = bgv.decrypt(ct, sk=sk, params=params)
    actual = encoding.decode(decrypted, params)
    assert message == actual[: len(message)], actual


def test_add_noise_free():
    random.seed(1)
    pk, sk, debug_data = bgv.gen_keys(ERROR_FREE_TEST_PARAMS)
    m1 = [1, 2, 3, 4]
    m2 = [2, 3, 4, 5]
    pt1 = encoding.encode(m1, ERROR_FREE_TEST_PARAMS)
    pt2 = encoding.encode(m2, ERROR_FREE_TEST_PARAMS)
    ct1 = bgv.encrypt(pt1, pk=pk, params=ERROR_FREE_TEST_PARAMS, debug_data=debug_data)
    ct2 = bgv.encrypt(pt2, pk=pk, params=ERROR_FREE_TEST_PARAMS, debug_data=debug_data)
    ct3 = bgv.add(ct1, ct2, params=ERROR_FREE_TEST_PARAMS)
    decrypted = bgv.decrypt(ct3, sk=sk, params=ERROR_FREE_TEST_PARAMS)
    actual = encoding.decode(decrypted, ERROR_FREE_TEST_PARAMS)
    assert [3, 5, 7, 9] == actual[: len(m1)], actual


def test_add_noisy():
    random.seed(1)
    params = bgv.BGVParams(
        poly_mod_degree=16,
        plaintext_coeff_modulus_num_bits=8,
        ciphertext_coeff_modulus_num_bits=48,
        modulus_chain_length=1,
        error_stdev=5,
    )
    pk, sk, debug_data = bgv.gen_keys(params)
    m1 = [1, 2, 3, 4]
    m2 = [2, 3, 4, 5]
    pt1 = encoding.encode(m1, params)
    pt2 = encoding.encode(m2, params)
    ct1 = bgv.encrypt(pt1, pk=pk, params=params, debug_data=debug_data)
    ct2 = bgv.encrypt(pt2, pk=pk, params=params, debug_data=debug_data)
    ct3 = bgv.add(ct1, ct2, params=params)
    decrypted = bgv.decrypt(ct3, sk=sk, params=params)
    actual = encoding.decode(decrypted, params)
    assert [3, 5, 7, 9] == actual[: len(m1)], actual


def test_iterated_add_noisy():
    # test how many times you can add before it fails to decrypt
    random.seed(1)
    params = bgv.BGVParams(
        poly_mod_degree=16,
        plaintext_coeff_modulus_num_bits=8,
        ciphertext_coeff_modulus_num_bits=13,
        modulus_chain_length=2,
        error_stdev=5,
    )
    pk, sk, debug_data = bgv.gen_keys(params)

    # fails at 256
    iters = 255
    m1 = [1, 2, 3, 4]
    pt1 = encoding.encode(m1, params)
    ct1 = bgv.encrypt(pt1, pk=pk, params=params, debug_data=debug_data)

    m2 = [1, 2, 3, 4]
    pt2 = encoding.encode(m2, params)
    ct2 = bgv.encrypt(pt2, pk=pk, params=params, debug_data=debug_data)

    ct = ct1
    expected = m1
    max_error = math.log2(
        params.ciphertext_coeff_modulus / (2 * params.plaintext_coeff_modulus) - 0.5
    )
    for i in range(iters):
        ct = bgv.add(ct, ct2, params=params)
        expected = [
            (x + y) % params.plaintext_coeff_modulus for x, y in zip(expected, m2)
        ]
        expected_pt = encoding.encode(expected, params)
        error_so_far = math.log2(
            bgv.extract_error_magnitude(ct, expected_pt, sk, params)
        )
        # run with `pytest -s` to see the print statements the largest will
        # look something like
        #
        #    i=254, error_so_far=13.279, max_error=13.749.
        #
        # The bound from https://eprint.iacr.org/2021/204 appears slightly too
        # loose, since setting iters=256 still meets the bound at 13.7488, but
        # decryption fails. But there's a good chance my implementation is also
        # slightly wrong.
        print(f"{i=}, {error_so_far=}, {max_error=}")

    decrypted = bgv.decrypt(ct, sk=sk, params=params)
    actual = encoding.decode(decrypted, params)
    assert expected == actual[: len(m1)], actual
