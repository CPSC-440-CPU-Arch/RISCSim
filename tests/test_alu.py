# AI-BEGIN
import pytest
from riscsim.cpu.alu import alu

# Helper function to convert integer to 32-bit binary list (MSB first)
def int_to_bin32(n):
    """Convert integer to 32-bit binary list (MSB at index 0, LSB at index 31)"""
    if n < 0:
        n = (1 << 32) + n  # Two's complement for negative numbers
    return [(n >> (31 - i)) & 1 for i in range(32)]

# Helper function to convert 32-bit binary list back to integer
def bin32_to_int(bits, signed=False):
    """Convert 32-bit binary list (MSB first) to integer"""
    val = sum(bit << (31 - i) for i, bit in enumerate(bits))
    if signed and bits[0] == 1:  # Negative in two's complement
        val -= (1 << 32)
    return val

"""
opcodes:
[0, 0, 0, 0] = and
[0, 0, 0, 1] = or
[0, 0, 1, 0] = add
[0, 1, 1, 0] = subtract
[0, 1, 1, 1] = a < b? (SLT)
[1, 1, 0, 0] = Bitwise NOR !(A|B)
[0, 0, 1, 1] = Bitwise XOR A ^ B
[1, 1, 0, 1] = NAND !(A & B)

Bit Flags = [Negative, Zero, Carryout, Overflow]

"""

# ==================== OPCODE TESTS (3-bit integers: 0-7) ====================

def test_alu_and():
    """Test AND operation [0,0,0,0]"""
    opcode = [0, 0, 0, 0]

    # 7 & 7 = 7 (111 & 111 = 111)
    result, flags = alu(int_to_bin32(7), int_to_bin32(7), opcode)
    assert bin32_to_int(result) == 7

    # 5 & 3 = 1 (101 & 011 = 001)
    result, flags = alu(int_to_bin32(5), int_to_bin32(3), opcode)
    assert bin32_to_int(result) == 1

    # 6 & 4 = 4 (110 & 100 = 100)
    result, flags = alu(int_to_bin32(6), int_to_bin32(4), opcode)
    assert bin32_to_int(result) == 4

    # 0 & 7 = 0 (Zero flag should be set)
    result, flags = alu(int_to_bin32(0), int_to_bin32(7), opcode)
    N, Z, C, V = flags
    assert bin32_to_int(result) == 0
    assert Z == 1  # Zero flag


def test_alu_or():
    """Test OR operation [0,0,0,1]"""
    opcode = [0, 0, 0, 1]

    # 4 | 2 = 6 (100 | 010 = 110)
    result, flags = alu(int_to_bin32(4), int_to_bin32(2), opcode)
    assert bin32_to_int(result) == 6

    # 3 | 4 = 7 (011 | 100 = 111)
    result, flags = alu(int_to_bin32(3), int_to_bin32(4), opcode)
    assert bin32_to_int(result) == 7

    # 0 | 0 = 0 (Zero flag should be set)
    result, flags = alu(int_to_bin32(0), int_to_bin32(0), opcode)
    N, Z, C, V = flags
    assert bin32_to_int(result) == 0
    assert Z == 1  # Zero flag


def test_alu_add():
    """Test ADD operation [0,0,1,0]"""
    opcode = [0, 0, 1, 0]

    # 3 + 2 = 5
    result, flags = alu(int_to_bin32(3), int_to_bin32(2), opcode)
    assert bin32_to_int(result) == 5

    # 4 + 3 = 7
    result, flags = alu(int_to_bin32(4), int_to_bin32(3), opcode)
    assert bin32_to_int(result) == 7

    # 0 + 0 = 0 (Zero flag should be set)
    result, flags = alu(int_to_bin32(0), int_to_bin32(0), opcode)
    N, Z, C, V = flags
    assert bin32_to_int(result) == 0
    assert Z == 1  # Zero flag

    # 7 + 1 = 8
    result, flags = alu(int_to_bin32(7), int_to_bin32(1), opcode)
    assert bin32_to_int(result) == 8


def test_alu_subtract():
    """Test SUBTRACT operation [0,1,1,0]"""
    opcode = [0, 1, 1, 0]

    # 5 - 3 = 2
    result, flags = alu(int_to_bin32(5), int_to_bin32(3), opcode)
    assert bin32_to_int(result) == 2

    # 7 - 7 = 0 (Zero flag should be set)
    result, flags = alu(int_to_bin32(7), int_to_bin32(7), opcode)
    N, Z, C, V = flags
    assert bin32_to_int(result) == 0
    assert Z == 1  # Zero flag

    # 3 - 5 = -2 (Negative result in two's complement)
    result, flags = alu(int_to_bin32(3), int_to_bin32(5), opcode)
    N, Z, C, V = flags
    assert bin32_to_int(result, signed=True) == -2
    assert N == 1  # Negative flag


def test_alu_slt():
    """Test SLT (Set Less Than) operation [0,1,1,1]"""
    opcode = [0, 1, 1, 1]

    # 3 < 5 = 1 (true)
    result, flags = alu(int_to_bin32(3), int_to_bin32(5), opcode)
    assert bin32_to_int(result) == 1

    # 5 < 3 = 0 (false)
    result, flags = alu(int_to_bin32(5), int_to_bin32(3), opcode)
    assert bin32_to_int(result) == 0

    # 4 < 4 = 0 (equal, not less than)
    result, flags = alu(int_to_bin32(4), int_to_bin32(4), opcode)
    N, Z, C, V = flags
    assert bin32_to_int(result) == 0
    assert Z == 1  # Zero flag when equal


def test_alu_nor():
    """Test NOR operation [1,1,0,0]"""
    opcode = [1, 1, 0, 0]

    # ~(5 | 3) = ~7 = NOT(0...0111) = 1...1000
    result, flags = alu(int_to_bin32(5), int_to_bin32(3), opcode)
    N, Z, C, V = flags
    # Result should be bitwise NOT of 7, which is all 1s except last 3 bits are 000
    expected = bin32_to_int(result, signed=True)
    assert expected < 0  # Result should be negative (MSB = 1)
    assert N == 1  # Negative flag

    # ~(0 | 0) = ~0 = all 1s (which is -1 in two's complement)
    result, flags = alu(int_to_bin32(0), int_to_bin32(0), opcode)
    N, Z, C, V = flags
    assert bin32_to_int(result, signed=True) == -1
    assert N == 1  # Negative flag


def test_alu_xor():
    """Test XOR operation [0,0,1,1]"""
    opcode = [0, 0, 1, 1]

    # 5 ^ 3 = 6 (101 ^ 011 = 110)
    result, flags = alu(int_to_bin32(5), int_to_bin32(3), opcode)
    assert bin32_to_int(result) == 6

    # 7 ^ 7 = 0 (Zero flag should be set)
    result, flags = alu(int_to_bin32(7), int_to_bin32(7), opcode)
    N, Z, C, V = flags
    assert bin32_to_int(result) == 0
    assert Z == 1  # Zero flag


def test_alu_nand():
    """Test NAND operation [1,1,0,1]"""
    opcode = [1, 1, 0, 1]

    # ~(7 & 7) = ~7 = NOT(111) in low 3 bits
    result, flags = alu(int_to_bin32(7), int_to_bin32(7), opcode)
    N, Z, C, V = flags
    # Result should be negative
    assert bin32_to_int(result, signed=True) < 0
    assert N == 1  # Negative flag

    # ~(5 & 3) = ~1 = NOT(001) in low 3 bits
    result, flags = alu(int_to_bin32(5), int_to_bin32(3), opcode)
    N, Z, C, V = flags
    # Result should be all 1s except LSB 3 bits = 110 (inverted from 001)
    assert bin32_to_int(result, signed=True) < 0
    assert N == 1  # Negative flag


# Phase 2: Control Signal Integration Tests

def test_alu_with_control_add():
    """Test ALU with control signals for ADD operation."""
    from riscsim.cpu.alu import alu_with_control
    from riscsim.cpu.control_signals import ControlSignals, ALU_OP_ADD
    
    # Create control signals
    signals = ControlSignals()
    signals.alu_op = ALU_OP_ADD
    
    # Operands: 5 + 3 = 8
    a = int_to_bin32(5)
    b = int_to_bin32(3)
    
    result_dict = alu_with_control(a, b, signals)
    
    # Verify result
    assert bin32_to_int(result_dict['result']) == 8
    
    # Verify flags
    assert result_dict['flags']['N'] == 0  # Positive result
    assert result_dict['flags']['Z'] == 0  # Not zero
    assert result_dict['flags']['V'] == 0  # No overflow
    
    # Verify trace
    assert 'ALU ADD' in result_dict['trace']
    assert 'N=0' in result_dict['trace']
    assert 'Z=0' in result_dict['trace']


def test_alu_with_control_subtract():
    """Test ALU with control signals for SUB operation."""
    from riscsim.cpu.alu import alu_with_control
    from riscsim.cpu.control_signals import ControlSignals, ALU_OP_SUB
    
    signals = ControlSignals()
    signals.alu_op = ALU_OP_SUB
    
    # Operands: 10 - 3 = 7
    a = int_to_bin32(10)
    b = int_to_bin32(3)
    
    result_dict = alu_with_control(a, b, signals)
    
    assert bin32_to_int(result_dict['result']) == 7
    assert result_dict['flags']['Z'] == 0
    assert 'ALU SUB' in result_dict['trace']


def test_alu_with_control_zero_flag():
    """Test that zero flag is set correctly with control signals."""
    from riscsim.cpu.alu import alu_with_control
    from riscsim.cpu.control_signals import ControlSignals, ALU_OP_SUB
    
    signals = ControlSignals()
    signals.alu_op = ALU_OP_SUB
    
    # 5 - 5 = 0
    a = int_to_bin32(5)
    b = int_to_bin32(5)
    
    result_dict = alu_with_control(a, b, signals)
    
    assert bin32_to_int(result_dict['result']) == 0
    assert result_dict['flags']['Z'] == 1  # Zero flag should be set
    assert result_dict['flags']['N'] == 0  # Not negative
    assert 'Z=1' in result_dict['trace']


def test_alu_with_control_overflow():
    """Test overflow detection with control signals."""
    from riscsim.cpu.alu import alu_with_control
    from riscsim.cpu.control_signals import ControlSignals, ALU_OP_ADD
    
    signals = ControlSignals()
    signals.alu_op = ALU_OP_ADD
    
    # INT_MAX + 1 causes overflow
    a = int_to_bin32(2147483647)  # 0x7FFFFFFF
    b = int_to_bin32(1)
    
    result_dict = alu_with_control(a, b, signals)
    
    assert result_dict['flags']['V'] == 1  # Overflow should be set
    assert result_dict['flags']['N'] == 1  # Result is negative
    assert 'V=1' in result_dict['trace']


def test_alu_with_control_and_operation():
    """Test AND operation with control signals."""
    from riscsim.cpu.alu import alu_with_control
    from riscsim.cpu.control_signals import ControlSignals, ALU_OP_AND
    
    signals = ControlSignals()
    signals.alu_op = ALU_OP_AND
    
    # 0xFF00FF00 & 0x00FF00FF = 0x00000000
    a = [1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0]
    b = [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]
    
    result_dict = alu_with_control(a, b, signals)
    
    # Result should be all zeros
    assert all(bit == 0 for bit in result_dict['result'])
    assert result_dict['flags']['Z'] == 1
    assert 'ALU AND' in result_dict['trace']


def test_alu_with_control_signals_preserved():
    """Test that control signals are preserved in result."""
    from riscsim.cpu.alu import alu_with_control
    from riscsim.cpu.control_signals import ControlSignals, ALU_OP_ADD
    
    signals = ControlSignals()
    signals.alu_op = ALU_OP_ADD
    signals.cycle = 42
    signals.rf_waddr = [0, 0, 0, 1, 1]  # r3
    
    a = int_to_bin32(5)
    b = int_to_bin32(3)
    
    result_dict = alu_with_control(a, b, signals)
    
    # Verify signals are preserved
    returned_signals = result_dict['signals']
    assert returned_signals.alu_op == ALU_OP_ADD
    assert returned_signals.cycle == 42
    assert returned_signals.rf_waddr == [0, 0, 0, 1, 1]


# AI-END

#if __name__ == "__main__":