# AI-BEGIN
"""
Test suite for RISC-V Barrel Shifter

Tests all three shift operations (SLL, SRL, SRA) with various shift amounts
and edge cases.
"""

import pytest
from riscsim.cpu.shifter import shifter


# Helper functions for test conversions (using host operators is OK in tests)
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


def hex_to_bin32(hex_str):
    """Convert hex string to 32-bit binary list (MSB at index 0)."""
    # Remove '0x' prefix if present
    hex_str = hex_str.replace('0x', '')
    n = int(hex_str, 16)
    return [(n >> (31 - i)) & 1 for i in range(32)]


def bin32_to_hex(bits):
    """Convert 32-bit binary list to hex string."""
    val = sum(bit << (31 - i) for i, bit in enumerate(bits))
    return f"0x{val:08X}"


class TestShiftLeftLogical:
    """Test SLL (Shift Left Logical) operation."""

    def test_sll_shift_by_0(self):
        """Shifting by 0 should return the same value."""
        bits = int_to_bin32(0x12345678)
        result = shifter(bits, 0, "SLL")
        assert bin32_to_hex(result) == "0x12345678"

    def test_sll_shift_by_1(self):
        """Test basic left shift by 1."""
        bits = int_to_bin32(0x00000001)
        result = shifter(bits, 1, "SLL")
        assert bin32_to_hex(result) == "0x00000002"

    def test_sll_shift_by_4(self):
        """Test left shift by 4."""
        bits = int_to_bin32(0x0000000F)
        result = shifter(bits, 4, "SLL")
        assert bin32_to_hex(result) == "0x000000F0"

    def test_sll_shift_by_8(self):
        """Test left shift by 8."""
        bits = int_to_bin32(0x000000FF)
        result = shifter(bits, 8, "SLL")
        assert bin32_to_hex(result) == "0x0000FF00"

    def test_sll_shift_by_16(self):
        """Test left shift by 16."""
        bits = int_to_bin32(0x0000FFFF)
        result = shifter(bits, 16, "SLL")
        assert bin32_to_hex(result) == "0xFFFF0000"

    def test_sll_shift_by_31(self):
        """Test left shift by maximum amount (31)."""
        bits = int_to_bin32(0x00000001)
        result = shifter(bits, 31, "SLL")
        assert bin32_to_hex(result) == "0x80000000"

    def test_sll_overflow(self):
        """Test that bits shifted out are lost."""
        bits = int_to_bin32(0x80000000)
        result = shifter(bits, 1, "SLL")
        assert bin32_to_hex(result) == "0x00000000"

    def test_sll_with_bit_array_shamt(self):
        """Test SLL with shamt as 5-bit array."""
        bits = int_to_bin32(0x00000001)
        shamt = [0, 0, 0, 1, 0]  # Binary for 2
        result = shifter(bits, shamt, "SLL")
        assert bin32_to_hex(result) == "0x00000004"

    def test_sll_with_bit_array_op(self):
        """Test SLL with operation code as bit array."""
        bits = int_to_bin32(0x00000001)
        result = shifter(bits, 3, [0, 0])  # [0,0] = SLL
        assert bin32_to_hex(result) == "0x00000008"


class TestShiftRightLogical:
    """Test SRL (Shift Right Logical) operation."""

    def test_srl_shift_by_0(self):
        """Shifting by 0 should return the same value."""
        bits = int_to_bin32(0x12345678)
        result = shifter(bits, 0, "SRL")
        assert bin32_to_hex(result) == "0x12345678"

    def test_srl_shift_by_1(self):
        """Test basic right shift by 1."""
        bits = int_to_bin32(0x80000000)
        result = shifter(bits, 1, "SRL")
        assert bin32_to_hex(result) == "0x40000000"

    def test_srl_shift_by_4(self):
        """Test right shift by 4."""
        bits = int_to_bin32(0xF0000000)
        result = shifter(bits, 4, "SRL")
        assert bin32_to_hex(result) == "0x0F000000"

    def test_srl_shift_by_8(self):
        """Test right shift by 8."""
        bits = int_to_bin32(0xFF000000)
        result = shifter(bits, 8, "SRL")
        assert bin32_to_hex(result) == "0x00FF0000"

    def test_srl_shift_by_16(self):
        """Test right shift by 16."""
        bits = int_to_bin32(0xFFFF0000)
        result = shifter(bits, 16, "SRL")
        assert bin32_to_hex(result) == "0x0000FFFF"

    def test_srl_shift_by_31(self):
        """Test right shift by maximum amount (31)."""
        bits = int_to_bin32(0x80000000)
        result = shifter(bits, 31, "SRL")
        assert bin32_to_hex(result) == "0x00000001"

    def test_srl_underflow(self):
        """Test that bits shifted out are lost."""
        bits = int_to_bin32(0x00000001)
        result = shifter(bits, 1, "SRL")
        assert bin32_to_hex(result) == "0x00000000"

    def test_srl_no_sign_extension(self):
        """Test that SRL fills with zeros (no sign extension)."""
        bits = int_to_bin32(0x80000000)  # Negative in two's complement
        result = shifter(bits, 4, "SRL")
        assert bin32_to_hex(result) == "0x08000000"  # Zero-filled

    def test_srl_with_bit_array_shamt(self):
        """Test SRL with shamt as 5-bit array."""
        bits = int_to_bin32(0x80000000)
        shamt = [0, 0, 0, 1, 0]  # Binary for 2
        result = shifter(bits, shamt, "SRL")
        assert bin32_to_hex(result) == "0x20000000"

    def test_srl_with_bit_array_op(self):
        """Test SRL with operation code as bit array."""
        bits = int_to_bin32(0x80000000)
        result = shifter(bits, 3, [0, 1])  # [0,1] = SRL
        assert bin32_to_hex(result) == "0x10000000"


class TestShiftRightArithmetic:
    """Test SRA (Shift Right Arithmetic) operation."""

    def test_sra_shift_by_0(self):
        """Shifting by 0 should return the same value."""
        bits = int_to_bin32(0x12345678)
        result = shifter(bits, 0, "SRA")
        assert bin32_to_hex(result) == "0x12345678"

    def test_sra_positive_number(self):
        """Test SRA on positive number (sign bit = 0)."""
        bits = int_to_bin32(0x7FFFFFFF)  # Max positive 32-bit
        result = shifter(bits, 1, "SRA")
        assert bin32_to_hex(result) == "0x3FFFFFFF"

    def test_sra_negative_number_shift_1(self):
        """Test SRA on negative number, shift by 1."""
        bits = int_to_bin32(0x80000000)  # Most negative 32-bit
        result = shifter(bits, 1, "SRA")
        assert bin32_to_hex(result) == "0xC0000000"  # Sign-extended

    def test_sra_negative_number_shift_4(self):
        """Test SRA on negative number, shift by 4."""
        bits = int_to_bin32(0x80000000)
        result = shifter(bits, 4, "SRA")
        assert bin32_to_hex(result) == "0xF8000000"  # Sign-extended

    def test_sra_negative_number_shift_8(self):
        """Test SRA on negative number, shift by 8."""
        bits = int_to_bin32(0xFF000000)
        result = shifter(bits, 8, "SRA")
        assert bin32_to_hex(result) == "0xFFFF0000"  # Sign-extended

    def test_sra_negative_number_shift_31(self):
        """Test SRA on negative number, shift by maximum (31)."""
        bits = int_to_bin32(0x80000000)
        result = shifter(bits, 31, "SRA")
        assert bin32_to_hex(result) == "0xFFFFFFFF"  # All ones

    def test_sra_positive_number_shift_31(self):
        """Test SRA on positive number, shift by maximum (31)."""
        bits = int_to_bin32(0x7FFFFFFF)
        result = shifter(bits, 31, "SRA")
        assert bin32_to_hex(result) == "0x00000000"  # All zeros

    def test_sra_preserves_sign(self):
        """Test that SRA preserves the sign bit."""
        # Test negative number
        bits_neg = int_to_bin32(-16)
        result_neg = shifter(bits_neg, 2, "SRA")
        assert bin32_to_int(result_neg, signed=True) == -4

        # Test positive number
        bits_pos = int_to_bin32(16)
        result_pos = shifter(bits_pos, 2, "SRA")
        assert bin32_to_int(result_pos, signed=True) == 4

    def test_sra_with_bit_array_shamt(self):
        """Test SRA with shamt as 5-bit array."""
        bits = int_to_bin32(0x80000000)
        shamt = [0, 0, 0, 1, 0]  # Binary for 2
        result = shifter(bits, shamt, "SRA")
        assert bin32_to_hex(result) == "0xE0000000"

    def test_sra_with_bit_array_op(self):
        """Test SRA with operation code as bit array."""
        bits = int_to_bin32(0x80000000)
        result = shifter(bits, 3, [1, 1])  # [1,1] = SRA
        assert bin32_to_hex(result) == "0xF0000000"


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_all_zeros(self):
        """Test shifting all zeros."""
        bits = int_to_bin32(0x00000000)
        assert bin32_to_hex(shifter(bits, 10, "SLL")) == "0x00000000"
        assert bin32_to_hex(shifter(bits, 10, "SRL")) == "0x00000000"
        assert bin32_to_hex(shifter(bits, 10, "SRA")) == "0x00000000"

    def test_all_ones(self):
        """Test shifting all ones."""
        bits = int_to_bin32(0xFFFFFFFF)
        assert bin32_to_hex(shifter(bits, 4, "SLL")) == "0xFFFFFFF0"
        assert bin32_to_hex(shifter(bits, 4, "SRL")) == "0x0FFFFFFF"
        assert bin32_to_hex(shifter(bits, 4, "SRA")) == "0xFFFFFFFF"

    def test_alternating_pattern(self):
        """Test shifting alternating bit pattern."""
        bits = int_to_bin32(0xAAAAAAAA)
        assert bin32_to_hex(shifter(bits, 1, "SLL")) == "0x55555554"
        assert bin32_to_hex(shifter(bits, 1, "SRL")) == "0x55555555"

    def test_combined_shift_amounts(self):
        """Test shift amounts that combine multiple stages."""
        bits = int_to_bin32(0x00000001)
        # 7 = 4 + 2 + 1 (stages 3, 4, 5)
        result = shifter(bits, 7, "SLL")
        assert bin32_to_hex(result) == "0x00000080"

    def test_shift_amount_boundary(self):
        """Test that shift amount is masked to 5 bits."""
        bits = int_to_bin32(0x00000001)
        # 32 should wrap to 0 (only lower 5 bits used: 32 & 0x1F = 0)
        result = shifter(bits, 32, "SLL")
        assert bin32_to_hex(result) == "0x00000001"  # No shift

    def test_shift_amount_33(self):
        """Test shift amount > 32."""
        bits = int_to_bin32(0x00000001)
        # 33 & 0x1F = 1
        result = shifter(bits, 33, "SLL")
        assert bin32_to_hex(result) == "0x00000002"  # Shift by 1

    def test_different_input_formats(self):
        """Test that different input formats produce same results."""
        bits = int_to_bin32(0x12345678)

        # String operation codes
        r1 = shifter(bits, 4, "SLL")
        r2 = shifter(bits, 4, "sll")  # Case insensitive
        assert r1 == r2

        # Bit array operation codes
        r3 = shifter(bits, 4, [0, 0])
        assert r1 == r3


class TestComprehensive:
    """Comprehensive tests comparing operations."""

    def test_sll_vs_srl_symmetry(self):
        """Test basic symmetry between left and right shifts."""
        bits = int_to_bin32(0x0000FF00)

        # Shift left then right should restore middle bits
        left = shifter(bits, 8, "SLL")
        back = shifter(left, 8, "SRL")
        assert bin32_to_hex(back) == "0x0000FF00"

    def test_srl_vs_sra_on_positive(self):
        """SRL and SRA should be identical for positive numbers."""
        bits = int_to_bin32(0x7FFFFFFF)

        srl_result = shifter(bits, 4, "SRL")
        sra_result = shifter(bits, 4, "SRA")
        assert srl_result == sra_result

    def test_srl_vs_sra_on_negative(self):
        """SRL and SRA should differ for negative numbers."""
        bits = int_to_bin32(0x80000000)

        srl_result = shifter(bits, 4, "SRL")
        sra_result = shifter(bits, 4, "SRA")
        assert srl_result != sra_result
        assert bin32_to_hex(srl_result) == "0x08000000"  # Zero-filled
        assert bin32_to_hex(sra_result) == "0xF8000000"  # Sign-filled

    def test_multiple_operations_sequence(self):
        """Test a sequence of operations."""
        bits = int_to_bin32(0x12345678)

        # SLL by 4
        result = shifter(bits, 4, "SLL")
        assert bin32_to_hex(result) == "0x23456780"

        # Then SRL by 8
        result = shifter(result, 8, "SRL")
        assert bin32_to_hex(result) == "0x00234567"


# Phase 2: Control Signal Integration Tests

def test_shifter_with_control_sll():
    """Test shifter with control signals for SLL operation."""
    from riscsim.cpu.shifter import shifter_with_control
    from riscsim.cpu.control_signals import ControlSignals, SH_OP_SLL
    
    signals = ControlSignals()
    signals.sh_op = SH_OP_SLL
    signals.sh_amount = [0, 0, 1, 0, 0]  # 4
    
    operand = int_to_bin32(0x12345678)
    
    result_dict = shifter_with_control(operand, signals)
    
    # Verify result
    assert bin32_to_hex(result_dict['result']) == "0x23456780"
    
    # Verify trace
    assert 'Shifter SLL' in result_dict['trace']
    assert 'by 4' in result_dict['trace']


def test_shifter_with_control_srl():
    """Test shifter with control signals for SRL operation."""
    from riscsim.cpu.shifter import shifter_with_control
    from riscsim.cpu.control_signals import ControlSignals, SH_OP_SRL
    
    signals = ControlSignals()
    signals.sh_op = SH_OP_SRL
    signals.sh_amount = [0, 1, 0, 0, 0]  # 8
    
    operand = int_to_bin32(0x12345678)
    
    result_dict = shifter_with_control(operand, signals)
    
    assert bin32_to_hex(result_dict['result']) == "0x00123456"
    assert 'Shifter SRL' in result_dict['trace']
    assert 'by 8' in result_dict['trace']


def test_shifter_with_control_sra():
    """Test shifter with control signals for SRA operation."""
    from riscsim.cpu.shifter import shifter_with_control
    from riscsim.cpu.control_signals import ControlSignals, SH_OP_SRA
    
    signals = ControlSignals()
    signals.sh_op = SH_OP_SRA
    signals.sh_amount = [0, 0, 1, 0, 0]  # 4
    
    # Negative number
    operand = int_to_bin32(0x80000000)
    
    result_dict = shifter_with_control(operand, signals)
    
    # Should preserve sign bit
    assert bin32_to_hex(result_dict['result']) == "0xF8000000"
    assert 'Shifter SRA' in result_dict['trace']


def test_shifter_with_control_zero_shift():
    """Test shifter with zero shift amount."""
    from riscsim.cpu.shifter import shifter_with_control
    from riscsim.cpu.control_signals import ControlSignals, SH_OP_SLL
    
    signals = ControlSignals()
    signals.sh_op = SH_OP_SLL
    signals.sh_amount = [0, 0, 0, 0, 0]  # 0
    
    operand = int_to_bin32(0x12345678)
    
    result_dict = shifter_with_control(operand, signals)
    
    # Should be unchanged
    assert bin32_to_hex(result_dict['result']) == "0x12345678"
    assert 'by 0' in result_dict['trace']


def test_shifter_with_control_max_shift():
    """Test shifter with maximum shift amount."""
    from riscsim.cpu.shifter import shifter_with_control
    from riscsim.cpu.control_signals import ControlSignals, SH_OP_SRL
    
    signals = ControlSignals()
    signals.sh_op = SH_OP_SRL
    signals.sh_amount = [1, 1, 1, 1, 1]  # 31
    
    operand = int_to_bin32(0xFFFFFFFF)
    
    result_dict = shifter_with_control(operand, signals)
    
    # Should shift almost everything out
    assert bin32_to_int(result_dict['result']) == 1
    assert 'by 31' in result_dict['trace']


def test_shifter_with_control_signals_preserved():
    """Test that control signals are preserved in result."""
    from riscsim.cpu.shifter import shifter_with_control
    from riscsim.cpu.control_signals import ControlSignals, SH_OP_SLL
    
    signals = ControlSignals()
    signals.sh_op = SH_OP_SLL
    signals.sh_amount = [0, 0, 0, 1, 0]  # 2
    signals.cycle = 99
    signals.rf_waddr = [0, 0, 1, 0, 0]  # r4
    
    operand = int_to_bin32(0x00000001)
    
    result_dict = shifter_with_control(operand, signals)
    
    # Verify signals are preserved
    returned_signals = result_dict['signals']
    assert returned_signals.sh_op == SH_OP_SLL
    assert returned_signals.sh_amount == [0, 0, 0, 1, 0]
    assert returned_signals.cycle == 99
    assert returned_signals.rf_waddr == [0, 0, 1, 0, 0]


# AI-END
