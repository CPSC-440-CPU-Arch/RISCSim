# AI-BEGIN
"""
Test Control Unit ALU Integration (Phase 2)

Tests for cycle-accurate ALU execution through the Control Unit:
- ALU operations with actual computation
- Cycle-by-cycle state transitions
- Register file integration
- Control signal generation
- Trace verification
"""

import pytest
from riscsim.cpu.control_unit import ControlUnit
from riscsim.cpu.registers import RegisterFile
from riscsim.cpu.control_signals import ALU_OP_ADD, ALU_OP_SUB, ALU_OP_AND, ALU_OP_OR, ALU_OP_XOR


class TestControlUnitALU:
    """Test ALU integration with Control Unit."""
    
    def test_alu_add_cycle_by_cycle(self):
        """Test ALU ADD operation cycle-by-cycle."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize registers: r1=10, r2=15
        rf.write_int_reg([0,0,0,0,1], [0]*28 + [1,0,1,0])  # r1 = 10
        rf.write_int_reg([0,0,0,1,0], [0]*28 + [1,1,1,1])  # r2 = 15
        
        # Start ADD operation: r3 = r1 + r2
        cu.start_alu_operation(
            ALU_OP_ADD,
            [0,0,0,0,1],  # rs1 = r1
            [0,0,0,1,0],  # rs2 = r2
            [0,0,0,1,1]   # rd = r3
        )
        
        assert cu.state == cu.STATE_EXECUTE
        assert cu.current_op_type == cu.OP_ALU
        
        # Cycle 1: Execute ALU operation
        complete = cu.tick()
        assert not complete
        assert cu.state == cu.STATE_WRITEBACK
        assert cu.signals.rf_we == 1
        assert cu.alu_result == [0]*27 + [1,1,0,0,1]  # 25
        
        # Cycle 2: Writeback
        complete = cu.tick()
        assert complete
        assert cu.state == cu.STATE_IDLE
        assert cu.signals.rf_we == 0
        
        # Verify result written to r3
        result = rf.read_int_reg([0,0,0,1,1])
        assert result == [0]*27 + [1,1,0,0,1]  # 25
    
    def test_alu_sub_with_trace(self):
        """Test ALU SUB operation with trace verification."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize: r5=42, r6=20
        rf.write_int_reg([0,0,1,0,1], [0]*26 + [1,0,1,0,1,0])  # r5 = 42
        rf.write_int_reg([0,0,1,1,0], [0]*27 + [1,0,1,0,0])   # r6 = 20
        
        # Execute: r7 = r5 - r6 = 22
        result = cu.execute_alu_instruction(
            ALU_OP_SUB,
            [0,0,1,0,1],  # rs1 = r5
            [0,0,1,1,0],  # rs2 = r6
            [0,0,1,1,1]   # rd = r7
        )
        
        assert result['success']
        assert result['cycles'] == 2  # EXECUTE + WRITEBACK
        assert len(result['trace']) > 0
        
        # Verify result
        r7_value = rf.read_int_reg([0,0,1,1,1])
        assert r7_value == [0]*27 + [1,0,1,1,0]  # 22
    
    def test_alu_and_or_xor_sequence(self):
        """Test sequence of AND, OR, XOR operations."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize: r1=0b11110000, r2=0b10101010
        rf.write_int_reg([0,0,0,0,1], [0]*24 + [1,1,1,1,0,0,0,0])
        rf.write_int_reg([0,0,0,1,0], [0]*24 + [1,0,1,0,1,0,1,0])
        
        # Test AND: r3 = r1 & r2 = 0b10100000
        cu.reset()
        result = cu.execute_alu_instruction(
            ALU_OP_AND,
            [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1]
        )
        assert result['success']
        r3 = rf.read_int_reg([0,0,0,1,1])
        assert r3 == [0]*24 + [1,0,1,0,0,0,0,0]
        
        # Test OR: r4 = r1 | r2 = 0b11111010
        cu.reset()
        result = cu.execute_alu_instruction(
            ALU_OP_OR,
            [0,0,0,0,1], [0,0,0,1,0], [0,0,1,0,0]
        )
        assert result['success']
        r4 = rf.read_int_reg([0,0,1,0,0])
        assert r4 == [0]*24 + [1,1,1,1,1,0,1,0]
        
        # Test XOR: r5 = r1 ^ r2 = 0b01011010
        cu.reset()
        result = cu.execute_alu_instruction(
            ALU_OP_XOR,
            [0,0,0,0,1], [0,0,0,1,0], [0,0,1,0,1]
        )
        assert result['success']
        r5 = rf.read_int_reg([0,0,1,0,1])
        assert r5 == [0]*24 + [0,1,0,1,1,0,1,0]
    
    def test_alu_result_writeback(self):
        """Test that ALU results are written back correctly."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Set up operands
        rf.write_int_reg([0,0,0,0,1], [0]*29 + [1,0,0])  # r1 = 4
        rf.write_int_reg([0,0,0,1,0], [0]*29 + [0,1,1])   # r2 = 3
        
        # Execute ADD
        cu.execute_alu_instruction(
            ALU_OP_ADD,
            [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1]
        )
        
        # Check r3 = 7
        r3 = rf.read_int_reg([0,0,0,1,1])
        assert r3 == [0]*29 + [1,1,1]
        
        # Ensure r1 and r2 unchanged
        r1 = rf.read_int_reg([0,0,0,0,1])
        r2 = rf.read_int_reg([0,0,0,1,0])
        assert r1 == [0]*29 + [1,0,0]
        assert r2 == [0]*29 + [0,1,1]
    
    def test_alu_control_signals_each_cycle(self):
        """Test control signal generation at each cycle."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        rf.write_int_reg([0,0,0,0,1], [0]*31 + [1])  # r1 = 1
        rf.write_int_reg([0,0,0,1,0], [0]*31 + [1])  # r2 = 1
        
        # Start operation
        cu.start_alu_operation(
            ALU_OP_ADD,
            [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1]
        )
        
        # Check initial signals
        assert cu.signals.alu_op == ALU_OP_ADD
        assert cu.signals.rf_raddr_a == [0,0,0,0,1]
        assert cu.signals.rf_raddr_b == [0,0,0,1,0]
        assert cu.signals.rf_waddr == [0,0,0,1,1]
        assert cu.signals.src_a_sel == 0
        assert cu.signals.src_b_sel == 0
        
        # Cycle 1: EXECUTE
        cu.tick()
        assert cu.signals.rf_we == 1
        
        # Cycle 2: WRITEBACK
        cu.tick()
        assert cu.signals.rf_we == 0
        assert cu.is_idle()
    
    def test_alu_with_different_registers(self):
        """Test ALU with various register combinations."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize multiple registers
        for i in range(1, 11):
            addr = [0] * (5 - len(bin(i)[2:])) + [int(b) for b in bin(i)[2:]]
            value = [0] * (32 - len(bin(i)[2:])) + [int(b) for b in bin(i)[2:]]
            rf.write_int_reg(addr, value)
        
        # Test r10 = r5 + r8 (5 + 8 = 13)
        cu.execute_alu_instruction(
            ALU_OP_ADD,
            [0,0,1,0,1],  # r5
            [0,1,0,0,0],  # r8
            [0,1,0,1,0]   # r10
        )
        
        r10 = rf.read_int_reg([0,1,0,1,0])
        expected = [0] * 28 + [1,1,0,1]  # 13
        assert r10 == expected
    
    def test_alu_x0_hardwired_to_zero(self):
        """Test that x0 remains zero even when used as destination."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Set up operands
        rf.write_int_reg([0,0,0,0,1], [0]*31 + [1])  # r1 = 1
        rf.write_int_reg([0,0,0,1,0], [0]*31 + [1])  # r2 = 1
        
        # Try to write to x0 (should be ignored)
        cu.execute_alu_instruction(
            ALU_OP_ADD,
            [0,0,0,0,1], [0,0,0,1,0],
            [0,0,0,0,0]  # rd = x0
        )
        
        # Verify x0 is still zero
        x0 = rf.read_int_reg([0,0,0,0,0])
        assert x0 == [0] * 32
    
    def test_alu_operation_isolation(self):
        """Test that operations don't interfere with each other."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize
        rf.write_int_reg([0,0,0,0,1], [0]*30 + [1,0])  # r1 = 2
        rf.write_int_reg([0,0,0,1,0], [0]*30 + [1,1])  # r2 = 3
        
        # First operation: r3 = r1 + r2
        cu.execute_alu_instruction(
            ALU_OP_ADD,
            [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1]
        )
        r3 = rf.read_int_reg([0,0,0,1,1])
        
        # Reset and do second operation: r4 = r1 - r2
        cu.reset()
        cu.execute_alu_instruction(
            ALU_OP_SUB,
            [0,0,0,0,1], [0,0,0,1,0], [0,0,1,0,0]
        )
        r4 = rf.read_int_reg([0,0,1,0,0])
        
        # Verify r3 unchanged
        r3_check = rf.read_int_reg([0,0,0,1,1])
        assert r3_check == r3
        
        # Verify results are different
        assert r3 != r4
# AI-END
