# AI-BEGIN
"""
Test Control Unit Shifter Integration (Phase 3)

Tests for cycle-accurate Shifter execution through the Control Unit:
- Shifter operations with actual computation
- SLL, SRL, SRA operations
- Cycle-by-cycle state transitions
- Register file integration
- Control signal generation
"""

import pytest
from riscsim.cpu.control_unit import ControlUnit
from riscsim.cpu.registers import RegisterFile
from riscsim.cpu.control_signals import SH_OP_SLL, SH_OP_SRL, SH_OP_SRA


class TestControlUnitShifter:
    """Test Shifter integration with Control Unit."""
    
    def test_shifter_sll_cycle_by_cycle(self):
        """Test Shifter SLL (Shift Left Logical) operation cycle-by-cycle."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize r1 = 0b00000001 (1)
        rf.write_int_reg([0,0,0,0,1], [0]*31 + [1])
        
        # Start SLL operation: r2 = r1 << 4
        cu.start_shifter_operation(
            SH_OP_SLL,
            [0,0,0,0,1],  # rs1 = r1
            [0,0,1,0,0],  # shamt = 4
            [0,0,0,1,0]   # rd = r2
        )
        
        assert cu.state == cu.STATE_EXECUTE
        assert cu.current_op_type == cu.OP_SHIFTER
        
        # Cycle 1: Execute shifter operation
        complete = cu.tick()
        assert not complete
        assert cu.state == cu.STATE_WRITEBACK
        assert cu.signals.rf_we == 1
        assert cu.shifter_result == [0]*27 + [1,0,0,0,0]  # 16
        
        # Cycle 2: Writeback
        complete = cu.tick()
        assert complete
        assert cu.state == cu.STATE_IDLE
        
        # Verify result written to r2
        result = rf.read_int_reg([0,0,0,1,0])
        assert result == [0]*27 + [1,0,0,0,0]  # 16
    
    def test_shifter_srl_with_trace(self):
        """Test Shifter SRL (Shift Right Logical) with trace."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize r3 = 0b10000000 (128)
        rf.write_int_reg([0,0,0,1,1], [0]*24 + [1,0,0,0,0,0,0,0])
        
        # Execute: r4 = r3 >> 3 = 16
        result = cu.execute_shifter_instruction(
            SH_OP_SRL,
            [0,0,0,1,1],  # rs1 = r3
            [0,0,0,1,1],  # shamt = 3
            [0,0,1,0,0]   # rd = r4
        )
        
        assert result['success']
        assert result['cycles'] == 2  # EXECUTE + WRITEBACK
        assert len(result['trace']) > 0
        
        # Verify result
        r4_value = rf.read_int_reg([0,0,1,0,0])
        assert r4_value == [0]*27 + [1,0,0,0,0]  # 16
    
    def test_shifter_sra_execution(self):
        """Test Shifter SRA (Shift Right Arithmetic) preserves sign."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize r5 = -16 (0xFFFFFFF0 in 32-bit two's complement)
        rf.write_int_reg([0,0,1,0,1], [1]*28 + [0,0,0,0])
        
        # Execute: r6 = r5 >> 2 (arithmetic) = -4
        result = cu.execute_shifter_instruction(
            SH_OP_SRA,
            [0,0,1,0,1],  # rs1 = r5
            [0,0,0,1,0],  # shamt = 2
            [0,0,1,1,0]   # rd = r6
        )
        
        assert result['success']
        
        # Verify result: -4 = 0xFFFFFFFC
        r6_value = rf.read_int_reg([0,0,1,1,0])
        assert r6_value == [1]*30 + [0,0]  # Sign extended
        assert r6_value[0] == 1  # Sign bit preserved
    
    def test_shifter_result_writeback(self):
        """Test that Shifter results are written back correctly."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Set up operand
        rf.write_int_reg([0,0,0,0,1], [0]*29 + [1,0,0])  # r1 = 4
        
        # Execute SLL by 1: 4 << 1 = 8
        cu.execute_shifter_instruction(
            SH_OP_SLL,
            [0,0,0,0,1],  # rs1 = r1
            [0,0,0,0,1],  # shamt = 1
            [0,0,0,1,0]   # rd = r2
        )
        
        # Check r2 = 8 (0b1000)
        r2 = rf.read_int_reg([0,0,0,1,0])
        assert r2 == [0]*28 + [1,0,0,0]  # 8
        
        # Ensure r1 unchanged
        r1 = rf.read_int_reg([0,0,0,0,1])
        assert r1 == [0]*29 + [1,0,0]  # 4
    
    def test_shifter_control_signals(self):
        """Test control signal generation during shifter operation."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        rf.write_int_reg([0,0,0,0,1], [0]*31 + [1])  # r1 = 1
        
        # Start operation
        cu.start_shifter_operation(
            SH_OP_SLL,
            [0,0,0,0,1],  # rs1 = r1
            [0,0,1,0,0],  # shamt = 4
            [0,0,0,1,0]   # rd = r2
        )
        
        # Check initial signals
        assert cu.signals.sh_op == SH_OP_SLL
        assert cu.signals.sh_amount == [0,0,1,0,0]
        assert cu.signals.rf_raddr_a == [0,0,0,0,1]
        assert cu.signals.rf_waddr == [0,0,0,1,0]
        
        # Cycle 1: EXECUTE
        cu.tick()
        assert cu.signals.rf_we == 1
        
        # Cycle 2: WRITEBACK
        cu.tick()
        assert cu.signals.rf_we == 0
        assert cu.is_idle()
    
    def test_shifter_variable_amounts(self):
        """Test shifter with various shift amounts."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize r1 = 255 (0xFF)
        rf.write_int_reg([0,0,0,0,1], [0]*24 + [1,1,1,1,1,1,1,1])
        
        # Test shift by 0 (no change)
        cu.execute_shifter_instruction(
            SH_OP_SLL,
            [0,0,0,0,1], [0,0,0,0,0], [0,0,0,1,0]
        )
        r2 = rf.read_int_reg([0,0,0,1,0])
        assert r2 == [0]*24 + [1,1,1,1,1,1,1,1]  # 255
        
        # Test shift by 8
        cu.reset()
        cu.execute_shifter_instruction(
            SH_OP_SLL,
            [0,0,0,0,1], [0,1,0,0,0], [0,0,0,1,1]
        )
        r3 = rf.read_int_reg([0,0,0,1,1])
        assert r3 == [0]*16 + [1,1,1,1,1,1,1,1] + [0]*8  # 65280
# AI-END
