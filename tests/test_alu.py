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


#if __name__ == "__main__":