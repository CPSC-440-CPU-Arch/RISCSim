# AI-BEGIN
"""
RISC-V Instruction Decoder for RV32I base instruction set.

Decodes 32-bit RISC-V instructions into their component fields and generates
appropriate control signals for the datapath.

Supports all six RISC-V instruction formats:
- R-type: Register-register operations (ADD, SUB, AND, OR, XOR, SLL, SRL, SRA)
- I-type: Immediate operations (ADDI, ANDI, ORI, XORI, SLLI, SRLI, SRAI, LW, JALR)
- S-type: Store operations (SW)
- B-type: Branch operations (BEQ, BNE)
- U-type: Upper immediate operations (LUI, AUIPC)
- J-type: Jump operations (JAL)

Convention: All bit arrays use MSB-at-index-0 convention.
"""

from typing import List, Tuple, Optional
from riscsim.utils.bit_utils import (
    slice_bits, concat_bits, sign_extend, zero_extend
)


class DecodedInstruction:
    """Container for decoded instruction fields.
    
    Attributes:
        instr_type: Instruction format type ('R', 'I', 'S', 'B', 'U', 'J')
        opcode: 7-bit opcode field
        funct3: 3-bit function field (for R, I, S, B types)
        funct7: 7-bit function field (for R-type)
        rd: 5-bit destination register
        rs1: 5-bit source register 1
        rs2: 5-bit source register 2
        immediate: 32-bit sign-extended immediate value
        mnemonic: Human-readable instruction name (e.g., 'ADD', 'ADDI')
    """
    
    def __init__(self):
        self.instr_type: str = ""
        self.opcode: List[int] = []
        self.funct3: List[int] = []
        self.funct7: List[int] = []
        self.rd: List[int] = []
        self.rs1: List[int] = []
        self.rs2: List[int] = []
        self.immediate: List[int] = []
        self.mnemonic: str = ""
        
    def __repr__(self):
        return (f"DecodedInstruction({self.mnemonic}, type={self.instr_type}, "
                f"rd={self.rd}, rs1={self.rs1}, rs2={self.rs2})")


class InstructionDecoder:
    """
    Decode 32-bit RISC-V instructions into control signals.
    
    The decoder extracts instruction fields based on the RISC-V instruction format
    and generates appropriate control signals for the datapath.
    
    RISC-V Instruction Format Breakdown (bit positions):
    
    R-type: funct7[31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]
    I-type: imm[31:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]
    S-type: imm[31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | imm[11:7] | opcode[6:0]
    B-type: imm[31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | imm[11:7] | opcode[6:0]
    U-type: imm[31:12] | rd[11:7] | opcode[6:0]
    J-type: imm[31:12] | rd[11:7] | opcode[6:0]
    
    All operations use bit-level manipulation without host arithmetic operators.
    """
    
    def __init__(self):
        """Initialize the instruction decoder."""
        pass
    
    def decode(self, instruction: List[int]) -> DecodedInstruction:
        """
        Decode a 32-bit RISC-V instruction.
        
        Args:
            instruction: 32-bit instruction as bit array [MSB...LSB]
            
        Returns:
            DecodedInstruction object with all fields populated
            
        Raises:
            ValueError: If instruction format is invalid
        """
        if len(instruction) != 32:
            raise ValueError(f"Instruction must be 32 bits, got {len(instruction)}")
        
        decoded = DecodedInstruction()
        
        # Extract opcode (bits 6:0)
        decoded.opcode = self.extract_opcode(instruction)
        
        # Determine instruction type based on opcode
        decoded.instr_type = self._identify_instruction_type(decoded.opcode)
        
        # Extract fields based on instruction type
        if decoded.instr_type == 'R':
            decoded.rd = self.extract_rd(instruction)
            decoded.rs1 = self.extract_rs1(instruction)
            decoded.rs2 = self.extract_rs2(instruction)
            decoded.funct3 = self.extract_funct3(instruction)
            decoded.funct7 = self.extract_funct7(instruction)
            decoded.immediate = [0] * 32  # R-type has no immediate
            decoded.mnemonic = self._decode_r_type(decoded.funct3, decoded.funct7)
            
        elif decoded.instr_type == 'I':
            decoded.rd = self.extract_rd(instruction)
            decoded.rs1 = self.extract_rs1(instruction)
            decoded.funct3 = self.extract_funct3(instruction)
            decoded.immediate = self.extract_imm_i(instruction)
            decoded.mnemonic = self._decode_i_type(decoded.opcode, decoded.funct3, instruction)
            
        elif decoded.instr_type == 'S':
            decoded.rs1 = self.extract_rs1(instruction)
            decoded.rs2 = self.extract_rs2(instruction)
            decoded.funct3 = self.extract_funct3(instruction)
            decoded.immediate = self.extract_imm_s(instruction)
            decoded.mnemonic = self._decode_s_type(decoded.funct3)
            
        elif decoded.instr_type == 'B':
            decoded.rs1 = self.extract_rs1(instruction)
            decoded.rs2 = self.extract_rs2(instruction)
            decoded.funct3 = self.extract_funct3(instruction)
            decoded.immediate = self.extract_imm_b(instruction)
            decoded.mnemonic = self._decode_b_type(decoded.funct3)
            
        elif decoded.instr_type == 'U':
            decoded.rd = self.extract_rd(instruction)
            decoded.immediate = self.extract_imm_u(instruction)
            decoded.mnemonic = self._decode_u_type(decoded.opcode)
            
        elif decoded.instr_type == 'J':
            decoded.rd = self.extract_rd(instruction)
            decoded.immediate = self.extract_imm_j(instruction)
            decoded.mnemonic = 'JAL'
            
        else:
            # Unknown instruction type - extract basic fields but don't decode
            decoded.rd = self.extract_rd(instruction)
            decoded.rs1 = self.extract_rs1(instruction)
            decoded.rs2 = self.extract_rs2(instruction)
            decoded.funct3 = self.extract_funct3(instruction)
            decoded.funct7 = self.extract_funct7(instruction)
            decoded.immediate = [0] * 32
            decoded.mnemonic = 'UNKNOWN'
        
        return decoded
    
    def extract_opcode(self, instruction: List[int]) -> List[int]:
        """Extract opcode field (bits 6:0).
        
        Args:
            instruction: 32-bit instruction
            
        Returns:
            7-bit opcode
        """
        # Opcode is bits [31:25] in MSB-first convention (last 7 bits)
        return slice_bits(instruction, 25, 32)
    
    def extract_funct3(self, instruction: List[int]) -> List[int]:
        """Extract funct3 field (bits 14:12).
        
        Args:
            instruction: 32-bit instruction
            
        Returns:
            3-bit funct3
        """
        # funct3 is bits [14:12] -> indices [17:20] in MSB-first
        return slice_bits(instruction, 17, 20)
    
    def extract_funct7(self, instruction: List[int]) -> List[int]:
        """Extract funct7 field (bits 31:25).
        
        Args:
            instruction: 32-bit instruction
            
        Returns:
            7-bit funct7
        """
        # funct7 is bits [31:25] -> indices [0:7] in MSB-first
        return slice_bits(instruction, 0, 7)
    
    def extract_rd(self, instruction: List[int]) -> List[int]:
        """Extract rd (destination register) field (bits 11:7).
        
        Args:
            instruction: 32-bit instruction
            
        Returns:
            5-bit register number
        """
        # rd is bits [11:7] -> indices [20:25] in MSB-first
        return slice_bits(instruction, 20, 25)
    
    def extract_rs1(self, instruction: List[int]) -> List[int]:
        """Extract rs1 (source register 1) field (bits 19:15).
        
        Args:
            instruction: 32-bit instruction
            
        Returns:
            5-bit register number
        """
        # rs1 is bits [19:15] -> indices [12:17] in MSB-first
        return slice_bits(instruction, 12, 17)
    
    def extract_rs2(self, instruction: List[int]) -> List[int]:
        """Extract rs2 (source register 2) field (bits 24:20).
        
        Args:
            instruction: 32-bit instruction
            
        Returns:
            5-bit register number
        """
        # rs2 is bits [24:20] -> indices [7:12] in MSB-first
        return slice_bits(instruction, 7, 12)
    
    def extract_imm_i(self, instruction: List[int]) -> List[int]:
        """Extract I-type immediate (bits 31:20) with sign extension.
        
        I-type immediate: imm[31:20]
        
        Args:
            instruction: 32-bit instruction
            
        Returns:
            32-bit sign-extended immediate
        """
        # I-type immediate is bits [31:20] -> indices [0:12] in MSB-first
        imm_12 = slice_bits(instruction, 0, 12)
        return sign_extend(imm_12, 32)
    
    def extract_imm_s(self, instruction: List[int]) -> List[int]:
        """Extract S-type immediate with sign extension.
        
        S-type immediate: imm[31:25] | imm[11:7]
        Reassemble: {imm[31:25], imm[11:7]}
        
        Args:
            instruction: 32-bit instruction
            
        Returns:
            32-bit sign-extended immediate
        """
        # S-type splits immediate: [31:25] and [11:7]
        imm_11_5 = slice_bits(instruction, 0, 7)   # bits [31:25]
        imm_4_0 = slice_bits(instruction, 20, 25)  # bits [11:7]
        imm_12 = concat_bits(imm_11_5, imm_4_0)  # Concatenate to form 12-bit
        return sign_extend(imm_12, 32)
    
    def extract_imm_b(self, instruction: List[int]) -> List[int]:
        """Extract B-type immediate with sign extension.
        
        B-type immediate encoding:
        imm[12|10:5] in bits[31:25], imm[4:1|11] in bits[11:7]
        Reassemble as: {imm[12], imm[10:5], imm[4:1], 0}
        
        Args:
            instruction: 32-bit instruction
            
        Returns:
            32-bit sign-extended immediate (always even, bit 0 = 0)
        """
        # B-type: imm[12] = bit[31], imm[10:5] = bits[30:25]
        #         imm[4:1] = bits[11:8], imm[11] = bit[7]
        imm_12 = slice_bits(instruction, 0, 1)     # bit[31]
        imm_10_5 = slice_bits(instruction, 1, 7)   # bits[30:25]
        imm_4_1 = slice_bits(instruction, 20, 24)  # bits[11:8]
        imm_11 = slice_bits(instruction, 24, 25)   # bit[7]
        
        # Reassemble: imm[12:11:10:5:4:1:0]
        imm_13 = concat_bits(imm_12, imm_11, imm_10_5, imm_4_1, [0])
        return sign_extend(imm_13, 32)
    
    def extract_imm_u(self, instruction: List[int]) -> List[int]:
        """Extract U-type immediate (bits 31:12) with zero extension.
        
        U-type immediate: imm[31:12] in upper 20 bits, lower 12 bits = 0
        
        Args:
            instruction: 32-bit instruction
            
        Returns:
            32-bit immediate (upper 20 bits set, lower 12 bits zero)
        """
        # U-type: imm[31:12] -> indices [0:20]
        imm_31_12 = slice_bits(instruction, 0, 20)
        # Append 12 zero bits for lower portion
        return concat_bits(imm_31_12, [0] * 12)
    
    def extract_imm_j(self, instruction: List[int]) -> List[int]:
        """Extract J-type immediate with sign extension.
        
        J-type immediate encoding:
        imm[20|10:1|11|19:12] in bits[31:12]
        Reassemble as: {imm[20], imm[19:12], imm[11], imm[10:1], 0}
        
        Args:
            instruction: 32-bit instruction
            
        Returns:
            32-bit sign-extended immediate (always even, bit 0 = 0)
        """
        # J-type: imm[20] = bit[31], imm[10:1] = bits[30:21]
        #         imm[11] = bit[20], imm[19:12] = bits[19:12]
        imm_20 = slice_bits(instruction, 0, 1)      # bit[31]
        imm_10_1 = slice_bits(instruction, 1, 11)   # bits[30:21]
        imm_11 = slice_bits(instruction, 11, 12)    # bit[20]
        imm_19_12 = slice_bits(instruction, 12, 20) # bits[19:12]
        
        # Reassemble: imm[20:19:12:11:10:1:0]
        imm_21 = concat_bits(imm_20, imm_19_12, imm_11, imm_10_1, [0])
        return sign_extend(imm_21, 32)
    
    def _identify_instruction_type(self, opcode: List[int]) -> str:
        """Identify instruction type from opcode.
        
        Args:
            opcode: 7-bit opcode
            
        Returns:
            Instruction type: 'R', 'I', 'S', 'B', 'U', 'J'
        """
        # Convert opcode to comparable format (MSB-first: bits 6:0)
        # R-type: 0110011 (0x33)
        # I-type: 0010011 (0x13) - immediate ALU ops
        #         0000011 (0x03) - load
        #         1100111 (0x67) - JALR
        # S-type: 0100011 (0x23)
        # B-type: 1100011 (0x63)
        # U-type: 0110111 (0x37) - LUI
        #         0010111 (0x17) - AUIPC
        # J-type: 1101111 (0x6F) - JAL
        
        if opcode == [0,1,1,0,0,1,1]:  # 0110011
            return 'R'
        elif opcode == [0,0,1,0,0,1,1]:  # 0010011 (immediate ALU)
            return 'I'
        elif opcode == [0,0,0,0,0,1,1]:  # 0000011 (load)
            return 'I'
        elif opcode == [1,1,0,0,1,1,1]:  # 1100111 (JALR)
            return 'I'
        elif opcode == [0,1,0,0,0,1,1]:  # 0100011 (store)
            return 'S'
        elif opcode == [1,1,0,0,0,1,1]:  # 1100011 (branch)
            return 'B'
        elif opcode == [0,1,1,0,1,1,1]:  # 0110111 (LUI)
            return 'U'
        elif opcode == [0,0,1,0,1,1,1]:  # 0010111 (AUIPC)
            return 'U'
        elif opcode == [1,1,0,1,1,1,1]:  # 1101111 (JAL)
            return 'J'
        else:
            # Unknown opcode
            return 'UNKNOWN'
    
    def _decode_r_type(self, funct3: List[int], funct7: List[int]) -> str:
        """Decode R-type instruction mnemonic.
        
        Args:
            funct3: 3-bit function code
            funct7: 7-bit function code
            
        Returns:
            Instruction mnemonic
        """
        # funct3 determines base operation
        # funct7 distinguishes variants (e.g., ADD vs SUB, SRL vs SRA)
        
        if funct3 == [0,0,0]:  # 000
            if funct7 == [0,0,0,0,0,0,0]:  # 0000000
                return 'ADD'
            elif funct7 == [0,1,0,0,0,0,0]:  # 0100000
                return 'SUB'
        elif funct3 == [0,0,1]:  # 001
            return 'SLL'
        elif funct3 == [0,1,0]:  # 010
            return 'SLT'
        elif funct3 == [0,1,1]:  # 011
            return 'SLTU'
        elif funct3 == [1,0,0]:  # 100
            return 'XOR'
        elif funct3 == [1,0,1]:  # 101
            if funct7 == [0,0,0,0,0,0,0]:  # 0000000
                return 'SRL'
            elif funct7 == [0,1,0,0,0,0,0]:  # 0100000
                return 'SRA'
        elif funct3 == [1,1,0]:  # 110
            return 'OR'
        elif funct3 == [1,1,1]:  # 111
            return 'AND'
        
        return 'UNKNOWN_R'
    
    def _decode_i_type(self, opcode: List[int], funct3: List[int], 
                       instruction: List[int]) -> str:
        """Decode I-type instruction mnemonic.
        
        Args:
            opcode: 7-bit opcode
            funct3: 3-bit function code
            instruction: Full 32-bit instruction (for shift amount check)
            
        Returns:
            Instruction mnemonic
        """
        # Check if immediate ALU op (0010011) or load (0000011) or JALR (1100111)
        if opcode == [0,0,1,0,0,1,1]:  # 0x13 - immediate ALU
            if funct3 == [0,0,0]:  # 000
                return 'ADDI'
            elif funct3 == [0,0,1]:  # 001
                # SLLI: check funct7 (bits 31:25) should be 0000000
                return 'SLLI'
            elif funct3 == [0,1,0]:  # 010
                return 'SLTI'
            elif funct3 == [0,1,1]:  # 011
                return 'SLTIU'
            elif funct3 == [1,0,0]:  # 100
                return 'XORI'
            elif funct3 == [1,0,1]:  # 101
                # Check bit 30 (index 1) to distinguish SRLI vs SRAI
                funct7_bit = instruction[1]  # bit 30
                if funct7_bit == 0:
                    return 'SRLI'
                else:
                    return 'SRAI'
            elif funct3 == [1,1,0]:  # 110
                return 'ORI'
            elif funct3 == [1,1,1]:  # 111
                return 'ANDI'
        elif opcode == [0,0,0,0,0,1,1]:  # 0x03 - load
            if funct3 == [0,1,0]:  # 010
                return 'LW'
            # Can add LB, LH, LBU, LHU here
        elif opcode == [1,1,0,0,1,1,1]:  # 0x67 - JALR
            return 'JALR'
        
        return 'UNKNOWN_I'
    
    def _decode_s_type(self, funct3: List[int]) -> str:
        """Decode S-type instruction mnemonic.
        
        Args:
            funct3: 3-bit function code
            
        Returns:
            Instruction mnemonic
        """
        if funct3 == [0,1,0]:  # 010
            return 'SW'
        # Can add SB, SH here
        return 'UNKNOWN_S'
    
    def _decode_b_type(self, funct3: List[int]) -> str:
        """Decode B-type instruction mnemonic.
        
        Args:
            funct3: 3-bit function code
            
        Returns:
            Instruction mnemonic
        """
        if funct3 == [0,0,0]:  # 000
            return 'BEQ'
        elif funct3 == [0,0,1]:  # 001
            return 'BNE'
        elif funct3 == [1,0,0]:  # 100
            return 'BLT'
        elif funct3 == [1,0,1]:  # 101
            return 'BGE'
        elif funct3 == [1,1,0]:  # 110
            return 'BLTU'
        elif funct3 == [1,1,1]:  # 111
            return 'BGEU'
        return 'UNKNOWN_B'
    
    def _decode_u_type(self, opcode: List[int]) -> str:
        """Decode U-type instruction mnemonic.
        
        Args:
            opcode: 7-bit opcode
            
        Returns:
            Instruction mnemonic
        """
        if opcode == [0,1,1,0,1,1,1]:  # 0110111 - LUI
            return 'LUI'
        elif opcode == [0,0,1,0,1,1,1]:  # 0010111 - AUIPC
            return 'AUIPC'
        return 'UNKNOWN_U'

# AI-END
