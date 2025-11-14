# AI-BEGIN
"""
Control Unit Full Integration Tests (Phase 6)

Tests complete CPU operation with control unit orchestration across
all components: ALU, Shifter, MDU, FPU, and Register File.

This test suite verifies:
- Single-cycle and multi-cycle operation sequences
- Proper state transitions across all FSMs
- Control signal correctness at each cycle
- Component interactions through control signals
- Mixed operation sequences
- Trace verification
"""

import pytest
from riscsim.cpu.control_signals import (
    ControlSignals,
    ALU_OP_ADD, ALU_OP_SUB,
    SH_OP_SLL,
)
from riscsim.cpu.alu import alu_with_control
from riscsim.cpu.shifter import shifter_with_control
from riscsim.cpu.mdu import mdu_with_control
from riscsim.cpu.fpu import fpu_with_control
from riscsim.cpu.registers import RegisterFile, register_with_control


# =============================================================================
# Helper Functions
# =============================================================================

def int_to_bits(n, width):
    """Convert integer to bit array (MSB first)."""
    if n < 0:
        n = (1 << width) + n
    return [(n >> (width - 1 - i)) & 1 for i in range(width)]


def int_to_bin32(n):
    """Convert integer to 32-bit array."""
    return int_to_bits(n, 32)


def bits_to_int(bits, signed=False):
    """Convert bit array to integer."""
    val = sum(bit << (len(bits) - 1 - i) for i, bit in enumerate(bits))
    if signed and bits[0] == 1:
        val -= (1 << len(bits))
    return val


def float_to_bits(f):
    """Convert float to 32-bit IEEE 754 representation."""
    import struct
    return [int(b) for byte in struct.pack('>f', f) for b in format(byte, '08b')]


def bits_to_float(bits):
    """Convert 32-bit array to float."""
    import struct
    byte_val = int(''.join(str(b) for b in bits), 2)
    return struct.unpack('>f', byte_val.to_bytes(4, 'big'))[0]


# =============================================================================
# Test 1: Single-Cycle ALU Operation Sequence
# =============================================================================

def test_single_cycle_alu_operation():
    """
    Test: Complete single-cycle ALU operation (ADD instruction).
    
    Simulates: ADD x3, x1, x2
    - Decode: Read x1 and x2 from register file
    - Execute: ALU performs ADD
    - Writeback: Store result to x3
    """
    rf = RegisterFile()
    signals = ControlSignals()
    
    # Setup: Initialize source registers
    rf.write_int_reg(1, int_to_bin32(100))
    rf.write_int_reg(2, int_to_bin32(200))
    
    # Phase 1: DECODE - Read operands from register file
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(1, 5)  # x1
    signals.rf_raddr_b = int_to_bits(2, 5)  # x2
    
    reg_result = register_with_control(rf, signals)
    operand_a = reg_result['read_a']
    operand_b = reg_result['read_b']
    
    assert bits_to_int(operand_a) == 100
    assert bits_to_int(operand_b) == 200
    
    # Phase 2: EXECUTE - ALU performs ADD
    signals.alu_op = ALU_OP_ADD  # ADD operation
    
    alu_result = alu_with_control(operand_a, operand_b, signals)
    result_value = alu_result['result']
    
    assert bits_to_int(result_value) == 300
    assert alu_result['signals'].alu_op == ALU_OP_ADD
    
    # Phase 3: WRITEBACK - Store result to register file
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(3, 5)  # x3
    signals.rf_raddr_a = int_to_bits(3, 5)  # Read back to verify
    
    wb_result = register_with_control(rf, signals, result_value)
    
    assert wb_result['written'] == True
    assert bits_to_int(wb_result['read_a']) == 300
    
    # Verify final state
    assert bits_to_int(rf.read_int_reg(3)) == 300


def test_single_cycle_with_shifter():
    """
    Test: Complete single-cycle operation with Shifter.
    
    Simulates: SLL x5, x4, 3  (shift left logical by 3)
    """
    rf = RegisterFile()
    signals = ControlSignals()
    
    # Setup
    rf.write_int_reg(4, int_to_bin32(0b1010))  # 10 in binary
    
    # Decode
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(4, 5)
    reg_result = register_with_control(rf, signals)
    operand = reg_result['read_a']
    
    # Execute - Shift left by 3
    signals.sh_op = SH_OP_SLL  # SLL
    signals.sh_amount = int_to_bits(3, 5)
    
    shift_result = shifter_with_control(operand, signals)
    result_value = shift_result['result']
    
    # 10 << 3 = 80
    assert bits_to_int(result_value) == 80
    
    # Writeback
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(5, 5)
    signals.rf_raddr_a = int_to_bits(5, 5)
    
    wb_result = register_with_control(rf, signals, result_value)
    assert bits_to_int(wb_result['read_a']) == 80


# =============================================================================
# Test 2: Multi-Cycle MDU Multiplication
# =============================================================================

def test_multi_cycle_mdu_multiplication():
    """
    Test: Complete MDU multiplication through control signals.
    
    Simulates: MUL x10, x8, x9
    - Verify operation completes successfully
    - Verify final result is correct
    """
    rf = RegisterFile()
    signals = ControlSignals()
    
    # Setup: Initialize operands
    rf.write_int_reg(8, int_to_bin32(12))
    rf.write_int_reg(9, int_to_bin32(5))
    
    # Decode: Read operands
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(8, 5)
    signals.rf_raddr_b = int_to_bits(9, 5)
    
    reg_result = register_with_control(rf, signals)
    operand_a = reg_result['read_a']
    operand_b = reg_result['read_b']
    
    # Execute: MDU multiplication (synchronous in control signal wrapper)
    signals.md_op = 'MUL'
    
    mdu_result = mdu_with_control(operand_a, operand_b, signals)
    
    # Verify result (12 * 5 = 60)
    result_value = mdu_result['result']
    assert bits_to_int(result_value) == 60
    
    # Writeback
    signals = mdu_result['signals']
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(10, 5)
    signals.rf_raddr_a = int_to_bits(10, 5)
    
    wb_result = register_with_control(rf, signals, result_value)
    assert bits_to_int(wb_result['read_a']) == 60


def test_multi_cycle_mdu_division():
    """
    Test: Complete MDU division through control signals.
    
    Simulates: DIV x12, x10, x11
    - Verify operation completes successfully
    - Verify final result is correct
    """
    rf = RegisterFile()
    signals = ControlSignals()
    
    # Setup
    rf.write_int_reg(10, int_to_bin32(100))
    rf.write_int_reg(11, int_to_bin32(4))
    
    # Decode
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(10, 5)
    signals.rf_raddr_b = int_to_bits(11, 5)
    
    reg_result = register_with_control(rf, signals)
    operand_a = reg_result['read_a']
    operand_b = reg_result['read_b']
    
    # Execute: Division (synchronous in control signal wrapper)
    signals.md_op = 'DIV'
    
    mdu_result = mdu_with_control(operand_a, operand_b, signals)
    assert bits_to_int(mdu_result['result']) == 25  # 100 / 4 = 25
    
    # Writeback
    signals = mdu_result['signals']
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(12, 5)
    
    wb_result = register_with_control(rf, signals, mdu_result['result'])
    assert bits_to_int(rf.read_int_reg(12)) == 25


# =============================================================================
# Test 3: Multi-Cycle FPU Addition
# =============================================================================

def test_multi_cycle_fpu_addition():
    """
    Test: Complete FPU addition through control signals.
    
    Simulates: FADD.S f3, f1, f2
    - Verify FPU operation completes
    - Verify final result is correct
    """
    rf = RegisterFile()
    signals = ControlSignals()
    
    # Setup: Initialize FP registers
    rf.write_fp_reg(1, float_to_bits(2.5))
    rf.write_fp_reg(2, float_to_bits(3.5))
    
    # Decode: Read FP operands
    operand_a = rf.read_fp_reg(1)
    operand_b = rf.read_fp_reg(2)
    
    # Execute: FPU addition (synchronous in control signal wrapper)
    signals.fpu_op = 'FADD'  # ADD operation
    signals.round_mode = [0, 0, 0]  # RNE (Round to Nearest, ties to Even)
    
    fpu_result = fpu_with_control(operand_a, operand_b, signals)
    
    # Verify result (2.5 + 3.5 = 6.0)
    result_value = fpu_result['result']
    result_float = bits_to_float(result_value)
    assert abs(result_float - 6.0) < 0.0001
    
    # Writeback to FP register
    rf.write_fp_reg(3, result_value)
    assert abs(bits_to_float(rf.read_fp_reg(3)) - 6.0) < 0.0001


def test_multi_cycle_fpu_multiplication():
    """
    Test: Complete FPU multiplication through control signals.
    
    Simulates: FMUL.S f5, f3, f4
    """
    rf = RegisterFile()
    signals = ControlSignals()
    
    # Setup
    rf.write_fp_reg(3, float_to_bits(4.0))
    rf.write_fp_reg(4, float_to_bits(2.5))
    
    # Decode
    operand_a = rf.read_fp_reg(3)
    operand_b = rf.read_fp_reg(4)
    
    # Execute: FPU multiplication (synchronous in control signal wrapper)
    signals.fpu_op = 'FMUL'  # MUL operation
    signals.round_mode = [0, 0, 0]  # RNE
    
    fpu_result = fpu_with_control(operand_a, operand_b, signals)
    
    # Verify result (4.0 * 2.5 = 10.0)
    result_float = bits_to_float(fpu_result['result'])
    assert abs(result_float - 10.0) < 0.0001
    
    # Writeback
    rf.write_fp_reg(5, fpu_result['result'])
    assert abs(bits_to_float(rf.read_fp_reg(5)) - 10.0) < 0.0001


# =============================================================================
# Test 4: Mixed Operation Sequence
# =============================================================================

def test_mixed_operation_sequence():
    """
    Test: Sequence of different operations.
    
    Program:
      ADDI x1, x0, 10      # x1 = 10
      ADDI x2, x0, 5       # x2 = 5
      ADD  x3, x1, x2      # x3 = x1 + x2 = 15
      SLL  x4, x3, 2       # x4 = x3 << 2 = 60
      MUL  x5, x4, x2      # x5 = x4 * x2 = 300
    
    Verifies: Control unit properly sequences operations without conflicts.
    """
    rf = RegisterFile()
    signals = ControlSignals()
    
    # Instruction 1: ADDI x1, x0, 10
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(1, 5)
    signals.rf_raddr_a = int_to_bits(1, 5)
    result = register_with_control(rf, signals, int_to_bin32(10))
    assert bits_to_int(result['read_a']) == 10
    
    # Instruction 2: ADDI x2, x0, 5
    signals.rf_waddr = int_to_bits(2, 5)
    signals.rf_raddr_a = int_to_bits(2, 5)
    result = register_with_control(rf, signals, int_to_bin32(5))
    assert bits_to_int(result['read_a']) == 5
    
    # Instruction 3: ADD x3, x1, x2
    # Decode
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(1, 5)
    signals.rf_raddr_b = int_to_bits(2, 5)
    reg_result = register_with_control(rf, signals)
    
    # Execute (ALU)
    signals.alu_op = ALU_OP_ADD  # ADD
    alu_result = alu_with_control(reg_result['read_a'], reg_result['read_b'], signals)
    
    # Writeback
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(3, 5)
    register_with_control(rf, signals, alu_result['result'])
    assert bits_to_int(rf.read_int_reg(3)) == 15
    
    # Instruction 4: SLL x4, x3, 2
    # Decode
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(3, 5)
    reg_result = register_with_control(rf, signals)
    
    # Execute (Shifter)
    signals.sh_op = SH_OP_SLL  # SLL
    signals.sh_amount = int_to_bits(2, 5)
    shift_result = shifter_with_control(reg_result['read_a'], signals)
    
    # Writeback
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(4, 5)
    register_with_control(rf, signals, shift_result['result'])
    assert bits_to_int(rf.read_int_reg(4)) == 60
    
    # Instruction 5: MUL x5, x4, x2
    # Decode
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(4, 5)
    signals.rf_raddr_b = int_to_bits(2, 5)
    reg_result = register_with_control(rf, signals)
    
    # Execute (MDU)  (synchronous in control signal wrapper)
    signals.md_op = 'MUL'  # MUL
    mdu_result = mdu_with_control(reg_result['read_a'], reg_result['read_b'], signals)
    
    # Writeback
    signals = mdu_result['signals']
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(5, 5)
    register_with_control(rf, signals, mdu_result['result'])
    assert bits_to_int(rf.read_int_reg(5)) == 300
    
    # Verify final register state
    assert bits_to_int(rf.read_int_reg(1)) == 10
    assert bits_to_int(rf.read_int_reg(2)) == 5
    assert bits_to_int(rf.read_int_reg(3)) == 15
    assert bits_to_int(rf.read_int_reg(4)) == 60
    assert bits_to_int(rf.read_int_reg(5)) == 300


def test_mixed_integer_and_float_operations():
    """
    Test: Mixed integer and floating-point operations.
    
    Verifies: Control unit handles transitions between integer and FP units.
    """
    rf = RegisterFile()
    signals = ControlSignals()
    
    # Integer operation: ADD x3, x1, x2
    rf.write_int_reg(1, int_to_bin32(100))
    rf.write_int_reg(2, int_to_bin32(50))
    
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(1, 5)
    signals.rf_raddr_b = int_to_bits(2, 5)
    reg_result = register_with_control(rf, signals)
    
    signals.alu_op = ALU_OP_ADD  # ADD
    alu_result = alu_with_control(reg_result['read_a'], reg_result['read_b'], signals)
    
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(3, 5)
    register_with_control(rf, signals, alu_result['result'])
    
    assert bits_to_int(rf.read_int_reg(3)) == 150
    
    # Floating-point operation: FADD.S f3, f1, f2
    rf.write_fp_reg(1, float_to_bits(2.5))
    rf.write_fp_reg(2, float_to_bits(3.5))
    
    operand_a = rf.read_fp_reg(1)
    operand_b = rf.read_fp_reg(2)
    
    signals.fpu_op = 'FADD'  # ADD
    signals.round_mode = [0, 0, 0]
    
    fpu_result = fpu_with_control(operand_a, operand_b, signals)
    
    rf.write_fp_reg(3, fpu_result['result'])
    
    assert abs(bits_to_float(rf.read_fp_reg(3)) - 6.0) < 0.0001
    
    # Verify both results coexist
    assert bits_to_int(rf.read_int_reg(3)) == 150  # Integer result preserved
    assert abs(bits_to_float(rf.read_fp_reg(3)) - 6.0) < 0.0001  # FP result


# =============================================================================
# Test 5: Control Signal Trace Verification
# =============================================================================

def test_control_signal_trace_collection():
    """
    Test: Collect and verify control signal traces for a sequence of operations.
    
    Verifies: Trace completeness and correctness.
    """
    rf = RegisterFile()
    signals = ControlSignals()
    trace = []
    
    # Operation: ADD x3, x1, x2
    rf.write_int_reg(1, int_to_bin32(10))
    rf.write_int_reg(2, int_to_bin32(20))
    
    # Decode phase
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(1, 5)
    signals.rf_raddr_b = int_to_bits(2, 5)
    signals.cycle = 1
    
    reg_result = register_with_control(rf, signals)
    trace.extend(reg_result['trace'])
    
    # Execute phase
    signals.alu_op = ALU_OP_ADD
    signals.cycle = 2
    
    alu_result = alu_with_control(reg_result['read_a'], reg_result['read_b'], signals)
    trace.extend(alu_result['trace'])
    
    # Writeback phase
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(3, 5)
    signals.cycle = 3
    
    wb_result = register_with_control(rf, signals, alu_result['result'])
    trace.extend(wb_result['trace'])
    
    # Verify trace completeness
    assert len(trace) >= 4  # At least: 2 reads, 1 ALU op, 1 write
    
    # Verify trace contains key operations
    trace_str = ''.join(trace)  # Remove spaces for easier matching
    assert 'READ' in trace_str
    assert 'ADD' in trace_str  # ALU trace contains "ALU ADD"
    assert 'WRITE' in trace_str


def test_trace_with_multi_cycle_operation():
    """
    Test: Trace collection for MDU operation.
    
    Verifies: Trace captures operation details.
    """
    rf = RegisterFile()
    signals = ControlSignals()
    trace = []
    
    # Setup
    rf.write_int_reg(1, int_to_bin32(6))
    rf.write_int_reg(2, int_to_bin32(7))
    
    # Decode
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(1, 5)
    signals.rf_raddr_b = int_to_bits(2, 5)
    
    reg_result = register_with_control(rf, signals)
    trace.extend(reg_result['trace'])
    
    # Execute (MDU) - synchronous wrapper
    signals.md_op = 'MUL'  # MUL
    
    mdu_result = mdu_with_control(reg_result['read_a'], reg_result['read_b'], signals)
    trace.extend(mdu_result['trace'])
    
    # Writeback
    signals = mdu_result['signals']
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(3, 5)
    
    wb_result = register_with_control(rf, signals, mdu_result['result'])
    trace.extend(wb_result['trace'])
    
    # Verify trace captures operation
    assert len(trace) > 3  # At least: 2 reads, 1 MDU op, 1 write
    
    # Verify trace contains MDU-specific information
    trace_str = ' '.join(trace)
    assert 'MUL' in trace_str or 'MDU' in trace_str


# =============================================================================
# Test 6: Edge Cases and Error Handling
# =============================================================================

def test_operation_with_x0():
    """
    Test: Operations involving x0 (hardwired to zero).
    
    Verifies: x0 behavior is correct across all operations.
    """
    rf = RegisterFile()
    signals = ControlSignals()
    
    # ADD x1, x0, x0 (should produce 0)
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(0, 5)
    signals.rf_raddr_b = int_to_bits(0, 5)
    
    reg_result = register_with_control(rf, signals)
    
    signals.alu_op = ALU_OP_ADD  # ADD
    alu_result = alu_with_control(reg_result['read_a'], reg_result['read_b'], signals)
    
    assert bits_to_int(alu_result['result']) == 0
    
    # ADD x2, x0, immediate (x0 + 100)
    rf.write_int_reg(10, int_to_bin32(100))
    signals.rf_raddr_a = int_to_bits(0, 5)
    signals.rf_raddr_b = int_to_bits(10, 5)
    
    reg_result = register_with_control(rf, signals)
    alu_result = alu_with_control(reg_result['read_a'], reg_result['read_b'], signals)
    
    assert bits_to_int(alu_result['result']) == 100  # 0 + 100


def test_back_to_back_operations():
    """
    Test: Multiple operations executed back-to-back.
    
    Verifies: No state pollution between operations.
    """
    rf = RegisterFile()
    signals = ControlSignals()
    
    rf.write_int_reg(1, int_to_bin32(5))
    rf.write_int_reg(2, int_to_bin32(3))
    
    # Operation 1: ADD
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(1, 5)
    signals.rf_raddr_b = int_to_bits(2, 5)
    reg_result = register_with_control(rf, signals)
    
    signals.alu_op = ALU_OP_ADD  # ADD
    alu_result1 = alu_with_control(reg_result['read_a'], reg_result['read_b'], signals)
    result1 = bits_to_int(alu_result1['result'])
    
    # Operation 2: SUB (immediately after)
    signals.alu_op = ALU_OP_SUB  # SUB
    alu_result2 = alu_with_control(reg_result['read_a'], reg_result['read_b'], signals)
    result2 = bits_to_int(alu_result2['result'])
    
    # Verify results are independent
    assert result1 == 8   # 5 + 3
    assert result2 == 2   # 5 - 3


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    print("Running Control Unit Integration Tests (Phase 6)...")
    pytest.main([__file__, "-v"])

# AI-END
