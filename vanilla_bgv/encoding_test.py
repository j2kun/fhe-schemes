import galois
from hypothesis import given, settings
from hypothesis import strategies as st
from vanilla_bgv.encoding import decode, encode
from vanilla_bgv.params import BGVParams

PRIME_32_BITS = 3349476853


def test_encode_decode():
  input = [1, 2, 3]
  params = BGVParams(
      poly_mod_degree=1024,
      plaintext_coeff_modulus=PRIME_32_BITS,
  )
  actual = decode(encode(input, params), params)
  # the input is zero-padded to size 1024
  assert actual[: len(input)] == input


@given(
    st.integers(min_value=4, max_value=128),
    st.integers(min_value=4, max_value=16),
    st.integers(),
)
@settings(deadline=None)  # numba jit compilation is slow on first run
def test_encode_decode_hypothesis(
    coeff_modulus_num_bits, log2_poly_mod_degree, prime_seed
):
  poly_mod_degree = 2**log2_poly_mod_degree
  coeff_modulus = galois.random_prime(
      bits=coeff_modulus_num_bits, seed=prime_seed
  )
  params = BGVParams(
      poly_mod_degree=poly_mod_degree,
      plaintext_coeff_modulus=coeff_modulus,
  )
  input = list(range(poly_mod_degree))
  actual = decode(encode(input, params), params)
  assert actual[: len(input)] == input
