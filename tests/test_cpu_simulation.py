# AI-BEGIN
"""
Comprehensive CPU Simulation Test Suite

This test suite simulates complete CPU functionality by running realistic programs
that combine all CPU components: ALU, Shifter, MDU, FPU, and Register File.

Test Phases:
1. Basic Component Integration - Verify all components work together
2. Integer Arithmetic Programs - Simulate realistic integer computations
3. Floating-Point Programs - Simulate scientific floating-point calculations
4. Mixed Integer/Float Operations - Test interleaved integer and FP operations
5. Complex Real-World Scenarios - Simulate complete programs like matrix operations

Each test represents a small program executing on the simulated CPU.
"""

import pytest
from riscsim.cpu.alu import alu
from riscsim.cpu.shifter import shifter
from riscsim.cpu.mdu import mul, mulh, div, rem
from riscsim.cpu.fpu import pack_f32, unpack_f32, fadd_f32, fsub_f32, fmul_f32
from riscsim.cpu.registers import RegisterFile
from riscsim.utils.bit_utils import bits_to_hex_string, hex_string_to_bits, int_to_bits_unsigned
from riscsim.utils.twos_complement import encode_twos_complement, decode_twos_complement


# ============================================================================
# Helper Functions
# ============================================================================

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


# ============================================================================
# Phase 1: Basic Component Integration Tests
# ============================================================================

class TestPhase1ComponentIntegration:
    """
    Phase 1: Verify all CPU components work together correctly.
    
    Tests basic operations combining ALU, Shifter, MDU, FPU, and Register File.
    """
    
    def test_all_alu_operations(self):
        """Test all ALU operations in sequence with register file."""
        rf = RegisterFile()
        
        # Setup: Load test values
        rf.write_int_reg(1, int_to_bin32(0xFF00FF00))  # x1 = pattern A
        rf.write_int_reg(2, int_to_bin32(0x00FF00FF))  # x2 = pattern B
        rf.write_int_reg(3, int_to_bin32(100))         # x3 = 100
        rf.write_int_reg(4, int_to_bin32(50))          # x4 = 50
        
        # Test AND operation
        result, _ = alu(rf.read_int_reg(1), rf.read_int_reg(2), [0, 0, 0, 0])
        rf.write_int_reg(5, result)
        assert bin32_to_int(rf.read_int_reg(5)) == 0x00000000
        
        # Test OR operation
        result, _ = alu(rf.read_int_reg(1), rf.read_int_reg(2), [0, 0, 0, 1])
        rf.write_int_reg(6, result)
        assert bin32_to_int(rf.read_int_reg(6)) == 0xFFFFFFFF
        
        # Test ADD operation
        result, _ = alu(rf.read_int_reg(3), rf.read_int_reg(4), [0, 0, 1, 0])
        rf.write_int_reg(7, result)
        assert bin32_to_int(rf.read_int_reg(7)) == 150
        
        # Test SUB operation
        result, _ = alu(rf.read_int_reg(3), rf.read_int_reg(4), [0, 1, 1, 0])
        rf.write_int_reg(8, result)
        assert bin32_to_int(rf.read_int_reg(8), signed=True) == 50
        
        # Test XOR operation
        result, _ = alu(rf.read_int_reg(1), rf.read_int_reg(2), [0, 0, 1, 1])
        rf.write_int_reg(9, result)
        assert bin32_to_int(rf.read_int_reg(9)) == 0xFFFFFFFF
        
        print("✓ All ALU operations working correctly with register file")
    
    def test_all_shift_operations(self):
        """Test all shifter operations with various shift amounts."""
        rf = RegisterFile()
        
        # Setup: Load test value
        test_val = int_to_bin32(0x12345678)
        rf.write_int_reg(1, test_val)
        
        # Test SLL (Shift Left Logical)
        for shamt in [0, 1, 4, 8, 16]:
            result = shifter(rf.read_int_reg(1), shamt, "SLL")
            rf.write_int_reg(2, result)
            # Verify shifted value
            expected = (0x12345678 << shamt) & 0xFFFFFFFF
            assert bin32_to_int(rf.read_int_reg(2)) == expected, f"SLL by {shamt} failed"
        
        # Test SRL (Shift Right Logical)
        for shamt in [0, 1, 4, 8, 16]:
            result = shifter(rf.read_int_reg(1), shamt, "SRL")
            rf.write_int_reg(3, result)
            expected = 0x12345678 >> shamt
            assert bin32_to_int(rf.read_int_reg(3)) == expected, f"SRL by {shamt} failed"
        
        # Test SRA (Shift Right Arithmetic) with negative number
        neg_val = int_to_bin32(-16)  # 0xFFFFFFF0
        rf.write_int_reg(4, neg_val)
        
        result = shifter(rf.read_int_reg(4), 2, "SRA")
        rf.write_int_reg(5, result)
        # SRA preserves sign bit, so -16 >> 2 = -4
        assert bin32_to_int(rf.read_int_reg(5), signed=True) == -4
        
        print("✓ All shifter operations working correctly")
    
    def test_mdu_operations(self):
        """Test MDU multiply and divide operations."""
        rf = RegisterFile()
        
        # Test MUL: 123 * 456
        rf.write_int_reg(1, int_to_bin32(123))
        rf.write_int_reg(2, int_to_bin32(456))
        
        mul_result = mul(rf.read_int_reg(1), rf.read_int_reg(2))
        rf.write_int_reg(3, mul_result['result'])
        
        assert bin32_to_int(rf.read_int_reg(3)) == 123 * 456
        print(f"  MUL: 123 * 456 = {bin32_to_int(rf.read_int_reg(3))}")
        
        # Test MULH: signed high word
        rf.write_int_reg(4, int_to_bin32(100000))
        rf.write_int_reg(5, int_to_bin32(100000))
        
        mulh_result = mulh(rf.read_int_reg(4), rf.read_int_reg(5))
        rf.write_int_reg(6, mulh_result['result'])
        
        # 100000 * 100000 = 10,000,000,000 (requires more than 32 bits)
        print(f"  MULH: 100000 * 100000 high word = {bits_to_hex_string(rf.read_int_reg(6))}")
        
        # Test DIV: 1000 / 7
        rf.write_int_reg(7, int_to_bin32(1000))
        rf.write_int_reg(8, int_to_bin32(7))
        
        div_result = div(rf.read_int_reg(7), rf.read_int_reg(8))
        rf.write_int_reg(9, div_result['quotient'])
        rf.write_int_reg(10, div_result['remainder'])
        
        assert bin32_to_int(rf.read_int_reg(9)) == 1000 // 7
        assert bin32_to_int(rf.read_int_reg(10)) == 1000 % 7
        print(f"  DIV: 1000 / 7 = {bin32_to_int(rf.read_int_reg(9))} remainder {bin32_to_int(rf.read_int_reg(10))}")
        
        # Test REM: remainder operation
        rem_result = rem(rf.read_int_reg(7), rf.read_int_reg(8))
        rf.write_int_reg(11, rem_result['remainder'])
        assert bin32_to_int(rf.read_int_reg(11)) == 1000 % 7
        
        print("✓ MDU operations working correctly")
    
    def test_fpu_operations(self):
        """Test FPU operations with floating-point register file."""
        rf = RegisterFile()
        
        # Test FADD
        rf.write_fp_reg(1, pack_f32(3.14159))
        rf.write_fp_reg(2, pack_f32(2.71828))
        
        fadd_result = fadd_f32(rf.read_fp_reg(1), rf.read_fp_reg(2))
        rf.write_fp_reg(3, fadd_result['result'])
        
        result_val = unpack_f32(rf.read_fp_reg(3))
        assert abs(result_val - (3.14159 + 2.71828)) < 1e-5
        print(f"  FADD: 3.14159 + 2.71828 = {result_val}")
        
        # Test FSUB
        fsub_result = fsub_f32(rf.read_fp_reg(1), rf.read_fp_reg(2))
        rf.write_fp_reg(4, fsub_result['result'])
        
        result_val = unpack_f32(rf.read_fp_reg(4))
        assert abs(result_val - (3.14159 - 2.71828)) < 1e-5
        print(f"  FSUB: 3.14159 - 2.71828 = {result_val}")
        
        # Test FMUL
        rf.write_fp_reg(5, pack_f32(2.5))
        rf.write_fp_reg(6, pack_f32(4.0))
        
        fmul_result = fmul_f32(rf.read_fp_reg(5), rf.read_fp_reg(6))
        rf.write_fp_reg(7, fmul_result['result'])
        
        result_val = unpack_f32(rf.read_fp_reg(7))
        assert abs(result_val - 10.0) < 1e-5
        print(f"  FMUL: 2.5 * 4.0 = {result_val}")
        
        print("✓ FPU operations working correctly")
    
    def test_register_file_isolation(self):
        """Test that integer and FP register files are isolated."""
        rf = RegisterFile()
        
        # Write same register number in both files
        rf.write_int_reg(5, int_to_bin32(12345))
        rf.write_fp_reg(5, pack_f32(67.89))
        
        # Read back and verify independence
        int_val = bin32_to_int(rf.read_int_reg(5))
        fp_val = unpack_f32(rf.read_fp_reg(5))
        
        assert int_val == 12345
        assert abs(fp_val - 67.89) < 1e-5
        
        # Verify x0 is always zero
        rf.write_int_reg(0, int_to_bin32(99999))
        assert bin32_to_int(rf.read_int_reg(0)) == 0
        
        print("✓ Register file isolation working correctly")


# ============================================================================
# Phase 2: Integer Arithmetic Program Simulations
# ============================================================================

class TestPhase2IntegerPrograms:
    """
    Phase 2: Simulate realistic integer arithmetic programs.
    
    Programs include: Fibonacci sequence, array sum, bit manipulation,
    and division with remainder.
    """
    
    def test_fibonacci_sequence(self):
        """
        Simulate computing Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34
        
        Algorithm:
            f[0] = 0
            f[1] = 1
            for i in 2..n:
                f[i] = f[i-1] + f[i-2]
        """
        rf = RegisterFile()
        
        # Initialize
        rf.write_int_reg(1, int_to_bin32(0))   # f[n-2] = 0
        rf.write_int_reg(2, int_to_bin32(1))   # f[n-1] = 1
        
        fib_sequence = [0, 1]
        
        # Compute next 8 Fibonacci numbers
        for i in range(8):
            # f[n] = f[n-1] + f[n-2]
            result, _ = alu(rf.read_int_reg(2), rf.read_int_reg(1), [0, 0, 1, 0])  # ADD
            rf.write_int_reg(3, result)
            
            fib_val = bin32_to_int(rf.read_int_reg(3))
            fib_sequence.append(fib_val)
            
            # Shift: f[n-2] = f[n-1], f[n-1] = f[n]
            rf.write_int_reg(1, rf.read_int_reg(2))
            rf.write_int_reg(2, rf.read_int_reg(3))
        
        # Verify Fibonacci sequence
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        assert fib_sequence == expected
        
        print(f"✓ Fibonacci sequence computed: {fib_sequence}")
    
    def test_array_sum(self):
        """
        Simulate computing sum of an array: [10, 20, 30, 40, 50]
        Expected sum: 150
        """
        rf = RegisterFile()
        
        # Load array values into registers x1-x5
        array = [10, 20, 30, 40, 50]
        for i, val in enumerate(array, 1):
            rf.write_int_reg(i, int_to_bin32(val))
        
        # Initialize sum to 0 in x10
        rf.write_int_reg(10, int_to_bin32(0))
        
        # Accumulate sum
        for i in range(1, 6):
            result, _ = alu(rf.read_int_reg(10), rf.read_int_reg(i), [0, 0, 1, 0])  # ADD
            rf.write_int_reg(10, result)
        
        total_sum = bin32_to_int(rf.read_int_reg(10))
        assert total_sum == 150
        
        print(f"✓ Array sum computed: {total_sum}")
    
    def test_multiply_by_shifting(self):
        """
        Simulate multiplication using shifts and adds: 25 * 13
        
        Algorithm: 25 * 13 = 25 * (8 + 4 + 1) = (25 << 3) + (25 << 2) + 25
        Expected: 325
        """
        rf = RegisterFile()
        
        # Load multiplicand: x1 = 25
        rf.write_int_reg(1, int_to_bin32(25))
        
        # Compute 25 << 3 (25 * 8 = 200)
        shifted_8 = shifter(rf.read_int_reg(1), 3, "SLL")
        rf.write_int_reg(2, shifted_8)
        
        # Compute 25 << 2 (25 * 4 = 100)
        shifted_4 = shifter(rf.read_int_reg(1), 2, "SLL")
        rf.write_int_reg(3, shifted_4)
        
        # Sum: (25 << 3) + (25 << 2)
        temp_sum, _ = alu(rf.read_int_reg(2), rf.read_int_reg(3), [0, 0, 1, 0])
        rf.write_int_reg(4, temp_sum)
        
        # Add original value: sum + 25
        final_result, _ = alu(rf.read_int_reg(4), rf.read_int_reg(1), [0, 0, 1, 0])
        rf.write_int_reg(5, final_result)
        
        result = bin32_to_int(rf.read_int_reg(5))
        assert result == 325
        
        print(f"✓ Multiplication by shifting: 25 * 13 = {result}")
    
    def test_division_with_remainder(self):
        """
        Simulate division with remainder: 1234 / 17
        
        Expected: quotient = 72, remainder = 10
        """
        rf = RegisterFile()
        
        # Load dividend and divisor
        rf.write_int_reg(1, int_to_bin32(1234))
        rf.write_int_reg(2, int_to_bin32(17))
        
        # Perform division using MDU
        div_result = div(rf.read_int_reg(1), rf.read_int_reg(2))
        rf.write_int_reg(3, div_result['quotient'])
        rf.write_int_reg(4, div_result['remainder'])
        
        quotient = bin32_to_int(rf.read_int_reg(3))
        remainder = bin32_to_int(rf.read_int_reg(4))
        
        assert quotient == 72
        assert remainder == 10
        
        # Verify: dividend = quotient * divisor + remainder
        mul_result = mul(rf.read_int_reg(3), rf.read_int_reg(2))
        rf.write_int_reg(5, mul_result['result'])
        
        verification, _ = alu(rf.read_int_reg(5), rf.read_int_reg(4), [0, 0, 1, 0])
        rf.write_int_reg(6, verification)
        
        assert bin32_to_int(rf.read_int_reg(6)) == 1234
        
        print(f"✓ Division: 1234 / 17 = {quotient} remainder {remainder}")
    
    def test_bit_manipulation_extract_field(self):
        """
        Simulate extracting bit field from a 32-bit value.
        
        Extract bits [15:8] from 0xABCD1234
        Expected: 0x12
        """
        rf = RegisterFile()
        
        # Load value: x1 = 0xABCD1234
        rf.write_int_reg(1, int_to_bin32(0xABCD1234))
        
        # Shift right by 8 to align target bits
        shifted = shifter(rf.read_int_reg(1), 8, "SRL")
        rf.write_int_reg(2, shifted)
        
        # Mask with 0xFF to extract lower 8 bits
        mask = int_to_bin32(0xFF)
        rf.write_int_reg(3, mask)
        
        result, _ = alu(rf.read_int_reg(2), rf.read_int_reg(3), [0, 0, 0, 0])  # AND
        rf.write_int_reg(4, result)
        
        extracted = bin32_to_int(rf.read_int_reg(4))
        assert extracted == 0x12
        
        print(f"✓ Bit field extraction: bits[15:8] of 0xABCD1234 = {hex(extracted)}")
    
    def test_absolute_value(self):
        """
        Simulate computing absolute value of signed integers.
        
        Test cases: -42 -> 42, 100 -> 100, -1 -> 1
        """
        rf = RegisterFile()
        
        test_cases = [-42, 100, -1, -2147483647]
        
        for test_val in test_cases:
            # Load value
            rf.write_int_reg(1, int_to_bin32(test_val))
            
            # Extract sign bit (MSB)
            val = rf.read_int_reg(1)
            is_negative = val[0] == 1
            
            if is_negative:
                # Compute two's complement: invert and add 1
                zero = int_to_bin32(0)
                negated, _ = alu(zero, rf.read_int_reg(1), [0, 1, 1, 0])  # SUB: 0 - val
                rf.write_int_reg(2, negated)
            else:
                rf.write_int_reg(2, rf.read_int_reg(1))
            
            result = bin32_to_int(rf.read_int_reg(2), signed=True)
            expected = abs(test_val) if test_val != -2147483648 else 2147483647
            
            # Handle overflow case for INT_MIN
            if test_val == -2147483648:
                assert result == -2147483648  # Overflow wraps
            else:
                assert result == expected
        
        print(f"✓ Absolute value computed correctly for multiple test cases")


# ============================================================================
# Phase 3: Floating-Point Program Simulations
# ============================================================================

class TestPhase3FloatingPointPrograms:
    """
    Phase 3: Simulate realistic floating-point programs.
    
    Programs include: vector dot product, polynomial evaluation,
    statistical calculations.
    """
    
    def test_vector_dot_product(self):
        """
        Simulate vector dot product: a · b
        
        a = [1.0, 2.0, 3.0]
        b = [4.0, 5.0, 6.0]
        Expected: 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32.0
        """
        rf = RegisterFile()
        
        # Load vector a into f1-f3
        rf.write_fp_reg(1, pack_f32(1.0))
        rf.write_fp_reg(2, pack_f32(2.0))
        rf.write_fp_reg(3, pack_f32(3.0))
        
        # Load vector b into f4-f6
        rf.write_fp_reg(4, pack_f32(4.0))
        rf.write_fp_reg(5, pack_f32(5.0))
        rf.write_fp_reg(6, pack_f32(6.0))
        
        # Compute products
        prod1 = fmul_f32(rf.read_fp_reg(1), rf.read_fp_reg(4))
        rf.write_fp_reg(7, prod1['result'])  # f7 = 1.0 * 4.0 = 4.0
        
        prod2 = fmul_f32(rf.read_fp_reg(2), rf.read_fp_reg(5))
        rf.write_fp_reg(8, prod2['result'])  # f8 = 2.0 * 5.0 = 10.0
        
        prod3 = fmul_f32(rf.read_fp_reg(3), rf.read_fp_reg(6))
        rf.write_fp_reg(9, prod3['result'])  # f9 = 3.0 * 6.0 = 18.0
        
        # Sum products
        sum1 = fadd_f32(rf.read_fp_reg(7), rf.read_fp_reg(8))
        rf.write_fp_reg(10, sum1['result'])  # f10 = 4.0 + 10.0 = 14.0
        
        sum2 = fadd_f32(rf.read_fp_reg(10), rf.read_fp_reg(9))
        rf.write_fp_reg(11, sum2['result'])  # f11 = 14.0 + 18.0 = 32.0
        
        dot_product = unpack_f32(rf.read_fp_reg(11))
        assert abs(dot_product - 32.0) < 1e-5
        
        print(f"✓ Vector dot product: [1,2,3] · [4,5,6] = {dot_product}")
    
    def test_polynomial_evaluation(self):
        """
        Simulate evaluating polynomial: P(x) = 2x² + 3x + 1
        
        Evaluate at x = 4.0
        Expected: 2(16) + 3(4) + 1 = 32 + 12 + 1 = 45.0
        """
        rf = RegisterFile()
        
        # Load coefficients and x
        rf.write_fp_reg(1, pack_f32(2.0))  # a = 2
        rf.write_fp_reg(2, pack_f32(3.0))  # b = 3
        rf.write_fp_reg(3, pack_f32(1.0))  # c = 1
        rf.write_fp_reg(4, pack_f32(4.0))  # x = 4
        
        # Compute x²
        x_squared = fmul_f32(rf.read_fp_reg(4), rf.read_fp_reg(4))
        rf.write_fp_reg(5, x_squared['result'])  # f5 = 16.0
        
        # Compute 2x²
        term1 = fmul_f32(rf.read_fp_reg(1), rf.read_fp_reg(5))
        rf.write_fp_reg(6, term1['result'])  # f6 = 32.0
        
        # Compute 3x
        term2 = fmul_f32(rf.read_fp_reg(2), rf.read_fp_reg(4))
        rf.write_fp_reg(7, term2['result'])  # f7 = 12.0
        
        # Sum: 2x² + 3x
        sum1 = fadd_f32(rf.read_fp_reg(6), rf.read_fp_reg(7))
        rf.write_fp_reg(8, sum1['result'])  # f8 = 44.0
        
        # Add constant: 2x² + 3x + 1
        result = fadd_f32(rf.read_fp_reg(8), rf.read_fp_reg(3))
        rf.write_fp_reg(9, result['result'])  # f9 = 45.0
        
        poly_value = unpack_f32(rf.read_fp_reg(9))
        assert abs(poly_value - 45.0) < 1e-5
        
        print(f"✓ Polynomial P(4) = 2x² + 3x + 1 = {poly_value}")
    
    def test_statistical_mean(self):
        """
        Simulate computing mean of floating-point values.
        
        Data: [2.5, 4.5, 6.5, 8.5]
        Expected mean: (2.5 + 4.5 + 6.5 + 8.5) / 4 = 22.0 / 4 = 5.5
        """
        rf = RegisterFile()
        
        # Load data into f1-f4
        data = [2.5, 4.5, 6.5, 8.5]
        for i, val in enumerate(data, 1):
            rf.write_fp_reg(i, pack_f32(val))
        
        # Compute sum
        sum1 = fadd_f32(rf.read_fp_reg(1), rf.read_fp_reg(2))
        rf.write_fp_reg(5, sum1['result'])
        
        sum2 = fadd_f32(rf.read_fp_reg(3), rf.read_fp_reg(4))
        rf.write_fp_reg(6, sum2['result'])
        
        total_sum = fadd_f32(rf.read_fp_reg(5), rf.read_fp_reg(6))
        rf.write_fp_reg(7, total_sum['result'])  # f7 = 22.0
        
        # Divide by count (using multiplication by reciprocal since we don't have FDIV)
        # 1/4 = 0.25
        rf.write_fp_reg(8, pack_f32(0.25))
        
        mean_result = fmul_f32(rf.read_fp_reg(7), rf.read_fp_reg(8))
        rf.write_fp_reg(9, mean_result['result'])
        
        mean = unpack_f32(rf.read_fp_reg(9))
        assert abs(mean - 5.5) < 1e-5
        
        print(f"✓ Statistical mean of [2.5, 4.5, 6.5, 8.5] = {mean}")
    
    def test_distance_calculation(self):
        """
        Simulate computing Euclidean distance: √((x₂-x₁)² + (y₂-y₁)²)
        
        Point A: (1.0, 2.0)
        Point B: (4.0, 6.0)
        Expected: √(9 + 16) = √25 = 5.0
        """
        rf = RegisterFile()
        
        # Load points
        rf.write_fp_reg(1, pack_f32(1.0))  # x1
        rf.write_fp_reg(2, pack_f32(2.0))  # y1
        rf.write_fp_reg(3, pack_f32(4.0))  # x2
        rf.write_fp_reg(4, pack_f32(6.0))  # y2
        
        # Compute dx = x2 - x1
        dx = fsub_f32(rf.read_fp_reg(3), rf.read_fp_reg(1))
        rf.write_fp_reg(5, dx['result'])  # f5 = 3.0
        
        # Compute dy = y2 - y1
        dy = fsub_f32(rf.read_fp_reg(4), rf.read_fp_reg(2))
        rf.write_fp_reg(6, dy['result'])  # f6 = 4.0
        
        # Compute dx²
        dx_squared = fmul_f32(rf.read_fp_reg(5), rf.read_fp_reg(5))
        rf.write_fp_reg(7, dx_squared['result'])  # f7 = 9.0
        
        # Compute dy²
        dy_squared = fmul_f32(rf.read_fp_reg(6), rf.read_fp_reg(6))
        rf.write_fp_reg(8, dy_squared['result'])  # f8 = 16.0
        
        # Sum: dx² + dy²
        sum_squares = fadd_f32(rf.read_fp_reg(7), rf.read_fp_reg(8))
        rf.write_fp_reg(9, sum_squares['result'])  # f9 = 25.0
        
        distance_squared = unpack_f32(rf.read_fp_reg(9))
        assert abs(distance_squared - 25.0) < 1e-5
        
        # Note: We would need FSQRT to get actual distance, but squared distance is good
        print(f"✓ Distance squared between (1,2) and (4,6) = {distance_squared}")


# ============================================================================
# Phase 4: Mixed Integer/Float Operations
# ============================================================================

class TestPhase4MixedOperations:
    """
    Phase 4: Test programs that use both integer and floating-point operations.
    
    Programs include: integer-to-float conversion simulation, mixed calculations.
    """
    
    def test_mixed_calculation_temperature_conversion(self):
        """
        Simulate temperature conversion: Celsius to Fahrenheit
        
        Formula: F = (9/5) * C + 32
        Test: 25°C = 77°F
        
        Uses integer for constant 32, float for rest.
        """
        rf = RegisterFile()
        
        # Integer part: constant 32
        rf.write_int_reg(1, int_to_bin32(32))
        
        # Float part: C = 25.0, factor = 9/5 = 1.8
        rf.write_fp_reg(1, pack_f32(25.0))    # Celsius
        rf.write_fp_reg(2, pack_f32(1.8))     # 9/5
        
        # Compute (9/5) * C
        temp_product = fmul_f32(rf.read_fp_reg(2), rf.read_fp_reg(1))
        rf.write_fp_reg(3, temp_product['result'])  # f3 = 45.0
        
        # Convert integer 32 to float (simulation: just pack it)
        rf.write_fp_reg(4, pack_f32(32.0))
        
        # Add: (9/5) * C + 32
        fahrenheit = fadd_f32(rf.read_fp_reg(3), rf.read_fp_reg(4))
        rf.write_fp_reg(5, fahrenheit['result'])
        
        result = unpack_f32(rf.read_fp_reg(5))
        assert abs(result - 77.0) < 1e-5
        
        print(f"✓ Temperature conversion: 25°C = {result}°F")
    
    def test_fixed_point_simulation(self):
        """
        Simulate fixed-point arithmetic using integers.
        
        Represent numbers as Q16.16 format (16 bits integer, 16 bits fraction).
        Compute: 3.25 + 2.75 = 6.0
        """
        rf = RegisterFile()
        
        # Q16.16 representation: multiply by 2^16 = 65536
        # 3.25 * 65536 = 212992
        # 2.75 * 65536 = 180224
        
        val1 = int(3.25 * 65536)
        val2 = int(2.75 * 65536)
        
        rf.write_int_reg(1, int_to_bin32(val1))
        rf.write_int_reg(2, int_to_bin32(val2))
        
        # Add fixed-point numbers
        result, _ = alu(rf.read_int_reg(1), rf.read_int_reg(2), [0, 0, 1, 0])
        rf.write_int_reg(3, result)
        
        # Convert back to float
        fixed_result = bin32_to_int(rf.read_int_reg(3))
        float_result = fixed_result / 65536.0
        
        assert abs(float_result - 6.0) < 1e-10
        
        print(f"✓ Fixed-point arithmetic: 3.25 + 2.75 = {float_result}")
    
    def test_scientific_calculation_kinetic_energy(self):
        """
        Simulate kinetic energy calculation: KE = (1/2) * m * v²
        
        Mass (integer): m = 10 kg
        Velocity (float): v = 5.0 m/s
        Expected: KE = 0.5 * 10 * 25 = 125.0 J
        """
        rf = RegisterFile()
        
        # Integer mass
        rf.write_int_reg(1, int_to_bin32(10))
        
        # Float velocity
        rf.write_fp_reg(1, pack_f32(5.0))
        
        # Compute v²
        v_squared = fmul_f32(rf.read_fp_reg(1), rf.read_fp_reg(1))
        rf.write_fp_reg(2, v_squared['result'])  # f2 = 25.0
        
        # Convert mass to float
        rf.write_fp_reg(3, pack_f32(10.0))
        
        # Compute m * v²
        mv_squared = fmul_f32(rf.read_fp_reg(3), rf.read_fp_reg(2))
        rf.write_fp_reg(4, mv_squared['result'])  # f4 = 250.0
        
        # Multiply by 0.5
        rf.write_fp_reg(5, pack_f32(0.5))
        ke = fmul_f32(rf.read_fp_reg(4), rf.read_fp_reg(5))
        rf.write_fp_reg(6, ke['result'])
        
        kinetic_energy = unpack_f32(rf.read_fp_reg(6))
        assert abs(kinetic_energy - 125.0) < 1e-4
        
        print(f"✓ Kinetic energy: KE = 0.5 * 10 * 5² = {kinetic_energy} J")


# ============================================================================
# Phase 5: Complex Real-World Scenarios
# ============================================================================

class TestPhase5ComplexScenarios:
    """
    Phase 5: Simulate complex real-world programs.
    
    Programs include: matrix operations, complete algorithms,
    multi-step calculations.
    """
    
    def test_matrix_vector_multiply_2x2(self):
        """
        Simulate 2x2 matrix-vector multiplication using FPU.
        
        Matrix A = [[2.0, 3.0],
                    [4.0, 5.0]]
        Vector x = [1.0, 2.0]
        
        Expected: A*x = [8.0, 14.0]
        """
        rf = RegisterFile()
        
        # Load matrix A row-major into f1-f4
        rf.write_fp_reg(1, pack_f32(2.0))  # A[0,0]
        rf.write_fp_reg(2, pack_f32(3.0))  # A[0,1]
        rf.write_fp_reg(3, pack_f32(4.0))  # A[1,0]
        rf.write_fp_reg(4, pack_f32(5.0))  # A[1,1]
        
        # Load vector x into f5-f6
        rf.write_fp_reg(5, pack_f32(1.0))  # x[0]
        rf.write_fp_reg(6, pack_f32(2.0))  # x[1]
        
        # Compute y[0] = A[0,0]*x[0] + A[0,1]*x[1]
        prod1 = fmul_f32(rf.read_fp_reg(1), rf.read_fp_reg(5))
        rf.write_fp_reg(7, prod1['result'])  # f7 = 2.0
        
        prod2 = fmul_f32(rf.read_fp_reg(2), rf.read_fp_reg(6))
        rf.write_fp_reg(8, prod2['result'])  # f8 = 6.0
        
        y0 = fadd_f32(rf.read_fp_reg(7), rf.read_fp_reg(8))
        rf.write_fp_reg(9, y0['result'])  # f9 = 8.0
        
        # Compute y[1] = A[1,0]*x[0] + A[1,1]*x[1]
        prod3 = fmul_f32(rf.read_fp_reg(3), rf.read_fp_reg(5))
        rf.write_fp_reg(10, prod3['result'])  # f10 = 4.0
        
        prod4 = fmul_f32(rf.read_fp_reg(4), rf.read_fp_reg(6))
        rf.write_fp_reg(11, prod4['result'])  # f11 = 10.0
        
        y1 = fadd_f32(rf.read_fp_reg(10), rf.read_fp_reg(11))
        rf.write_fp_reg(12, y1['result'])  # f12 = 14.0
        
        result_y0 = unpack_f32(rf.read_fp_reg(9))
        result_y1 = unpack_f32(rf.read_fp_reg(12))
        
        assert abs(result_y0 - 8.0) < 1e-5
        assert abs(result_y1 - 14.0) < 1e-5
        
        print(f"✓ Matrix-vector multiply: y = [{result_y0}, {result_y1}]")
    
    def test_power_of_two_checker(self):
        """
        Simulate checking if a number is a power of 2.
        
        Algorithm: n is power of 2 if (n & (n-1)) == 0 and n != 0
        Test: 16 is power of 2, 15 is not
        """
        rf = RegisterFile()
        
        test_cases = [
            (16, True),   # 2^4
            (15, False),  # Not power of 2
            (32, True),   # 2^5
            (31, False),  # Not power of 2
            (1, True),    # 2^0
            (0, False),   # Special case
        ]
        
        for n, expected in test_cases:
            # Load n
            rf.write_int_reg(1, int_to_bin32(n))
            
            # Compute n - 1
            one = int_to_bin32(1)
            rf.write_int_reg(2, one)
            n_minus_1, _ = alu(rf.read_int_reg(1), rf.read_int_reg(2), [0, 1, 1, 0])  # SUB
            rf.write_int_reg(3, n_minus_1)
            
            # Compute n & (n-1)
            result, _ = alu(rf.read_int_reg(1), rf.read_int_reg(3), [0, 0, 0, 0])  # AND
            rf.write_int_reg(4, result)
            
            # Check if result is zero and n is not zero
            is_zero = bin32_to_int(rf.read_int_reg(4)) == 0
            n_not_zero = n != 0
            
            is_power_of_2 = is_zero and n_not_zero
            assert is_power_of_2 == expected
        
        print(f"✓ Power of 2 checker working correctly")
    
    def test_greatest_common_divisor(self):
        """
        Simulate Euclidean algorithm for GCD.
        
        GCD(48, 18) = 6
        Algorithm: GCD(a,b) = GCD(b, a mod b) until b == 0
        """
        rf = RegisterFile()
        
        # Initialize: a = 48, b = 18
        rf.write_int_reg(1, int_to_bin32(48))
        rf.write_int_reg(2, int_to_bin32(18))
        
        steps = []
        
        # Euclidean algorithm
        while True:
            a = bin32_to_int(rf.read_int_reg(1))
            b = bin32_to_int(rf.read_int_reg(2))
            
            steps.append((a, b))
            
            if b == 0:
                break
            
            # Compute a mod b using division
            div_result = div(rf.read_int_reg(1), rf.read_int_reg(2))
            remainder = div_result['remainder']
            
            # Shift: a = b, b = remainder
            rf.write_int_reg(1, rf.read_int_reg(2))
            rf.write_int_reg(2, remainder)
        
        gcd = bin32_to_int(rf.read_int_reg(1))
        assert gcd == 6
        
        print(f"✓ GCD(48, 18) = {gcd}, computed in {len(steps)} steps")
    
    def test_complete_program_quadratic_roots(self):
        """
        Simulate computing discriminant of quadratic equation ax² + bx + c = 0
        
        Discriminant: Δ = b² - 4ac
        Test: a=1, b=5, c=6 -> Δ = 25 - 24 = 1
        """
        rf = RegisterFile()
        
        # Load coefficients
        rf.write_fp_reg(1, pack_f32(1.0))  # a
        rf.write_fp_reg(2, pack_f32(5.0))  # b
        rf.write_fp_reg(3, pack_f32(6.0))  # c
        
        # Compute b²
        b_squared = fmul_f32(rf.read_fp_reg(2), rf.read_fp_reg(2))
        rf.write_fp_reg(4, b_squared['result'])  # f4 = 25.0
        
        # Compute 4ac
        rf.write_fp_reg(5, pack_f32(4.0))
        
        ac = fmul_f32(rf.read_fp_reg(1), rf.read_fp_reg(3))
        rf.write_fp_reg(6, ac['result'])  # f6 = 6.0
        
        four_ac = fmul_f32(rf.read_fp_reg(5), rf.read_fp_reg(6))
        rf.write_fp_reg(7, four_ac['result'])  # f7 = 24.0
        
        # Compute discriminant: b² - 4ac
        discriminant = fsub_f32(rf.read_fp_reg(4), rf.read_fp_reg(7))
        rf.write_fp_reg(8, discriminant['result'])
        
        delta = unpack_f32(rf.read_fp_reg(8))
        assert abs(delta - 1.0) < 1e-5
        
        print(f"✓ Quadratic discriminant: Δ = b² - 4ac = {delta}")
    
    def test_sorting_network_4_elements(self):
        """
        Simulate a simple 4-element sorting network using compare-swap.
        
        Input: [40, 10, 30, 20]
        Expected output: [10, 20, 30, 40]
        """
        rf = RegisterFile()
        
        # Load unsorted array into x1-x4
        rf.write_int_reg(1, int_to_bin32(40))
        rf.write_int_reg(2, int_to_bin32(10))
        rf.write_int_reg(3, int_to_bin32(30))
        rf.write_int_reg(4, int_to_bin32(20))
        
        def compare_swap(reg_a, reg_b):
            """Compare and swap if a > b using SLT."""
            # Compute a - b
            diff, flags = alu(rf.read_int_reg(reg_a), rf.read_int_reg(reg_b), [0, 1, 1, 0])
            
            # If result is negative (N flag set), then a < b, no swap needed
            # If result is positive or zero, swap
            N = flags[0]
            
            if N == 0 and not all(bit == 0 for bit in diff):  # a > b, need swap
                temp = rf.read_int_reg(reg_a)
                rf.write_int_reg(reg_a, rf.read_int_reg(reg_b))
                rf.write_int_reg(reg_b, temp)
        
        # Sorting network for 4 elements (Batcher odd-even mergesort)
        compare_swap(1, 2)
        compare_swap(3, 4)
        compare_swap(1, 3)
        compare_swap(2, 4)
        compare_swap(2, 3)
        
        # Read sorted values
        sorted_vals = [bin32_to_int(rf.read_int_reg(i)) for i in range(1, 5)]
        
        assert sorted_vals == [10, 20, 30, 40]
        
        print(f"✓ Sorting network: [40,10,30,20] -> {sorted_vals}")


# ============================================================================
# Integration Test: Complete CPU Simulation
# ============================================================================

class TestCompleteCPUSimulation:
    """
    Complete end-to-end CPU simulation test.
    
    Simulates a complex program that uses ALL CPU components together.
    """
    
    def test_complete_simulation_physics_engine_step(self):
        """
        Simulate a single step of a physics engine.
        
        Update particle position and velocity:
        - v_new = v_old + a*dt (floating-point)
        - p_new = p_old + v_new*dt (floating-point)
        - collision detection (integer bit operations)
        
        Particle: pos=(10.0, 20.0), vel=(2.0, 3.0), accel=(0.0, -9.8)
        dt = 0.1
        
        Expected:
        - v_new = (2.0, 2.02)  # vy = 3.0 + (-9.8)*0.1 = 2.02
        - p_new = (10.2, 20.202)
        """
        rf = RegisterFile()
        
        print("\n=== Physics Engine Simulation ===")
        
        # Initial state (floating-point)
        rf.write_fp_reg(1, pack_f32(10.0))  # px
        rf.write_fp_reg(2, pack_f32(20.0))  # py
        rf.write_fp_reg(3, pack_f32(2.0))   # vx
        rf.write_fp_reg(4, pack_f32(3.0))   # vy
        rf.write_fp_reg(5, pack_f32(0.0))   # ax
        rf.write_fp_reg(6, pack_f32(-9.8))  # ay
        rf.write_fp_reg(7, pack_f32(0.1))   # dt
        
        print(f"Initial position: ({unpack_f32(rf.read_fp_reg(1))}, {unpack_f32(rf.read_fp_reg(2))})")
        print(f"Initial velocity: ({unpack_f32(rf.read_fp_reg(3))}, {unpack_f32(rf.read_fp_reg(4))})")
        
        # Step 1: Update velocity - v_new = v_old + a*dt
        
        # vx_new = vx + ax*dt
        ax_dt = fmul_f32(rf.read_fp_reg(5), rf.read_fp_reg(7))
        rf.write_fp_reg(10, ax_dt['result'])
        
        vx_new = fadd_f32(rf.read_fp_reg(3), rf.read_fp_reg(10))
        rf.write_fp_reg(11, vx_new['result'])
        
        # vy_new = vy + ay*dt
        ay_dt = fmul_f32(rf.read_fp_reg(6), rf.read_fp_reg(7))
        rf.write_fp_reg(12, ay_dt['result'])
        
        vy_new = fadd_f32(rf.read_fp_reg(4), rf.read_fp_reg(12))
        rf.write_fp_reg(13, vy_new['result'])
        
        print(f"New velocity: ({unpack_f32(rf.read_fp_reg(11))}, {unpack_f32(rf.read_fp_reg(13))})")
        
        # Step 2: Update position - p_new = p_old + v_new*dt
        
        # px_new = px + vx_new*dt
        vx_dt = fmul_f32(rf.read_fp_reg(11), rf.read_fp_reg(7))
        rf.write_fp_reg(14, vx_dt['result'])
        
        px_new = fadd_f32(rf.read_fp_reg(1), rf.read_fp_reg(14))
        rf.write_fp_reg(15, px_new['result'])
        
        # py_new = py + vy_new*dt
        vy_dt = fmul_f32(rf.read_fp_reg(13), rf.read_fp_reg(7))
        rf.write_fp_reg(16, vy_dt['result'])
        
        py_new = fadd_f32(rf.read_fp_reg(2), rf.read_fp_reg(16))
        rf.write_fp_reg(17, py_new['result'])
        
        print(f"New position: ({unpack_f32(rf.read_fp_reg(15))}, {unpack_f32(rf.read_fp_reg(17))})")
        
        # Step 3: Collision detection (check if y < 0 using integer)
        # Convert float to integer for boundary check
        py_value = unpack_f32(rf.read_fp_reg(17))
        
        # Use integer comparison
        py_int = int(py_value * 100)  # Scale for precision
        rf.write_int_reg(1, int_to_bin32(py_int))
        rf.write_int_reg(2, int_to_bin32(0))
        
        # Check if py < 0 using SUB and checking sign
        diff, flags = alu(rf.read_int_reg(1), rf.read_int_reg(2), [0, 1, 1, 0])
        collision = flags[0]  # N flag indicates negative (collision)
        
        print(f"Collision detected: {collision == 1}")
        
        # Verify physics calculations
        vx_final = unpack_f32(rf.read_fp_reg(11))
        vy_final = unpack_f32(rf.read_fp_reg(13))
        px_final = unpack_f32(rf.read_fp_reg(15))
        py_final = unpack_f32(rf.read_fp_reg(17))
        
        assert abs(vx_final - 2.0) < 1e-5
        assert abs(vy_final - 2.02) < 1e-3
        assert abs(px_final - 10.2) < 1e-5
        assert abs(py_final - 20.202) < 1e-3
        
        print("\n✓ Complete physics simulation successful!")
        print(f"  Final state verified: pos=({px_final:.3f}, {py_final:.3f}), vel=({vx_final:.3f}, {vy_final:.3f})")


# ============================================================================
# Performance and Stress Tests
# ============================================================================

class TestPerformanceAndStress:
    """
    Performance and stress tests for CPU simulation.
    """
    
    def test_long_computation_chain(self):
        """Test a long chain of ALU operations (50 additions)."""
        rf = RegisterFile()
        
        # Start with x1 = 1
        rf.write_int_reg(1, int_to_bin32(1))
        
        # Perform 50 successive additions: x1 = x1 + 1
        for i in range(50):
            one = int_to_bin32(1)
            rf.write_int_reg(2, one)
            result, _ = alu(rf.read_int_reg(1), rf.read_int_reg(2), [0, 0, 1, 0])
            rf.write_int_reg(1, result)
        
        # Result should be 51
        final_val = bin32_to_int(rf.read_int_reg(1))
        assert final_val == 51
        
        print(f"✓ Long computation chain: 50 additions completed, result = {final_val}")
    
    def test_register_file_stress(self):
        """Stress test register file with many reads/writes."""
        rf = RegisterFile()
        
        # Write to all integer registers (except x0)
        for i in range(1, 32):
            rf.write_int_reg(i, int_to_bin32(i * 100))
        
        # Write to all FP registers
        for i in range(32):
            rf.write_fp_reg(i, pack_f32(float(i) * 1.5))
        
        # Verify all values
        for i in range(1, 32):
            val = bin32_to_int(rf.read_int_reg(i))
            assert val == i * 100
        
        for i in range(32):
            val = unpack_f32(rf.read_fp_reg(i))
            assert abs(val - (i * 1.5)) < 1e-5
        
        print("✓ Register file stress test: 63 registers written and verified")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
# AI-END
