from hypothesis import given, settings
from hypothesis import strategies as st
from vanilla_bgv.encoding import decode, encode
from vanilla_bgv.params import BGVParams


TEST_PARAMS = BGVParams(
    poly_mod_degree=2**4,
    plaintext_coeff_modulus_num_bits=8,
    ciphertext_coeff_modulus_num_bits=32,
    modulus_chain_length=2,
)


def test_encode_decode():
    input = [1, 2, 3]
    actual = decode(encode(input, TEST_PARAMS), TEST_PARAMS)
    # the input is zero-padded to size 1024
    assert actual[: len(input)] == input


@given(
    st.integers(min_value=4, max_value=16),
    st.integers(min_value=4, max_value=8),
    st.integers(),
)
@settings(deadline=None)  # numba jit compilation is slow on first run
def test_encode_decode_hypothesis(
    coeff_modulus_num_bits, log2_poly_mod_degree, prime_seed
):
    poly_mod_degree = 2**log2_poly_mod_degree
    params = BGVParams(
        poly_mod_degree=poly_mod_degree,
        plaintext_coeff_modulus_num_bits=coeff_modulus_num_bits,
        ciphertext_coeff_modulus_num_bits=32,
        modulus_chain_length=2,
    )
    input = list(range(poly_mod_degree))
    actual = decode(encode(input, params), params)
    assert actual[: len(input)] == input


def test_encoded_coefficients_are_in_signed_half_range():
    poly_mod_degree = 2**4
    input = list(range(poly_mod_degree))
    actual = encode(input, TEST_PARAMS)
    assert actual.min() >= -TEST_PARAMS.plaintext_coeff_modulus // 2, actual
    assert actual.max() < TEST_PARAMS.plaintext_coeff_modulus // 2, actual
