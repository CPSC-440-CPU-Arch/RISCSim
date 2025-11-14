# AI-BEGIN: Claude Code (Anthropic) - November 14, 2025
# Prompt: "Implement Phase 3 single-cycle datapath connecting fetch, decode, execute, memory, writeback stages"
"""
Single-Cycle RISC-V Datapath Implementation

This module implements a single-cycle datapath that connects all CPU components:
- Fetch: Instruction fetch from memory
- Decode: Instruction decode and control signal generation
- Execute: ALU/Shifter/MDU/FPU operations
- Memory: Data memory read/write
- Writeback: Register file update

The datapath executes one complete instruction per cycle, with all stages
completing within a single clock cycle.

Convention: All bit arrays use MSB-at-index-0 convention.
"""

from typing import Optional, List
from riscsim.cpu.memory import Memory
from riscsim.cpu.registers import RegisterFile
from riscsim.cpu.fetch import FetchUnit
from riscsim.cpu.decoder import InstructionDecoder, DecodedInstruction
from riscsim.cpu.control_signals import ControlSignals, ALU_OP_ADD, ALU_OP_SUB, ALU_OP_AND, ALU_OP_OR, ALU_OP_XOR, SH_OP_SLL, SH_OP_SRL, SH_OP_SRA
from riscsim.cpu.alu import alu
from riscsim.cpu.shifter import shifter
from riscsim.utils.bit_utils import (
    bits_to_int_unsigned,
    int_to_bits_unsigned,
    slice_bits, concat_bits, sign_extend
)


class CycleResult:
    """Result of single cycle execution.
    
    Captures all relevant information about what happened during
    one cycle of execution.
    
    Attributes:
        pc: Program counter value at start of cycle (32-bit)
        instruction: Fetched instruction (32-bit)
        decoded: Decoded instruction information
        signals: Control signals used during execution
        alu_result: ALU output (32-bit)
        mem_data: Memory read data if applicable (32-bit or None)
        writeback_data: Data written to register file (32-bit)
        branch_taken: Whether branch was taken
        cycle_num: Cycle number
    """
    
    def __init__(self):
        self.pc: List[int] = [0] * 32
        self.instruction: List[int] = [0] * 32
        self.decoded: Optional[DecodedInstruction] = None
        self.signals: Optional[ControlSignals] = None
        self.alu_result: List[int] = [0] * 32
        self.mem_data: Optional[List[int]] = None
        self.writeback_data: List[int] = [0] * 32
        self.branch_taken: bool = False
        self.cycle_num: int = 0
        
    def __repr__(self):
        pc_val = bits_to_int_unsigned(self.pc)
        instr_val = bits_to_int_unsigned(self.instruction)
        mnemonic = self.decoded.mnemonic if self.decoded else "UNKNOWN"
        return (f"CycleResult(cycle={self.cycle_num}, pc=0x{pc_val:08x}, "
                f"instr=0x{instr_val:08x}, mnemonic={mnemonic}, "
                f"branch_taken={self.branch_taken})")


class Datapath:
    """
    Single-cycle RISC-V datapath.
    
    Connects fetch, decode, execute, memory, writeback stages into
    a complete single-cycle execution pipeline.
    
    Features:
    - Single-cycle execution (all stages complete in one cycle)
    - Support for RV32I base instruction set
    - ALU, Shifter operations
    - Memory load/store
    - Branch/jump instructions
    - Register file writeback
    
    Convention:
    - All bit arrays use MSB-at-index-0
    - PC managed by FetchUnit
    - Uses existing ALU (no host operators in critical path)
    """
    
    def __init__(self, memory: Memory, register_file: RegisterFile):
        """
        Initialize datapath with memory and register file.
        
        Args:
            memory: Memory object for instruction and data access
            register_file: RegisterFile for integer register operations
        """
        self.memory = memory
        self.register_file = register_file
        self.fetch_unit = FetchUnit(memory, initial_pc=0x00000000)
        self.decoder = InstructionDecoder()
        self.cycle_count = 0
        
    def execute_cycle(self) -> CycleResult:
        """
        Execute one complete cycle of the datapath.
        
        Performs all five stages:
        1. Fetch: Read instruction from memory
        2. Decode: Decode instruction and generate control signals
        3. Execute: Perform ALU/Shifter operation
        4. Memory: Read/write data memory
        5. Writeback: Write result to register file
        
        Returns:
            CycleResult containing cycle execution information
        """
        result = CycleResult()
        result.cycle_num = self.cycle_count
        self.cycle_count += 1
        
        # Stage 1: Fetch
        instruction = self._fetch_stage(result)
        
        # Stage 2: Decode
        decoded, signals = self._decode_stage(instruction, result)
        
        # Stage 3: Execute
        alu_result, branch_taken = self._execute_stage(decoded, signals, result)
        
        # Stage 4: Memory
        mem_data = self._memory_stage(signals, alu_result, decoded, result)
        
        # Stage 5: Writeback
        self._writeback_stage(signals, alu_result, mem_data, decoded, result)
        
        return result
    
    def _fetch_stage(self, result: CycleResult) -> List[int]:
        """
        Fetch instruction from memory at current PC.
        
        Args:
            result: CycleResult to populate
            
        Returns:
            32-bit instruction
        """
        result.pc = self.fetch_unit.get_pc().copy()
        instruction = self.fetch_unit.fetch()
        result.instruction = instruction.copy()
        return instruction
    
    def _decode_stage(self, instruction: List[int], result: CycleResult) -> tuple:
        """
        Decode instruction and generate control signals.
        
        Args:
            instruction: 32-bit instruction
            result: CycleResult to populate
            
        Returns:
            Tuple of (DecodedInstruction, ControlSignals)
        """
        decoded = self.decoder.decode(instruction)
        signals = self._generate_control_signals(decoded)
        
        result.decoded = decoded
        result.signals = signals
        
        return decoded, signals
    
    def _execute_stage(self, decoded: DecodedInstruction, signals: ControlSignals,
                       result: CycleResult) -> tuple:
        """
        Execute ALU/Shifter operation.
        
        Args:
            decoded: Decoded instruction
            signals: Control signals
            result: CycleResult to populate
            
        Returns:
            Tuple of (alu_result, branch_taken)
        """
        # Read source operands from register file
        rs1_data = self.register_file.read_int_reg(bits_to_int_unsigned(decoded.rs1))
        rs2_data = self.register_file.read_int_reg(bits_to_int_unsigned(decoded.rs2))
        
        # Select ALU source A (rs1 or PC for AUIPC)
        if signals.alu_src_a == 1:
            # AUIPC uses PC as source A
            alu_src_a = result.pc.copy()
        else:
            alu_src_a = rs1_data.copy()
        
        # Select ALU source B (rs2 or immediate)
        if signals.alu_src_b == 1:
            # Use immediate
            alu_src_b = decoded.immediate.copy()
        else:
            alu_src_b = rs2_data.copy()
        
        # Perform operation based on instruction type
        alu_result = [0] * 32
        branch_taken = False
        
        if decoded.mnemonic in ['ADD', 'ADDI', 'LW', 'SW', 'AUIPC', 'JAL', 'JALR']:
            # Addition
            alu_result, flags = alu(alu_src_a, alu_src_b, ALU_OP_ADD)
        elif decoded.mnemonic == 'SUB':
            # Subtraction
            alu_result, flags = alu(alu_src_a, alu_src_b, ALU_OP_SUB)
        elif decoded.mnemonic in ['AND', 'ANDI']:
            # Bitwise AND
            alu_result, flags = alu(alu_src_a, alu_src_b, ALU_OP_AND)
        elif decoded.mnemonic in ['OR', 'ORI']:
            # Bitwise OR
            alu_result, flags = alu(alu_src_a, alu_src_b, ALU_OP_OR)
        elif decoded.mnemonic in ['XOR', 'XORI']:
            # Bitwise XOR
            alu_result, flags = alu(alu_src_a, alu_src_b, ALU_OP_XOR)
        elif decoded.mnemonic in ['SLL', 'SLLI']:
            # Shift left logical
            shift_amount = slice_bits(alu_src_b, 27, 32)  # Lower 5 bits
            alu_result = shifter(alu_src_a, shift_amount, [0, 0])
        elif decoded.mnemonic in ['SRL', 'SRLI']:
            # Shift right logical
            shift_amount = slice_bits(alu_src_b, 27, 32)  # Lower 5 bits
            alu_result = shifter(alu_src_a, shift_amount, [0, 1])
        elif decoded.mnemonic in ['SRA', 'SRAI']:
            # Shift right arithmetic
            shift_amount = slice_bits(alu_src_b, 27, 32)  # Lower 5 bits
            alu_result = shifter(alu_src_a, shift_amount, [1, 1])
        elif decoded.mnemonic == 'LUI':
            # LUI: Load upper immediate (already in decoded.immediate)
            alu_result = decoded.immediate.copy()
        elif decoded.mnemonic in ['BEQ', 'BNE']:
            # Branch comparison using ALU subtraction
            diff_result, flags = alu(rs1_data, rs2_data, ALU_OP_SUB)
            # flags is [N, Z, C, V]
            zero = flags[1]  # Z flag
            
            if decoded.mnemonic == 'BEQ':
                # Branch if equal (zero flag set)
                branch_taken = (zero == 1)
            else:  # BNE
                # Branch if not equal (zero flag clear)
                branch_taken = (zero == 0)
            
            # Calculate branch target using ALU: PC + immediate
            alu_result, _ = alu(result.pc, decoded.immediate, ALU_OP_ADD)
        
        result.alu_result = alu_result.copy()
        result.branch_taken = branch_taken
        
        # Update PC based on control flow
        if decoded.mnemonic == 'JAL':
            # Jump to PC + immediate
            self.fetch_unit.branch_to(alu_result)
        elif decoded.mnemonic == 'JALR':
            # Jump to rs1 + immediate, set LSB to 0
            target = alu_result.copy()
            target[31] = 0  # Clear LSB for alignment
            self.fetch_unit.branch_to(target)
        elif branch_taken:
            # Branch taken, jump to branch target
            self.fetch_unit.branch_to(alu_result)
        else:
            # Normal PC increment (PC + 4)
            self.fetch_unit.increment_pc()
        
        return alu_result, branch_taken
    
    def _memory_stage(self, signals: ControlSignals, alu_result: List[int],
                      decoded: DecodedInstruction, result: CycleResult) -> Optional[List[int]]:
        """
        Perform memory read/write operations.
        
        Args:
            signals: Control signals
            alu_result: ALU result (used as memory address)
            decoded: Decoded instruction
            result: CycleResult to populate
            
        Returns:
            Memory read data (32-bit) or None if no read
        """
        mem_data = None
        
        if signals.mem_read:
            # Load word from memory
            mem_data = self.memory.read_word(alu_result)
            result.mem_data = mem_data.copy()
        elif signals.mem_write:
            # Store word to memory
            # Get data from rs2
            rs2_data = self.register_file.read_int_reg(bits_to_int_unsigned(decoded.rs2))
            self.memory.write_word(alu_result, rs2_data)
        
        return mem_data
    
    def _writeback_stage(self, signals: ControlSignals, alu_result: List[int],
                        mem_data: Optional[List[int]], decoded: DecodedInstruction,
                        result: CycleResult):
        """
        Write result back to register file.
        
        Args:
            signals: Control signals
            alu_result: ALU result
            mem_data: Memory read data (if applicable)
            decoded: Decoded instruction
            result: CycleResult to populate
        """
        if signals.result_src == 1 and mem_data is not None:
            # Write memory data to register
            writeback_data = mem_data.copy()
        elif signals.result_src == 2:
            # Write PC+4 to register (for JAL/JALR)
            # Get next PC using ALU
            four = int_to_bits_unsigned(4, 32)
            pc_plus_4, _ = alu(result.pc, four, ALU_OP_ADD)
            writeback_data = pc_plus_4
        else:
            # Write ALU result to register
            writeback_data = alu_result.copy()
        
        result.writeback_data = writeback_data.copy()
        
        # Write to register file if rd != 0
        rd_num = bits_to_int_unsigned(decoded.rd)
        if rd_num != 0 and signals.rf_we:
            self.register_file.write_int_reg(rd_num, writeback_data)
    
    def _generate_control_signals(self, decoded: DecodedInstruction) -> ControlSignals:
        """
        Generate control signals based on decoded instruction.
        
        Args:
            decoded: Decoded instruction
            
        Returns:
            ControlSignals for this instruction
        """
        signals = ControlSignals()
        
        # Default: no memory access, no branch/jump
        signals.mem_read = 0
        signals.mem_write = 0
        signals.branch = 0
        signals.jump = 0
        signals.result_src = 0  # ALU result
        signals.pc_src = 0  # PC+4
        signals.alu_src_a = 0  # rs1
        signals.alu_src_b = 0  # rs2
        signals.rf_we = 0  # No write by default
        
        # Set control signals based on instruction type
        if decoded.mnemonic in ['ADD', 'SUB', 'AND', 'OR', 'XOR', 'SLL', 'SRL', 'SRA']:
            # R-type arithmetic/logical
            signals.alu_src_b = 0  # rs2
            signals.rf_we = 1
            signals.result_src = 0  # ALU result
        elif decoded.mnemonic in ['ADDI', 'ANDI', 'ORI', 'XORI', 'SLLI', 'SRLI', 'SRAI']:
            # I-type immediate operations
            signals.alu_src_b = 1  # immediate
            signals.rf_we = 1
            signals.result_src = 0  # ALU result
        elif decoded.mnemonic == 'LW':
            # Load word
            signals.alu_src_b = 1  # immediate (offset)
            signals.mem_read = 1
            signals.rf_we = 1
            signals.result_src = 1  # Memory data
        elif decoded.mnemonic == 'SW':
            # Store word
            signals.alu_src_b = 1  # immediate (offset)
            signals.mem_write = 1
            signals.rf_we = 0  # No writeback
        elif decoded.mnemonic in ['BEQ', 'BNE']:
            # Branch instructions
            signals.branch = 1
            signals.alu_src_b = 0  # Compare rs2
            signals.rf_we = 0  # No writeback
        elif decoded.mnemonic == 'JAL':
            # Jump and link
            signals.jump = 1
            signals.alu_src_b = 1  # immediate
            signals.rf_we = 1
            signals.result_src = 2  # PC+4
        elif decoded.mnemonic == 'JALR':
            # Jump and link register
            signals.jump = 1
            signals.alu_src_b = 1  # immediate
            signals.rf_we = 1
            signals.result_src = 2  # PC+4
        elif decoded.mnemonic == 'LUI':
            # Load upper immediate
            signals.alu_src_b = 1  # immediate (already shifted)
            signals.rf_we = 1
            signals.result_src = 0  # ALU result (immediate)
        elif decoded.mnemonic == 'AUIPC':
            # Add upper immediate to PC
            signals.alu_src_a = 1  # PC
            signals.alu_src_b = 1  # immediate
            signals.rf_we = 1
            signals.result_src = 0  # ALU result
        
        return signals
    
    def get_pc(self) -> List[int]:
        """
        Get current program counter value.
        
        Returns:
            32-bit PC value
        """
        return self.fetch_unit.get_pc()
    
    def set_pc(self, addr: int):
        """
        Set program counter to specific address.
        
        Args:
            addr: Target address as integer
        """
        addr_bits = int_to_bits_unsigned(addr, 32)
        self.fetch_unit.branch_to(addr_bits)
    
    def get_cycle_count(self) -> int:
        """
        Get total number of cycles executed.
        
        Returns:
            Cycle count
        """
        return self.cycle_count


# AI-END
