"""
Tests for Control Unit Performance Counters (Phase 7, Task 2)

Tests the performance monitoring and statistics capabilities of the Control Unit.
"""

import pytest
from riscsim.cpu.control_unit import ControlUnit
from riscsim.cpu.control_signals import ALU_OP_ADD, ALU_OP_SUB, SH_OP_SLL


def int_to_5bit(value):
    """Helper to convert integer to 5-bit array."""
    return [(value >> i) & 1 for i in range(5)]


def int_to_32bit(value):
    """Helper to convert integer to 32-bit array."""
    if value < 0:
        value = (1 << 32) + value
    return [(value >> i) & 1 for i in range(32)]


class TestPerformanceCounters:
    """Test basic performance counter functionality."""
    
    def test_counters_initialized_to_zero(self):
        """Test that all performance counters start at zero."""
        cu = ControlUnit()
        
        assert cu.total_cycles == 0
        assert cu.instruction_count == 0
        assert cu.alu_cycles == 0
        assert cu.shifter_cycles == 0
        assert cu.mdu_cycles == 0
        assert cu.fpu_cycles == 0
        assert cu.idle_cycles == 0
    
    def test_total_cycles_increment(self):
        """Test that total_cycles increments with each tick."""
        cu = ControlUnit()
        
        # Execute a simple ALU operation
        cu.execute_alu_instruction(ALU_OP_ADD,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        # ALU takes 2 cycles (EXECUTE + WRITEBACK)
        assert cu.total_cycles == 2
    
    def test_instruction_count_increment(self):
        """Test that instruction_count increments on completion."""
        cu = ControlUnit()
        
        # Execute multiple instructions
        cu.execute_alu_instruction(ALU_OP_ADD,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        cu.execute_alu_instruction(ALU_OP_SUB,
                                   int_to_5bit(4), int_to_5bit(5), int_to_5bit(6))
        
        assert cu.instruction_count == 2
    
    def test_alu_cycles_tracking(self):
        """Test that ALU cycles are tracked correctly."""
        cu = ControlUnit()
        
        # Execute ALU operation
        cu.execute_alu_instruction(ALU_OP_ADD,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        # ALU takes 2 cycles
        assert cu.alu_cycles == 2
        assert cu.total_cycles == 2
    
    def test_shifter_cycles_tracking(self):
        """Test that Shifter cycles are tracked correctly."""
        cu = ControlUnit()
        
        # Execute Shifter operation
        cu.execute_shifter_instruction(SH_OP_SLL,
                                       int_to_5bit(1), int_to_5bit(4), int_to_5bit(3))
        
        # Shifter takes 2 cycles
        assert cu.shifter_cycles == 2
        assert cu.total_cycles == 2
    
    def test_mdu_cycles_tracking(self):
        """Test that MDU cycles are tracked correctly."""
        cu = ControlUnit()
        
        # Set up operands
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(6))  # r1 = 6
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(7))  # r2 = 7
        
        # Execute MDU MUL operation
        cu.execute_mdu_instruction('MUL',
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        # MDU MUL takes 33 cycles (1 setup + 32 iterations)
        assert cu.mdu_cycles == 33
        assert cu.total_cycles == 33
        assert cu.instruction_count == 1
    
    def test_fpu_cycles_tracking(self):
        """Test that FPU cycles are tracked correctly."""
        cu = ControlUnit()
        
        # Set up FP operands (1.0 and 2.0)
        fp_1_0 = int_to_32bit(0x3F800000)  # 1.0 in IEEE 754
        fp_2_0 = int_to_32bit(0x40000000)  # 2.0 in IEEE 754
        cu.register_file.write_fp_reg(int_to_5bit(1), fp_1_0)
        cu.register_file.write_fp_reg(int_to_5bit(2), fp_2_0)
        
        # Execute FPU FADD operation
        cu.execute_fpu_instruction('FADD',
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        # FPU takes 5 cycles (ALIGN, OP, NORMALIZE, ROUND, WRITEBACK)
        assert cu.fpu_cycles == 5
        assert cu.total_cycles == 5
        assert cu.instruction_count == 1
    
    def test_mixed_operation_cycles(self):
        """Test cycle tracking with mixed operation types."""
        cu = ControlUnit()
        
        # Setup
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(20))
        
        # Execute different operations
        cu.execute_alu_instruction(ALU_OP_ADD,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        cu.execute_shifter_instruction(SH_OP_SLL,
                                       int_to_5bit(3), int_to_5bit(2), int_to_5bit(4))
        
        # Verify counts
        assert cu.alu_cycles == 2
        assert cu.shifter_cycles == 2
        assert cu.total_cycles == 4
        assert cu.instruction_count == 2


class TestPerformanceStats:
    """Test performance statistics calculation."""
    
    def test_get_performance_stats_structure(self):
        """Test that get_performance_stats returns correct structure."""
        cu = ControlUnit()
        
        # Execute some operations
        cu.execute_alu_instruction(ALU_OP_ADD,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        stats = cu.get_performance_stats()
        
        # Check all required fields exist
        assert 'total_cycles' in stats
        assert 'instruction_count' in stats
        assert 'cpi' in stats
        assert 'ipc' in stats
        assert 'alu_cycles' in stats
        assert 'shifter_cycles' in stats
        assert 'mdu_cycles' in stats
        assert 'fpu_cycles' in stats
        assert 'idle_cycles' in stats
        assert 'alu_utilization' in stats
        assert 'shifter_utilization' in stats
        assert 'mdu_utilization' in stats
        assert 'fpu_utilization' in stats
        assert 'idle_utilization' in stats
    
    def test_cpi_calculation(self):
        """Test CPI (Cycles Per Instruction) calculation."""
        cu = ControlUnit()
        
        # Execute 2 ALU instructions (2 cycles each = 4 total)
        cu.execute_alu_instruction(ALU_OP_ADD,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        cu.execute_alu_instruction(ALU_OP_SUB,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(4))
        
        stats = cu.get_performance_stats()
        
        # CPI = total_cycles / instruction_count = 4 / 2 = 2.0
        assert stats['cpi'] == 2.0
        assert stats['ipc'] == 0.5
    
    def test_utilization_percentages(self):
        """Test functional unit utilization percentages."""
        cu = ControlUnit()
        
        # Execute 1 ALU (2 cycles) and 1 Shifter (2 cycles) = 4 total
        cu.execute_alu_instruction(ALU_OP_ADD,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        cu.execute_shifter_instruction(SH_OP_SLL,
                                       int_to_5bit(3), int_to_5bit(2), int_to_5bit(4))
        
        stats = cu.get_performance_stats()
        
        # Each unit used 2 out of 4 cycles = 50%
        assert stats['alu_utilization'] == 50.0
        assert stats['shifter_utilization'] == 50.0
        assert stats['mdu_utilization'] == 0.0
        assert stats['fpu_utilization'] == 0.0
    
    def test_mdu_high_utilization(self):
        """Test utilization with high-cycle MDU operation."""
        cu = ControlUnit()
        
        # Setup
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(6))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(7))
        
        # Execute 1 ALU (2 cycles) and 1 MDU (33 cycles) = 35 total
        cu.execute_alu_instruction(ALU_OP_ADD,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        cu.execute_mdu_instruction('MUL',
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(4))
        
        stats = cu.get_performance_stats()
        
        # ALU: 2/35 = 5.7%, MDU: 33/35 = 94.3%
        assert abs(stats['alu_utilization'] - 5.714) < 0.01
        assert abs(stats['mdu_utilization'] - 94.286) < 0.01
        assert stats['cpi'] == 17.5  # 35 cycles / 2 instructions
    
    def test_stats_with_no_operations(self):
        """Test stats work correctly with zero operations."""
        cu = ControlUnit()
        
        stats = cu.get_performance_stats()
        
        # Should not crash with zero counts
        assert stats['total_cycles'] == 0
        assert stats['instruction_count'] == 0
        assert stats['cpi'] == 0  # Avoid division by zero
        assert stats['ipc'] == 0


class TestPerformanceReset:
    """Test performance counter reset functionality."""
    
    def test_reset_performance_counters(self):
        """Test that reset_performance_counters clears all counters."""
        cu = ControlUnit()
        
        # Execute some operations
        cu.execute_alu_instruction(ALU_OP_ADD,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        cu.execute_shifter_instruction(SH_OP_SLL,
                                       int_to_5bit(3), int_to_5bit(2), int_to_5bit(4))
        
        # Verify counters have values
        assert cu.total_cycles > 0
        assert cu.instruction_count > 0
        
        # Reset counters
        cu.reset_performance_counters()
        
        # Verify all counters are zero
        assert cu.total_cycles == 0
        assert cu.instruction_count == 0
        assert cu.alu_cycles == 0
        assert cu.shifter_cycles == 0
        assert cu.mdu_cycles == 0
        assert cu.fpu_cycles == 0
        assert cu.idle_cycles == 0
    
    def test_reset_doesnt_affect_state(self):
        """Test that reset_performance_counters doesn't affect control unit state."""
        cu = ControlUnit()
        
        # Execute operation and set register
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(42))
        cu.execute_alu_instruction(ALU_OP_ADD,
                                   int_to_5bit(1), int_to_5bit(1), int_to_5bit(2))
        
        # Reset counters
        cu.reset_performance_counters()
        
        # State should be preserved
        assert cu.is_idle()
        value_bits = cu.register_file.read_int_reg(int_to_5bit(1))
        value = sum(bit << i for i, bit in enumerate(value_bits))
        assert value == 42
    
    def test_counters_work_after_reset(self):
        """Test that counters continue working after reset."""
        cu = ControlUnit()
        
        # Execute and reset
        cu.execute_alu_instruction(ALU_OP_ADD,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        cu.reset_performance_counters()
        
        # Execute again
        cu.execute_alu_instruction(ALU_OP_SUB,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(4))
        
        # Should only count the second operation
        assert cu.total_cycles == 2
        assert cu.instruction_count == 1
        assert cu.alu_cycles == 2


class TestPerformancePrinting:
    """Test performance statistics printing."""
    
    def test_print_performance_stats_no_crash(self):
        """Test that print_performance_stats doesn't crash."""
        cu = ControlUnit()
        
        # Execute some operations
        cu.execute_alu_instruction(ALU_OP_ADD,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        # Should not crash
        try:
            cu.print_performance_stats()
            success = True
        except Exception:
            success = False
        
        assert success
    
    def test_print_stats_with_zero_operations(self):
        """Test printing stats with no operations executed."""
        cu = ControlUnit()
        
        # Should handle zero gracefully
        try:
            cu.print_performance_stats()
            success = True
        except Exception:
            success = False
        
        assert success


class TestComplexScenarios:
    """Test performance counters in complex scenarios."""
    
    def test_long_program_sequence(self):
        """Test counters with a long sequence of operations."""
        cu = ControlUnit()
        
        # Setup
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(20))
        
        # Execute 10 ALU operations
        for i in range(10):
            cu.execute_alu_instruction(ALU_OP_ADD,
                                       int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        stats = cu.get_performance_stats()
        
        assert stats['instruction_count'] == 10
        assert stats['total_cycles'] == 20  # 2 cycles each
        assert stats['alu_cycles'] == 20
        assert stats['alu_utilization'] == 100.0
        assert stats['cpi'] == 2.0
    
    def test_mixed_program_with_all_units(self):
        """Test program using all functional units."""
        cu = ControlUnit()
        
        # Setup
        cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(20))
        fp_1_0 = int_to_32bit(0x3F800000)
        fp_2_0 = int_to_32bit(0x40000000)
        cu.register_file.write_fp_reg(int_to_5bit(3), fp_1_0)
        cu.register_file.write_fp_reg(int_to_5bit(4), fp_2_0)
        
        # Execute one of each type
        cu.execute_alu_instruction(ALU_OP_ADD,
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(5))
        cu.execute_shifter_instruction(SH_OP_SLL,
                                       int_to_5bit(1), int_to_5bit(2), int_to_5bit(6))
        cu.execute_mdu_instruction('MUL',
                                   int_to_5bit(1), int_to_5bit(2), int_to_5bit(7))
        cu.execute_fpu_instruction('FADD',
                                   int_to_5bit(3), int_to_5bit(4), int_to_5bit(8))
        
        stats = cu.get_performance_stats()
        
        # Verify all units were used
        assert stats['instruction_count'] == 4
        assert stats['alu_cycles'] == 2
        assert stats['shifter_cycles'] == 2
        assert stats['mdu_cycles'] == 33
        assert stats['fpu_cycles'] == 5
        assert stats['total_cycles'] == 42  # 2 + 2 + 33 + 5
        
        # All utilizations should sum to 100%
        total_util = (stats['alu_utilization'] + stats['shifter_utilization'] +
                     stats['mdu_utilization'] + stats['fpu_utilization'] +
                     stats['idle_utilization'])
        assert abs(total_util - 100.0) < 0.01
