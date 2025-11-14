#!/usr/bin/env python3
"""
RISC-V Instruction Encoder for Test Programs
Generates .hex files for Phase 5 test programs
"""

def encode_r_type(opcode, rd, funct3, rs1, rs2, funct7):
    """Encode R-type instruction."""
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def encode_i_type(opcode, rd, funct3, rs1, imm):
    """Encode I-type instruction."""
    imm_12 = imm & 0xFFF  # 12-bit immediate
    return (imm_12 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def encode_s_type(opcode, funct3, rs1, rs2, imm):
    """Encode S-type instruction."""
    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F
    return (imm_11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_4_0 << 7) | opcode

def encode_b_type(opcode, funct3, rs1, rs2, imm):
    """Encode B-type instruction."""
    imm_12 = (imm >> 12) & 0x1
    imm_10_5 = (imm >> 5) & 0x3F
    imm_4_1 = (imm >> 1) & 0xF
    imm_11 = (imm >> 11) & 0x1
    return (imm_12 << 31) | (imm_10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_4_1 << 8) | (imm_11 << 7) | opcode

def encode_u_type(opcode, rd, imm):
    """Encode U-type instruction."""
    imm_31_12 = (imm >> 12) & 0xFFFFF
    return (imm_31_12 << 12) | (rd << 7) | opcode

def encode_j_type(opcode, rd, imm):
    """Encode J-type instruction."""
    imm_20 = (imm >> 20) & 0x1
    imm_10_1 = (imm >> 1) & 0x3FF
    imm_11 = (imm >> 11) & 0x1
    imm_19_12 = (imm >> 12) & 0xFF
    return (imm_20 << 31) | (imm_19_12 << 12) | (imm_11 << 20) | (imm_10_1 << 21) | (rd << 7) | opcode

# Instruction encoders
def add(rd, rs1, rs2):
    return encode_r_type(0b0110011, rd, 0b000, rs1, rs2, 0b0000000)

def sub(rd, rs1, rs2):
    return encode_r_type(0b0110011, rd, 0b000, rs1, rs2, 0b0100000)

def addi(rd, rs1, imm):
    return encode_i_type(0b0010011, rd, 0b000, rs1, imm)

def andi(rd, rs1, imm):
    return encode_i_type(0b0010011, rd, 0b111, rs1, imm)

def ori(rd, rs1, imm):
    return encode_i_type(0b0010011, rd, 0b110, rs1, imm)

def xori(rd, rs1, imm):
    return encode_i_type(0b0010011, rd, 0b100, rs1, imm)

def and_op(rd, rs1, rs2):
    return encode_r_type(0b0110011, rd, 0b111, rs1, rs2, 0b0000000)

def or_op(rd, rs1, rs2):
    return encode_r_type(0b0110011, rd, 0b110, rs1, rs2, 0b0000000)

def xor(rd, rs1, rs2):
    return encode_r_type(0b0110011, rd, 0b100, rs1, rs2, 0b0000000)

def sll(rd, rs1, rs2):
    return encode_r_type(0b0110011, rd, 0b001, rs1, rs2, 0b0000000)

def srl(rd, rs1, rs2):
    return encode_r_type(0b0110011, rd, 0b101, rs1, rs2, 0b0000000)

def sra(rd, rs1, rs2):
    return encode_r_type(0b0110011, rd, 0b101, rs1, rs2, 0b0100000)

def slli(rd, rs1, shamt):
    return encode_i_type(0b0010011, rd, 0b001, rs1, shamt)

def srli(rd, rs1, shamt):
    return encode_i_type(0b0010011, rd, 0b101, rs1, shamt)

def srai(rd, rs1, shamt):
    return encode_i_type(0b0010011, rd, 0b101, rs1, shamt | 0x400)

def lw(rd, rs1, offset):
    return encode_i_type(0b0000011, rd, 0b010, rs1, offset)

def sw(rs1, rs2, offset):
    return encode_s_type(0b0100011, 0b010, rs1, rs2, offset)

def beq(rs1, rs2, offset):
    return encode_b_type(0b1100011, 0b000, rs1, rs2, offset)

def bne(rs1, rs2, offset):
    return encode_b_type(0b1100011, 0b001, rs1, rs2, offset)

def jal(rd, offset):
    return encode_j_type(0b1101111, rd, offset)

def jalr(rd, rs1, offset):
    return encode_i_type(0b1100111, rd, 0b000, rs1, offset)

def lui(rd, imm):
    return encode_u_type(0b0110111, rd, imm)

def auipc(rd, imm):
    return encode_u_type(0b0010111, rd, imm)

def write_hex_file(filename, instructions):
    """Write instructions to .hex file."""
    with open(filename, 'w') as f:
        for instr in instructions:
            f.write(f"{instr:08x}\n")
    print(f"Created {filename} with {len(instructions)} instructions")

if __name__ == "__main__":
    print("RISC-V Instruction Encoder for Phase 5 Test Programs")
    print("=" * 60)
