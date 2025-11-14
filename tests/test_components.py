# AI-BEGIN
import pytest
from riscsim.utils.components import oneBitAdder


@pytest.mark.parametrize("a,b,carry_in,expected_sum,expected_carry", [
    (0, 0, 0, 0, 0),  # 0 + 0 + 0 = 0, carry 0
    (0, 0, 1, 1, 0),  # 0 + 0 + 1 = 1, carry 0
    (0, 1, 0, 1, 0),  # 0 + 1 + 0 = 1, carry 0
    (0, 1, 1, 0, 1),  # 0 + 1 + 1 = 0, carry 1
    (1, 0, 0, 1, 0),  # 1 + 0 + 0 = 1, carry 0
    (1, 0, 1, 0, 1),  # 1 + 0 + 1 = 0, carry 1
    (1, 1, 0, 0, 1),  # 1 + 1 + 0 = 0, carry 1
    (1, 1, 1, 1, 1),  # 1 + 1 + 1 = 1, carry 1
])
def test_one_bit_adder(a, b, carry_in, expected_sum, expected_carry):
    """Test the oneBitAdder function with various input combinations."""
    sum_bit, carry_out = oneBitAdder(a, b, carry_in)
    assert sum_bit == expected_sum
    assert carry_out == expected_carry
# AI-END
