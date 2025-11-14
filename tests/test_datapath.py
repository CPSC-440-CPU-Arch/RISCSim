# AI-BEGIN: Claude Code (Anthropic) - November 14, 2025
# Prompt: "Create comprehensive Phase 3 datapath tests covering arithmetic, logical, shifts, memory, branches, jumps, and integration"
"""
Comprehensive Test Suite for Single-Cycle Datapath

Tests all aspects of the datapath including:
- Arithmetic operations (ADD, ADDI, SUB)
- Logical operations (AND, OR, XOR)
- Shift operations (SLL, SRL, SRA)
- Memory operations (LW, SW)
- Branch operations (BEQ, BNE)
- Jump operations (JAL, JALR)
- Upper immediate operations (LUI, AUIPC)
- Integration scenarios

Author: RISCSim Team
Date: November 14, 2025
"""

import pytest
from riscsim.cpu.datapath import Datapath, CycleResult
from riscsim.cpu.memory import Memory
from riscsim.cpu.registers import RegisterFile
from riscsim.utils.bit_utils import (
    int_to_bits_unsigned,
    bits_to_int_unsigned
)


class TestArithmetic:
    """Test arithmetic instructions through the datapath."""
    
    def test_add_instruction(self):
        """Test ADD R-type instruction: add x3, x1, x2"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load ADD x3, x1, x2 instruction
        # ADD: opcode=0110011, funct3=000, funct7=0000000
        # Encoding: 0000000 00010 00001 000 00011 0110011
        # = 0x002081B3
        addr = int_to_bits_unsigned(0x00000000, 32)
        instruction = int_to_bits_unsigned(0x002081B3, 32)
        mem.write_word(addr, instruction)
        
        # Set x1 = 5, x2 = 10
        rf.write_int_reg(1, int_to_bits_unsigned(5, 32))
        rf.write_int_reg(2, int_to_bits_unsigned(10, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify
        assert result.decoded.mnemonic == 'ADD'
        assert bits_to_int_unsigned(rf.read_int_reg(3)) == 15
        assert result.branch_taken == False
        
    def test_addi_instruction(self):
        """Test ADDI I-type instruction: addi x1, x0, 5"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load ADDI x1, x0, 5 instruction
        # ADDI: opcode=0010011, funct3=000, imm=5
        # Encoding: 000000000101 00000 000 00001 0010011
        # = 0x00500093
        instruction = int_to_bits_unsigned(0x00500093, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify
        assert result.decoded.mnemonic == 'ADDI'
        assert bits_to_int_unsigned(rf.read_int_reg(1)) == 5
        
    def test_sub_instruction(self):
        """Test SUB R-type instruction: sub x4, x2, x1"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load SUB x4, x2, x1 instruction
        # SUB: opcode=0110011, funct3=000, funct7=0100000
        # Encoding: 0100000 00001 00010 000 00100 0110011
        # = 0x40110233
        instruction = int_to_bits_unsigned(0x40110233, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x1 = 5, x2 = 10
        rf.write_int_reg(1, int_to_bits_unsigned(5, 32))
        rf.write_int_reg(2, int_to_bits_unsigned(10, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify
        assert result.decoded.mnemonic == 'SUB'
        assert bits_to_int_unsigned(rf.read_int_reg(4)) == 5
        
    def test_arithmetic_with_zero_register(self):
        """Test that writes to x0 are ignored"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load ADDI x0, x0, 100 instruction
        # This should not change x0
        instruction = int_to_bits_unsigned(0x06400013, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify x0 is still 0
        assert bits_to_int_unsigned(rf.read_int_reg(0)) == 0
        
    def test_arithmetic_overflow(self):
        """Test arithmetic with values that cause overflow"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load ADD x3, x1, x2 instruction
        instruction = int_to_bits_unsigned(0x002081B3, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x1 and x2 to large values that overflow
        rf.write_int_reg(1, int_to_bits_unsigned(0x7FFFFFFF, 32))  # Max positive
        rf.write_int_reg(2, int_to_bits_unsigned(1, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify overflow wraps around (no exception)
        assert bits_to_int_unsigned(rf.read_int_reg(3)) == 0x80000000


class TestLogical:
    """Test logical instructions through the datapath."""
    
    def test_and_instruction(self):
        """Test AND R-type instruction: and x3, x1, x2"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load AND x3, x1, x2 instruction
        # AND: opcode=0110011, funct3=111, funct7=0000000
        # Encoding: 0000000 00010 00001 111 00011 0110011
        # = 0x0020F1B3
        instruction = int_to_bits_unsigned(0x0020F1B3, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x1 = 0xFF00, x2 = 0xF0F0
        rf.write_int_reg(1, int_to_bits_unsigned(0xFF00, 32))
        rf.write_int_reg(2, int_to_bits_unsigned(0xF0F0, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify x3 = 0xFF00 & 0xF0F0 = 0xF000
        assert result.decoded.mnemonic == 'AND'
        assert bits_to_int_unsigned(rf.read_int_reg(3)) == 0xF000
        
    def test_or_instruction(self):
        """Test OR R-type instruction: or x3, x1, x2"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load OR x3, x1, x2 instruction
        # OR: opcode=0110011, funct3=110, funct7=0000000
        # Encoding: 0000000 00010 00001 110 00011 0110011
        # = 0x0020E1B3
        instruction = int_to_bits_unsigned(0x0020E1B3, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x1 = 0x00FF, x2 = 0xFF00
        rf.write_int_reg(1, int_to_bits_unsigned(0x00FF, 32))
        rf.write_int_reg(2, int_to_bits_unsigned(0xFF00, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify x3 = 0x00FF | 0xFF00 = 0xFFFF
        assert result.decoded.mnemonic == 'OR'
        assert bits_to_int_unsigned(rf.read_int_reg(3)) == 0xFFFF
        
    def test_xor_instruction(self):
        """Test XOR R-type instruction: xor x3, x1, x2"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load XOR x3, x1, x2 instruction
        # XOR: opcode=0110011, funct3=100, funct7=0000000
        # Encoding: 0000000 00010 00001 100 00011 0110011
        # = 0x0020C1B3
        instruction = int_to_bits_unsigned(0x0020C1B3, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x1 = 0xFFFF, x2 = 0xF0F0
        rf.write_int_reg(1, int_to_bits_unsigned(0xFFFF, 32))
        rf.write_int_reg(2, int_to_bits_unsigned(0xF0F0, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify x3 = 0xFFFF ^ 0xF0F0 = 0x0F0F
        assert result.decoded.mnemonic == 'XOR'
        assert bits_to_int_unsigned(rf.read_int_reg(3)) == 0x0F0F


class TestShifts:
    """Test shift instructions through the datapath."""
    
    def test_sll_instruction(self):
        """Test SLL (shift left logical) instruction"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load SLL x3, x1, x2 instruction
        # SLL: opcode=0110011, funct3=001, funct7=0000000
        # Encoding: 0000000 00010 00001 001 00011 0110011
        # = 0x002091B3
        instruction = int_to_bits_unsigned(0x002091B3, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x1 = 0x00000001, x2 = 4 (shift amount)
        rf.write_int_reg(1, int_to_bits_unsigned(0x00000001, 32))
        rf.write_int_reg(2, int_to_bits_unsigned(4, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify x3 = 0x00000001 << 4 = 0x00000010
        assert result.decoded.mnemonic == 'SLL'
        assert bits_to_int_unsigned(rf.read_int_reg(3)) == 0x00000010
        
    def test_srl_instruction(self):
        """Test SRL (shift right logical) instruction"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load SRL x3, x1, x2 instruction
        # SRL: opcode=0110011, funct3=101, funct7=0000000
        # Encoding: 0000000 00010 00001 101 00011 0110011
        # = 0x0020D1B3
        instruction = int_to_bits_unsigned(0x0020D1B3, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x1 = 0x00000080, x2 = 4 (shift amount)
        rf.write_int_reg(1, int_to_bits_unsigned(0x00000080, 32))
        rf.write_int_reg(2, int_to_bits_unsigned(4, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify x3 = 0x00000080 >> 4 = 0x00000008
        assert result.decoded.mnemonic == 'SRL'
        assert bits_to_int_unsigned(rf.read_int_reg(3)) == 0x00000008
        
    def test_sra_instruction(self):
        """Test SRA (shift right arithmetic) instruction"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load SRA x3, x1, x2 instruction
        # SRA: opcode=0110011, funct3=101, funct7=0100000
        # Encoding: 0100000 00010 00001 101 00011 0110011
        # = 0x4020D1B3
        instruction = int_to_bits_unsigned(0x4020D1B3, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x1 = 0x80000000 (negative), x2 = 4 (shift amount)
        rf.write_int_reg(1, int_to_bits_unsigned(0x80000000, 32))
        rf.write_int_reg(2, int_to_bits_unsigned(4, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify x3 = 0x80000000 >> 4 (arithmetic) = 0xF8000000
        assert result.decoded.mnemonic == 'SRA'
        assert bits_to_int_unsigned(rf.read_int_reg(3)) == 0xF8000000


class TestMemory:
    """Test memory load/store instructions through the datapath."""
    
    def test_lw_instruction(self):
        """Test LW (load word) instruction"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Write test data to memory at data region
        test_data = int_to_bits_unsigned(0xDEADBEEF, 32)
        mem.write_word(int_to_bits_unsigned(0x00010000, 32), test_data)
        
        # Load LW x4, 0(x5) instruction
        # LW: opcode=0000011, funct3=010
        # Encoding: 000000000000 00101 010 00100 0000011
        # = 0x0002A203
        instruction = int_to_bits_unsigned(0x0002A203, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x5 = 0x00010000 (data region base)
        rf.write_int_reg(5, int_to_bits_unsigned(0x00010000, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify x4 contains loaded data
        assert result.decoded.mnemonic == 'LW'
        assert bits_to_int_unsigned(rf.read_int_reg(4)) == 0xDEADBEEF
        
    def test_sw_instruction(self):
        """Test SW (store word) instruction"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load SW x3, 0(x5) instruction
        # SW: opcode=0100011, funct3=010
        # Encoding: 0000000 00011 00101 010 00000 0100011
        # = 0x0032A023
        instruction = int_to_bits_unsigned(0x0032A023, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x3 = 0x12345678, x5 = 0x00010000
        rf.write_int_reg(3, int_to_bits_unsigned(0x12345678, 32))
        rf.write_int_reg(5, int_to_bits_unsigned(0x00010000, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify data written to memory
        assert result.decoded.mnemonic == 'SW'
        stored_data = mem.read_word(int_to_bits_unsigned(0x00010000, 32))
        assert bits_to_int_unsigned(stored_data) == 0x12345678
        
    def test_lw_sw_sequence(self):
        """Test store followed by load sequence"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Instruction 1: SW x3, 0(x5) at PC=0x00000000
        sw_instr = int_to_bits_unsigned(0x0032A023, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), sw_instr)
        
        # Instruction 2: LW x4, 0(x5) at PC=0x00000004
        lw_instr = int_to_bits_unsigned(0x0002A203, 32)
        mem.write_word(int_to_bits_unsigned(0x00000004, 32), lw_instr)
        
        # Set x3 = 15, x5 = 0x00010000
        rf.write_int_reg(3, int_to_bits_unsigned(15, 32))
        rf.write_int_reg(5, int_to_bits_unsigned(0x00010000, 32))
        
        # Execute SW
        result1 = datapath.execute_cycle()
        assert result1.decoded.mnemonic == 'SW'
        
        # Execute LW
        result2 = datapath.execute_cycle()
        assert result2.decoded.mnemonic == 'LW'
        
        # Verify x4 contains stored value
        assert bits_to_int_unsigned(rf.read_int_reg(4)) == 15
        
    def test_memory_alignment(self):
        """Test that memory operations respect word alignment"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load LW x4, 0(x5) instruction
        instruction = int_to_bits_unsigned(0x0002A203, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x5 to aligned address
        rf.write_int_reg(5, int_to_bits_unsigned(0x00010000, 32))
        
        # Should execute without error
        result = datapath.execute_cycle()
        assert result.decoded.mnemonic == 'LW'


class TestBranches:
    """Test branch instructions through the datapath."""
    
    def test_beq_taken(self):
        """Test BEQ (branch if equal) when condition is true"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load BEQ x3, x4, 8 instruction (branch forward 8 bytes)
        # BEQ: opcode=1100011, funct3=000
        # imm = 8 = [0,0,0,0,0,0,0,0,1,0,0,0]
        # Encoding: 0 000000 00100 00011 000 1000 0 1100011
        # = 0x00418463
        instruction = int_to_bits_unsigned(0x00418463, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x3 = x4 = 15 (equal)
        rf.write_int_reg(3, int_to_bits_unsigned(15, 32))
        rf.write_int_reg(4, int_to_bits_unsigned(15, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify branch taken and PC updated
        assert result.decoded.mnemonic == 'BEQ'
        assert result.branch_taken == True
        # PC should be 0x00000000 + 8 = 0x00000008
        assert bits_to_int_unsigned(datapath.get_pc()) == 0x00000008
        
    def test_beq_not_taken(self):
        """Test BEQ (branch if equal) when condition is false"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load BEQ x3, x4, 8 instruction
        instruction = int_to_bits_unsigned(0x00418463, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x3 = 15, x4 = 10 (not equal)
        rf.write_int_reg(3, int_to_bits_unsigned(15, 32))
        rf.write_int_reg(4, int_to_bits_unsigned(10, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify branch not taken, PC incremented normally
        assert result.decoded.mnemonic == 'BEQ'
        assert result.branch_taken == False
        # PC should be 0x00000000 + 4 = 0x00000004
        assert bits_to_int_unsigned(datapath.get_pc()) == 0x00000004
        
    def test_bne_taken(self):
        """Test BNE (branch if not equal) when condition is true"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load BNE x3, x4, 8 instruction
        # BNE: opcode=1100011, funct3=001
        # Encoding: 0 000000 00100 00011 001 1000 0 1100011
        # = 0x00419463
        instruction = int_to_bits_unsigned(0x00419463, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x3 = 15, x4 = 10 (not equal)
        rf.write_int_reg(3, int_to_bits_unsigned(15, 32))
        rf.write_int_reg(4, int_to_bits_unsigned(10, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify branch taken
        assert result.decoded.mnemonic == 'BNE'
        assert result.branch_taken == True
        assert bits_to_int_unsigned(datapath.get_pc()) == 0x00000008
        
    def test_bne_not_taken(self):
        """Test BNE (branch if not equal) when condition is false"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load BNE x3, x4, 8 instruction
        instruction = int_to_bits_unsigned(0x00419463, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x3 = x4 = 15 (equal)
        rf.write_int_reg(3, int_to_bits_unsigned(15, 32))
        rf.write_int_reg(4, int_to_bits_unsigned(15, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify branch not taken
        assert result.decoded.mnemonic == 'BNE'
        assert result.branch_taken == False
        assert bits_to_int_unsigned(datapath.get_pc()) == 0x00000004


class TestJumps:
    """Test jump instructions through the datapath."""
    
    def test_jal_instruction(self):
        """Test JAL (jump and link) instruction"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load JAL x1, 16 instruction (jump forward 16 bytes)
        # JAL: opcode=1101111
        # imm[20:1] = 16 >> 1 = 8
        # Encoding: imm[20|10:1|11|19:12] rd opcode
        # = 0x010000EF
        instruction = int_to_bits_unsigned(0x010000EF, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify jump taken and return address saved
        assert result.decoded.mnemonic == 'JAL'
        # PC should jump to 0x00000000 + 16 = 0x00000010
        assert bits_to_int_unsigned(datapath.get_pc()) == 0x00000010
        # x1 should contain return address (PC+4 = 0x00000004)
        assert bits_to_int_unsigned(rf.read_int_reg(1)) == 0x00000004
        
    def test_jalr_instruction(self):
        """Test JALR (jump and link register) instruction"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load JALR x1, 8(x5) instruction
        # JALR: opcode=1100111, funct3=000
        # Encoding: 000000001000 00101 000 00001 1100111
        # = 0x008280E7
        instruction = int_to_bits_unsigned(0x008280E7, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Set x5 = 0x00000100
        rf.write_int_reg(5, int_to_bits_unsigned(0x00000100, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify jump taken to x5 + 8 = 0x00000108
        assert result.decoded.mnemonic == 'JALR'
        assert bits_to_int_unsigned(datapath.get_pc()) == 0x00000108
        # x1 should contain return address (PC+4 = 0x00000004)
        assert bits_to_int_unsigned(rf.read_int_reg(1)) == 0x00000004


class TestUpperImmediate:
    """Test upper immediate instructions through the datapath."""
    
    def test_lui_instruction(self):
        """Test LUI (load upper immediate) instruction"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load LUI x5, 0x00010 instruction
        # LUI: opcode=0110111
        # Encoding: imm[31:12] rd opcode
        # 0x00010 in upper 20 bits = 0x00010000
        # = 0x000102B7
        instruction = int_to_bits_unsigned(0x000102B7, 32)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), instruction)
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify x5 = 0x00010000
        assert result.decoded.mnemonic == 'LUI'
        assert bits_to_int_unsigned(rf.read_int_reg(5)) == 0x00010000
        
    def test_auipc_instruction(self):
        """Test AUIPC (add upper immediate to PC) instruction"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Set PC to 0x00001000
        datapath.set_pc(0x00001000)
        
        # Load AUIPC x5, 0x00001 instruction
        # AUIPC: opcode=0010111
        # Encoding: imm[31:12] rd opcode
        # = 0x00001297
        instruction = int_to_bits_unsigned(0x00001297, 32)
        mem.write_word(int_to_bits_unsigned(0x00001000, 32), instruction)
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify x5 = PC + (0x00001 << 12) = 0x00001000 + 0x00001000 = 0x00002000
        assert result.decoded.mnemonic == 'AUIPC'
        assert bits_to_int_unsigned(rf.read_int_reg(5)) == 0x00002000


class TestIntegration:
    """Test integrated datapath scenarios."""
    
    def test_sequential_execution(self):
        """Test sequential execution of multiple instructions"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load 3 sequential ADDI instructions
        # ADDI x1, x0, 5
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), int_to_bits_unsigned(0x00500093, 32))
        # ADDI x2, x0, 10
        mem.write_word(int_to_bits_unsigned(0x00000004, 32), int_to_bits_unsigned(0x00A00113, 32))
        # ADD x3, x1, x2
        mem.write_word(int_to_bits_unsigned(0x00000008, 32), int_to_bits_unsigned(0x002081B3, 32))
        
        # Execute 3 cycles
        result1 = datapath.execute_cycle()
        result2 = datapath.execute_cycle()
        result3 = datapath.execute_cycle()
        
        # Verify sequential execution
        assert bits_to_int_unsigned(result1.pc) == 0x00000000
        assert bits_to_int_unsigned(result2.pc) == 0x00000004
        assert bits_to_int_unsigned(result3.pc) == 0x00000008
        
        # Verify final state
        assert bits_to_int_unsigned(rf.read_int_reg(1)) == 5
        assert bits_to_int_unsigned(rf.read_int_reg(2)) == 10
        assert bits_to_int_unsigned(rf.read_int_reg(3)) == 15
        
    def test_register_dependencies(self):
        """Test instructions with register dependencies"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load instructions with dependencies
        # ADDI x1, x0, 5    -> x1 = 5
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), int_to_bits_unsigned(0x00500093, 32))
        # ADDI x2, x1, 3    -> x2 = x1 + 3 = 8
        mem.write_word(int_to_bits_unsigned(0x00000004, 32), int_to_bits_unsigned(0x00308113, 32))
        # ADD x3, x1, x2    -> x3 = x1 + x2 = 13
        mem.write_word(int_to_bits_unsigned(0x00000008, 32), int_to_bits_unsigned(0x002081B3, 32))
        
        # Execute 3 cycles
        datapath.execute_cycle()
        datapath.execute_cycle()
        datapath.execute_cycle()
        
        # Verify results
        assert bits_to_int_unsigned(rf.read_int_reg(1)) == 5
        assert bits_to_int_unsigned(rf.read_int_reg(2)) == 8
        assert bits_to_int_unsigned(rf.read_int_reg(3)) == 13
        
    def test_pc_increment(self):
        """Test that PC increments correctly"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load NOP-like instruction (ADDI x0, x0, 0)
        for i in range(10):
            mem.write_word(int_to_bits_unsigned(i * 4, 32), int_to_bits_unsigned(0x00000013, 32))
        
        # Execute 10 cycles
        for i in range(10):
            result = datapath.execute_cycle()
            # PC should be at i*4 at start of each cycle
            assert bits_to_int_unsigned(result.pc) == i * 4
        
        # Final PC should be at 10*4 = 40
        assert bits_to_int_unsigned(datapath.get_pc()) == 40
        
    def test_invalid_instruction(self):
        """Test handling of invalid/unknown instructions"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load invalid instruction (all zeros)
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), int_to_bits_unsigned(0x00000000, 32))
        
        # Execute - should not crash
        result = datapath.execute_cycle()
        
        # Verify execution completed (even if instruction is unknown)
        assert result.cycle_num == 0
        
    def test_halt_detection(self):
        """Test detection of halt condition (JAL x0, 0)"""
        # Setup
        mem = Memory(size_bytes=131072, base_addr=0x00000000)
        rf = RegisterFile()
        datapath = Datapath(mem, rf)
        
        # Load JAL x0, 0 instruction (infinite loop)
        # JAL: opcode=1101111, rd=x0, imm=0
        # = 0x0000006F
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), int_to_bits_unsigned(0x0000006F, 32))
        
        # Execute
        result = datapath.execute_cycle()
        
        # Verify it's a JAL to x0
        assert result.decoded.mnemonic == 'JAL'
        assert bits_to_int_unsigned(result.decoded.rd) == 0
        # PC should still be at 0 (jumped to self)
        assert bits_to_int_unsigned(datapath.get_pc()) == 0


# AI-END
