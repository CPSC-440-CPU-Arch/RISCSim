"""
Test suite for IEEE-754 Float32 Floating-Point Unit

Tests pack/unpack, arithmetic operations (add, sub, mul), special values,
and exception flags according to IEEE-754 standard.
"""

import pytest
import math
from riscsim.cpu.fpu import (
    pack_f32, unpack_f32, fadd_f32, fsub_f32, fmul_f32,
    extract_float32_fields, pack_float32_fields, is_special_value
)
from riscsim.utils.bit_utils import bits_to_hex_string, hex_string_to_bits


# Helper functions for testing
def float_to_bits(value):
    """Convert Python float to IEEE-754 bits (wrapper for pack_f32)."""
    return pack_f32(value)


def bits_to_float(bits):
    """Convert IEEE-754 bits to Python float (wrapper for unpack_f32)."""
    return unpack_f32(bits)


def hex_to_bits32(hex_str):
    """Convert hex string to 32-bit array."""
    return hex_string_to_bits(hex_str, 32)


def approx_equal(a, b, rel_tol=1e-6, abs_tol=1e-9):
    """Check if two floats are approximately equal."""
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class TestPackUnpack:
    """Test IEEE-754 pack and unpack functions."""

    def test_pack_positive_zero(self):
        """Pack +0.0 should give all zeros."""
        bits = pack_f32(0.0)
        assert bits_to_hex_string(bits) == "0x00000000"

    def test_pack_negative_zero(self):
        """Pack -0.0 should have sign bit set."""
        bits = pack_f32(-0.0)
        assert bits_to_hex_string(bits) == "0x80000000"

    def test_pack_one(self):
        """Pack 1.0 should give 0x3F800000."""
        bits = pack_f32(1.0)
        assert bits_to_hex_string(bits) == "0x3F800000"

    def test_pack_negative_one(self):
        """Pack -1.0 should give 0xBF800000."""
        bits = pack_f32(-1.0)
        assert bits_to_hex_string(bits) == "0xBF800000"

    def test_pack_two(self):
        """Pack 2.0 should give 0x40000000."""
        bits = pack_f32(2.0)
        assert bits_to_hex_string(bits) == "0x40000000"

    def test_pack_three_point_seven_five(self):
        """Pack 3.75 should give 0x40700000."""
        bits = pack_f32(3.75)
        assert bits_to_hex_string(bits) == "0x40700000"

    def test_pack_positive_infinity(self):
        """Pack +inf should give 0x7F800000."""
        bits = pack_f32(float('inf'))
        assert bits_to_hex_string(bits) == "0x7F800000"

    def test_pack_negative_infinity(self):
        """Pack -inf should give 0xFF800000."""
        bits = pack_f32(float('-inf'))
        assert bits_to_hex_string(bits) == "0xFF800000"

    def test_pack_nan(self):
        """Pack NaN should have exp=255 and non-zero fraction."""
        bits = pack_f32(float('nan'))
        sign, exp, frac = extract_float32_fields(bits)
        assert all(e == 1 for e in exp)  # exp = 255
        assert any(f == 1 for f in frac)  # frac != 0

    def test_unpack_positive_zero(self):
        """Unpack 0x00000000 should give +0.0."""
        bits = hex_to_bits32("0x00000000")
        value = unpack_f32(bits)
        assert value == 0.0

    def test_unpack_one(self):
        """Unpack 0x3F800000 should give 1.0."""
        bits = hex_to_bits32("0x3F800000")
        value = unpack_f32(bits)
        assert value == 1.0

    def test_unpack_three_point_seven_five(self):
        """Unpack 0x40700000 should give 3.75."""
        bits = hex_to_bits32("0x40700000")
        value = unpack_f32(bits)
        assert value == 3.75

    def test_unpack_positive_infinity(self):
        """Unpack 0x7F800000 should give +inf."""
        bits = hex_to_bits32("0x7F800000")
        value = unpack_f32(bits)
        assert math.isinf(value) and value > 0

    def test_unpack_negative_infinity(self):
        """Unpack 0xFF800000 should give -inf."""
        bits = hex_to_bits32("0xFF800000")
        value = unpack_f32(bits)
        assert math.isinf(value) and value < 0

    def test_unpack_nan(self):
        """Unpack NaN should give NaN."""
        bits = hex_to_bits32("0x7FC00000")  # Canonical NaN
        value = unpack_f32(bits)
        assert math.isnan(value)

    def test_roundtrip_positive_values(self):
        """Test pack/unpack roundtrip for various positive values."""
        test_values = [0.0, 1.0, 2.0, 0.5, 0.25, 10.0, 100.0, 1000.0]
        for val in test_values:
            bits = pack_f32(val)
            recovered = unpack_f32(bits)
            assert approx_equal(recovered, val), f"Failed for {val}"

    def test_roundtrip_negative_values(self):
        """Test pack/unpack roundtrip for various negative values."""
        test_values = [-1.0, -2.0, -0.5, -10.0, -100.0]
        for val in test_values:
            bits = pack_f32(val)
            recovered = unpack_f32(bits)
            assert approx_equal(recovered, val), f"Failed for {val}"


class TestSpecialValues:
    """Test detection and handling of special values."""

    def test_detect_positive_zero(self):
        """Detect +0 correctly."""
        bits = pack_f32(0.0)
        sign, exp, frac = extract_float32_fields(bits)
        is_zero, is_inf, is_nan, is_subn = is_special_value(exp, frac)
        assert is_zero is True
        assert sign == 0

    def test_detect_negative_zero(self):
        """Detect -0 correctly."""
        bits = pack_f32(-0.0)
        sign, exp, frac = extract_float32_fields(bits)
        is_zero, is_inf, is_nan, is_subn = is_special_value(exp, frac)
        assert is_zero is True
        assert sign == 1

    def test_detect_positive_infinity(self):
        """Detect +inf correctly."""
        bits = pack_f32(float('inf'))
        sign, exp, frac = extract_float32_fields(bits)
        is_zero, is_inf, is_nan, is_subn = is_special_value(exp, frac)
        assert is_inf is True
        assert sign == 0

    def test_detect_negative_infinity(self):
        """Detect -inf correctly."""
        bits = pack_f32(float('-inf'))
        sign, exp, frac = extract_float32_fields(bits)
        is_zero, is_inf, is_nan, is_subn = is_special_value(exp, frac)
        assert is_inf is True
        assert sign == 1

    def test_detect_nan(self):
        """Detect NaN correctly."""
        bits = pack_f32(float('nan'))
        sign, exp, frac = extract_float32_fields(bits)
        is_zero, is_inf, is_nan, is_subn = is_special_value(exp, frac)
        assert is_nan is True

    def test_normal_value_not_special(self):
        """Normal values should not be detected as special."""
        bits = pack_f32(1.5)
        sign, exp, frac = extract_float32_fields(bits)
        is_zero, is_inf, is_nan, is_subn = is_special_value(exp, frac)
        assert is_zero is False
        assert is_inf is False
        assert is_nan is False


class TestFloatAddition:
    """Test IEEE-754 floating-point addition."""

    def test_add_simple_positives(self):
        """Test 1.0 + 2.0 = 3.0."""
        a = pack_f32(1.0)
        b = pack_f32(2.0)
        result_dict = fadd_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert approx_equal(result, 3.0)

    def test_add_example_from_spec(self):
        """Test 1.5 + 2.25 = 3.75 (expected 0x40700000)."""
        a = pack_f32(1.5)
        b = pack_f32(2.25)
        result_dict = fadd_f32(a, b)
        result_bits = result_dict['result']
        assert bits_to_hex_string(result_bits) == "0x40700000"
        result_val = unpack_f32(result_bits)
        assert approx_equal(result_val, 3.75)

    def test_add_zero_identity(self):
        """Test x + 0 = x."""
        a = pack_f32(5.5)
        b = pack_f32(0.0)
        result_dict = fadd_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert approx_equal(result, 5.5)

    def test_add_positive_zeros(self):
        """Test +0 + +0 = +0."""
        a = pack_f32(0.0)
        b = pack_f32(0.0)
        result_dict = fadd_f32(a, b)
        result_bits = result_dict['result']
        sign, exp, frac = extract_float32_fields(result_bits)
        is_zero, _, _, _ = is_special_value(exp, frac)
        assert is_zero is True
        assert sign == 0  # Positive zero

    def test_add_mixed_signs_to_zero(self):
        """Test x + (-x) = +0."""
        a = pack_f32(3.14)
        b = pack_f32(-3.14)
        result_dict = fadd_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert approx_equal(result, 0.0, abs_tol=1e-6)

    def test_add_infinity_same_sign(self):
        """Test +inf + +inf = +inf."""
        a = pack_f32(float('inf'))
        b = pack_f32(float('inf'))
        result_dict = fadd_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert math.isinf(result) and result > 0

    def test_add_infinity_opposite_sign(self):
        """Test +inf + -inf = NaN (invalid)."""
        a = pack_f32(float('inf'))
        b = pack_f32(float('-inf'))
        result_dict = fadd_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert math.isnan(result)
        assert result_dict['flags']['invalid'] == 1

    def test_add_nan_propagation(self):
        """Test NaN + x = NaN."""
        a = pack_f32(float('nan'))
        b = pack_f32(1.0)
        result_dict = fadd_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert math.isnan(result)
        assert result_dict['flags']['invalid'] == 1

    def test_add_large_numbers_overflow(self):
        """Test overflow: very large + very large = inf."""
        a = pack_f32(3.4e38)
        b = pack_f32(3.4e38)
        result_dict = fadd_f32(a, b)
        result = unpack_f32(result_dict['result'])
        # Should overflow to infinity
        assert math.isinf(result)
        assert result_dict['flags']['overflow'] == 1


class TestFloatSubtraction:
    """Test IEEE-754 floating-point subtraction."""

    def test_sub_simple(self):
        """Test 5.0 - 3.0 = 2.0."""
        a = pack_f32(5.0)
        b = pack_f32(3.0)
        result_dict = fsub_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert approx_equal(result, 2.0)

    def test_sub_to_zero(self):
        """Test x - x = 0."""
        a = pack_f32(7.25)
        b = pack_f32(7.25)
        result_dict = fsub_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert approx_equal(result, 0.0, abs_tol=1e-6)

    def test_sub_zero(self):
        """Test x - 0 = x."""
        a = pack_f32(4.5)
        b = pack_f32(0.0)
        result_dict = fsub_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert approx_equal(result, 4.5)

    def test_sub_from_zero(self):
        """Test 0 - x = -x."""
        a = pack_f32(0.0)
        b = pack_f32(3.5)
        result_dict = fsub_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert approx_equal(result, -3.5)

    def test_sub_negative_result(self):
        """Test 2.0 - 5.0 = -3.0."""
        a = pack_f32(2.0)
        b = pack_f32(5.0)
        result_dict = fsub_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert approx_equal(result, -3.0)

    def test_sub_infinity_same_sign(self):
        """Test +inf - +inf = NaN (invalid)."""
        a = pack_f32(float('inf'))
        b = pack_f32(float('inf'))
        result_dict = fsub_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert math.isnan(result)
        assert result_dict['flags']['invalid'] == 1


class TestFloatMultiplication:
    """Test IEEE-754 floating-point multiplication."""

    def test_mul_simple(self):
        """Test 2.0 * 3.0 = 6.0."""
        a = pack_f32(2.0)
        b = pack_f32(3.0)
        result_dict = fmul_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert approx_equal(result, 6.0)

    def test_mul_by_one(self):
        """Test x * 1.0 = x."""
        a = pack_f32(7.5)
        b = pack_f32(1.0)
        result_dict = fmul_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert approx_equal(result, 7.5)

    def test_mul_by_zero(self):
        """Test x * 0 = 0."""
        a = pack_f32(123.45)
        b = pack_f32(0.0)
        result_dict = fmul_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert result == 0.0

    def test_mul_negative_signs(self):
        """Test (-2.0) * 3.0 = -6.0."""
        a = pack_f32(-2.0)
        b = pack_f32(3.0)
        result_dict = fmul_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert approx_equal(result, -6.0)

    def test_mul_both_negative(self):
        """Test (-2.0) * (-3.0) = 6.0."""
        a = pack_f32(-2.0)
        b = pack_f32(-3.0)
        result_dict = fmul_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert approx_equal(result, 6.0)

    def test_mul_infinity_by_number(self):
        """Test inf * 2.0 = inf."""
        a = pack_f32(float('inf'))
        b = pack_f32(2.0)
        result_dict = fmul_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert math.isinf(result) and result > 0

    def test_mul_infinity_by_zero(self):
        """Test inf * 0 = NaN (invalid)."""
        a = pack_f32(float('inf'))
        b = pack_f32(0.0)
        result_dict = fmul_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert math.isnan(result)
        assert result_dict['flags']['invalid'] == 1

    def test_mul_large_numbers_overflow(self):
        """Test overflow: very large * very large = inf."""
        a = pack_f32(1e30)
        b = pack_f32(1e30)
        result_dict = fmul_f32(a, b)
        result = unpack_f32(result_dict['result'])
        # Should overflow to infinity
        assert math.isinf(result)
        assert result_dict['flags']['overflow'] == 1

    def test_mul_small_numbers_underflow(self):
        """Test underflow: very small * very small."""
        a = pack_f32(1e-20)
        b = pack_f32(1e-20)
        result_dict = fmul_f32(a, b)
        # Result should underflow (might be zero or subnormal)
        # Just check that underflow flag is set
        assert result_dict['flags']['underflow'] == 1

    def test_mul_fractional(self):
        """Test 0.5 * 0.25 = 0.125."""
        a = pack_f32(0.5)
        b = pack_f32(0.25)
        result_dict = fmul_f32(a, b)
        result = unpack_f32(result_dict['result'])
        assert approx_equal(result, 0.125)


class TestFloatTrace:
    """Test that operations produce trace output."""

    def test_add_produces_trace(self):
        """Test that addition produces trace information."""
        a = pack_f32(1.0)
        b = pack_f32(2.0)
        result_dict = fadd_f32(a, b)
        assert 'trace' in result_dict
        assert len(result_dict['trace']) > 0
        assert isinstance(result_dict['trace'], list)

    def test_sub_produces_trace(self):
        """Test that subtraction produces trace information."""
        a = pack_f32(5.0)
        b = pack_f32(3.0)
        result_dict = fsub_f32(a, b)
        assert 'trace' in result_dict
        assert len(result_dict['trace']) > 0
        # Should mention FSUB and negation
        assert any('FSUB' in str(t) for t in result_dict['trace'])

    def test_mul_produces_trace(self):
        """Test that multiplication produces trace information."""
        a = pack_f32(2.0)
        b = pack_f32(3.0)
        result_dict = fmul_f32(a, b)
        assert 'trace' in result_dict
        assert len(result_dict['trace']) > 0


class TestExceptionFlags:
    """Test IEEE-754 exception flags."""

    def test_invalid_flag_inf_minus_inf(self):
        """Test invalid flag for inf - inf."""
        a = pack_f32(float('inf'))
        b = pack_f32(float('inf'))
        result_dict = fsub_f32(a, b)
        assert result_dict['flags']['invalid'] == 1

    def test_invalid_flag_nan_operand(self):
        """Test invalid flag for NaN operand."""
        a = pack_f32(float('nan'))
        b = pack_f32(1.0)
        result_dict = fadd_f32(a, b)
        assert result_dict['flags']['invalid'] == 1

    def test_overflow_flag(self):
        """Test overflow flag for large addition."""
        a = pack_f32(3.4e38)
        b = pack_f32(3.4e38)
        result_dict = fadd_f32(a, b)
        assert result_dict['flags']['overflow'] == 1

    def test_no_flags_for_normal_operation(self):
        """Test that normal operations don't set exception flags."""
        a = pack_f32(1.0)
        b = pack_f32(2.0)
        result_dict = fadd_f32(a, b)
        flags = result_dict['flags']
        assert flags['invalid'] == 0
        assert flags['divide_by_zero'] == 0
        assert flags['overflow'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
