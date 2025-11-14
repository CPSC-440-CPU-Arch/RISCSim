# AI-BEGIN
"""
Test suite for Control Unit (FSM) and Control Signals

Tests the control unit's ability to:
- Generate and manage control signals
- Sequence multi-cycle operations
- Track state transitions
- Produce operation traces
"""

import pytest
from riscsim.cpu.control_unit import ControlUnit
from riscsim.cpu.control_signals import (
    ControlSignals,
    ALU_OP_ADD, ALU_OP_SUB, ALU_OP_AND,
    SH_OP_SLL, SH_OP_SRL,
    FPU_STATE_IDLE, FPU_STATE_ALIGN, FPU_STATE_OP,
    FPU_STATE_NORMALIZE, FPU_STATE_ROUND, FPU_STATE_WRITEBACK,
    MDU_STATE_IDLE, MDU_STATE_MUL_SHIFT, MDU_STATE_DIV_TESTBIT,
    decode_alu_op, decode_shifter_op, format_control_signals
)


class TestControlSignals:
    """Test ControlSignals class functionality."""
    
    def test_initialization(self):
        """Test that control signals initialize to default values."""
        signals = ControlSignals()
        
        assert signals.alu_op == [0, 0, 0, 0]
        assert signals.rf_we == 0
        assert signals.rf_waddr == [0] * 5
        assert signals.rf_raddr_a == [0] * 5
        assert signals.rf_raddr_b == [0] * 5
        assert signals.src_a_sel == 0
        assert signals.src_b_sel == 0
        assert signals.sh_op == [0, 0, 0]
        assert signals.sh_amount == [0] * 5
        assert signals.md_start == 0
        assert signals.md_busy == 0
        assert signals.md_done == 0
        assert signals.md_op == 'IDLE'
        assert signals.fpu_start == 0
        assert signals.fpu_state == 'IDLE'
        assert signals.fpu_op == 'IDLE'
        assert signals.round_mode == 'RNE'
        assert signals.cycle == 0
        assert signals.pc == [0] * 32
    
    def test_to_dict_and_from_dict(self):
        """Test conversion to/from dictionary."""
        signals1 = ControlSignals()
        signals1.alu_op = ALU_OP_ADD
        signals1.rf_we = 1
        signals1.rf_waddr = [0, 0, 0, 1, 1]  # Register 3
        signals1.cycle = 42
        
        # Convert to dict
        signal_dict = signals1.to_dict()
        
        # Create new signals from dict
        signals2 = ControlSignals()
        signals2.from_dict(signal_dict)
        
        assert signals2.alu_op == ALU_OP_ADD
        assert signals2.rf_we == 1
        assert signals2.rf_waddr == [0, 0, 0, 1, 1]
        assert signals2.cycle == 42
    
    def test_copy(self):
        """Test deep copy of control signals."""
        signals1 = ControlSignals()
        signals1.alu_op = ALU_OP_SUB
        signals1.rf_we = 1
        signals1.cycle = 10
        
        signals2 = signals1.copy()
        
        # Verify copy has same values
        assert signals2.alu_op == ALU_OP_SUB
        assert signals2.rf_we == 1
        assert signals2.cycle == 10
        
        # Verify it's a deep copy (modifying one doesn't affect the other)
        signals2.alu_op[0] = 1
        assert signals1.alu_op != signals2.alu_op
    
    def test_reset(self):
        """Test reset of control signals."""
        signals = ControlSignals()
        signals.alu_op = ALU_OP_ADD
        signals.rf_we = 1
        signals.cycle = 100
        
        signals.reset()
        
        assert signals.alu_op == [0, 0, 0, 0]
        assert signals.rf_we == 0
        assert signals.cycle == 0
    
    def test_decode_alu_op(self):
        """Test ALU opcode decoding."""
        assert decode_alu_op(ALU_OP_ADD) == 'ADD'
        assert decode_alu_op(ALU_OP_SUB) == 'SUB'
        assert decode_alu_op(ALU_OP_AND) == 'AND'
        assert decode_alu_op([1, 1, 1, 1]) == 'UNKNOWN'
    
    def test_decode_shifter_op(self):
        """Test shifter opcode decoding."""
        assert decode_shifter_op(SH_OP_SLL) == 'SLL'
        assert decode_shifter_op(SH_OP_SRL) == 'SRL'
        assert decode_shifter_op([1, 1, 1]) == 'UNKNOWN'
    
    def test_format_control_signals(self):
        """Test control signal formatting."""
        signals = ControlSignals()
        signals.cycle = 5
        signals.alu_op = ALU_OP_ADD
        
        formatted = format_control_signals(signals)
        
        assert 'Cycle 5:' in formatted
        assert 'ALU_OP: 0010' in formatted
        assert 'RF:' in formatted
        assert 'MDU:' in formatted
        assert 'FPU:' in formatted


class TestControlUnitBasics:
    """Test basic Control Unit functionality."""
    
    def test_initialization(self):
        """Test Control Unit initialization."""
        cu = ControlUnit()
        
        assert cu.state == ControlUnit.STATE_IDLE
        assert cu.mdu_state == MDU_STATE_IDLE
        assert cu.fpu_state == FPU_STATE_IDLE
        assert cu.current_op_type is None
        assert len(cu.trace) == 0
    
    def test_reset(self):
        """Test Control Unit reset."""
        cu = ControlUnit()
        cu.state = ControlUnit.STATE_EXECUTE
        cu.signals.cycle = 100
        cu.trace.append({'test': 'data'})
        
        cu.reset()
        
        assert cu.state == ControlUnit.STATE_IDLE
        assert cu.signals.cycle == 0
        assert len(cu.trace) == 0
    
    def test_is_idle(self):
        """Test idle state checking."""
        cu = ControlUnit()
        
        assert cu.is_idle()
        assert not cu.is_busy()
        
        cu.state = ControlUnit.STATE_EXECUTE
        
        assert not cu.is_idle()
        assert cu.is_busy()
    
    def test_get_current_state(self):
        """Test getting current FSM state."""
        cu = ControlUnit()
        cu.signals.cycle = 10
        
        state = cu.get_current_state()
        
        assert state['main_state'] == ControlUnit.STATE_IDLE
        assert state['mdu_state'] == MDU_STATE_IDLE
        assert state['fpu_state'] == FPU_STATE_IDLE
        assert 'signals' in state


class TestControlUnitALUOperations:
    """Test Control Unit ALU operation sequencing."""
    
    def test_start_alu_operation(self):
        """Test starting an ALU operation."""
        cu = ControlUnit()
        
        # Start ADD operation: r3 = r1 + r2
        cu.start_alu_operation(
            alu_op=ALU_OP_ADD,
            rs1_addr=[0, 0, 0, 0, 1],  # r1
            rs2_addr=[0, 0, 0, 1, 0],  # r2
            rd_addr=[0, 0, 0, 1, 1]    # r3
        )
        
        assert cu.state == ControlUnit.STATE_EXECUTE
        assert cu.current_op_type == ControlUnit.OP_ALU
        assert cu.signals.alu_op == ALU_OP_ADD
        assert cu.signals.rf_raddr_a == [0, 0, 0, 0, 1]
        assert cu.signals.rf_raddr_b == [0, 0, 0, 1, 0]
        assert cu.signals.rf_waddr == [0, 0, 0, 1, 1]
        assert len(cu.trace) == 1
    
    def test_alu_operation_complete_sequence(self):
        """Test complete ALU operation sequence."""
        cu = ControlUnit()
        
        cu.start_alu_operation(
            alu_op=ALU_OP_ADD,
            rs1_addr=[0, 0, 0, 0, 1],
            rs2_addr=[0, 0, 0, 1, 0],
            rd_addr=[0, 0, 0, 1, 1]
        )
        
        # Tick 1: EXECUTE → WRITEBACK
        done = cu.tick()
        assert not done
        assert cu.state == ControlUnit.STATE_WRITEBACK
        assert cu.signals.rf_we == 1
        
        # Tick 2: WRITEBACK → IDLE (complete)
        done = cu.tick()
        assert done
        assert cu.state == ControlUnit.STATE_IDLE
        assert cu.signals.rf_we == 0
        assert cu.is_idle()


class TestControlUnitShifterOperations:
    """Test Control Unit Shifter operation sequencing."""
    
    def test_start_shifter_operation(self):
        """Test starting a shifter operation."""
        cu = ControlUnit()
        
        # Start SLL operation: r2 = r1 << 5
        cu.start_shifter_operation(
            sh_op=SH_OP_SLL,
            rs1_addr=[0, 0, 0, 0, 1],  # r1
            sh_amount=[0, 0, 1, 0, 1],  # 5
            rd_addr=[0, 0, 0, 1, 0]     # r2
        )
        
        assert cu.state == ControlUnit.STATE_EXECUTE
        assert cu.current_op_type == ControlUnit.OP_SHIFTER
        assert cu.signals.sh_op == SH_OP_SLL
        assert cu.signals.sh_amount == [0, 0, 1, 0, 1]
        assert cu.signals.rf_raddr_a == [0, 0, 0, 0, 1]
        assert cu.signals.rf_waddr == [0, 0, 0, 1, 0]
    
    def test_shifter_operation_complete_sequence(self):
        """Test complete shifter operation sequence."""
        cu = ControlUnit()
        
        cu.start_shifter_operation(
            sh_op=SH_OP_SRL,
            rs1_addr=[0, 0, 0, 0, 1],
            sh_amount=[0, 0, 0, 1, 0],
            rd_addr=[0, 0, 0, 1, 0]
        )
        
        # Tick 1: EXECUTE → WRITEBACK
        done = cu.tick()
        assert not done
        assert cu.state == ControlUnit.STATE_WRITEBACK
        
        # Tick 2: WRITEBACK → IDLE
        done = cu.tick()
        assert done
        assert cu.is_idle()


class TestControlUnitMDUOperations:
    """Test Control Unit MDU operation sequencing."""
    
    def test_start_mdu_mul_operation(self):
        """Test starting an MDU multiply operation."""
        cu = ControlUnit()
        
        cu.start_mdu_operation(
            mdu_op='MUL',
            rs1_addr=[0, 0, 0, 0, 1],
            rs2_addr=[0, 0, 0, 1, 0],
            rd_addr=[0, 0, 0, 1, 1]
        )
        
        assert cu.current_op_type == ControlUnit.OP_MDU
        assert cu.signals.md_op == 'MUL'
        assert cu.signals.md_busy == 1
        assert cu.signals.md_done == 0
        assert cu.mdu_state == MDU_STATE_MUL_SHIFT
    
    def test_start_mdu_div_operation(self):
        """Test starting an MDU divide operation."""
        cu = ControlUnit()
        
        cu.start_mdu_operation(
            mdu_op='DIV',
            rs1_addr=[0, 0, 0, 0, 1],
            rs2_addr=[0, 0, 0, 1, 0],
            rd_addr=[0, 0, 0, 1, 1]
        )
        
        assert cu.current_op_type == ControlUnit.OP_MDU
        assert cu.signals.md_op == 'DIV'
        assert cu.signals.md_busy == 1
        assert cu.mdu_state == MDU_STATE_DIV_TESTBIT
    
    def test_mdu_multiply_multi_cycle(self):
        """Test MDU multiply goes through multiple cycles."""
        cu = ControlUnit()
        
        cu.start_mdu_operation(
            mdu_op='MUL',
            rs1_addr=[0, 0, 0, 0, 1],
            rs2_addr=[0, 0, 0, 1, 0],
            rd_addr=[0, 0, 0, 1, 1]
        )
        
        # Should take multiple cycles (32 iterations + writeback)
        cycle_count = 0
        done = False
        max_cycles = 100  # Safety limit
        
        while not done and cycle_count < max_cycles:
            done = cu.tick()
            cycle_count += 1
        
        assert done
        assert cu.is_idle()
        assert cycle_count > 2  # Should take more than just a few cycles
        assert cu.signals.md_busy == 0
        
    def test_mdu_divide_multi_cycle(self):
        """Test MDU divide goes through multiple cycles."""
        cu = ControlUnit()
        
        cu.start_mdu_operation(
            mdu_op='DIV',
            rs1_addr=[0, 0, 0, 0, 1],
            rs2_addr=[0, 0, 0, 1, 0],
            rd_addr=[0, 0, 0, 1, 1]
        )
        
        cycle_count = 0
        done = False
        max_cycles = 100
        
        while not done and cycle_count < max_cycles:
            done = cu.tick()
            cycle_count += 1
        
        assert done
        assert cu.is_idle()
        assert cycle_count > 2


class TestControlUnitFPUOperations:
    """Test Control Unit FPU operation sequencing."""
    
    def test_start_fpu_operation(self):
        """Test starting an FPU operation."""
        cu = ControlUnit()
        
        cu.start_fpu_operation(
            fpu_op='FADD',
            rs1_addr=[0, 0, 0, 0, 1],
            rs2_addr=[0, 0, 0, 1, 0],
            rd_addr=[0, 0, 0, 1, 1],
            round_mode='RNE'
        )
        
        assert cu.current_op_type == ControlUnit.OP_FPU
        assert cu.signals.fpu_op == 'FADD'
        assert cu.signals.round_mode == 'RNE'
        assert cu.fpu_state == FPU_STATE_ALIGN
    
    def test_fpu_operation_state_sequence(self):
        """Test FPU operation goes through all states."""
        cu = ControlUnit()
        
        cu.start_fpu_operation(
            fpu_op='FADD',
            rs1_addr=[0, 0, 0, 0, 1],
            rs2_addr=[0, 0, 0, 1, 0],
            rd_addr=[0, 0, 0, 1, 1]
        )
        
        # Track state progression
        states_seen = [cu.fpu_state]
        
        # Tick through all states
        done = False
        while not done:
            done = cu.tick()
            states_seen.append(cu.fpu_state)
        
        # Verify state sequence: ALIGN → OP → NORMALIZE → ROUND → WRITEBACK → IDLE
        assert FPU_STATE_ALIGN in states_seen
        assert FPU_STATE_OP in states_seen
        assert FPU_STATE_NORMALIZE in states_seen
        assert FPU_STATE_ROUND in states_seen
        assert FPU_STATE_WRITEBACK in states_seen
        assert cu.fpu_state == FPU_STATE_IDLE
        assert cu.is_idle()


class TestControlUnitTrace:
    """Test Control Unit trace functionality."""
    
    def test_trace_collection(self):
        """Test that traces are collected during operation."""
        cu = ControlUnit()
        
        cu.start_alu_operation(
            alu_op=ALU_OP_ADD,
            rs1_addr=[0, 0, 0, 0, 1],
            rs2_addr=[0, 0, 0, 1, 0],
            rd_addr=[0, 0, 0, 1, 1]
        )
        
        initial_trace_len = len(cu.trace)
        assert initial_trace_len > 0
        
        # Run to completion
        while not cu.tick():
            pass
        
        # Trace should have grown
        assert len(cu.trace) > initial_trace_len
    
    def test_trace_content(self):
        """Test trace content structure."""
        cu = ControlUnit()
        
        cu.start_alu_operation(
            alu_op=ALU_OP_ADD,
            rs1_addr=[0, 0, 0, 0, 1],
            rs2_addr=[0, 0, 0, 1, 0],
            rd_addr=[0, 0, 0, 1, 1]
        )
        
        trace = cu.get_trace()
        
        assert len(trace) > 0
        for entry in trace:
            assert 'cycle' in entry
            assert 'message' in entry
            assert 'signals' in entry
            assert isinstance(entry['signals'], ControlSignals)
    
    def test_trace_reset(self):
        """Test that reset clears trace."""
        cu = ControlUnit()
        
        cu.start_alu_operation(
            alu_op=ALU_OP_ADD,
            rs1_addr=[0, 0, 0, 0, 1],
            rs2_addr=[0, 0, 0, 1, 0],
            rd_addr=[0, 0, 0, 1, 1]
        )
        
        assert len(cu.trace) > 0
        
        cu.reset()
        
        assert len(cu.trace) == 0


class TestControlUnitErrorHandling:
    """Test Control Unit error handling."""
    
    def test_cannot_start_operation_when_busy(self):
        """Test that starting an operation when busy raises error."""
        cu = ControlUnit()
        
        cu.start_alu_operation(
            alu_op=ALU_OP_ADD,
            rs1_addr=[0, 0, 0, 0, 1],
            rs2_addr=[0, 0, 0, 1, 0],
            rd_addr=[0, 0, 0, 1, 1]
        )
        
        # Try to start another operation while first is running
        with pytest.raises(AssertionError):
            cu.start_alu_operation(
                alu_op=ALU_OP_SUB,
                rs1_addr=[0, 0, 0, 0, 1],
                rs2_addr=[0, 0, 0, 1, 0],
                rd_addr=[0, 0, 0, 1, 1]
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
# AI-END
