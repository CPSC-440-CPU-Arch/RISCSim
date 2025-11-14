# AI-BEGIN
"""
Test Control Unit Data Path Infrastructure (Phase 1)

Tests for data path components of the Control Unit:
- Operand storage
- Multiplexer selection
- Register file integration
- Result selection
"""

import pytest
from riscsim.cpu.control_unit import ControlUnit
from riscsim.cpu.registers import RegisterFile
from riscsim.cpu.control_signals import ALU_OP_ADD


class TestControlUnitDataPath:
    """Test data path infrastructure in Control Unit."""
    
    def test_operand_storage(self):
        """Test that Control Unit can store operand values."""
        cu = ControlUnit()
        
        # Initially should be zeros
        assert cu.operand_a == [0] * 32
        assert cu.operand_b == [0] * 32
        assert cu.immediate == [0] * 32
        
        # Manually set operands
        cu.operand_a = [0, 0, 0, 0, 1, 0, 1, 0] + [0] * 24  # 42
        cu.operand_b = [0, 0, 1, 0, 1, 0, 0, 0] + [0] * 24  # 20
        cu.immediate = [1, 1, 1, 1, 1, 1, 1, 1] + [0] * 24  # 255
        
        assert cu.operand_a == [0, 0, 0, 0, 1, 0, 1, 0] + [0] * 24
        assert cu.operand_b == [0, 0, 1, 0, 1, 0, 0, 0] + [0] * 24
        assert cu.immediate == [1, 1, 1, 1, 1, 1, 1, 1] + [0] * 24
        
        # Test reset clears them
        cu.reset()
        assert cu.operand_a == [0] * 32
        assert cu.operand_b == [0] * 32
        assert cu.immediate == [0] * 32
    
    def test_src_a_multiplexer(self):
        """Test source A multiplexer selection."""
        cu = ControlUnit()
        
        # Set up test data
        cu.operand_a = [0, 0, 0, 0, 1, 0, 1, 0] + [0] * 24  # 42
        cu.immediate = [1, 1, 1, 1, 1, 1, 1, 1] + [0] * 24  # 255
        
        # src_a_sel = 0: select register
        cu.signals.src_a_sel = 0
        result = cu._select_operand_a()
        assert result == [0, 0, 0, 0, 1, 0, 1, 0] + [0] * 24
        
        # src_a_sel = 1: select immediate
        cu.signals.src_a_sel = 1
        result = cu._select_operand_a()
        assert result == [1, 1, 1, 1, 1, 1, 1, 1] + [0] * 24
        
        # src_a_sel = 2: select PC (not implemented, should return zeros)
        cu.signals.src_a_sel = 2
        result = cu._select_operand_a()
        assert result == [0] * 32
    
    def test_src_b_multiplexer(self):
        """Test source B multiplexer selection."""
        cu = ControlUnit()
        
        # Set up test data
        cu.operand_b = [0, 0, 1, 0, 1, 0, 0, 0] + [0] * 24  # 20
        cu.immediate = [1, 1, 1, 1, 1, 1, 1, 1] + [0] * 24  # 255
        
        # src_b_sel = 0: select register
        cu.signals.src_b_sel = 0
        result = cu._select_operand_b()
        assert result == [0, 0, 1, 0, 1, 0, 0, 0] + [0] * 24
        
        # src_b_sel = 1: select immediate
        cu.signals.src_b_sel = 1
        result = cu._select_operand_b()
        assert result == [1, 1, 1, 1, 1, 1, 1, 1] + [0] * 24
        
        # src_b_sel = 2: select constant (4)
        cu.signals.src_b_sel = 2
        result = cu._select_operand_b()
        assert result == [0, 0, 1, 0, 0] + [0] * 27  # 4
    
    def test_register_read_integration(self):
        """Test reading from register file into operands."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Write some values to registers
        rf.write_int_reg([0, 0, 1, 0, 1], [0, 0, 0, 0, 1, 0, 1, 0] + [0] * 24)  # r5 = 42
        rf.write_int_reg([0, 0, 1, 1, 0], [0, 0, 1, 0, 1, 0, 0, 0] + [0] * 24)  # r6 = 20
        
        # Set control signals to read r5 and r6
        cu.signals.rf_raddr_a = [0, 0, 1, 0, 1]  # r5
        cu.signals.rf_raddr_b = [0, 0, 1, 1, 0]  # r6
        
        # Read registers
        cu._read_registers()
        
        # Check operands were loaded correctly
        assert cu.operand_a == [0, 0, 0, 0, 1, 0, 1, 0] + [0] * 24  # 42
        assert cu.operand_b == [0, 0, 1, 0, 1, 0, 0, 0] + [0] * 24  # 20
    
    def test_register_write_integration(self):
        """Test writing result to register file."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Set up writeback data and control signals
        cu.writeback_data = [0, 0, 1, 1, 1, 1, 0, 0] + [0] * 24  # 60
        cu.signals.rf_waddr = [0, 0, 1, 1, 1]  # r7
        cu.signals.rf_we = 1  # Enable write
        
        # Write to register
        cu._write_register()
        
        # Verify register was written
        result = rf.read_int_reg([0, 0, 1, 1, 1])  # Read r7
        assert result == [0, 0, 1, 1, 1, 1, 0, 0] + [0] * 24
        
        # Test that write doesn't happen when rf_we = 0
        cu.writeback_data = [1, 1, 1, 1, 1, 1, 1, 1] + [0] * 24  # 255
        cu.signals.rf_waddr = [0, 1, 0, 0, 0]  # r8
        cu.signals.rf_we = 0  # Disable write
        
        cu._write_register()
        
        # r8 should still be zero
        result = rf.read_int_reg([0, 1, 0, 0, 0])
        assert result == [0] * 32
    
    def test_result_multiplexer(self):
        """Test result multiplexer selects correct functional unit output."""
        cu = ControlUnit()
        
        # Set up different results
        cu.alu_result = [0, 0, 0, 0, 1, 0, 1, 0] + [0] * 24  # 42
        cu.shifter_result = [0, 0, 1, 0, 1, 0, 0, 0] + [0] * 24  # 20
        cu.mdu_result = [0, 0, 1, 1, 1, 1, 0, 0] + [0] * 24  # 60
        cu.fpu_result = [1, 1, 1, 1, 1, 1, 1, 1] + [0] * 24  # 255
        
        # Select ALU result
        cu.current_op_type = cu.OP_ALU
        result = cu._select_result()
        assert result == [0, 0, 0, 0, 1, 0, 1, 0] + [0] * 24
        
        # Select Shifter result
        cu.current_op_type = cu.OP_SHIFTER
        result = cu._select_result()
        assert result == [0, 0, 1, 0, 1, 0, 0, 0] + [0] * 24
        
        # Select MDU result
        cu.current_op_type = cu.OP_MDU
        result = cu._select_result()
        assert result == [0, 0, 1, 1, 1, 1, 0, 0] + [0] * 24
        
        # Select FPU result
        cu.current_op_type = cu.OP_FPU
        result = cu._select_result()
        assert result == [1, 1, 1, 1, 1, 1, 1, 1] + [0] * 24
        
        # Unknown operation type should return zeros
        cu.current_op_type = 'UNKNOWN'
        result = cu._select_result()
        assert result == [0] * 32
    
    def test_immediate_value_setting(self):
        """Test setting immediate values for I-type instructions."""
        cu = ControlUnit()
        
        # Set immediate value
        imm_value = [0, 0, 0, 1, 0, 0, 1, 0] + [0] * 24  # 18
        cu.set_immediate(imm_value)
        
        assert cu.immediate == imm_value
        
        # Test getter methods
        assert cu.get_operand_a() == [0] * 32
        assert cu.get_operand_b() == [0] * 32
        assert cu.get_writeback_data() == [0] * 32
        
        # Modify and check getters return copies
        cu.operand_a = [1] * 32
        assert cu.get_operand_a() == [1] * 32
        retrieved = cu.get_operand_a()
        retrieved[0] = 0
        assert cu.operand_a[0] == 1  # Original unchanged
    
    def test_data_path_with_register_file_integration(self):
        """Test complete data path flow with register file."""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Initialize registers
        rf.write_int_reg([0, 0, 0, 0, 1], [0, 0, 0, 1, 0, 1, 0, 0] + [0] * 24)  # r1 = 10
        rf.write_int_reg([0, 0, 0, 1, 0], [0, 0, 0, 1, 1, 1, 1, 0] + [0] * 24)  # r2 = 15
        
        # Configure to read r1 and r2
        cu.signals.rf_raddr_a = [0, 0, 0, 0, 1]
        cu.signals.rf_raddr_b = [0, 0, 0, 1, 0]
        
        # Read operands
        cu._read_registers()
        
        assert cu.operand_a == [0, 0, 0, 1, 0, 1, 0, 0] + [0] * 24  # 10
        assert cu.operand_b == [0, 0, 0, 1, 1, 1, 1, 0] + [0] * 24  # 15
        
        # Simulate ALU operation (10 + 15 = 25)
        cu.current_op_type = cu.OP_ALU
        cu.alu_result = [0, 0, 0, 1, 1, 0, 0, 1] + [0] * 24  # 25
        
        # Select result and prepare writeback
        cu.writeback_data = cu._select_result()
        assert cu.writeback_data == [0, 0, 0, 1, 1, 0, 0, 1] + [0] * 24
        
        # Write back to r3
        cu.signals.rf_waddr = [0, 0, 0, 1, 1]  # r3
        cu.signals.rf_we = 1
        cu._write_register()
        
        # Verify r3 has the result
        result = rf.read_int_reg([0, 0, 0, 1, 1])
        assert result == [0, 0, 0, 1, 1, 0, 0, 1] + [0] * 24  # 25
# AI-END
