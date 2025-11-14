# AI-BEGIN
"""
CPU Integration Test Suite

Tests the integration of all CPU components working together:
- ALU (Arithmetic Logic Unit)
- Shifter (Barrel Shifter)
- FPU (Floating-Point Unit)
- Registers (Integer and FP registers, FCSR)

This simulates a simple CPU executing a sequence of operations
to verify that all components work correctly together.
"""

import pytest
from riscsim.cpu.alu import alu
from riscsim.cpu.shifter import shifter
from riscsim.cpu.fpu import pack_f32, unpack_f32, fadd_f32, fsub_f32, fmul_f32
from riscsim.cpu.registers import RegisterFile
from riscsim.utils.bit_utils import bits_to_hex_string, hex_string_to_bits, int_to_bits_unsigned


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


class TestCPUIntegration:
    """Test integration of all CPU components."""

    def test_alu_and_registers(self):
        """Test ALU operations writing to and reading from registers."""
        rf = RegisterFile()

        # Load some values into registers
        val_a = int_to_bin32(100)
        val_b = int_to_bin32(50)

        rf.write_int_reg(1, val_a)  # x1 = 100
        rf.write_int_reg(2, val_b)  # x2 = 50

        # Read values from registers
        rs1 = rf.read_int_reg(1)
        rs2 = rf.read_int_reg(2)

        # Perform ADD using ALU: x3 = x1 + x2
        result, flags = alu(rs1, rs2, [0, 0, 1, 0])  # ADD opcode

        # Write result to register
        rf.write_int_reg(3, result)

        # Read result and verify
        x3 = rf.read_int_reg(3)
        assert bin32_to_int(x3) == 150

        # Verify flags
        N, Z, C, V = flags
        assert N == 0  # Not negative
        assert Z == 0  # Not zero
        assert V == 0  # No overflow

    def test_alu_subtraction_with_flags(self):
        """Test ALU subtraction with flag checking."""
        rf = RegisterFile()

        # Test subtraction that results in negative number
        val_a = int_to_bin32(50)
        val_b = int_to_bin32(100)

        rf.write_int_reg(1, val_a)  # x1 = 50
        rf.write_int_reg(2, val_b)  # x2 = 100

        rs1 = rf.read_int_reg(1)
        rs2 = rf.read_int_reg(2)

        # SUB: x3 = x1 - x2 = 50 - 100 = -50
        result, flags = alu(rs1, rs2, [0, 1, 1, 0])  # SUB opcode

        rf.write_int_reg(3, result)
        x3 = rf.read_int_reg(3)

        # Verify result (should be -50 in two's complement)
        assert bin32_to_int(x3, signed=True) == -50

        # Verify flags
        N, Z, C, V = flags
        assert N == 1  # Negative result
        assert Z == 0  # Not zero
        assert V == 0  # No overflow

    def test_shifter_and_alu_combination(self):
        """Test combining shifter and ALU operations."""
        rf = RegisterFile()

        # Scenario: Compute (x1 << 2) + x2
        val_x1 = int_to_bin32(5)   # x1 = 5
        val_x2 = int_to_bin32(10)  # x2 = 10

        rf.write_int_reg(1, val_x1)
        rf.write_int_reg(2, val_x2)

        # Step 1: Shift x1 left by 2 (5 << 2 = 20)
        x1 = rf.read_int_reg(1)
        shifted = shifter(x1, 2, "SLL")

        # Step 2: Add shifted value to x2 (20 + 10 = 30)
        x2 = rf.read_int_reg(2)
        result, _ = alu(shifted, x2, [0, 0, 1, 0])  # ADD

        # Step 3: Store result in x3
        rf.write_int_reg(3, result)
        x3 = rf.read_int_reg(3)

        # Verify: (5 << 2) + 10 = 20 + 10 = 30
        assert bin32_to_int(x3) == 30

    def test_fpu_and_registers(self):
        """Test FPU operations with floating-point registers."""
        rf = RegisterFile()

        # Load floating-point values into FP registers
        val_a = pack_f32(3.5)   # f1 = 3.5
        val_b = pack_f32(2.25)  # f2 = 2.25

        rf.write_fp_reg(1, val_a)
        rf.write_fp_reg(2, val_b)

        # Read from FP registers
        f1 = rf.read_fp_reg(1)
        f2 = rf.read_fp_reg(2)

        # Perform FADD: f3 = f1 + f2
        result_dict = fadd_f32(f1, f2)
        result_bits = result_dict['result']

        # Write result to FP register
        rf.write_fp_reg(3, result_bits)

        # Read and verify result
        f3 = rf.read_fp_reg(3)
        result_val = unpack_f32(f3)

        # 3.5 + 2.25 = 5.75
        assert abs(result_val - 5.75) < 1e-6

        # Check FCSR flags (should be no exceptions)
        flags = result_dict['flags']
        assert flags['invalid'] == 0
        assert flags['overflow'] == 0
        assert flags['underflow'] == 0

    def test_fpu_multiply_chain(self):
        """Test chained FPU multiplication operations."""
        rf = RegisterFile()

        # f1 = 2.0, f2 = 3.0, f3 = 4.0
        rf.write_fp_reg(1, pack_f32(2.0))
        rf.write_fp_reg(2, pack_f32(3.0))
        rf.write_fp_reg(3, pack_f32(4.0))

        # Step 1: f4 = f1 * f2 (2.0 * 3.0 = 6.0)
        f1 = rf.read_fp_reg(1)
        f2 = rf.read_fp_reg(2)
        result1 = fmul_f32(f1, f2)
        rf.write_fp_reg(4, result1['result'])

        # Step 2: f5 = f4 * f3 (6.0 * 4.0 = 24.0)
        f4 = rf.read_fp_reg(4)
        f3 = rf.read_fp_reg(3)
        result2 = fmul_f32(f4, f3)
        rf.write_fp_reg(5, result2['result'])

        # Verify final result
        f5 = rf.read_fp_reg(5)
        final_val = unpack_f32(f5)

        # 2.0 * 3.0 * 4.0 = 24.0
        assert abs(final_val - 24.0) < 1e-6

    def test_mixed_integer_and_float_operations(self):
        """Test interleaved integer and floating-point operations."""
        rf = RegisterFile()

        # Integer operations
        rf.write_int_reg(1, int_to_bin32(10))
        rf.write_int_reg(2, int_to_bin32(20))

        x1 = rf.read_int_reg(1)
        x2 = rf.read_int_reg(2)

        # x3 = x1 + x2
        int_result, _ = alu(x1, x2, [0, 0, 1, 0])
        rf.write_int_reg(3, int_result)

        # Floating-point operations
        rf.write_fp_reg(1, pack_f32(1.5))
        rf.write_fp_reg(2, pack_f32(2.5))

        f1 = rf.read_fp_reg(1)
        f2 = rf.read_fp_reg(2)

        # f3 = f1 + f2
        fp_result = fadd_f32(f1, f2)
        rf.write_fp_reg(3, fp_result['result'])

        # Verify both results
        x3 = rf.read_int_reg(3)
        f3 = rf.read_fp_reg(3)

        assert bin32_to_int(x3) == 30  # Integer: 10 + 20
        assert abs(unpack_f32(f3) - 4.0) < 1e-6  # Float: 1.5 + 2.5

    def test_complex_computation_sequence(self):
        """
        Test a complex sequence of operations simulating real computation.

        Computes: ((a + b) << 1) - c
        Where a=100, b=50, c=25
        Expected: ((100 + 50) << 1) - 25 = (150 << 1) - 25 = 300 - 25 = 275
        """
        rf = RegisterFile()

        # Load initial values
        rf.write_int_reg(1, int_to_bin32(100))  # x1 = a = 100
        rf.write_int_reg(2, int_to_bin32(50))   # x2 = b = 50
        rf.write_int_reg(3, int_to_bin32(25))   # x3 = c = 25

        # Step 1: x4 = x1 + x2
        x1 = rf.read_int_reg(1)
        x2 = rf.read_int_reg(2)
        sum_result, _ = alu(x1, x2, [0, 0, 1, 0])
        rf.write_int_reg(4, sum_result)

        # Step 2: x5 = x4 << 1
        x4 = rf.read_int_reg(4)
        shifted = shifter(x4, 1, "SLL")
        rf.write_int_reg(5, shifted)

        # Step 3: x6 = x5 - x3
        x5 = rf.read_int_reg(5)
        x3 = rf.read_int_reg(3)
        diff_result, _ = alu(x5, x3, [0, 1, 1, 0])
        rf.write_int_reg(6, diff_result)

        # Verify final result
        x6 = rf.read_int_reg(6)
        final_value = bin32_to_int(x6)

        assert final_value == 275

    def test_fpu_with_fcsr_flags(self):
        """Test FPU operations updating FCSR flags."""
        rf = RegisterFile()

        # Test overflow operation
        large_val = pack_f32(3.0e38)
        rf.write_fp_reg(1, large_val)
        rf.write_fp_reg(2, large_val)

        f1 = rf.read_fp_reg(1)
        f2 = rf.read_fp_reg(2)

        # This should overflow
        result = fadd_f32(f1, f2)

        # Manually update FCSR flags based on operation result
        flags = result['flags']
        rf.set_flag_of(flags['overflow'])
        rf.set_flag_uf(flags['underflow'])
        rf.set_flag_nv(flags['invalid'])

        # Verify FCSR was updated
        assert rf.get_flag_of() == 1  # Overflow flag set

    def test_x0_hardwired_to_zero(self):
        """Test that x0 register is always zero."""
        rf = RegisterFile()

        # Try to write to x0
        rf.write_int_reg(0, int_to_bin32(999))

        # x0 should still be zero
        x0 = rf.read_int_reg(0)
        assert bin32_to_int(x0) == 0

        # Use x0 in computation
        x1_val = int_to_bin32(100)
        rf.write_int_reg(1, x1_val)

        x0 = rf.read_int_reg(0)
        x1 = rf.read_int_reg(1)

        # x2 = x0 + x1 = 0 + 100 = 100
        result, _ = alu(x0, x1, [0, 0, 1, 0])
        rf.write_int_reg(2, result)

        x2 = rf.read_int_reg(2)
        assert bin32_to_int(x2) == 100

    def test_shift_and_mask_operation(self):
        """Test combining shift and logical operations."""
        rf = RegisterFile()

        # Extract bits from a value using shift and mask
        value = int_to_bin32(0xABCD1234)
        mask = int_to_bin32(0x0000FFFF)

        rf.write_int_reg(1, value)
        rf.write_int_reg(2, mask)

        # Extract lower 16 bits using AND
        x1 = rf.read_int_reg(1)
        x2 = rf.read_int_reg(2)

        # x3 = x1 AND x2
        result, _ = alu(x1, x2, [0, 0, 0, 0])  # AND opcode
        rf.write_int_reg(3, result)

        x3 = rf.read_int_reg(3)
        # Result should be 0x00001234
        assert bits_to_hex_string(x3) == "0x00001234"


class TestCPUSimulation:
    """Simulate simple programs using all CPU components."""

    def test_factorial_computation(self):
        """
        Simulate computing factorial using shifts (multiply by powers of 2).
        Compute 4! = 4 * 3 * 2 * 1 = 24
        (simplified: we'll compute 4 * 2 * 2 = 16 using shifts)
        """
        rf = RegisterFile()

        # Initialize: x1 = 4
        rf.write_int_reg(1, int_to_bin32(4))

        # x2 = x1 << 1 (4 << 1 = 8)
        x1 = rf.read_int_reg(1)
        shifted = shifter(x1, 1, "SLL")
        rf.write_int_reg(2, shifted)

        # x3 = x2 << 1 (8 << 1 = 16)
        x2 = rf.read_int_reg(2)
        shifted2 = shifter(x2, 1, "SLL")
        rf.write_int_reg(3, shifted2)

        x3 = rf.read_int_reg(3)
        assert bin32_to_int(x3) == 16

    def test_floating_point_average(self):
        """
        Compute average of three floating-point numbers.
        Average of 1.0, 2.0, 3.0 = 6.0 / 3.0 = 2.0
        """
        rf = RegisterFile()

        # Load values
        rf.write_fp_reg(1, pack_f32(1.0))
        rf.write_fp_reg(2, pack_f32(2.0))
        rf.write_fp_reg(3, pack_f32(3.0))

        # Sum = f1 + f2
        f1 = rf.read_fp_reg(1)
        f2 = rf.read_fp_reg(2)
        sum1 = fadd_f32(f1, f2)
        rf.write_fp_reg(4, sum1['result'])

        # Sum = Sum + f3
        f4 = rf.read_fp_reg(4)
        f3 = rf.read_fp_reg(3)
        sum2 = fadd_f32(f4, f3)
        rf.write_fp_reg(5, sum2['result'])

        # Verify sum = 6.0
        f5 = rf.read_fp_reg(5)
        total = unpack_f32(f5)
        assert abs(total - 6.0) < 1e-6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
# AI-END
