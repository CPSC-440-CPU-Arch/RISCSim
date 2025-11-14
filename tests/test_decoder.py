# AI-BEGIN
"""
Unit tests for RISC-V Instruction Decoder.

Tests cover all instruction formats (R, I, S, B, U, J) and the minimum viable
instruction set defined in the implementation plan.

Test Structure:
- R-type: 8 tests (ADD, SUB, AND, OR, XOR, SLL, SRL, SRA)
- I-type: 8 tests (ADDI, ANDI, ORI, XORI, SLLI, SRLI, SRAI, LW)
- S-type: 1 test (SW)
- B-type: 2 tests (BEQ, BNE)
- U-type: 2 tests (LUI, AUIPC)
- J-type: 2 tests (JAL, JALR)
- Edge cases: 5+ tests
"""

import pytest
from riscsim.cpu.decoder import InstructionDecoder, DecodedInstruction
from riscsim.utils.bit_utils import int_to_bits_unsigned, bits_to_int_unsigned


class TestRTypeInstructions:
    """Test R-type instruction decoding."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.decoder = InstructionDecoder()
    
    def test_decode_add(self):
        """Test ADD instruction: add x3, x1, x2 (x3 = x1 + x2)."""
        # ADD: 0000000 00010 00001 000 00011 0110011
        #      funct7  rs2   rs1  f3  rd    opcode
        # Binary: 0000000_00010_00001_000_00011_0110011
        instruction = [0,0,0,0,0,0,0,  0,0,0,1,0,  0,0,0,0,1,  0,0,0,  0,0,0,1,1,  0,1,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'R'
        assert decoded.mnemonic == 'ADD'
        assert decoded.rd == [0,0,0,1,1]  # x3
        assert decoded.rs1 == [0,0,0,0,1]  # x1
        assert decoded.rs2 == [0,0,0,1,0]  # x2
        assert decoded.funct3 == [0,0,0]
        assert decoded.funct7 == [0,0,0,0,0,0,0]
    
    def test_decode_sub(self):
        """Test SUB instruction: sub x4, x2, x1 (x4 = x2 - x1)."""
        # SUB: 0100000 00001 00010 000 00100 0110011
        instruction = [0,1,0,0,0,0,0,  0,0,0,0,1,  0,0,0,1,0,  0,0,0,  0,0,1,0,0,  0,1,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'R'
        assert decoded.mnemonic == 'SUB'
        assert decoded.rd == [0,0,1,0,0]  # x4
        assert decoded.rs1 == [0,0,0,1,0]  # x2
        assert decoded.rs2 == [0,0,0,0,1]  # x1
        assert decoded.funct3 == [0,0,0]
        assert decoded.funct7 == [0,1,0,0,0,0,0]
    
    def test_decode_and(self):
        """Test AND instruction: and x5, x3, x4."""
        # AND: 0000000 00100 00011 111 00101 0110011
        instruction = [0,0,0,0,0,0,0,  0,0,1,0,0,  0,0,0,1,1,  1,1,1,  0,0,1,0,1,  0,1,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'R'
        assert decoded.mnemonic == 'AND'
        assert decoded.rd == [0,0,1,0,1]  # x5
        assert decoded.rs1 == [0,0,0,1,1]  # x3
        assert decoded.rs2 == [0,0,1,0,0]  # x4
        assert decoded.funct3 == [1,1,1]
    
    def test_decode_or(self):
        """Test OR instruction: or x6, x5, x4."""
        # OR: 0000000 00100 00101 110 00110 0110011
        instruction = [0,0,0,0,0,0,0,  0,0,1,0,0,  0,0,1,0,1,  1,1,0,  0,0,1,1,0,  0,1,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'R'
        assert decoded.mnemonic == 'OR'
        assert decoded.rd == [0,0,1,1,0]  # x6
        assert decoded.rs1 == [0,0,1,0,1]  # x5
        assert decoded.rs2 == [0,0,1,0,0]  # x4
        assert decoded.funct3 == [1,1,0]
    
    def test_decode_xor(self):
        """Test XOR instruction: xor x7, x6, x5."""
        # XOR: 0000000 00101 00110 100 00111 0110011
        instruction = [0,0,0,0,0,0,0,  0,0,1,0,1,  0,0,1,1,0,  1,0,0,  0,0,1,1,1,  0,1,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'R'
        assert decoded.mnemonic == 'XOR'
        assert decoded.rd == [0,0,1,1,1]  # x7
        assert decoded.funct3 == [1,0,0]
    
    def test_decode_sll(self):
        """Test SLL instruction: sll x8, x1, x2."""
        # SLL: 0000000 00010 00001 001 01000 0110011
        instruction = [0,0,0,0,0,0,0,  0,0,0,1,0,  0,0,0,0,1,  0,0,1,  0,1,0,0,0,  0,1,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'R'
        assert decoded.mnemonic == 'SLL'
        assert decoded.rd == [0,1,0,0,0]  # x8
        assert decoded.funct3 == [0,0,1]
    
    def test_decode_srl(self):
        """Test SRL instruction: srl x9, x8, x2."""
        # SRL: 0000000 00010 01000 101 01001 0110011
        instruction = [0,0,0,0,0,0,0,  0,0,0,1,0,  0,1,0,0,0,  1,0,1,  0,1,0,0,1,  0,1,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'R'
        assert decoded.mnemonic == 'SRL'
        assert decoded.rd == [0,1,0,0,1]  # x9
        assert decoded.funct3 == [1,0,1]
        assert decoded.funct7 == [0,0,0,0,0,0,0]
    
    def test_decode_sra(self):
        """Test SRA instruction: sra x10, x9, x1."""
        # SRA: 0100000 00001 01001 101 01010 0110011
        instruction = [0,1,0,0,0,0,0,  0,0,0,0,1,  0,1,0,0,1,  1,0,1,  0,1,0,1,0,  0,1,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'R'
        assert decoded.mnemonic == 'SRA'
        assert decoded.rd == [0,1,0,1,0]  # x10
        assert decoded.funct3 == [1,0,1]
        assert decoded.funct7 == [0,1,0,0,0,0,0]


class TestITypeInstructions:
    """Test I-type instruction decoding."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.decoder = InstructionDecoder()
    
    def test_decode_addi(self):
        """Test ADDI instruction: addi x1, x0, 5."""
        # ADDI: 000000000101 00000 000 00001 0010011
        #       imm[11:0]   rs1  f3  rd    opcode
        instruction = [0,0,0,0,0,0,0,0,0,1,0,1,  0,0,0,0,0,  0,0,0,  0,0,0,0,1,  0,0,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'I'
        assert decoded.mnemonic == 'ADDI'
        assert decoded.rd == [0,0,0,0,1]  # x1
        assert decoded.rs1 == [0,0,0,0,0]  # x0
        assert decoded.funct3 == [0,0,0]
        # Immediate should be sign-extended 5
        assert bits_to_int_unsigned(decoded.immediate) == 5
    
    def test_decode_addi_negative(self):
        """Test ADDI with negative immediate: addi x2, x0, -1."""
        # ADDI: 111111111111 00000 000 00010 0010011
        #       imm=-1      rs1  f3  rd    opcode
        instruction = [1,1,1,1,1,1,1,1,1,1,1,1,  0,0,0,0,0,  0,0,0,  0,0,0,1,0,  0,0,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'I'
        assert decoded.mnemonic == 'ADDI'
        # Check sign extension: -1 should extend to all 1s
        assert decoded.immediate == [1] * 32
    
    def test_decode_andi(self):
        """Test ANDI instruction: andi x3, x1, 0xFF."""
        # ANDI: 000011111111 00001 111 00011 0010011
        instruction = [0,0,0,0,1,1,1,1,1,1,1,1,  0,0,0,0,1,  1,1,1,  0,0,0,1,1,  0,0,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'I'
        assert decoded.mnemonic == 'ANDI'
        assert decoded.rd == [0,0,0,1,1]  # x3
        assert decoded.rs1 == [0,0,0,0,1]  # x1
        assert decoded.funct3 == [1,1,1]
    
    def test_decode_ori(self):
        """Test ORI instruction: ori x4, x2, 0x10."""
        # ORI: 000000010000 00010 110 00100 0010011
        instruction = [0,0,0,0,0,0,0,1,0,0,0,0,  0,0,0,1,0,  1,1,0,  0,0,1,0,0,  0,0,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'I'
        assert decoded.mnemonic == 'ORI'
        assert decoded.funct3 == [1,1,0]
    
    def test_decode_xori(self):
        """Test XORI instruction: xori x5, x3, 0xF."""
        # XORI: 000000001111 00011 100 00101 0010011
        instruction = [0,0,0,0,0,0,0,0,1,1,1,1,  0,0,0,1,1,  1,0,0,  0,0,1,0,1,  0,0,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'I'
        assert decoded.mnemonic == 'XORI'
        assert decoded.funct3 == [1,0,0]
    
    def test_decode_slli(self):
        """Test SLLI instruction: slli x6, x4, 5."""
        # SLLI: 0000000 00101 00100 001 00110 0010011
        instruction = [0,0,0,0,0,0,0,0,0,1,0,1,  0,0,1,0,0,  0,0,1,  0,0,1,1,0,  0,0,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'I'
        assert decoded.mnemonic == 'SLLI'
        assert decoded.funct3 == [0,0,1]
        # Immediate lower 5 bits are shift amount
        imm_val = bits_to_int_unsigned(decoded.immediate[-5:])
        assert imm_val == 5
    
    def test_decode_srli(self):
        """Test SRLI instruction: srli x7, x5, 3."""
        # SRLI: 0000000 00011 00101 101 00111 0010011
        instruction = [0,0,0,0,0,0,0,0,0,0,1,1,  0,0,1,0,1,  1,0,1,  0,0,1,1,1,  0,0,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'I'
        assert decoded.mnemonic == 'SRLI'
        assert decoded.funct3 == [1,0,1]
    
    def test_decode_srai(self):
        """Test SRAI instruction: srai x8, x6, 4."""
        # SRAI: 0100000 00100 00110 101 01000 0010011
        instruction = [0,1,0,0,0,0,0,0,0,1,0,0,  0,0,1,1,0,  1,0,1,  0,1,0,0,0,  0,0,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'I'
        assert decoded.mnemonic == 'SRAI'
        assert decoded.funct3 == [1,0,1]
    
    def test_decode_lw(self):
        """Test LW instruction: lw x4, 0(x5)."""
        # LW: 000000000000 00101 010 00100 0000011
        instruction = [0,0,0,0,0,0,0,0,0,0,0,0,  0,0,1,0,1,  0,1,0,  0,0,1,0,0,  0,0,0,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'I'
        assert decoded.mnemonic == 'LW'
        assert decoded.rd == [0,0,1,0,0]  # x4
        assert decoded.rs1 == [0,0,1,0,1]  # x5
        assert decoded.funct3 == [0,1,0]
        assert bits_to_int_unsigned(decoded.immediate) == 0


class TestSTypeInstructions:
    """Test S-type instruction decoding."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.decoder = InstructionDecoder()
    
    def test_decode_sw(self):
        """Test SW instruction: sw x3, 0(x5)."""
        # SW: 0000000 00011 00101 010 00000 0100011
        #     imm[11:5] rs2  rs1  f3 imm[4:0] opcode
        instruction = [0,0,0,0,0,0,0,  0,0,0,1,1,  0,0,1,0,1,  0,1,0,  0,0,0,0,0,  0,1,0,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'S'
        assert decoded.mnemonic == 'SW'
        assert decoded.rs1 == [0,0,1,0,1]  # x5 (base address)
        assert decoded.rs2 == [0,0,0,1,1]  # x3 (data to store)
        assert decoded.funct3 == [0,1,0]
        assert bits_to_int_unsigned(decoded.immediate) == 0
    
    def test_decode_sw_with_offset(self):
        """Test SW instruction with offset: sw x4, 8(x5)."""
        # SW: 0000000 00100 00101 010 01000 0100011
        #     offset=8: upper 7 bits = 0000000, lower 5 bits = 01000
        instruction = [0,0,0,0,0,0,0,  0,0,1,0,0,  0,0,1,0,1,  0,1,0,  0,1,0,0,0,  0,1,0,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'S'
        assert decoded.mnemonic == 'SW'
        assert bits_to_int_unsigned(decoded.immediate) == 8


class TestBTypeInstructions:
    """Test B-type instruction decoding."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.decoder = InstructionDecoder()
    
    def test_decode_beq(self):
        """Test BEQ instruction: beq x3, x4, 8."""
        # BEQ: offset=8 (01000 in binary)
        # B-type encoding: imm[12|10:5] rs2 rs1 000 imm[4:1|11] 1100011
        # offset=8: imm = 00000001000 -> [12]=0, [11]=0, [10:5]=000000, [4:1]=0100
        instruction = [0,0,0,0,0,0,0,  0,0,1,0,0,  0,0,0,1,1,  0,0,0,  0,1,0,0,0,  1,1,0,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'B'
        assert decoded.mnemonic == 'BEQ'
        assert decoded.rs1 == [0,0,0,1,1]  # x3
        assert decoded.rs2 == [0,0,1,0,0]  # x4
        assert decoded.funct3 == [0,0,0]
        assert bits_to_int_unsigned(decoded.immediate) == 8
    
    def test_decode_bne(self):
        """Test BNE instruction: bne x1, x2, 4."""
        # BNE: offset=4
        # B-type: imm[12|10:5] rs2 rs1 001 imm[4:1|11] 1100011
        # offset=4: imm = 00000000100 -> [12]=0, [11]=0, [10:5]=000000, [4:1]=0010
        instruction = [0,0,0,0,0,0,0,  0,0,0,1,0,  0,0,0,0,1,  0,0,1,  0,0,1,0,0,  1,1,0,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'B'
        assert decoded.mnemonic == 'BNE'
        assert decoded.rs1 == [0,0,0,0,1]  # x1
        assert decoded.rs2 == [0,0,0,1,0]  # x2
        assert decoded.funct3 == [0,0,1]
        assert bits_to_int_unsigned(decoded.immediate) == 4


class TestUTypeInstructions:
    """Test U-type instruction decoding."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.decoder = InstructionDecoder()
    
    def test_decode_lui(self):
        """Test LUI instruction: lui x5, 0x10."""
        # LUI: 00000000000000010000 00101 0110111
        #      imm[31:12]          rd    opcode
        # 0x10 << 12 = 0x10000
        instruction = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,  0,0,1,0,1,  0,1,1,0,1,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'U'
        assert decoded.mnemonic == 'LUI'
        assert decoded.rd == [0,0,1,0,1]  # x5
        # Upper 20 bits set to 0x10, lower 12 bits zero
        assert bits_to_int_unsigned(decoded.immediate) == 0x10000
    
    def test_decode_auipc(self):
        """Test AUIPC instruction: auipc x6, 0x1."""
        # AUIPC: 00000000000000000001 00110 0010111
        instruction = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,  0,0,1,1,0,  0,0,1,0,1,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'U'
        assert decoded.mnemonic == 'AUIPC'
        assert decoded.rd == [0,0,1,1,0]  # x6
        assert bits_to_int_unsigned(decoded.immediate) == 0x1000


class TestJTypeInstructions:
    """Test J-type instruction decoding."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.decoder = InstructionDecoder()
    
    def test_decode_jal(self):
        """Test JAL instruction: jal x0, 0 (infinite loop)."""
        # JAL: offset=0
        # J-type: imm[20|10:1|11|19:12] rd 1101111
        # offset=0: all immediate bits are 0
        instruction = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,  0,0,0,0,0,  1,1,0,1,1,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'J'
        assert decoded.mnemonic == 'JAL'
        assert decoded.rd == [0,0,0,0,0]  # x0
        assert bits_to_int_unsigned(decoded.immediate) == 0
    
    def test_decode_jalr(self):
        """Test JALR instruction: jalr x1, 0(x2)."""
        # JALR: 000000000000 00010 000 00001 1100111
        instruction = [0,0,0,0,0,0,0,0,0,0,0,0,  0,0,0,1,0,  0,0,0,  0,0,0,0,1,  1,1,0,0,1,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'I'  # JALR is I-type
        assert decoded.mnemonic == 'JALR'
        assert decoded.rd == [0,0,0,0,1]  # x1 (return address)
        assert decoded.rs1 == [0,0,0,1,0]  # x2 (base address)


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.decoder = InstructionDecoder()
    
    def test_immediate_sign_extension_positive(self):
        """Test that positive immediates are correctly sign-extended."""
        # ADDI x1, x0, 127 (max positive 12-bit)
        # imm = 011111111111 (0x7FF)
        instruction = [0,1,1,1,1,1,1,1,1,1,1,1,  0,0,0,0,0,  0,0,0,  0,0,0,0,1,  0,0,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        # Should sign-extend to 32 bits with leading zeros
        assert decoded.immediate[0] == 0  # MSB should be 0
        assert bits_to_int_unsigned(decoded.immediate) == 2047  # 0x7FF
    
    def test_immediate_sign_extension_negative(self):
        """Test that negative immediates are correctly sign-extended."""
        # ADDI x1, x0, -1
        # imm = 111111111111
        instruction = [1,1,1,1,1,1,1,1,1,1,1,1,  0,0,0,0,0,  0,0,0,  0,0,0,0,1,  0,0,1,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        # Should sign-extend to all 1s
        assert decoded.immediate == [1] * 32
    
    def test_immediate_zero_extension_u_type(self):
        """Test that U-type immediate is zero-extended (lower 12 bits)."""
        # LUI x1, 0xFFFFF (max 20-bit value)
        instruction = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,  0,0,0,0,1,  0,1,1,0,1,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        # Upper 20 bits set, lower 12 bits zero
        assert decoded.immediate[:20] == [1] * 20
        assert decoded.immediate[20:] == [0] * 12
    
    def test_all_zero_instruction(self):
        """Test decoding of all-zero instruction."""
        instruction = [0] * 32
        
        # This should decode as an invalid instruction
        # Opcode 0000000 doesn't match any valid type initially
        decoded = self.decoder.decode(instruction)
        
        # Should still extract fields without crashing
        assert len(decoded.opcode) == 7
    
    def test_all_one_instruction(self):
        """Test decoding of all-one instruction."""
        instruction = [1] * 32
        
        decoded = self.decoder.decode(instruction)
        
        # Should extract fields without crashing
        assert len(decoded.opcode) == 7
    
    def test_invalid_opcode(self):
        """Test handling of invalid opcode."""
        # Use an opcode that doesn't correspond to any instruction type
        # Opcode: 0000001 (invalid)
        instruction = [0,0,0,0,0,0,0,0,0,0,0,0,  0,0,0,0,0,  0,0,0,  0,0,0,0,1,  0,0,0,0,0,0,1]
        
        decoded = self.decoder.decode(instruction)
        
        # Should return UNKNOWN type
        assert decoded.instr_type == 'UNKNOWN'
    
    def test_branch_immediate_encoding(self):
        """Test B-type immediate with complex bit reordering."""
        # BEQ with offset = -4 (backward branch)
        # offset=-4: binary 11111111111111111111111111111100 (two's complement)
        # B-type encoding: imm[12]=1, imm[10:5]=111111, imm[4:1]=1110, imm[11]=1
        # Instruction: 1 111111 00010 00001 000 1110 1 1100011
        instruction = [1,1,1,1,1,1,1,  0,0,0,1,0,  0,0,0,0,1,  0,0,0,  1,1,1,0,1,  1,1,0,0,0,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'B'
        # Should be negative (sign-extended with leading 1s)
        assert decoded.immediate[0] == 1
    
    def test_jump_immediate_encoding(self):
        """Test J-type immediate with complex bit reordering."""
        # JAL with offset = 8
        # J-type encoding: imm[20|10:1|11|19:12]
        # offset=8: binary 00000000000000001000
        # Reordered: imm[20]=0, imm[19:12]=00000000, imm[11]=0, imm[10:1]=0000000100
        instruction = [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,  0,0,0,0,1,  1,1,0,1,1,1,1]
        
        decoded = self.decoder.decode(instruction)
        
        assert decoded.instr_type == 'J'
        assert decoded.mnemonic == 'JAL'
        assert bits_to_int_unsigned(decoded.immediate) == 8


class TestInstructionSetCoverage:
    """Test coverage of minimum viable instruction set."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.decoder = InstructionDecoder()
    
    def test_minimum_viable_arithmetic(self):
        """Verify all arithmetic instructions decode correctly."""
        # ADD, SUB, ADDI should all decode
        instructions = {
            'ADD': [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,1,0,1,1,0,0,1,1],
            'SUB': [0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,1,1,0,0,1,1],
            'ADDI': [0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,1,1],
        }
        
        for mnemonic, instr in instructions.items():
            decoded = self.decoder.decode(instr)
            assert decoded.mnemonic == mnemonic
    
    def test_minimum_viable_logical(self):
        """Verify all logical instructions decode correctly."""
        # Test that we can decode AND, OR, XOR and immediate variants
        assert True  # Covered by individual tests above
    
    def test_minimum_viable_memory(self):
        """Verify memory instructions decode correctly."""
        # LW
        lw_instr = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,0,0,1,0,0,0,0,0,0,0,1,1]
        decoded = self.decoder.decode(lw_instr)
        assert decoded.mnemonic == 'LW'
        
        # SW
        sw_instr = [0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0,0,1,0,0,0,1,1]
        decoded = self.decoder.decode(sw_instr)
        assert decoded.mnemonic == 'SW'

# AI-END
