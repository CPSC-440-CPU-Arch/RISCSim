# AI-BEGIN
"""
Comprehensive test suite for RISC-V Register File.

Tests cover:
- Basic functionality (read/write operations)
- Edge cases (invalid inputs, boundaries, isolation)
- Performance (bulk operations, stress testing)
- FCSR operations (field isolation, individual flags)
"""

import pytest
from riscsim.cpu.registers import RegisterFile


# =============================================================================
# Helper Functions (OK to use in tests, not in implementation)
# =============================================================================

def int_to_bin32(n):
    """Convert integer to 32-bit binary list (MSB at index 0)."""
    if n < 0:
        n = (1 << 32) + n  # Two's complement for negative numbers
    return [(n >> (31 - i)) & 1 for i in range(32)]


def bin32_to_int(bits, signed=False):
    """Convert 32-bit binary list back to integer."""
    val = sum(bit << (31 - i) for i, bit in enumerate(bits))
    if signed and bits[0] == 1:  # Negative in two's complement
        val -= (1 << 32)
    return val


def int_to_bits(n, width):
    """Convert integer to bit array of specified width (MSB first)."""
    if n < 0:
        n = (1 << width) + n
    return [(n >> (width - 1 - i)) & 1 for i in range(width)]


def bits_to_int(bits):
    """Convert bit array to integer."""
    return sum(bit << (len(bits) - 1 - i) for i, bit in enumerate(bits))


# =============================================================================
# Basic Functionality Tests
# =============================================================================

def test_register_file_initialization():
    """Test that RegisterFile initializes with all zeros."""
    rf = RegisterFile()

    # All integer registers should be zero
    for i in range(32):
        assert rf.read_int_reg(i) == [0] * 32, f"x{i} not initialized to zero"

    # All FP registers should be zero
    for i in range(32):
        assert rf.read_fp_reg(i) == [0] * 32, f"f{i} not initialized to zero"

    # FCSR should be zero
    assert rf.read_fcsr() == [0] * 8, "FCSR not initialized to zero"


def test_x0_hardwired_to_zero():
    """Test that x0 always reads zero and writes are ignored."""
    rf = RegisterFile()

    # x0 should initially read as zero
    assert rf.read_int_reg(0) == [0] * 32

    # Try to write all ones to x0 (should be silently ignored)
    ones = [1] * 32
    rf.write_int_reg(0, ones)

    # x0 should still be zero
    assert rf.read_int_reg(0) == [0] * 32

    # Try to write a specific pattern to x0
    pattern = int_to_bin32(0xAAAAAAAA)
    rf.write_int_reg(0, pattern)

    # x0 should still be zero
    assert rf.read_int_reg(0) == [0] * 32


def test_int_reg_basic_read_write():
    """Test basic integer register read/write operations."""
    rf = RegisterFile()

    # Test register x1
    value1 = int_to_bin32(42)
    rf.write_int_reg(1, value1)
    result1 = rf.read_int_reg(1)
    assert bin32_to_int(result1) == 42

    # Test register x5
    value5 = int_to_bin32(12345)
    rf.write_int_reg(5, value5)
    result5 = rf.read_int_reg(5)
    assert bin32_to_int(result5) == 12345

    # Test register x31
    value31 = int_to_bin32(0xDEADBEEF)
    rf.write_int_reg(31, value31)
    result31 = rf.read_int_reg(31)
    assert bin32_to_int(result31) == 0xDEADBEEF


def test_fp_reg_basic_read_write():
    """Test basic FP register read/write operations."""
    rf = RegisterFile()

    # Test register f0
    value0 = int_to_bin32(0x3F800000)  # IEEE 754 for 1.0
    rf.write_fp_reg(0, value0)
    result0 = rf.read_fp_reg(0)
    assert bin32_to_int(result0) == 0x3F800000

    # Test register f15
    value15 = int_to_bin32(0x40000000)  # IEEE 754 for 2.0
    rf.write_fp_reg(15, value15)
    result15 = rf.read_fp_reg(15)
    assert bin32_to_int(result15) == 0x40000000

    # Test register f31
    value31 = int_to_bin32(0xC0000000)  # IEEE 754 for -2.0
    rf.write_fp_reg(31, value31)
    result31 = rf.read_fp_reg(31)
    assert bin32_to_int(result31) == 0xC0000000


def test_fcsr_basic_read_write():
    """Test basic FCSR read/write operations."""
    rf = RegisterFile()

    # Write a specific pattern to FCSR
    fcsr_value = [1, 0, 1, 0, 1, 0, 1, 0]  # 0xAA
    rf.write_fcsr(fcsr_value)
    result = rf.read_fcsr()
    assert result == fcsr_value

    # Write all ones
    fcsr_ones = [1] * 8
    rf.write_fcsr(fcsr_ones)
    result = rf.read_fcsr()
    assert result == fcsr_ones

    # Write all zeros
    fcsr_zeros = [0] * 8
    rf.write_fcsr(fcsr_zeros)
    result = rf.read_fcsr()
    assert result == fcsr_zeros


# =============================================================================
# Edge Case Tests
# =============================================================================

def test_invalid_int_register_number():
    """Test that invalid integer register numbers raise ValueError."""
    rf = RegisterFile()

    # Test negative register number
    with pytest.raises(ValueError, match="Invalid integer register number"):
        rf.read_int_reg(-1)

    with pytest.raises(ValueError, match="Invalid integer register number"):
        rf.write_int_reg(-1, [0] * 32)

    # Test register number >= 32
    with pytest.raises(ValueError, match="Invalid integer register number"):
        rf.read_int_reg(32)

    with pytest.raises(ValueError, match="Invalid integer register number"):
        rf.write_int_reg(33, [0] * 32)

    # Test very large register number
    with pytest.raises(ValueError, match="Invalid integer register number"):
        rf.read_int_reg(1000)


def test_invalid_fp_register_number():
    """Test that invalid FP register numbers raise ValueError."""
    rf = RegisterFile()

    # Test negative register number
    with pytest.raises(ValueError, match="Invalid FP register number"):
        rf.read_fp_reg(-1)

    with pytest.raises(ValueError, match="Invalid FP register number"):
        rf.write_fp_reg(-5, [0] * 32)

    # Test register number >= 32
    with pytest.raises(ValueError, match="Invalid FP register number"):
        rf.read_fp_reg(32)

    with pytest.raises(ValueError, match="Invalid FP register number"):
        rf.write_fp_reg(40, [0] * 32)


def test_invalid_bit_width_int_reg():
    """Test that wrong bit width values raise ValueError for int registers."""
    rf = RegisterFile()

    # Too few bits
    with pytest.raises(ValueError, match="Value must be 32 bits"):
        rf.write_int_reg(5, [0] * 16)

    # Too many bits
    with pytest.raises(ValueError, match="Value must be 32 bits"):
        rf.write_int_reg(5, [0] * 64)

    # Empty array
    with pytest.raises(ValueError, match="Value must be 32 bits"):
        rf.write_int_reg(5, [])

    # Single bit
    with pytest.raises(ValueError, match="Value must be 32 bits"):
        rf.write_int_reg(5, [1])


def test_invalid_bit_width_fp_reg():
    """Test that wrong bit width values raise ValueError for FP registers."""
    rf = RegisterFile()

    # Too few bits
    with pytest.raises(ValueError, match="Value must be 32 bits"):
        rf.write_fp_reg(10, [0] * 8)

    # Too many bits
    with pytest.raises(ValueError, match="Value must be 32 bits"):
        rf.write_fp_reg(10, [1] * 48)


def test_invalid_fcsr_width():
    """Test that wrong bit width for FCSR raises ValueError."""
    rf = RegisterFile()

    # Too few bits
    with pytest.raises(ValueError, match="FCSR value must be 8 bits"):
        rf.write_fcsr([0] * 4)

    # Too many bits
    with pytest.raises(ValueError, match="FCSR value must be 8 bits"):
        rf.write_fcsr([1] * 16)


def test_boundary_values_int_reg():
    """Test boundary values for integer registers."""
    rf = RegisterFile()

    # All zeros
    all_zeros = [0] * 32
    rf.write_int_reg(10, all_zeros)
    assert rf.read_int_reg(10) == all_zeros

    # All ones (maximum value)
    all_ones = [1] * 32
    rf.write_int_reg(10, all_ones)
    assert rf.read_int_reg(10) == all_ones

    # Alternating pattern 10101010...
    pattern1 = [1, 0] * 16
    rf.write_int_reg(10, pattern1)
    assert rf.read_int_reg(10) == pattern1

    # Alternating pattern 01010101...
    pattern2 = [0, 1] * 16
    rf.write_int_reg(10, pattern2)
    assert rf.read_int_reg(10) == pattern2

    # Only MSB set (sign bit)
    msb_only = [1] + [0] * 31
    rf.write_int_reg(10, msb_only)
    assert rf.read_int_reg(10) == msb_only

    # Only LSB set
    lsb_only = [0] * 31 + [1]
    rf.write_int_reg(10, lsb_only)
    assert rf.read_int_reg(10) == lsb_only


def test_register_isolation_int():
    """Test that writing to one int register doesn't affect others."""
    rf = RegisterFile()

    # Write different values to multiple registers
    rf.write_int_reg(1, int_to_bin32(111))
    rf.write_int_reg(2, int_to_bin32(222))
    rf.write_int_reg(3, int_to_bin32(333))
    rf.write_int_reg(31, int_to_bin32(999))

    # Verify each register has the correct value
    assert bin32_to_int(rf.read_int_reg(1)) == 111
    assert bin32_to_int(rf.read_int_reg(2)) == 222
    assert bin32_to_int(rf.read_int_reg(3)) == 333
    assert bin32_to_int(rf.read_int_reg(31)) == 999

    # Verify other registers are still zero
    for i in [4, 5, 10, 15, 20, 25, 30]:
        assert rf.read_int_reg(i) == [0] * 32, f"x{i} was affected"


def test_register_isolation_fp():
    """Test that writing to one FP register doesn't affect others."""
    rf = RegisterFile()

    # Write different values to multiple registers
    rf.write_fp_reg(0, int_to_bin32(0x3F800000))
    rf.write_fp_reg(5, int_to_bin32(0x40000000))
    rf.write_fp_reg(10, int_to_bin32(0x40400000))
    rf.write_fp_reg(31, int_to_bin32(0xC0000000))

    # Verify each register has the correct value
    assert bin32_to_int(rf.read_fp_reg(0)) == 0x3F800000
    assert bin32_to_int(rf.read_fp_reg(5)) == 0x40000000
    assert bin32_to_int(rf.read_fp_reg(10)) == 0x40400000
    assert bin32_to_int(rf.read_fp_reg(31)) == 0xC0000000

    # Verify other registers are still zero
    for i in [1, 2, 3, 15, 20, 25]:
        assert rf.read_fp_reg(i) == [0] * 32, f"f{i} was affected"


def test_multiple_writes_to_same_register():
    """Test that multiple writes to the same register work correctly (last write wins)."""
    rf = RegisterFile()

    # Write multiple values to x7
    rf.write_int_reg(7, int_to_bin32(100))
    assert bin32_to_int(rf.read_int_reg(7)) == 100

    rf.write_int_reg(7, int_to_bin32(200))
    assert bin32_to_int(rf.read_int_reg(7)) == 200

    rf.write_int_reg(7, int_to_bin32(300))
    assert bin32_to_int(rf.read_int_reg(7)) == 300

    # Same for FP register
    rf.write_fp_reg(12, int_to_bin32(111))
    rf.write_fp_reg(12, int_to_bin32(222))
    rf.write_fp_reg(12, int_to_bin32(333))
    assert bin32_to_int(rf.read_fp_reg(12)) == 333


def test_copy_semantics():
    """Test that returned values are copies, not references."""
    rf = RegisterFile()

    # Write a value to x5
    original = int_to_bin32(42)
    rf.write_int_reg(5, original)

    # Read the value
    read_value = rf.read_int_reg(5)

    # Modify the read value
    read_value[0] = 1 if read_value[0] == 0 else 0

    # Verify the register wasn't affected
    assert rf.read_int_reg(5) == original

    # Same test for FP registers
    fp_original = int_to_bin32(100)
    rf.write_fp_reg(10, fp_original)
    fp_read = rf.read_fp_reg(10)
    fp_read[5] = 1 if fp_read[5] == 0 else 0
    assert rf.read_fp_reg(10) == fp_original


# =============================================================================
# Performance Tests
# =============================================================================

def test_bulk_operations_all_int_registers():
    """Test writing and reading all 32 integer registers."""
    rf = RegisterFile()

    # Write unique values to all registers (except x0)
    for i in range(1, 32):
        value = int_to_bin32(i * 1000)
        rf.write_int_reg(i, value)

    # Verify all values
    for i in range(1, 32):
        expected = i * 1000
        actual = bin32_to_int(rf.read_int_reg(i))
        assert actual == expected, f"x{i} has wrong value"

    # Verify x0 is still zero
    assert rf.read_int_reg(0) == [0] * 32


def test_bulk_operations_all_fp_registers():
    """Test writing and reading all 32 FP registers."""
    rf = RegisterFile()

    # Write unique values to all FP registers
    for i in range(32):
        value = int_to_bin32(i * 2000)
        rf.write_fp_reg(i, value)

    # Verify all values
    for i in range(32):
        expected = i * 2000
        actual = bin32_to_int(rf.read_fp_reg(i))
        assert actual == expected, f"f{i} has wrong value"


def test_stress_repeated_operations():
    """Stress test with many repeated operations."""
    rf = RegisterFile()

    # Perform 1000 write/read cycles on various registers
    for iteration in range(100):
        for reg in [1, 5, 10, 15, 20, 25, 30, 31]:
            value = int_to_bin32((iteration * reg) & 0xFFFFFFFF)
            rf.write_int_reg(reg, value)
            read_back = rf.read_int_reg(reg)
            assert read_back == value


def test_interleaved_int_fp_operations():
    """Test interleaved integer and FP register operations."""
    rf = RegisterFile()

    # Interleave int and FP writes
    for i in range(16):
        rf.write_int_reg(i, int_to_bin32(i * 100))
        rf.write_fp_reg(i, int_to_bin32(i * 200))

    # Verify all values
    for i in range(16):
        assert bin32_to_int(rf.read_int_reg(i)) == i * 100
        assert bin32_to_int(rf.read_fp_reg(i)) == i * 200


# =============================================================================
# FCSR Specific Tests
# =============================================================================

def test_rounding_mode_operations():
    """Test FCSR rounding mode field operations."""
    rf = RegisterFile()

    # Test RNE (Round to Nearest, ties to Even) = [0,0,0]
    rf.set_rounding_mode([0, 0, 0])
    assert rf.get_rounding_mode() == [0, 0, 0]

    # Test RTZ (Round Toward Zero) = [0,0,1]
    rf.set_rounding_mode([0, 0, 1])
    assert rf.get_rounding_mode() == [0, 0, 1]

    # Test RDN (Round Down) = [0,1,0]
    rf.set_rounding_mode([0, 1, 0])
    assert rf.get_rounding_mode() == [0, 1, 0]

    # Test RUP (Round Up) = [0,1,1]
    rf.set_rounding_mode([0, 1, 1])
    assert rf.get_rounding_mode() == [0, 1, 1]

    # Test RMM = [1,0,0]
    rf.set_rounding_mode([1, 0, 0])
    assert rf.get_rounding_mode() == [1, 0, 0]


def test_fflags_operations():
    """Test FCSR exception flags field operations."""
    rf = RegisterFile()

    # Test all zeros
    rf.set_fflags([0, 0, 0, 0, 0])
    assert rf.get_fflags() == [0, 0, 0, 0, 0]

    # Test all ones
    rf.set_fflags([1, 1, 1, 1, 1])
    assert rf.get_fflags() == [1, 1, 1, 1, 1]

    # Test specific pattern
    rf.set_fflags([1, 0, 1, 0, 1])
    assert rf.get_fflags() == [1, 0, 1, 0, 1]


def test_individual_exception_flags():
    """Test setting and getting individual exception flags."""
    rf = RegisterFile()

    # Initially all flags should be zero
    assert rf.get_flag_nv() == 0
    assert rf.get_flag_dz() == 0
    assert rf.get_flag_of() == 0
    assert rf.get_flag_uf() == 0
    assert rf.get_flag_nx() == 0

    # Set NV (Invalid Operation) flag
    rf.set_flag_nv(1)
    assert rf.get_flag_nv() == 1
    assert rf.get_flag_dz() == 0  # Others unaffected

    # Set DZ (Divide by Zero) flag
    rf.set_flag_dz(1)
    assert rf.get_flag_dz() == 1
    assert rf.get_flag_nv() == 1  # Previous flag still set

    # Set OF (Overflow) flag
    rf.set_flag_of(1)
    assert rf.get_flag_of() == 1

    # Set UF (Underflow) flag
    rf.set_flag_uf(1)
    assert rf.get_flag_uf() == 1

    # Set NX (Inexact) flag
    rf.set_flag_nx(1)
    assert rf.get_flag_nx() == 1

    # Verify all flags are set
    assert rf.get_fflags() == [1, 1, 1, 1, 1]

    # Clear NV flag
    rf.set_flag_nv(0)
    assert rf.get_flag_nv() == 0
    assert rf.get_fflags() == [0, 1, 1, 1, 1]


def test_fcsr_field_isolation():
    """Test that frm and fflags fields don't interfere with each other."""
    rf = RegisterFile()

    # Set rounding mode to [1,0,1]
    rf.set_rounding_mode([1, 0, 1])
    assert rf.get_rounding_mode() == [1, 0, 1]
    assert rf.get_fflags() == [0, 0, 0, 0, 0]  # Flags should be zero

    # Set fflags to [1,1,0,0,1]
    rf.set_fflags([1, 1, 0, 0, 1])
    assert rf.get_fflags() == [1, 1, 0, 0, 1]
    assert rf.get_rounding_mode() == [1, 0, 1]  # Rounding mode unchanged

    # Change rounding mode again
    rf.set_rounding_mode([0, 1, 0])
    assert rf.get_rounding_mode() == [0, 1, 0]
    assert rf.get_fflags() == [1, 1, 0, 0, 1]  # Flags unchanged


def test_fcsr_full_roundtrip():
    """Test reading and writing full FCSR preserves all bits."""
    rf = RegisterFile()

    # Set specific FCSR pattern: frm=[1,0,1], fflags=[0,1,1,0,1]
    # Binary: 10101101 = 0xAD
    fcsr_pattern = [1, 0, 1, 0, 1, 1, 0, 1]
    rf.write_fcsr(fcsr_pattern)

    # Read back
    result = rf.read_fcsr()
    assert result == fcsr_pattern

    # Verify fields
    assert rf.get_rounding_mode() == [1, 0, 1]
    assert rf.get_fflags() == [0, 1, 1, 0, 1]


def test_invalid_rounding_mode_width():
    """Test that invalid rounding mode width raises ValueError."""
    rf = RegisterFile()

    with pytest.raises(ValueError, match="Rounding mode must be 3 bits"):
        rf.set_rounding_mode([0, 0])  # Too few bits

    with pytest.raises(ValueError, match="Rounding mode must be 3 bits"):
        rf.set_rounding_mode([0, 0, 0, 0])  # Too many bits


def test_invalid_fflags_width():
    """Test that invalid fflags width raises ValueError."""
    rf = RegisterFile()

    with pytest.raises(ValueError, match="Exception flags must be 5 bits"):
        rf.set_fflags([0, 0, 0])  # Too few bits

    with pytest.raises(ValueError, match="Exception flags must be 5 bits"):
        rf.set_fflags([1, 1, 1, 1, 1, 1])  # Too many bits


# =============================================================================
# Control Signal Integration Tests
# =============================================================================

def test_register_with_control_basic_read():
    """Test basic register read using control signals."""
    from riscsim.cpu.registers import RegisterFile, register_with_control
    from riscsim.cpu.control_signals import ControlSignals

    rf = RegisterFile()
    signals = ControlSignals()

    # Pre-load some values
    rf.write_int_reg(5, int_to_bin32(42))
    rf.write_int_reg(10, int_to_bin32(100))

    # Set up read addresses
    signals.rf_raddr_a = int_to_bits(5, 5)
    signals.rf_raddr_b = int_to_bits(10, 5)
    signals.rf_we = 0  # No write

    result = register_with_control(rf, signals)

    assert bin32_to_int(result['read_a']) == 42
    assert bin32_to_int(result['read_b']) == 100
    assert result['written'] == False
    assert 'READ_A' in result['trace'][0]
    assert 'READ_B' in result['trace'][1]


def test_register_with_control_basic_write():
    """Test basic register write using control signals."""
    from riscsim.cpu.registers import RegisterFile, register_with_control
    from riscsim.cpu.control_signals import ControlSignals

    rf = RegisterFile()
    signals = ControlSignals()

    # Set up write operation
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(7, 5)
    signals.rf_raddr_a = int_to_bits(7, 5)  # Read back the written value
    signals.rf_raddr_b = int_to_bits(0, 5)  # x0

    write_data = int_to_bin32(255)
    result = register_with_control(rf, signals, write_data)

    assert result['written'] == True
    assert bin32_to_int(result['read_a']) == 255
    assert bin32_to_int(result['read_b']) == 0  # x0 always 0
    assert 'WRITE' in result['trace'][0]


def test_register_with_control_x0_hardwired():
    """Test that x0 remains zero even with write enable."""
    from riscsim.cpu.registers import RegisterFile, register_with_control
    from riscsim.cpu.control_signals import ControlSignals

    rf = RegisterFile()
    signals = ControlSignals()

    # Try to write to x0
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(0, 5)  # x0
    signals.rf_raddr_a = int_to_bits(0, 5)
    signals.rf_raddr_b = int_to_bits(0, 5)

    write_data = int_to_bin32(999)
    result = register_with_control(rf, signals, write_data)

    # x0 should still be 0
    assert bin32_to_int(result['read_a']) == 0
    assert bin32_to_int(result['read_b']) == 0
    assert result['written'] == True  # Write was attempted


def test_register_with_control_write_then_read_sequence():
    """Test write followed by read in sequence."""
    from riscsim.cpu.registers import RegisterFile, register_with_control
    from riscsim.cpu.control_signals import ControlSignals

    rf = RegisterFile()
    signals = ControlSignals()

    # Step 1: Write to x15
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(15, 5)
    signals.rf_raddr_a = int_to_bits(0, 5)
    signals.rf_raddr_b = int_to_bits(0, 5)

    result1 = register_with_control(rf, signals, int_to_bin32(777))
    assert result1['written'] == True

    # Step 2: Read from x15
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(15, 5)
    signals.rf_raddr_b = int_to_bits(0, 5)

    result2 = register_with_control(rf, signals)
    assert bin32_to_int(result2['read_a']) == 777
    assert result2['written'] == False


def test_register_with_control_multiple_writes():
    """Test multiple writes to different registers."""
    from riscsim.cpu.registers import RegisterFile, register_with_control
    from riscsim.cpu.control_signals import ControlSignals

    rf = RegisterFile()
    signals = ControlSignals()

    # Write to multiple registers
    test_values = [(1, 10), (5, 50), (10, 100), (20, 200), (31, 310)]

    signals.rf_we = 1
    for reg, val in test_values:
        signals.rf_waddr = int_to_bits(reg, 5)
        signals.rf_raddr_a = int_to_bits(0, 5)
        signals.rf_raddr_b = int_to_bits(0, 5)
        register_with_control(rf, signals, int_to_bin32(val))

    # Verify all values
    signals.rf_we = 0
    for reg, expected_val in test_values:
        signals.rf_raddr_a = int_to_bits(reg, 5)
        signals.rf_raddr_b = int_to_bits(0, 5)
        result = register_with_control(rf, signals)
        assert bin32_to_int(result['read_a']) == expected_val


def test_register_with_control_simultaneous_write_read():
    """Test simultaneous write to one register and read from another."""
    from riscsim.cpu.registers import RegisterFile, register_with_control
    from riscsim.cpu.control_signals import ControlSignals

    rf = RegisterFile()
    signals = ControlSignals()

    # Pre-load x5 with a value
    rf.write_int_reg(5, int_to_bin32(500))

    # Write to x10, read from x5 and x0
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(10, 5)
    signals.rf_raddr_a = int_to_bits(5, 5)
    signals.rf_raddr_b = int_to_bits(0, 5)

    result = register_with_control(rf, signals, int_to_bin32(1000))

    assert result['written'] == True
    assert bin32_to_int(result['read_a']) == 500  # Read from x5
    assert bin32_to_int(result['read_b']) == 0    # Read from x0
    
    # Verify write took effect
    assert bin32_to_int(rf.read_int_reg(10)) == 1000


def test_register_with_control_signal_preservation():
    """Test that control signals are preserved in result."""
    from riscsim.cpu.registers import RegisterFile, register_with_control
    from riscsim.cpu.control_signals import ControlSignals

    rf = RegisterFile()
    signals = ControlSignals()

    # Set various control signals
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(8, 5)
    signals.rf_raddr_a = int_to_bits(3, 5)
    signals.rf_raddr_b = int_to_bits(12, 5)
    signals.cycle = 42
    signals.pc = [0] * 31 + [1]

    result = register_with_control(rf, signals, int_to_bin32(88))

    # Verify signals are preserved
    assert result['signals'].rf_we == 1
    assert bits_to_int(result['signals'].rf_waddr) == 8
    assert bits_to_int(result['signals'].rf_raddr_a) == 3
    assert bits_to_int(result['signals'].rf_raddr_b) == 12
    assert result['signals'].cycle == 42


def test_register_with_control_trace_output():
    """Test that trace includes correct operation information."""
    from riscsim.cpu.registers import RegisterFile, register_with_control
    from riscsim.cpu.control_signals import ControlSignals

    rf = RegisterFile()
    signals = ControlSignals()

    # Perform write operation
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(15, 5)
    signals.rf_raddr_a = int_to_bits(15, 5)
    signals.rf_raddr_b = int_to_bits(20, 5)

    result = register_with_control(rf, signals, int_to_bin32(999))

    # Check trace contains expected operations
    trace_str = ' '.join(result['trace'])
    assert 'WRITE' in trace_str
    assert 'x15' in trace_str
    assert 'READ_A' in trace_str
    assert 'READ_B' in trace_str
    assert 'x20' in trace_str


def test_register_with_control_no_write_data_error():
    """Test that error is raised when write_data is missing with rf_we=1."""
    from riscsim.cpu.registers import RegisterFile, register_with_control
    from riscsim.cpu.control_signals import ControlSignals

    rf = RegisterFile()
    signals = ControlSignals()

    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(5, 5)

    with pytest.raises(ValueError, match="write_data required"):
        register_with_control(rf, signals)  # Missing write_data


def test_register_with_control_invalid_write_data_width():
    """Test that error is raised when write_data has wrong width."""
    from riscsim.cpu.registers import RegisterFile, register_with_control
    from riscsim.cpu.control_signals import ControlSignals

    rf = RegisterFile()
    signals = ControlSignals()

    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(5, 5)

    with pytest.raises(ValueError, match="must be 32 bits"):
        register_with_control(rf, signals, [1] * 16)  # Wrong width


def test_register_with_control_boundary_addresses():
    """Test control signal integration with boundary register addresses."""
    from riscsim.cpu.registers import RegisterFile, register_with_control
    from riscsim.cpu.control_signals import ControlSignals

    rf = RegisterFile()
    signals = ControlSignals()

    # Test x0 (lower boundary)
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(0, 5)
    signals.rf_raddr_b = int_to_bits(0, 5)
    result = register_with_control(rf, signals)
    assert bin32_to_int(result['read_a']) == 0
    assert bin32_to_int(result['read_b']) == 0

    # Test x31 (upper boundary)
    rf.write_int_reg(31, int_to_bin32(0xFFFFFFFF))
    signals.rf_raddr_a = int_to_bits(31, 5)
    signals.rf_raddr_b = int_to_bits(31, 5)
    result = register_with_control(rf, signals)
    assert bin32_to_int(result['read_a'], signed=False) == 0xFFFFFFFF
    assert bin32_to_int(result['read_b'], signed=False) == 0xFFFFFFFF


def test_register_with_control_full_register_scan():
    """Test reading all 32 registers using control signals."""
    from riscsim.cpu.registers import RegisterFile, register_with_control
    from riscsim.cpu.control_signals import ControlSignals

    rf = RegisterFile()
    signals = ControlSignals()

    # Write unique values to all registers
    signals.rf_we = 1
    for i in range(32):
        signals.rf_waddr = int_to_bits(i, 5)
        signals.rf_raddr_a = int_to_bits(0, 5)
        signals.rf_raddr_b = int_to_bits(0, 5)
        register_with_control(rf, signals, int_to_bin32(i * 10))

    # Read and verify all registers
    signals.rf_we = 0
    for i in range(32):
        signals.rf_raddr_a = int_to_bits(i, 5)
        signals.rf_raddr_b = int_to_bits(0, 5)
        result = register_with_control(rf, signals)
        expected = 0 if i == 0 else i * 10  # x0 always 0
        assert bin32_to_int(result['read_a']) == expected


# =============================================================================
# Run standalone tests with output
# =============================================================================

if __name__ == "__main__":
    print("Running RegisterFile tests...")
    pytest.main([__file__, "-v"])

# AI-END

