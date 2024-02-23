from hypothesis import given
from hypothesis import strategies as st
from vanilla_bgv.number_theory import find_ntt_prime


def test_find_ntt_prime():
    num_bits = 4
    m = 8
    assert find_ntt_prime(num_bits, m) == 17


@given(
    st.integers(min_value=4, max_value=128),
    st.integers(min_value=5, max_value=32),
)
def test_find_ntt_prime_satisfies_modulus_req(num_bits, log2_m):
    m = 2**log2_m
    actual = find_ntt_prime(num_bits, m)
    assert actual % m == 1
