"""
Tests for Control Unit Programs and System Integration (Phase 8)

Tests complete program execution through the Control Unit FSM,
verifying cycle accuracy, data correctness, and system integration.
"""

import pytest
from riscsim.cpu.control_unit import ControlUnit
from riscsim.cpu.control_signals import ALU_OP_ADD, ALU_OP_SUB, SH_OP_SLL


def int_to_5bit(value):
    """Helper to convert integer to 5-bit array (MSB-first)."""
    return [(value >> (4 - i)) & 1 for i in range(5)]


def int_to_32bit(value):
    """Helper to convert integer to 32-bit array (MSB-first)."""
    if value < 0:
        value = (1 << 32) + value
    return [(value >> (31 - i)) & 1 for i in range(32)]


def bits_to_int(bits):
    """Helper to convert bit array (MSB-first) to integer."""
    value = sum(bit << (len(bits) - 1 - i) for i, bit in enumerate(bits))
    # Handle signed 32-bit
    if len(bits) == 32 and bits[0] == 1:  # MSB is sign bit
        value -= (1 << 32)
    return value


class TestFibonacciProgram:
    """Test Fibonacci sequence calculation program."""
    
    def test_fibonacci_small(self):
        """Test Fibonacci for small values."""
        cu = ControlUnit()
        
        # Calculate fib(5) = 5
        # fib sequence: 0, 1, 1, 2, 3, 5
        n = 5
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(0))     # r1 = 0
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(1))     # r2 = 1
        cu.register_file.write_int_reg(int_to_5bit(3), int_to_32bit(n-1))   # r3 = 4 iterations
        
        # Execute loop
        for _ in range(n-1):
            cu.execute_instruction('ALU', ALU_OP_ADD,
                                  int_to_5bit(1), int_to_5bit(2), int_to_5bit(4))
            cu.execute_instruction('ALU', ALU_OP_ADD,
                                  int_to_5bit(2), int_to_5bit(0), int_to_5bit(1))
            cu.execute_instruction('ALU', ALU_OP_ADD,
                                  int_to_5bit(4), int_to_5bit(0), int_to_5bit(2))
        
        # Get result
        result_bits = cu.register_file.read_int_reg(int_to_5bit(2))
        result = bits_to_int(result_bits)
        
        assert result == 5
    
    def test_fibonacci_medium(self):
        """Test Fibonacci for medium values."""
        cu = ControlUnit()
        
        # Calculate fib(10) = 55
        n = 10
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(0))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(1))
        cu.register_file.write_int_reg(int_to_5bit(3), int_to_32bit(n-1))
        
        for _ in range(n-1):
            cu.execute_instruction('ALU', ALU_OP_ADD,
                                  int_to_5bit(1), int_to_5bit(2), int_to_5bit(4))
            cu.execute_instruction('ALU', ALU_OP_ADD,
                                  int_to_5bit(2), int_to_5bit(0), int_to_5bit(1))
            cu.execute_instruction('ALU', ALU_OP_ADD,
                                  int_to_5bit(4), int_to_5bit(0), int_to_5bit(2))
        
        result_bits = cu.register_file.read_int_reg(int_to_5bit(2))
        result = bits_to_int(result_bits)
        
        assert result == 55
    
    def test_fibonacci_cycle_count(self):
        """Test that Fibonacci has expected cycle count."""
        cu = ControlUnit()
        
        n = 5
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(0))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(1))
        cu.register_file.write_int_reg(int_to_5bit(3), int_to_32bit(n-1))
        
        for _ in range(n-1):
            cu.execute_instruction('ALU', ALU_OP_ADD,
                                  int_to_5bit(1), int_to_5bit(2), int_to_5bit(4))
            cu.execute_instruction('ALU', ALU_OP_ADD,
                                  int_to_5bit(2), int_to_5bit(0), int_to_5bit(1))
            cu.execute_instruction('ALU', ALU_OP_ADD,
                                  int_to_5bit(4), int_to_5bit(0), int_to_5bit(2))
        
        stats = cu.get_performance_stats()
        
        # 4 iterations * 3 ALU ops * 2 cycles = 24 cycles
        assert stats['total_cycles'] == 24
        assert stats['instruction_count'] == 12  # 4 iterations * 3 instructions
        assert stats['cpi'] == 2.0


class TestFactorialProgram:
    """Test factorial calculation program."""
    
    def test_factorial_small(self):
        """Test factorial for small values."""
        cu = ControlUnit()
        
        # Calculate 3! = 6
        n = 3
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(1))  # result = 1
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(1))  # counter = 1
        cu.register_file.write_int_reg(int_to_5bit(4), int_to_32bit(1))  # constant 1
        
        for i in range(1, n + 1):
            cu.execute_instruction('MDU', 'MUL',
                                  int_to_5bit(1), int_to_5bit(2), int_to_5bit(1))
            cu.execute_instruction('ALU', ALU_OP_ADD,
                                  int_to_5bit(2), int_to_5bit(4), int_to_5bit(2))
        
        result_bits = cu.register_file.read_int_reg(int_to_5bit(1))
        result = bits_to_int(result_bits)
        
        assert result == 6
    
    def test_factorial_medium(self):
        """Test factorial for medium values."""
        cu = ControlUnit()
        
        # Calculate 5! = 120
        n = 5
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(1))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(1))
        cu.register_file.write_int_reg(int_to_5bit(4), int_to_32bit(1))
        
        for i in range(1, n + 1):
            cu.execute_instruction('MDU', 'MUL',
                                  int_to_5bit(1), int_to_5bit(2), int_to_5bit(1))
            cu.execute_instruction('ALU', ALU_OP_ADD,
                                  int_to_5bit(2), int_to_5bit(4), int_to_5bit(2))
        
        result_bits = cu.register_file.read_int_reg(int_to_5bit(1))
        result = bits_to_int(result_bits)
        
        assert result == 120
    
    def test_factorial_uses_mdu(self):
        """Test that factorial uses MDU for multiplication."""
        cu = ControlUnit()
        
        n = 3
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(1))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(1))
        cu.register_file.write_int_reg(int_to_5bit(4), int_to_32bit(1))
        
        for i in range(1, n + 1):
            cu.execute_instruction('MDU', 'MUL',
                                  int_to_5bit(1), int_to_5bit(2), int_to_5bit(1))
            cu.execute_instruction('ALU', ALU_OP_ADD,
                                  int_to_5bit(2), int_to_5bit(4), int_to_5bit(2))
        
        stats = cu.get_performance_stats()
        
        # Should have MDU cycles (33 per MUL × 3 iterations = 99)
        assert stats['mdu_cycles'] == 99
        # Also has ALU cycles (2 per ADD × 3 iterations = 6)
        assert stats['alu_cycles'] == 6


class TestFloatingPointProgram:
    """Test floating-point calculation program."""
    
    def test_fp_addition_sequence(self):
        """Test sequence of FP additions."""
        cu = ControlUnit()
        
        # Set up: 1.0 + 2.0 + 3.0
        fp_1_0 = int_to_32bit(0x3F800000)
        fp_2_0 = int_to_32bit(0x40000000)
        fp_3_0 = int_to_32bit(0x40400000)
        
        cu.register_file.write_fp_reg(int_to_5bit(1), fp_1_0)
        cu.register_file.write_fp_reg(int_to_5bit(2), fp_2_0)
        cu.register_file.write_fp_reg(int_to_5bit(3), fp_3_0)
        
        # f4 = f1 + f2
        cu.execute_instruction('FPU', 'FADD',
                              int_to_5bit(1), int_to_5bit(2), int_to_5bit(4))
        
        # f5 = f4 + f3
        cu.execute_instruction('FPU', 'FADD',
                              int_to_5bit(4), int_to_5bit(3), int_to_5bit(5))
        
        # Get result
        result_bits = cu.register_file.read_fp_reg(int_to_5bit(5))
        result_int = sum(bit << (31 - i) for i, bit in enumerate(result_bits))
        
        # Result should be 6.0 = 0x40C00000
        assert result_int == 0x40C00000
    
    def test_fp_multiplication(self):
        """Test FP multiplication."""
        cu = ControlUnit()
        
        # Set up: 2.0 * 3.0 = 6.0
        fp_2_0 = int_to_32bit(0x40000000)
        fp_3_0 = int_to_32bit(0x40400000)
        
        cu.register_file.write_fp_reg(int_to_5bit(1), fp_2_0)
        cu.register_file.write_fp_reg(int_to_5bit(2), fp_3_0)
        
        # f3 = f1 * f2
        cu.execute_instruction('FPU', 'FMUL',
                              int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        result_bits = cu.register_file.read_fp_reg(int_to_5bit(3))
        result_int = sum(bit << (31 - i) for i, bit in enumerate(result_bits))
        
        # Result should be 6.0 = 0x40C00000
        assert result_int == 0x40C00000
    
    def test_fp_cycle_count(self):
        """Test FP operations have expected cycle count."""
        cu = ControlUnit()
        
        fp_1_0 = int_to_32bit(0x3F800000)
        fp_2_0 = int_to_32bit(0x40000000)
        
        cu.register_file.write_fp_reg(int_to_5bit(1), fp_1_0)
        cu.register_file.write_fp_reg(int_to_5bit(2), fp_2_0)
        
        # Execute 2 FP operations
        cu.execute_instruction('FPU', 'FADD',
                              int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        cu.execute_instruction('FPU', 'FMUL',
                              int_to_5bit(3), int_to_5bit(1), int_to_5bit(4))
        
        stats = cu.get_performance_stats()
        
        # 2 FPU ops × 5 cycles each = 10 cycles
        assert stats['fpu_cycles'] == 10
        assert stats['instruction_count'] == 2


class TestMixedOperationsProgram:
    """Test programs using multiple functional units."""
    
    def test_all_units_used(self):
        """Test that all functional units can be used in one program."""
        cu = ControlUnit()
        
        # Setup
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(20))
        fp_1_0 = int_to_32bit(0x3F800000)
        fp_2_0 = int_to_32bit(0x40000000)
        cu.register_file.write_fp_reg(int_to_5bit(10), fp_1_0)
        cu.register_file.write_fp_reg(int_to_5bit(11), fp_2_0)
        
        # Use each unit
        cu.execute_instruction('ALU', ALU_OP_ADD,
                              int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        cu.execute_instruction('SHIFTER', SH_OP_SLL,
                              int_to_5bit(1), rd_addr=int_to_5bit(4),
                              shamt=int_to_5bit(2))
        cu.execute_instruction('MDU', 'MUL',
                              int_to_5bit(1), int_to_5bit(2), int_to_5bit(5))
        cu.execute_instruction('FPU', 'FADD',
                              int_to_5bit(10), int_to_5bit(11), int_to_5bit(12))
        
        stats = cu.get_performance_stats()
        
        # Verify all units were used
        assert stats['alu_cycles'] > 0
        assert stats['shifter_cycles'] > 0
        assert stats['mdu_cycles'] > 0
        assert stats['fpu_cycles'] > 0
    
    def test_mixed_integer_fp_operations(self):
        """Test mixing integer and FP operations."""
        cu = ControlUnit()
        
        # Integer ops
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(5))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(3))
        cu.execute_instruction('ALU', ALU_OP_ADD,
                              int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        # FP ops
        fp_1_0 = int_to_32bit(0x3F800000)
        fp_2_0 = int_to_32bit(0x40000000)
        cu.register_file.write_fp_reg(int_to_5bit(10), fp_1_0)
        cu.register_file.write_fp_reg(int_to_5bit(11), fp_2_0)
        cu.execute_instruction('FPU', 'FADD',
                              int_to_5bit(10), int_to_5bit(11), int_to_5bit(12))
        
        # More integer ops
        cu.execute_instruction('ALU', ALU_OP_SUB,
                              int_to_5bit(3), int_to_5bit(1), int_to_5bit(4))
        
        stats = cu.get_performance_stats()
        
        # Should have both ALU and FPU cycles
        assert stats['alu_cycles'] == 4  # 2 ALU ops × 2 cycles
        assert stats['fpu_cycles'] == 5  # 1 FPU op × 5 cycles
        assert stats['instruction_count'] == 3


class TestCycleAccuracy:
    """Test cycle-accurate execution."""
    
    def test_alu_cycle_accuracy(self):
        """Test ALU operations take exactly 2 cycles."""
        cu = ControlUnit()
        
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(20))
        
        result = cu.execute_instruction('ALU', ALU_OP_ADD,
                                       int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        assert result['cycles'] == 2
    
    def test_shifter_cycle_accuracy(self):
        """Test Shifter operations take exactly 2 cycles."""
        cu = ControlUnit()
        
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        
        result = cu.execute_instruction('SHIFTER', SH_OP_SLL,
                                       int_to_5bit(1), rd_addr=int_to_5bit(2),
                                       shamt=int_to_5bit(3))
        
        assert result['cycles'] == 2
    
    def test_mdu_cycle_accuracy(self):
        """Test MDU operations take exactly 33 cycles."""
        cu = ControlUnit()
        
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(6))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(7))
        
        result = cu.execute_instruction('MDU', 'MUL',
                                       int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        assert result['cycles'] == 33
    
    def test_fpu_cycle_accuracy(self):
        """Test FPU operations take exactly 5 cycles."""
        cu = ControlUnit()
        
        fp_1_0 = int_to_32bit(0x3F800000)
        fp_2_0 = int_to_32bit(0x40000000)
        cu.register_file.write_fp_reg(int_to_5bit(1), fp_1_0)
        cu.register_file.write_fp_reg(int_to_5bit(2), fp_2_0)
        
        result = cu.execute_instruction('FPU', 'FADD',
                                       int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        assert result['cycles'] == 5
    
    def test_cumulative_cycle_count(self):
        """Test that total cycles accumulate correctly."""
        cu = ControlUnit()
        
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(20))
        
        # Execute 3 ALU ops (2 cycles each = 6 total)
        cu.execute_instruction('ALU', ALU_OP_ADD,
                              int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        cu.execute_instruction('ALU', ALU_OP_SUB,
                              int_to_5bit(3), int_to_5bit(1), int_to_5bit(4))
        cu.execute_instruction('ALU', ALU_OP_ADD,
                              int_to_5bit(4), int_to_5bit(2), int_to_5bit(5))
        
        stats = cu.get_performance_stats()
        
        assert stats['total_cycles'] == 6
        assert stats['instruction_count'] == 3


class TestDataCorrectness:
    """Test data correctness throughout execution."""
    
    def test_register_isolation(self):
        """Test that operations don't affect unrelated registers."""
        cu = ControlUnit()
        
        # Set up multiple registers
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(20))
        cu.register_file.write_int_reg(int_to_5bit(3), int_to_32bit(30))
        cu.register_file.write_int_reg(int_to_5bit(4), int_to_32bit(40))
        
        # Execute operation affecting only r5
        cu.execute_instruction('ALU', ALU_OP_ADD,
                              int_to_5bit(1), int_to_5bit(2), int_to_5bit(5))
        
        # Verify other registers unchanged
        r1 = bits_to_int(cu.register_file.read_int_reg(int_to_5bit(1)))
        r2 = bits_to_int(cu.register_file.read_int_reg(int_to_5bit(2)))
        r3 = bits_to_int(cu.register_file.read_int_reg(int_to_5bit(3)))
        r4 = bits_to_int(cu.register_file.read_int_reg(int_to_5bit(4)))
        
        assert r1 == 10
        assert r2 == 20
        assert r3 == 30
        assert r4 == 40
    
    def test_chain_of_dependencies(self):
        """Test correct data flow through chain of operations."""
        cu = ControlUnit()
        
        # Set up: r1 = 5, r2 = 3
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(5))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(3))
        
        # r3 = r1 + r2 = 8
        cu.execute_instruction('ALU', ALU_OP_ADD,
                              int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        # r4 = r3 + r1 = 13
        cu.execute_instruction('ALU', ALU_OP_ADD,
                              int_to_5bit(3), int_to_5bit(1), int_to_5bit(4))
        
        # r5 = r4 - r2 = 10
        cu.execute_instruction('ALU', ALU_OP_SUB,
                              int_to_5bit(4), int_to_5bit(2), int_to_5bit(5))
        
        # Verify all intermediate and final values
        r3 = bits_to_int(cu.register_file.read_int_reg(int_to_5bit(3)))
        r4 = bits_to_int(cu.register_file.read_int_reg(int_to_5bit(4)))
        r5 = bits_to_int(cu.register_file.read_int_reg(int_to_5bit(5)))
        
        assert r3 == 8
        assert r4 == 13
        assert r5 == 10
    
    def test_state_consistency_across_operations(self):
        """Test control unit state remains consistent."""
        cu = ControlUnit()
        
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(20))
        
        # Execute operation
        cu.execute_instruction('ALU', ALU_OP_ADD,
                              int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        # Should be idle after completion
        assert cu.is_idle()
        assert not cu.is_busy()
        
        # Should be able to execute another operation
        cu.execute_instruction('ALU', ALU_OP_SUB,
                              int_to_5bit(3), int_to_5bit(1), int_to_5bit(4))
        
        assert cu.is_idle()


class TestTraceValidation:
    """Test execution trace generation and validation."""
    
    def test_trace_captures_all_cycles(self):
        """Test that trace includes entry for each cycle."""
        cu = ControlUnit()
        
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(20))
        
        result = cu.execute_instruction('ALU', ALU_OP_ADD,
                                       int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        trace = result['trace']
        
        # Should have trace entries (at least one per cycle)
        assert len(trace) >= result['cycles']
        assert isinstance(trace, list)
    
    def test_trace_contains_state_info(self):
        """Test that trace entries contain state information."""
        cu = ControlUnit()
        
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(20))
        
        result = cu.execute_instruction('ALU', ALU_OP_ADD,
                                       int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        trace = result['trace']
        
        # Each trace entry should be a dict with info
        for entry in trace:
            assert isinstance(entry, dict)
            assert 'cycle' in entry
            assert 'message' in entry or 'state' in entry
