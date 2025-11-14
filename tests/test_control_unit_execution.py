"""
Test Control Unit Complete Instruction Execution (Phase 6)

Tests for the unified instruction execution interface:
- execute_instruction() - main high-level interface
- execute_and_get_result() - convenience method for result only
- execute_and_get_trace() - convenience method for trace only
- execute_with_timeout() - safety wrapper with timeout
"""

import pytest
from riscsim.cpu.control_unit import ControlUnit
from riscsim.cpu.registers import RegisterFile
from riscsim.cpu.control_signals import (
    ALU_OP_ADD, ALU_OP_SUB,
    SH_OP_SLL, SH_OP_SRL, SH_OP_SRA
)


def int_to_5bit(n: int):
    """Convert integer to 5-bit register address"""
    return [int(b) for b in format(n & 0x1F, '05b')]


def int_to_32bit(n: int):
    """Convert integer to 32-bit array"""
    if n < 0:
        n = (1 << 32) + n
    return [int(b) for b in format(n & 0xFFFFFFFF, '032b')]


def bits_to_int(bits):
    """Convert bit array to integer"""
    result = 0
    for bit in bits:
        result = (result << 1) | bit
    if len(bits) == 32 and bits[0] == 1:
        result = result - (1 << 32)
    return result


class TestUnifiedInstructionExecution:
    """Test unified execute_instruction() interface"""
    
    def test_execute_alu_add_instruction(self):
        """Test execute_instruction with ALU ADD operation"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup: r1 = 10, r2 = 20
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(20))
        
        # Execute: r3 = r1 + r2
        result = cu.execute_instruction(
            'ALU',
            ALU_OP_ADD,
            int_to_5bit(1),  # rs1
            int_to_5bit(2),  # rs2
            int_to_5bit(3)   # rd
        )
        
        assert result['success'] is True
        assert result['cycles'] == 2  # ALU takes 2 cycles
        assert bits_to_int(result['result']) == 30
        
        # Verify register was written
        r3 = rf.read_int_reg(int_to_5bit(3))
        assert bits_to_int(r3) == 30
    
    def test_execute_shifter_sll_instruction(self):
        """Test execute_instruction with Shifter SLL operation"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup: r1 = 8
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(8))
        
        # Execute: r2 = r1 << 3 (8 << 3 = 64)
        result = cu.execute_instruction(
            'SHIFTER',
            SH_OP_SLL,
            int_to_5bit(1),  # rs1
            rd_addr=int_to_5bit(2),  # rd
            shamt=int_to_5bit(3)  # shift by 3
        )
        
        assert result['success'] is True
        assert result['cycles'] == 2  # Shifter takes 2 cycles
        assert bits_to_int(result['result']) == 64
        
        # Verify register was written
        r2 = rf.read_int_reg(int_to_5bit(2))
        assert bits_to_int(r2) == 64
    
    def test_execute_mdu_mul_instruction(self):
        """Test execute_instruction with MDU MUL operation"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup: r1 = 7, r2 = 6
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(7))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(6))
        
        # Execute: r3 = r1 * r2 (7 * 6 = 42)
        result = cu.execute_instruction(
            'MDU',
            'MUL',
            int_to_5bit(1),  # rs1
            int_to_5bit(2),  # rs2
            int_to_5bit(3)   # rd
        )
        
        assert result['success'] is True
        assert result['cycles'] == 33  # MDU takes 32 cycles + writeback
        assert bits_to_int(result['result']) == 42
        
        # Verify register was written
        r3 = rf.read_int_reg(int_to_5bit(3))
        assert bits_to_int(r3) == 42
    
    def test_execute_mdu_div_instruction(self):
        """Test execute_instruction with MDU DIV operation"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup: r1 = 50, r2 = 7
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(50))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(7))
        
        # Execute: r3 = r1 / r2 (50 / 7 = 7, remainder 1)
        result = cu.execute_instruction(
            'MDU',
            'DIV',
            int_to_5bit(1),  # rs1
            int_to_5bit(2),  # rs2
            int_to_5bit(3)   # rd
        )
        
        assert result['success'] is True
        assert result['cycles'] == 33  # MDU takes 32 cycles + writeback
        assert bits_to_int(result['result']) == 7  # quotient
        
        # Verify quotient and remainder are available
        assert 'quotient' in result
        assert 'remainder' in result
    
    def test_execute_fpu_fadd_instruction(self):
        """Test execute_instruction with FPU FADD operation"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup FP registers: f1 = 1.5, f2 = 2.5
        # 1.5 = 0x3FC00000
        f1_bits = [0] + [0,1,1,1,1,1,1,1] + [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        # 2.5 = 0x40200000
        f2_bits = [0] + [1,0,0,0,0,0,0,0] + [0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        
        rf.write_fp_reg(int_to_5bit(1), f1_bits)
        rf.write_fp_reg(int_to_5bit(2), f2_bits)
        
        # Execute: f3 = f1 + f2 (1.5 + 2.5 = 4.0)
        result = cu.execute_instruction(
            'FPU',
            'FADD',
            int_to_5bit(1),  # rs1
            int_to_5bit(2),  # rs2
            int_to_5bit(3),  # rd
            rounding_mode=[0, 0, 0]
        )
        
        assert result['success'] is True
        assert result['cycles'] == 5  # FPU takes 5 cycles
        
        # Verify FP register was written (4.0 = 0x40800000)
        f3 = rf.read_fp_reg(int_to_5bit(3))
        expected_4_0 = [0] + [1,0,0,0,0,0,0,1] + [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        assert f3 == expected_4_0
    
    def test_execute_with_trace(self):
        """Test that execute_instruction returns full trace"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(5))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(3))
        
        # Execute ADD
        result = cu.execute_instruction('ALU', ALU_OP_ADD,
                                       int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        # Verify trace exists and has content
        assert 'trace' in result
        assert len(result['trace']) > 0
        # Trace includes start message + execution cycles
        assert len(result['trace']) >= result['cycles']
    
    def test_mixed_instruction_sequence(self):
        """Test executing multiple different instruction types in sequence"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup initial values
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(5))
        
        # 1. ALU: r3 = r1 + r2 (10 + 5 = 15)
        result1 = cu.execute_instruction('ALU', ALU_OP_ADD,
                                        int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        assert result1['success']
        assert bits_to_int(result1['result']) == 15
        
        # 2. Shifter: r4 = r3 << 2 (15 << 2 = 60)
        result2 = cu.execute_instruction('SHIFTER', SH_OP_SLL,
                                        int_to_5bit(3), rd_addr=int_to_5bit(4),
                                        shamt=int_to_5bit(2))
        assert result2['success']
        assert bits_to_int(result2['result']) == 60
        
        # 3. MDU: r5 = r4 * r2 (60 * 5 = 300)
        result3 = cu.execute_instruction('MDU', 'MUL',
                                        int_to_5bit(4), int_to_5bit(2), int_to_5bit(5))
        assert result3['success']
        assert bits_to_int(result3['result']) == 300
        
        # Verify all results in register file
        assert bits_to_int(rf.read_int_reg(int_to_5bit(3))) == 15
        assert bits_to_int(rf.read_int_reg(int_to_5bit(4))) == 60
        assert bits_to_int(rf.read_int_reg(int_to_5bit(5))) == 300


class TestConvenienceMethods:
    """Test convenience methods for instruction execution"""
    
    def test_execute_and_get_result(self):
        """Test execute_and_get_result returns only the result"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(15))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(7))
        
        # Execute and get result directly
        result = cu.execute_and_get_result('ALU', ALU_OP_SUB,
                                          int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        # Should return 32-bit array
        assert len(result) == 32
        assert bits_to_int(result) == 8  # 15 - 7 = 8
    
    def test_execute_and_get_result_failure(self):
        """Test execute_and_get_result raises error on failure"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        
        # Try to execute with timeout = 0 (will fail)
        with pytest.raises(RuntimeError, match="Instruction failed to complete"):
            cu.execute_and_get_result('ALU', ALU_OP_ADD,
                                     int_to_5bit(1), int_to_5bit(1), int_to_5bit(2),
                                     max_cycles=0)
    
    def test_execute_and_get_trace(self):
        """Test execute_and_get_trace returns only the trace"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(5))
        
        # Execute and get trace
        trace = cu.execute_and_get_trace('MDU', 'MUL',
                                        int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        # Should return list of trace entries
        assert isinstance(trace, list)
        # MDU takes 33 cycles, trace includes start + all cycle messages
        assert len(trace) >= 33
        
        # Each entry should have trace information
        for entry in trace:
            assert isinstance(entry, dict)
    
    def test_execute_with_timeout(self):
        """Test execute_with_timeout adds timeout protection"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(100))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(7))
        
        # Execute with reasonable timeout
        result = cu.execute_with_timeout('MDU', 'DIV',
                                        int_to_5bit(1), int_to_5bit(2), int_to_5bit(3),
                                        timeout_cycles=50)
        
        assert result['success'] is True
        assert result['timed_out'] is False
        assert result['cycles'] == 33
        assert bits_to_int(result['result']) == 14  # 100 / 7 = 14
    
    def test_execute_with_timeout_exceeded(self):
        """Test execute_with_timeout detects timeout"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(5))
        
        # Execute with insufficient timeout for MDU (needs 33 cycles)
        result = cu.execute_with_timeout('MDU', 'MUL',
                                        int_to_5bit(1), int_to_5bit(2), int_to_5bit(3),
                                        timeout_cycles=10)
        
        assert result['success'] is False
        assert result['timed_out'] is True
        assert result['cycles'] == 10  # Stopped at timeout


class TestInstructionDecoding:
    """Test instruction decoding and routing"""
    
    def test_invalid_operation_type(self):
        """Test that invalid operation type raises error"""
        cu = ControlUnit()
        
        with pytest.raises(ValueError, match="Unknown operation type"):
            cu.execute_instruction('INVALID', ALU_OP_ADD,
                                 int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
    
    def test_shifter_requires_shamt(self):
        """Test that shifter operations require shamt parameter"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        
        # Try shifter without shamt - should fail
        with pytest.raises(AssertionError, match="Shifter operations require shamt"):
            cu.execute_instruction('SHIFTER', SH_OP_SLL,
                                 int_to_5bit(1), rd_addr=int_to_5bit(2))
    
    def test_must_be_idle_before_execute(self):
        """Test that control unit must be idle before executing"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(5))
        
        # Start an operation manually
        cu.start_alu_operation(ALU_OP_ADD, int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        # Try to execute another instruction - should fail
        with pytest.raises(AssertionError, match="Control unit must be idle"):
            cu.execute_instruction('ALU', ALU_OP_SUB,
                                 int_to_5bit(1), int_to_5bit(2), int_to_5bit(4))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
