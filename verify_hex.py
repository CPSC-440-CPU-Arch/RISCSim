#!/usr/bin/env python3
"""
Verify that test_base.hex matches test_base.s by decoding the machine code.
"""

def decode_instruction(hex_str):
    """Decode a 32-bit RISC-V instruction to assembly."""
    instr = int(hex_str, 16)

    # Extract opcode (bits 0-6)
    opcode = instr & 0x7F
    rd = (instr >> 7) & 0x1F
    funct3 = (instr >> 12) & 0x7
    rs1 = (instr >> 15) & 0x1F
    rs2 = (instr >> 20) & 0x1F
    funct7 = (instr >> 25) & 0x7F

    # I-type immediate
    imm_i = (instr >> 20)
    if imm_i & 0x800:  # Sign extend
        imm_i |= 0xFFFFF000
    imm_i = (imm_i ^ 0xFFFFFFFF) + 1 if imm_i & 0x80000000 else imm_i

    # U-type immediate
    imm_u = instr >> 12

    # B-type immediate
    imm_b = ((instr >> 7) & 0x1E) | ((instr >> 20) & 0x7E0) | ((instr << 4) & 0x800) | ((instr >> 19) & 0x1000)
    if imm_b & 0x1000:
        imm_b |= 0xFFFFE000
    imm_b = (imm_b ^ 0xFFFFFFFF) + 1 if imm_b & 0x80000000 else imm_b

    # J-type immediate
    imm_j = ((instr >> 20) & 0x7FE) | ((instr >> 9) & 0x800) | (instr & 0xFF000) | ((instr >> 11) & 0x100000)
    if imm_j & 0x100000:
        imm_j |= 0xFFE00000

    reg_names = ['x0', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9',
                 'x10', 'x11', 'x12', 'x13', 'x14', 'x15', 'x16', 'x17', 'x18', 'x19',
                 'x20', 'x21', 'x22', 'x23', 'x24', 'x25', 'x26', 'x27', 'x28', 'x29',
                 'x30', 'x31']

    # Decode based on opcode
    if opcode == 0b0010011:  # I-type (ADDI, etc.)
        if funct3 == 0b000:
            return f"addi {reg_names[rd]}, {reg_names[rs1]}, {imm_i & 0xFFF if imm_i >= 0 else imm_i}"
    elif opcode == 0b0110011:  # R-type (ADD, SUB, etc.)
        if funct3 == 0b000 and funct7 == 0b0000000:
            return f"add {reg_names[rd]}, {reg_names[rs1]}, {reg_names[rs2]}"
        elif funct3 == 0b000 and funct7 == 0b0100000:
            return f"sub {reg_names[rd]}, {reg_names[rs1]}, {reg_names[rs2]}"
    elif opcode == 0b0110111:  # LUI
        return f"lui {reg_names[rd]}, 0x{imm_u:05x}"
    elif opcode == 0b0100011:  # S-type (SW)
        imm_s = ((instr >> 7) & 0x1F) | ((instr >> 20) & 0xFE0)
        if imm_s & 0x800:
            imm_s |= 0xFFFFF000
        return f"sw {reg_names[rs2]}, {imm_s}({reg_names[rs1]})"
    elif opcode == 0b0000011:  # I-type (LW)
        return f"lw {reg_names[rd]}, {imm_i}({reg_names[rs1]})"
    elif opcode == 0b1100011:  # B-type (BEQ, BNE)
        if funct3 == 0b000:
            return f"beq {reg_names[rs1]}, {reg_names[rs2]}, {imm_b}"
    elif opcode == 0b1101111:  # J-type (JAL)
        return f"jal {reg_names[rd]}, {imm_j}"

    return f"unknown (0x{instr:08x})"

def main():
    print("=" * 80)
    print("Verifying test_base.hex matches test_base.s")
    print("=" * 80)

    # Read hex file
    with open('tests/programs/test_base.hex', 'r') as f:
        hex_instructions = [line.strip() for line in f if line.strip()]

    # Expected assembly from test_base.s
    expected_asm = [
        "addi x1, x0, 5",
        "addi x2, x0, 10",
        "add x3, x1, x2",
        "sub x4, x2, x1",
        "lui x5, 0x00010",
        "sw x3, 0(x5)",
        "lw x4, 0(x5)",
        "beq x3, x4, 8",
        "addi x6, x0, 1",
        "addi x6, x0, 2",
        "jal x0, 0"
    ]

    print(f"\n{'Line':<6} {'Machine Code':<12} {'Decoded Assembly':<30} {'Expected':<30} {'Match':<6}")
    print("-" * 80)

    all_match = True
    for i, hex_instr in enumerate(hex_instructions, 1):
        decoded = decode_instruction(hex_instr)
        expected = expected_asm[i-1] if i <= len(expected_asm) else "N/A"

        # Normalize for comparison
        decoded_norm = decoded.replace(" ", "").replace(",", "").lower()
        expected_norm = expected.replace(" ", "").replace(",", "").lower()

        match = "✅" if decoded_norm == expected_norm else "❌"
        if match == "❌":
            all_match = False

        print(f"{i:<6} {hex_instr:<12} {decoded:<30} {expected:<30} {match:<6}")

    print("-" * 80)
    if all_match:
        print("\n✅ SUCCESS: test_base.hex perfectly matches test_base.s!")
        print("   The .hex file was correctly generated from the assembly source.")
    else:
        print("\n❌ MISMATCH: Some instructions don't match!")
        print("   The .hex file may have been generated differently.")
    print("=" * 80)

if __name__ == '__main__':
    main()
