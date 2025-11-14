# AI-BEGIN
"""
Test Control Unit MDU Integration (Phase 4)

Tests for cycle-accurate MDU execution through the Control Unit:
- Multi-cycle multiply operations (MUL, MULH, MULHU, MULHSU)
- Multi-cycle divide operations (DIV, DIVU, REM, REMU)
- State transitions (32+ cycles)
- md_busy and md_done signal management
- Register file integration with MDU results
"""

import pytest
from riscsim.cpu.control_unit import ControlUnit
from riscsim.cpu.registers import RegisterFile


class TestControlUnitMDU:
    """Test MDU integration with Control Unit."""
    
    def test_mul_32_cycles(self):
        """Test MUL operation completes in 32+ cycles."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize r1 = 6, r2 = 7
        rf.write_int_reg([0,0,0,0,1], [0]*29 + [1,1,0])  # r1 = 6
        rf.write_int_reg([0,0,0,1,0], [0]*29 + [1,1,1])  # r2 = 7
        
        # Execute: r3 = r1 * r2 = 42
        result = cu.execute_mdu_instruction(
            "MUL",
            [0,0,0,0,1],  # rs1 = r1
            [0,0,0,1,0],  # rs2 = r2
            [0,0,0,1,1]   # rd = r3
        )
        
        assert result['success']
        # MDU multiply takes 32 cycles for computation + 1 for writeback
        assert result['cycles'] >= 32
        assert result['cycles'] <= 35  # Should be around 33-34
        
        # Verify result: 6 * 7 = 42 = 0b101010
        r3 = rf.read_int_reg([0,0,0,1,1])
        assert r3 == [0]*26 + [1,0,1,0,1,0]  # 42
    
    def test_mul_partial_products(self):
        """Test MUL stores intermediate partial products."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize r1 = 15 (0xF), r2 = 16 (0x10)
        rf.write_int_reg([0,0,0,0,1], [0]*28 + [1,1,1,1])  # r1 = 15
        rf.write_int_reg([0,0,0,1,0], [0]*27 + [1,0,0,0,0])  # r2 = 16
        
        # Execute: r3 = r1 * r2 = 240
        result = cu.execute_mdu_instruction(
            "MUL",
            [0,0,0,0,1],
            [0,0,0,1,0],
            [0,0,0,1,1]
        )
        
        assert result['success']
        
        # Check that partial products were stored
        assert 'product_lo' in result
        assert 'product_hi' in result
        
        # Result should be 240 = 0xF0
        r3 = rf.read_int_reg([0,0,0,1,1])
        assert r3 == [0]*24 + [1,1,1,1,0,0,0,0]  # 240
    
    def test_mul_busy_done_signals(self):
        """Test md_busy and md_done signals during multiplication."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        rf.write_int_reg([0,0,0,0,1], [0]*31 + [1])  # r1 = 1
        rf.write_int_reg([0,0,0,1,0], [0]*31 + [1])  # r2 = 1
        
        # Start operation
        cu.start_mdu_operation("MUL", [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1])
        
        # Initially: busy=1, done=0
        assert cu.signals.md_busy == 1
        assert cu.signals.md_done == 0
        
        # Cycle through most of the operation
        for _ in range(31):
            complete = cu.tick()
            assert not complete
            # Should still be busy
            assert cu.signals.md_busy == 1
        
        # Next tick should transition to writeback
        cu.tick()
        assert cu.signals.md_busy == 0
        assert cu.signals.md_done == 1
        
        # Final tick completes
        complete = cu.tick()
        assert complete
        assert cu.signals.md_done == 0
    
    def test_div_cycle_by_cycle(self):
        """Test DIV operation state transitions cycle-by-cycle."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize r1 = 100, r2 = 10
        rf.write_int_reg([0,0,0,0,1], [0]*25 + [1,1,0,0,1,0,0])  # r1 = 100
        rf.write_int_reg([0,0,0,1,0], [0]*28 + [1,0,1,0])  # r2 = 10
        
        # Start DIV operation: r3 = r1 / r2 = 10
        cu.start_mdu_operation("DIV", [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1])
        
        # Import state constants
        from riscsim.cpu.control_signals import (
            MDU_STATE_DIV_TESTBIT, MDU_STATE_DIV_SUB,
            MDU_STATE_DIV_RESTORE, MDU_STATE_DIV_SHIFT
        )
        
        assert cu.mdu_state == MDU_STATE_DIV_TESTBIT
        
        # First cycle: TESTBIT → SUB
        complete = cu.tick()
        assert not complete
        assert cu.mdu_state == MDU_STATE_DIV_SUB
        
        # Second cycle: SUB → RESTORE
        complete = cu.tick()
        assert not complete
        assert cu.mdu_state == MDU_STATE_DIV_RESTORE
        
        # Third cycle: RESTORE → SHIFT
        complete = cu.tick()
        assert not complete
        assert cu.mdu_state == MDU_STATE_DIV_SHIFT
        
        # Fourth cycle: SHIFT → TESTBIT (loop continues)
        complete = cu.tick()
        assert not complete
        assert cu.mdu_state == MDU_STATE_DIV_TESTBIT
    
    def test_div_testbit_sub_restore_transitions(self):
        """Test division FSM state transitions through TESTBIT→SUB→RESTORE→SHIFT."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        rf.write_int_reg([0,0,0,0,1], [0]*28 + [1,0,0,0])  # r1 = 8
        rf.write_int_reg([0,0,0,1,0], [0]*30 + [1,0])  # r2 = 2
        
        # Execute: r3 = 8 / 2 = 4
        result = cu.execute_mdu_instruction(
            "DIV",
            [0,0,0,0,1],
            [0,0,0,1,0],
            [0,0,0,1,1]
        )
        
        assert result['success']
        
        # Check trace contains all state transitions
        trace = result['trace']
        # Extract just the messages from trace dictionaries
        trace_str = '\n'.join([entry['message'] if isinstance(entry, dict) else entry for entry in trace])
        
        assert 'TESTBIT → SUB' in trace_str
        assert 'SUB → RESTORE' in trace_str
        assert 'RESTORE → SHIFT' in trace_str
        assert 'SHIFT → TESTBIT' in trace_str or 'SHIFT → WRITEBACK' in trace_str
    
    def test_div_quotient_remainder_building(self):
        """Test that division correctly builds quotient and remainder."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize r1 = 17, r2 = 5
        rf.write_int_reg([0,0,0,0,1], [0]*27 + [1,0,0,0,1])  # r1 = 17
        rf.write_int_reg([0,0,0,1,0], [0]*29 + [1,0,1])  # r2 = 5
        
        # Execute DIV: r3 = 17 / 5 = 3
        div_result = cu.execute_mdu_instruction(
            "DIV",
            [0,0,0,0,1],
            [0,0,0,1,0],
            [0,0,0,1,1]
        )
        
        assert div_result['success']
        
        # Check quotient = 3
        r3 = rf.read_int_reg([0,0,0,1,1])
        assert r3 == [0]*30 + [1,1]  # 3
        
        # Check remainder stored = 2
        assert 'remainder' in div_result
        remainder = div_result['remainder']
        assert remainder == [0]*30 + [1,0]  # 2
        
        # Now test REM operation: r4 = 17 % 5 = 2
        cu.reset()
        rf.write_int_reg([0,0,0,0,1], [0]*27 + [1,0,0,0,1])  # r1 = 17
        rf.write_int_reg([0,0,0,1,0], [0]*29 + [1,0,1])  # r2 = 5
        
        rem_result = cu.execute_mdu_instruction(
            "REM",
            [0,0,0,0,1],
            [0,0,0,1,0],
            [0,0,1,0,0]  # rd = r4
        )
        
        assert rem_result['success']
        
        # Check remainder = 2
        r4 = rf.read_int_reg([0,0,1,0,0])
        assert r4 == [0]*30 + [1,0]  # 2
    
    def test_mdu_state_trace(self):
        """Test MDU operation generates detailed state trace."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        rf.write_int_reg([0,0,0,0,1], [0]*30 + [1,0])  # r1 = 2
        rf.write_int_reg([0,0,0,1,0], [0]*29 + [1,1,0])  # r2 = 6
        
        # Execute MUL
        result = cu.execute_mdu_instruction(
            "MUL",
            [0,0,0,0,1],
            [0,0,0,1,0],
            [0,0,0,1,1]
        )
        
        assert result['success']
        
        # Check trace has MDU state information
        trace = result['trace']
        assert len(trace) > 0
        
        # Extract messages from trace dictionaries
        trace_str = '\n'.join([entry['message'] if isinstance(entry, dict) else entry for entry in trace])
        assert 'MDU MUL' in trace_str
        assert 'SHIFT' in trace_str or 'ADD' in trace_str
    
    def test_mdu_writeback(self):
        """Test MDU results are written back correctly to register file."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Test multiple operations
        rf.write_int_reg([0,0,0,0,1], [0]*28 + [1,1,0,0])  # r1 = 12
        rf.write_int_reg([0,0,0,1,0], [0]*29 + [1,0,1])  # r2 = 5
        
        # MUL: 12 * 5 = 60
        cu.execute_mdu_instruction("MUL", [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1])
        r3 = rf.read_int_reg([0,0,0,1,1])
        assert r3 == [0]*26 + [1,1,1,1,0,0]  # 60
        
        # DIV: 12 / 5 = 2
        cu.reset()
        cu.execute_mdu_instruction("DIV", [0,0,0,0,1], [0,0,0,1,0], [0,0,1,0,0])
        r4 = rf.read_int_reg([0,0,1,0,0])
        assert r4 == [0]*30 + [1,0]  # 2
        
        # REM: 12 % 5 = 2
        cu.reset()
        cu.execute_mdu_instruction("REM", [0,0,0,0,1], [0,0,0,1,0], [0,0,1,0,1])
        r5 = rf.read_int_reg([0,0,1,0,1])
        assert r5 == [0]*30 + [1,0]  # 2
        
        # Ensure all source registers unchanged
        assert rf.read_int_reg([0,0,0,0,1]) == [0]*28 + [1,1,0,0]  # r1 = 12
        assert rf.read_int_reg([0,0,0,1,0]) == [0]*29 + [1,0,1]  # r2 = 5
# AI-END
