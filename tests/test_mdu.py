"""
Test suite for RISC-V Multiply/Divide Unit (MDU)

Tests all M extension operations:
- MUL, MULH, MULHU, MULHSU: Multiplication operations
- DIV, DIVU, REM, REMU: Division and remainder operations

Includes edge cases from RISC-V specification.
"""

import pytest
from riscsim.cpu.mdu import (
    mdu_mul, mdu_div, mul, mulh, mulhu, mulhsu,
    div, divu, rem, remu
)
from riscsim.utils.bit_utils import bits_to_hex_string, hex_string_to_bits


# Helper functions
def int_to_bin32(n):
    """Convert integer to 32-bit binary list (MSB at index 0)."""
    if n < 0:
        n = (1 << 32) + n  # Two's complement conversion
    return [(n >> (31 - i)) & 1 for i in range(32)]


def bin32_to_int(bits, signed=False):
    """Convert 32-bit binary list to integer."""
    val = sum(bit << (31 - i) for i, bit in enumerate(bits))
    if signed and bits[0] == 1:
        val -= (1 << 32)
    return val


def hex_to_bits32(hex_str):
    """Convert hex string to 32-bit array."""
    return hex_string_to_bits(hex_str, 32)


class TestMUL:
    """Test MUL (lower 32 bits of multiplication)."""

    def test_mul_simple_positive(self):
        """Test simple positive multiplication: 7 * 3 = 21."""
        a = int_to_bin32(7)
        b = int_to_bin32(3)
        result = mul(a, b)
        assert bin32_to_int(result['result']) == 21

    def test_mul_zero(self):
        """Test multiplication by zero."""
        a = int_to_bin32(12345)
        b = int_to_bin32(0)
        result = mul(a, b)
        assert bin32_to_int(result['result']) == 0

    def test_mul_one(self):
        """Test multiplication by one."""
        a = int_to_bin32(12345)
        b = int_to_bin32(1)
        result = mul(a, b)
        assert bin32_to_int(result['result']) == 12345

    def test_mul_negative_positive(self):
        """Test negative × positive."""
        a = int_to_bin32(-7)
        b = int_to_bin32(3)
        result = mul(a, b)
        assert bin32_to_int(result['result'], signed=True) == -21

    def test_mul_positive_negative(self):
        """Test positive × negative."""
        a = int_to_bin32(7)
        b = int_to_bin32(-3)
        result = mul(a, b)
        assert bin32_to_int(result['result'], signed=True) == -21

    def test_mul_both_negative(self):
        """Test negative × negative."""
        a = int_to_bin32(-7)
        b = int_to_bin32(-3)
        result = mul(a, b)
        assert bin32_to_int(result['result'], signed=True) == 21

    def test_mul_spec_example(self):
        """Test example from spec: 12345678 * -87654321."""
        a = int_to_bin32(12345678)
        b = int_to_bin32(-87654321)
        result = mul(a, b)
        # Expected low 32 bits: 0xD91D0712
        assert bits_to_hex_string(result['result']) == "0xD91D0712"
        # Should have overflow
        assert result['flags']['overflow'] == 1

    def test_mul_overflow_detection(self):
        """Test overflow flag for large multiplication."""
        a = int_to_bin32(0x10000)
        b = int_to_bin32(0x10000)
        result = mul(a, b)
        # Result = 0x100000000, low 32 bits = 0, but overflow
        assert bin32_to_int(result['result']) == 0
        assert result['flags']['overflow'] == 1

    def test_mul_no_overflow(self):
        """Test no overflow for small multiplication."""
        a = int_to_bin32(100)
        b = int_to_bin32(200)
        result = mul(a, b)
        assert bin32_to_int(result['result']) == 20000
        assert result['flags']['overflow'] == 0

    def test_mul_produces_trace(self):
        """Test that MUL produces trace output."""
        a = int_to_bin32(5)
        b = int_to_bin32(3)
        result = mul(a, b)
        assert 'trace' in result
        assert len(result['trace']) > 0


class TestMULH:
    """Test MULH (upper 32 bits, signed × signed)."""

    def test_mulh_simple(self):
        """Test MULH with simple values."""
        a = int_to_bin32(0x10000)
        b = int_to_bin32(0x10000)
        result = mulh(a, b)
        # 0x10000 * 0x10000 = 0x100000000
        # High 32 bits = 0x00000001
        assert bits_to_hex_string(result['result']) == "0x00000001"

    def test_mulh_spec_example(self):
        """Test example from spec: MULH 12345678 * -87654321."""
        a = int_to_bin32(12345678)
        b = int_to_bin32(-87654321)
        result = mulh(a, b)
        # Expected high 32 bits: 0xFFFC27C9
        assert bits_to_hex_string(result['result']) == "0xFFFC27C9"

    def test_mulh_negative_result(self):
        """Test MULH with negative result."""
        a = int_to_bin32(-100000)
        b = int_to_bin32(100000)
        result = mulh(a, b)
        # Result is negative, high bits should be sign-extended
        assert result['result'][0] == 1  # Negative

    def test_mulh_both_negative(self):
        """Test MULH with both operands negative."""
        a = int_to_bin32(-100000)
        b = int_to_bin32(-100000)
        result = mulh(a, b)
        # Result is positive
        assert result['result'][0] == 0  # Positive


class TestMULHU:
    """Test MULHU (upper 32 bits, unsigned × unsigned)."""

    def test_mulhu_simple(self):
        """Test MULHU with simple values."""
        a = int_to_bin32(0x10000)
        b = int_to_bin32(0x10000)
        result = mulhu(a, b)
        # Same as MULH for positive numbers
        assert bits_to_hex_string(result['result']) == "0x00000001"

    def test_mulhu_large_unsigned(self):
        """Test MULHU with large unsigned values."""
        a = int_to_bin32(0xFFFFFFFF)  # Max unsigned
        b = int_to_bin32(2)
        result = mulhu(a, b)
        # 0xFFFFFFFF * 2 = 0x1FFFFFFFE
        # High 32 bits = 0x00000001
        assert bits_to_hex_string(result['result']) == "0x00000001"


class TestMULHSU:
    """Test MULHSU (upper 32 bits, signed × unsigned)."""

    def test_mulhsu_positive_signed(self):
        """Test MULHSU with positive signed operand."""
        a = int_to_bin32(100000)
        b = int_to_bin32(100000)
        result = mulhsu(a, b)
        # Should be same as MULH/MULHU for positive numbers
        expected = mulh(a, b)
        assert result['result'] == expected['result']

    def test_mulhsu_negative_signed(self):
        """Test MULHSU with negative signed operand."""
        a = int_to_bin32(-1)  # 0xFFFFFFFF as signed
        b = int_to_bin32(0xFFFFFFFF)  # Max unsigned
        result = mulhsu(a, b)
        # -1 * 0xFFFFFFFF (unsigned) = -0xFFFFFFFF
        # High bits should reflect this
        assert result['result'][0] == 1  # Negative result


class TestDIV:
    """Test DIV (signed division quotient)."""

    def test_div_simple_positive(self):
        """Test simple positive division: 21 / 3 = 7."""
        a = int_to_bin32(21)
        b = int_to_bin32(3)
        result = div(a, b)
        assert bin32_to_int(result['quotient'], signed=True) == 7

    def test_div_spec_example(self):
        """Test example from spec: -7 / 3 = -2."""
        a = int_to_bin32(-7)
        b = int_to_bin32(3)
        result = div(a, b)
        # Quotient = -2 (0xFFFFFFFE)
        assert bits_to_hex_string(result['quotient']) == "0xFFFFFFFE"
        # Remainder = -1 (0xFFFFFFFF)
        assert bits_to_hex_string(result['remainder']) == "0xFFFFFFFF"

    def test_div_positive_by_negative(self):
        """Test positive / negative."""
        a = int_to_bin32(20)
        b = int_to_bin32(-3)
        result = div(a, b)
        # 20 / -3 = -6 (truncate toward zero)
        assert bin32_to_int(result['quotient'], signed=True) == -6

    def test_div_by_one(self):
        """Test division by 1."""
        a = int_to_bin32(12345)
        b = int_to_bin32(1)
        result = div(a, b)
        assert bin32_to_int(result['quotient'], signed=True) == 12345

    def test_div_by_zero(self):
        """Test division by zero: quotient = -1, remainder = dividend."""
        a = int_to_bin32(12345)
        b = int_to_bin32(0)
        result = div(a, b)
        # Quotient should be -1 (0xFFFFFFFF)
        assert bits_to_hex_string(result['quotient']) == "0xFFFFFFFF"
        # Remainder should be dividend
        assert result['remainder'] == a

    def test_div_overflow_int_min_by_neg_one(self):
        """Test overflow case: INT_MIN / -1."""
        a = hex_to_bits32("0x80000000")  # INT_MIN
        b = int_to_bin32(-1)
        result = div(a, b)
        # Should return INT_MIN as quotient
        assert bits_to_hex_string(result['quotient']) == "0x80000000"
        # Remainder should be 0
        assert bin32_to_int(result['remainder']) == 0
        # Overflow flag should be set
        assert result['flags']['overflow'] == 1


class TestDIVU:
    """Test DIVU (unsigned division quotient)."""

    def test_divu_simple(self):
        """Test simple unsigned division."""
        a = int_to_bin32(20)
        b = int_to_bin32(3)
        result = divu(a, b)
        assert bin32_to_int(result['quotient']) == 6

    def test_divu_spec_example(self):
        """Test example from spec: 0x80000000 / 3."""
        a = hex_to_bits32("0x80000000")
        b = int_to_bin32(3)
        result = divu(a, b)
        # 0x80000000 (2147483648) / 3 = 0x2AAAAAAA
        assert bits_to_hex_string(result['quotient']) == "0x2AAAAAAA"
        # Remainder = 2
        assert bits_to_hex_string(result['remainder']) == "0x00000002"

    def test_divu_by_zero(self):
        """Test unsigned division by zero."""
        a = int_to_bin32(12345)
        b = int_to_bin32(0)
        result = divu(a, b)
        # Quotient should be 0xFFFFFFFF
        assert bits_to_hex_string(result['quotient']) == "0xFFFFFFFF"
        # Remainder should be dividend
        assert result['remainder'] == a

    def test_divu_large_values(self):
        """Test unsigned division with large values."""
        a = hex_to_bits32("0xFFFFFFFF")  # Max unsigned
        b = int_to_bin32(2)
        result = divu(a, b)
        # 0xFFFFFFFF / 2 = 0x7FFFFFFF
        assert bits_to_hex_string(result['quotient']) == "0x7FFFFFFF"
        # Remainder = 1
        assert bin32_to_int(result['remainder']) == 1


class TestREM:
    """Test REM (signed division remainder)."""

    def test_rem_simple(self):
        """Test simple remainder: 22 % 5 = 2."""
        a = int_to_bin32(22)
        b = int_to_bin32(5)
        result = rem(a, b)
        assert bin32_to_int(result['remainder'], signed=True) == 2

    def test_rem_negative_dividend(self):
        """Test remainder with negative dividend: -7 % 3 = -1."""
        a = int_to_bin32(-7)
        b = int_to_bin32(3)
        result = rem(a, b)
        # Remainder has same sign as dividend
        assert bin32_to_int(result['remainder'], signed=True) == -1

    def test_rem_negative_divisor(self):
        """Test remainder with negative divisor: 7 % -3 = 1."""
        a = int_to_bin32(7)
        b = int_to_bin32(-3)
        result = rem(a, b)
        # Remainder has same sign as dividend
        assert bin32_to_int(result['remainder'], signed=True) == 1

    def test_rem_by_zero(self):
        """Test remainder by zero: remainder = dividend."""
        a = int_to_bin32(12345)
        b = int_to_bin32(0)
        result = rem(a, b)
        # Remainder should be dividend
        assert result['remainder'] == a


class TestREMU:
    """Test REMU (unsigned division remainder)."""

    def test_remu_simple(self):
        """Test simple unsigned remainder."""
        a = int_to_bin32(22)
        b = int_to_bin32(5)
        result = remu(a, b)
        assert bin32_to_int(result['remainder']) == 2

    def test_remu_large_values(self):
        """Test unsigned remainder with large values."""
        a = hex_to_bits32("0xFFFFFFFF")
        b = int_to_bin32(10)
        result = remu(a, b)
        # 0xFFFFFFFF % 10 = 5
        assert bin32_to_int(result['remainder']) == 5

    def test_remu_by_zero(self):
        """Test unsigned remainder by zero."""
        a = int_to_bin32(12345)
        b = int_to_bin32(0)
        result = remu(a, b)
        # Remainder should be dividend
        assert result['remainder'] == a


class TestMDUTrace:
    """Test that MDU operations produce trace output."""

    def test_mul_trace(self):
        """Test that multiplication produces cycle-by-cycle trace."""
        a = int_to_bin32(123)
        b = int_to_bin32(456)
        result = mul(a, b)
        trace = result['trace']
        assert len(trace) > 0
        assert any('Shift-Add Multiplication' in str(t) for t in trace)
        assert any('Cycle' in str(t) for t in trace)

    def test_div_trace(self):
        """Test that division produces cycle-by-cycle trace."""
        a = int_to_bin32(1000)
        b = int_to_bin32(7)
        result = div(a, b)
        trace = result['trace']
        assert len(trace) > 0
        assert any('Restoring Division' in str(t) for t in trace)
        assert any('Cycle' in str(t) for t in trace)

    def test_trace_shows_operations(self):
        """Test that trace shows actual operations performed."""
        a = int_to_bin32(15)
        b = int_to_bin32(3)
        result = mul(a, b)
        trace = result['trace']
        # Should show some additions happening
        trace_str = '\n'.join(result['trace'])
        assert 'Add' in trace_str or 'add' in trace_str


class TestMDUEdgeCases:
    """Test edge cases and boundary values."""

    def test_mul_max_positive(self):
        """Test multiplication with max positive value."""
        a = hex_to_bits32("0x7FFFFFFF")  # INT_MAX
        b = int_to_bin32(2)
        result = mul(a, b)
        # Should overflow
        assert result['flags']['overflow'] == 1

    def test_div_exact(self):
        """Test exact division (no remainder)."""
        a = int_to_bin32(100)
        b = int_to_bin32(10)
        result = div(a, b)
        assert bin32_to_int(result['quotient'], signed=True) == 10
        assert bin32_to_int(result['remainder']) == 0

    def test_div_with_remainder(self):
        """Test division with remainder."""
        a = int_to_bin32(107)
        b = int_to_bin32(10)
        result = div(a, b)
        assert bin32_to_int(result['quotient'], signed=True) == 10
        assert bin32_to_int(result['remainder'], signed=True) == 7

    def test_mul_powers_of_two(self):
        """Test multiplication by powers of 2."""
        a = int_to_bin32(5)
        b = int_to_bin32(16)  # 2^4
        result = mul(a, b)
        assert bin32_to_int(result['result']) == 80

    def test_div_powers_of_two(self):
        """Test division by powers of 2."""
        a = int_to_bin32(80)
        b = int_to_bin32(16)  # 2^4
        result = div(a, b)
        assert bin32_to_int(result['quotient'], signed=True) == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
