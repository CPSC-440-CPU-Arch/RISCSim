# AI-BEGIN
"""
Test Control Unit FPU Integration (Phase 5)

Tests for cycle-accurate FPU execution through the Control Unit:
- Multi-stage FPU operations (FADD, FSUB, FMUL)
- Pipeline stage transitions (ALIGN → OP → NORMALIZE → ROUND → WRITEBACK)
- Rounding mode handling
- Exception flag propagation
- Register file integration with FP results
"""

import pytest
from riscsim.cpu.control_unit import ControlUnit
from riscsim.cpu.registers import RegisterFile


class TestControlUnitFPU:
    """Test FPU integration with Control Unit."""
    
    def test_fadd_align_stage(self):
        """Test FPU FADD starts in ALIGN stage."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Write float values to FP registers
        # f1 = 1.0 (0x3F800000), f2 = 2.0 (0x40000000)
        rf.write_fp_reg([0,0,0,0,1], [0,0,1,1,1,1,1,1,1] + [0]*23)  # 1.0
        rf.write_fp_reg([0,0,0,1,0], [0,1,0,0,0,0,0,0,0] + [0]*23)  # 2.0
        
        # Start FADD operation
        cu.start_fpu_operation("FADD", [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1])
        
        # Import FPU state constants
        from riscsim.cpu.control_signals import FPU_STATE_ALIGN
        
        # Should start in ALIGN state
        assert cu.fpu_state == FPU_STATE_ALIGN
        assert cu.signals.fpu_state == FPU_STATE_ALIGN
    
    def test_fadd_op_stage(self):
        """Test FPU transitions from ALIGN to OP stage."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        rf.write_fp_reg([0,0,0,0,1], [0,0,1,1,1,1,1,1,1] + [0]*23)  # 1.0
        rf.write_fp_reg([0,0,0,1,0], [0,1,0,0,0,0,0,0,0] + [0]*23)  # 2.0
        
        cu.start_fpu_operation("FADD", [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1])
        
        # Import FPU state constants
        from riscsim.cpu.control_signals import FPU_STATE_OP
        
        # First tick: ALIGN → OP
        complete = cu.tick()
        assert not complete
        assert cu.fpu_state == FPU_STATE_OP
        assert cu.signals.fpu_state == FPU_STATE_OP
    
    def test_fadd_normalize_stage(self):
        """Test FPU transitions through NORMALIZE stage."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        rf.write_fp_reg([0,0,0,0,1], [0,0,1,1,1,1,1,1,1] + [0]*23)  # 1.0
        rf.write_fp_reg([0,0,0,1,0], [0,1,0,0,0,0,0,0,0] + [0]*23)  # 2.0
        
        cu.start_fpu_operation("FADD", [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1])
        
        # Import FPU state constants
        from riscsim.cpu.control_signals import FPU_STATE_NORMALIZE
        
        # Tick through ALIGN → OP
        cu.tick()
        
        # Second tick: OP → NORMALIZE
        complete = cu.tick()
        assert not complete
        assert cu.fpu_state == FPU_STATE_NORMALIZE
        assert cu.signals.fpu_state == FPU_STATE_NORMALIZE
    
    def test_fadd_round_stage(self):
        """Test FPU transitions through ROUND stage."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        rf.write_fp_reg([0,0,0,0,1], [0,0,1,1,1,1,1,1,1] + [0]*23)  # 1.0
        rf.write_fp_reg([0,0,0,1,0], [0,1,0,0,0,0,0,0,0] + [0]*23)  # 2.0
        
        cu.start_fpu_operation("FADD", [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1])
        
        # Import FPU state constants
        from riscsim.cpu.control_signals import FPU_STATE_ROUND
        
        # Tick through ALIGN → OP → NORMALIZE
        cu.tick()
        cu.tick()
        
        # Third tick: NORMALIZE → ROUND
        complete = cu.tick()
        assert not complete
        assert cu.fpu_state == FPU_STATE_ROUND
        assert cu.signals.fpu_state == FPU_STATE_ROUND
    
    def test_fadd_complete_pipeline(self):
        """Test FADD completes through entire pipeline."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # f1 = 1.0, f2 = 2.0 → f3 = 3.0
        rf.write_fp_reg([0,0,0,0,1], [0,0,1,1,1,1,1,1,1] + [0]*23)  # 1.0
        rf.write_fp_reg([0,0,0,1,0], [0,1,0,0,0,0,0,0,0] + [0]*23)  # 2.0
        
        # Execute complete FADD
        result = cu.execute_fpu_instruction(
            "FADD",
            [0,0,0,0,1],  # f1
            [0,0,0,1,0],  # f2
            [0,0,0,1,1]   # f3
        )
        
        assert result['success']
        # FADD pipeline: ALIGN → OP → NORMALIZE → ROUND → WRITEBACK = 5 cycles
        assert result['cycles'] == 5
        
        # Check result: 1.0 + 2.0 = 3.0 (0x40400000)
        # 3.0 = 0 10000000 10000000000000000000000
        f3 = rf.read_fp_reg([0,0,0,1,1])
        expected_3_0 = [0,1,0,0,0,0,0,0,0,1] + [0]*22
        assert f3 == expected_3_0
    
    def test_fmul_pipeline_stages(self):
        """Test FMUL goes through all pipeline stages."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # f1 = 2.0, f2 = 3.0 → f3 = 6.0
        rf.write_fp_reg([0,0,0,0,1], [0,1,0,0,0,0,0,0,0] + [0]*23)  # 2.0
        rf.write_fp_reg([0,0,0,1,0], [0,1,0,0,0,0,0,0,0,1] + [0]*22)  # 3.0
        
        result = cu.execute_fpu_instruction(
            "FMUL",
            [0,0,0,0,1],
            [0,0,0,1,0],
            [0,0,0,1,1]
        )
        
        assert result['success']
        assert result['cycles'] == 5  # Same 5-stage pipeline
        
        # Check trace shows all stages
        trace = result['trace']
        trace_str = '\n'.join([entry['message'] if isinstance(entry, dict) else entry for entry in trace])
        
        assert 'ALIGN → OP' in trace_str
        assert 'OP → NORMALIZE' in trace_str
        assert 'NORMALIZE → ROUND' in trace_str
        assert 'ROUND → WRITEBACK' in trace_str
    
    def test_fpu_state_transitions(self):
        """Test FPU state signal updates at each stage."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        rf.write_fp_reg([0,0,0,0,1], [0,0,1,1,1,1,1,1,1] + [0]*23)  # 1.0
        rf.write_fp_reg([0,0,0,1,0], [0,0,1,1,1,1,1,1,1] + [0]*23)  # 1.0
        
        # Import FPU state constants
        from riscsim.cpu.control_signals import (
            FPU_STATE_ALIGN, FPU_STATE_OP, FPU_STATE_NORMALIZE,
            FPU_STATE_ROUND, FPU_STATE_WRITEBACK, FPU_STATE_IDLE
        )
        
        cu.start_fpu_operation("FADD", [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1])
        
        # Cycle 0: ALIGN
        assert cu.fpu_state == FPU_STATE_ALIGN
        cu.tick()
        
        # Cycle 1: OP
        assert cu.fpu_state == FPU_STATE_OP
        cu.tick()
        
        # Cycle 2: NORMALIZE
        assert cu.fpu_state == FPU_STATE_NORMALIZE
        cu.tick()
        
        # Cycle 3: ROUND
        assert cu.fpu_state == FPU_STATE_ROUND
        cu.tick()
        
        # Cycle 4: WRITEBACK
        assert cu.fpu_state == FPU_STATE_WRITEBACK
        complete = cu.tick()
        
        # After completion: IDLE
        assert complete
        assert cu.fpu_state == FPU_STATE_IDLE
    
    def test_fpu_rounding_modes(self):
        """Test FPU handles different rounding modes."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Set up operands
        rf.write_fp_reg([0,0,0,0,1], [0,0,1,1,1,1,1,1,1] + [0]*23)  # 1.0
        rf.write_fp_reg([0,0,0,1,0], [0,0,1,1,1,1,1,1,1] + [0]*23)  # 1.0
        
        # Test with RNE mode (default [0,0,0])
        result_rne = cu.execute_fpu_instruction(
            "FADD",
            [0,0,0,0,1],
            [0,0,0,1,0],
            [0,0,0,1,1],
            rounding_mode=[0,0,0]
        )
        
        assert result_rne['success']
        assert cu.signals.round_mode == [0,0,0]
        
        # Test with RTZ mode [0,0,1]
        cu.reset()
        rf.write_fp_reg([0,0,0,0,1], [0,0,1,1,1,1,1,1,1] + [0]*23)  # 1.0
        rf.write_fp_reg([0,0,0,1,0], [0,0,1,1,1,1,1,1,1] + [0]*23)  # 1.0
        
        result_rtz = cu.execute_fpu_instruction(
            "FADD",
            [0,0,0,0,1],
            [0,0,0,1,0],
            [0,0,1,0,0],  # Different dest
            rounding_mode=[0,0,1]
        )
        
        assert result_rtz['success']
    
    def test_fsub_operation(self):
        """Test FSUB (subtraction) works correctly."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # f1 = 5.0 (0x40A00000), f2 = 3.0 (0x40400000) → f3 = 2.0
        # 5.0 = 0 10000001 01000000000000000000000
        rf.write_fp_reg([0,0,0,0,1], [0,1,0,0,0,0,0,0,1,0,1] + [0]*21)  # 5.0
        rf.write_fp_reg([0,0,0,1,0], [0,1,0,0,0,0,0,0,0,1] + [0]*22)  # 3.0
        
        result = cu.execute_fpu_instruction(
            "FSUB",
            [0,0,0,0,1],  # f1 = 5.0
            [0,0,0,1,0],  # f2 = 3.0
            [0,0,0,1,1]   # f3 = 2.0
        )
        
        assert result['success']
        assert result['cycles'] == 5
        
        # Result should be 2.0
        f3 = rf.read_fp_reg([0,0,0,1,1])
        # 2.0 = 0 10000000 00000000000000000000000
        expected_2_0 = [0,1,0,0,0,0,0,0,0] + [0]*23
        assert f3 == expected_2_0
    
    def test_fpu_writeback_to_register(self):
        """Test FPU results are written back to FP registers."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Multiple operations to different registers
        # f1 = 1.0, f2 = 1.0
        rf.write_fp_reg([0,0,0,0,1], [0,0,1,1,1,1,1,1,1] + [0]*23)
        rf.write_fp_reg([0,0,0,1,0], [0,0,1,1,1,1,1,1,1] + [0]*23)
        
        # f3 = f1 + f2 = 2.0
        cu.execute_fpu_instruction("FADD", [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1])
        f3 = rf.read_fp_reg([0,0,0,1,1])
        assert f3 == [0,1,0,0,0,0,0,0,0] + [0]*23  # 2.0
        
        # f4 = f1 * f2 = 1.0
        cu.reset()
        cu.execute_fpu_instruction("FMUL", [0,0,0,0,1], [0,0,0,1,0], [0,0,1,0,0])
        f4 = rf.read_fp_reg([0,0,1,0,0])
        assert f4 == [0,0,1,1,1,1,1,1,1] + [0]*23  # 1.0
        
        # Ensure source registers unchanged
        assert rf.read_fp_reg([0,0,0,0,1]) == [0,0,1,1,1,1,1,1,1] + [0]*23
        assert rf.read_fp_reg([0,0,0,1,0]) == [0,0,1,1,1,1,1,1,1] + [0]*23
# AI-END
