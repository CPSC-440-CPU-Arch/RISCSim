"""
Comprehensive Control Unit Integration Tests

Tests the complete Control Unit with all functional units (ALU, Shifter, MDU, FPU)
to validate end-to-end operation sequences, state transitions, and data path integrity.
"""

import pytest
from riscsim.cpu.control_unit import ControlUnit
from riscsim.cpu.registers import RegisterFile
from riscsim.cpu.control_signals import (
    ALU_OP_ADD, ALU_OP_SUB, ALU_OP_AND, ALU_OP_OR, ALU_OP_XOR,
    SH_OP_SLL, SH_OP_SRL, SH_OP_SRA
)


def int_to_5bit(n: int):
    """Convert integer to 5-bit register address"""
    return [int(b) for b in format(n & 0x1F, '05b')]


def int_to_32bit(n: int):
    """Convert integer to 32-bit array"""
    if n < 0:
        n = (1 << 32) + n  # Two's complement
    return [int(b) for b in format(n & 0xFFFFFFFF, '032b')]


def bits_to_int(bits):
    """Convert bit array to integer"""
    result = 0
    for bit in bits:
        result = (result << 1) | bit
    # Check if negative (sign bit is 1)
    if len(bits) == 32 and bits[0] == 1:
        result = result - (1 << 32)
    return result


class TestComprehensiveControlUnit:
    """Comprehensive tests for the fully integrated Control Unit"""
    
    def test_sequential_operations_all_units(self):
        """Test executing operations from all functional units in sequence"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # 1. ALU Operation: r3 = r1 + r2 (10 + 20 = 30)
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(20))
        
        result = cu.execute_alu_instruction(
            ALU_OP_ADD,
            int_to_5bit(1),  # rs1
            int_to_5bit(2),  # rs2
            int_to_5bit(3)   # rd
        )
        
        assert result['success'] is True
        r3_value = rf.read_int_reg(int_to_5bit(3))
        assert r3_value == int_to_32bit(30), f"Expected 30, got {bits_to_int(r3_value)}"
        
        # 2. Shifter Operation: r5 = r3 << 2 (30 << 2 = 120)
        result = cu.execute_shifter_instruction(
            SH_OP_SLL,
            int_to_5bit(3),  # rs1
            int_to_5bit(2),  # shamt
            int_to_5bit(5)   # rd
        )
        
        assert result['success'] is True
        r5_value = rf.read_int_reg(int_to_5bit(5))
        assert r5_value == int_to_32bit(120), f"Expected 120, got {bits_to_int(r5_value)}"
        
        # 3. MDU Operation: r7 = r5 * r3 (120 * 30 = 3600)
        result = cu.execute_mdu_instruction(
            "MUL",  # MDU operation
            int_to_5bit(5),  # rs1
            int_to_5bit(3),  # rs2
            int_to_5bit(7)   # rd
        )
        
        assert result['success'] is True
        assert result['cycles'] == 33  # MDU takes 32 cycles + 1 writeback
        r7_value = rf.read_int_reg(int_to_5bit(7))
        assert r7_value == int_to_32bit(3600), f"Expected 3600, got {bits_to_int(r7_value)}"
        
        # 4. FPU Operation: f2 = f0 + f1 (1.5 + 2.5 = 4.0)
        # IEEE-754: 1.5 = 0x3FC00000
        f0_bits = [0] + [0,1,1,1,1,1,1,1] + [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        # IEEE-754: 2.5 = 0x40200000
        f1_bits = [0] + [1,0,0,0,0,0,0,0] + [0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        
        rf.write_fp_reg(int_to_5bit(0), f0_bits)
        rf.write_fp_reg(int_to_5bit(1), f1_bits)
        
        result = cu.execute_fpu_instruction(
            "FADD",  # FPU operation
            int_to_5bit(0),  # rs1
            int_to_5bit(1),  # rs2
            int_to_5bit(2),  # rd
            [0, 0, 0]  # round_mode = RNE
        )
        
        assert result['success'] is True
        assert result['cycles'] == 5  # FPU takes 5 cycles
        f2_value = rf.read_fp_reg(int_to_5bit(2))
        # IEEE-754: 4.0 = 0x40800000
        expected_4_0 = [0] + [1,0,0,0,0,0,0,1] + [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        assert f2_value == expected_4_0, f"Expected 4.0, got {f2_value}"
        
        # Verify all units returned to IDLE state
        assert cu.state == cu.STATE_IDLE
        assert cu.current_op_type is None
    
    
    def test_complex_computation_sequence(self):
        """Test a complex sequence: (a + b) * (c - d) >> 2"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup registers: a=8, b=4, c=20, d=5
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(8))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(4))
        rf.write_int_reg(int_to_5bit(3), int_to_32bit(20))
        rf.write_int_reg(int_to_5bit(4), int_to_32bit(5))
        
        # Step 1: r10 = r1 + r2 (8 + 4 = 12)
        cu.execute_alu_instruction(ALU_OP_ADD, int_to_5bit(1), int_to_5bit(2), int_to_5bit(10))
        r10 = rf.read_int_reg(int_to_5bit(10))
        assert bits_to_int(r10) == 12, "Expected r10 = 12"
        
        # Step 2: r11 = r3 - r4 (20 - 5 = 15)
        cu.execute_alu_instruction(ALU_OP_SUB, int_to_5bit(3), int_to_5bit(4), int_to_5bit(11))
        r11 = rf.read_int_reg(int_to_5bit(11))
        assert bits_to_int(r11) == 15, "Expected r11 = 15"
        
        # Step 3: r12 = r10 * r11 (12 * 15 = 180)
        cu.execute_mdu_instruction("MUL", int_to_5bit(10), int_to_5bit(11), int_to_5bit(12))
        r12 = rf.read_int_reg(int_to_5bit(12))
        assert bits_to_int(r12) == 180, "Expected r12 = 180"
        
        # Step 4: r13 = r12 >> 2 (180 >> 2 = 45)
        cu.execute_shifter_instruction(SH_OP_SRL, int_to_5bit(12), int_to_5bit(2), int_to_5bit(13))
        r13 = rf.read_int_reg(int_to_5bit(13))
        assert bits_to_int(r13) == 45, "Expected r13 = 45"
    
    
    def test_register_isolation(self):
        """Test that operations don't corrupt unrelated registers"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup: Write known values to r1-r5
        for i in range(1, 6):
            rf.write_int_reg(int_to_5bit(i), int_to_32bit(i * 100))
        
        # Perform operation on r1, r2 -> r3
        cu.execute_alu_instruction(ALU_OP_ADD, int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
        
        # Verify r1 and r2 are unchanged
        assert bits_to_int(rf.read_int_reg(int_to_5bit(1))) == 100, "r1 should be unchanged"
        assert bits_to_int(rf.read_int_reg(int_to_5bit(2))) == 200, "r2 should be unchanged"
        
        # Verify r4 and r5 are unchanged
        assert bits_to_int(rf.read_int_reg(int_to_5bit(4))) == 400, "r4 should be unchanged"
        assert bits_to_int(rf.read_int_reg(int_to_5bit(5))) == 500, "r5 should be unchanged"
        
        # Verify r3 was modified to 300 (100 + 200)
        assert bits_to_int(rf.read_int_reg(int_to_5bit(3))) == 300, "r3 should have been modified to 300"
    
    
    def test_zero_register_immutability(self):
        """Test that r0 always reads as zero"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Try to write to r0
        rf.write_int_reg(int_to_5bit(0), int_to_32bit(999))
        
        # Read back - should still be zero
        r0 = rf.read_int_reg(int_to_5bit(0))
        assert r0 == [0]*32, "r0 should always be zero"
        
        # Try to use r0 as destination in ALU
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(20))
        cu.execute_alu_instruction(ALU_OP_ADD, int_to_5bit(1), int_to_5bit(2), int_to_5bit(0))
        
        # r0 should still be zero
        r0 = rf.read_int_reg(int_to_5bit(0))
        assert r0 == [0]*32, "r0 should remain zero even when used as destination"
    
    
    def test_interleaved_integer_and_fp_operations(self):
        """Test that integer and FP operations maintain separate register spaces"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup: Write same pattern to both r10 and f10
        test_pattern = [1,0,1,0] + [0]*28
        rf.write_int_reg(int_to_5bit(10), test_pattern)
        rf.write_fp_reg(int_to_5bit(10), test_pattern)
        
        # Integer operation on r10: r11 = r10 + 100
        rf.write_int_reg(int_to_5bit(12), int_to_32bit(100))
        cu.execute_alu_instruction(ALU_OP_ADD, int_to_5bit(10), int_to_5bit(12), int_to_5bit(11))
        
        # FP operation on f10: f11 = f10 * 2.0
        # IEEE-754: 2.0 = 0x40000000
        f13_bits = [0] + [1,0,0,0,0,0,0,0] + [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        rf.write_fp_reg(int_to_5bit(13), f13_bits)
        cu.execute_fpu_instruction("FMUL", int_to_5bit(10), int_to_5bit(13), int_to_5bit(11), [0, 0, 0])
        
        # Verify: f10 should be unchanged by integer operation
        assert rf.read_fp_reg(int_to_5bit(10)) == test_pattern, "f10 should be unchanged"
        
        # Verify: r10 should be unchanged by FP operation
        assert rf.read_int_reg(int_to_5bit(10)) == test_pattern, "r10 should be unchanged"
        
        # Verify: r11 and f11 have different values
        r11 = rf.read_int_reg(int_to_5bit(11))
        f11 = rf.read_fp_reg(int_to_5bit(11))
        assert r11 != f11, "Integer and FP register spaces should be independent"
    
    
    def test_all_functional_units_cycle_counts(self):
        """Verify that each functional unit takes the expected number of cycles"""
        rf = RegisterFile()
        cu = ControlUnit(register_file=rf)
        
        # Setup operands
        rf.write_int_reg(int_to_5bit(1), int_to_32bit(10))
        rf.write_int_reg(int_to_5bit(2), int_to_32bit(5))
        
        # ALU: Should take 2 cycles (EXECUTE + WRITEBACK)
        result = cu.execute_alu_instruction(ALU_OP_ADD, int_to_5bit(1), int_to_5bit(2), int_to_5bit(10))
        assert result['cycles'] == 2, "ALU should take 2 cycles"
        
        # Shifter: Should take 2 cycles (EXECUTE + WRITEBACK)
        result = cu.execute_shifter_instruction(SH_OP_SLL, int_to_5bit(1), int_to_5bit(2), int_to_5bit(11))
        assert result['cycles'] == 2, "Shifter should take 2 cycles"
        
        # MDU: Should take 33 cycles (32 cycle operation + 1 writeback)
        result = cu.execute_mdu_instruction("MUL", int_to_5bit(1), int_to_5bit(2), int_to_5bit(12))
        assert result['cycles'] == 33, "MDU should take 33 cycles (32 + writeback)"
        
        # FPU: Should take 5 cycles (5-stage pipeline)
        f1 = [0] + [0,1,1,1,1,1,1,1] + [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]  # 1.5
        f2 = [0] + [1,0,0,0,0,0,0,0] + [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]  # 2.0
        rf.write_fp_reg(int_to_5bit(1), f1)
        rf.write_fp_reg(int_to_5bit(2), f2)
        result = cu.execute_fpu_instruction("FADD", int_to_5bit(1), int_to_5bit(2), int_to_5bit(10), [0, 0, 0])
        assert result['cycles'] == 5, "FPU should take 5 cycles"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
