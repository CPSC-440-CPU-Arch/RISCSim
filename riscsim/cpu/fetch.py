"""
Instruction Fetch Unit for RISC-V CPU Simulator

Implements instruction fetch with:
- PC (Program Counter) management
- Instruction fetch from memory
- PC increment logic
- Branch/jump target calculation

Author: RISCSim Team
Date: November 2025
"""

# AI-BEGIN: Claude Code (Anthropic) - November 14, 2025
# Prompt: "Implement Phase 1 fetch unit with PC management, following no-host-operators constraint"

from typing import List
from riscsim.utils.bit_utils import (
    bits_to_int_unsigned,
    int_to_bits_unsigned,
    zero_extend
)
from riscsim.cpu.alu import alu


class FetchUnit:
    """
    Instruction fetch unit with PC management.
    
    Features:
    - Fetches 32-bit instructions from memory
    - Manages Program Counter (PC)
    - PC increment (PC + 4) using ALU
    - Branch/jump to target address
    - PC alignment checking
    
    Convention:
    - PC is 32-bit value [MSB at index 0]
    - PC must be word-aligned (bits [1:0] = 00)
    - All arithmetic uses ALU (no host operators)
    """
    
    def __init__(self, memory, initial_pc: int = 0x00000000):
        """
        Initialize fetch unit.
        
        Args:
            memory: Memory object to fetch instructions from
            initial_pc: Initial PC value (default 0x00000000)
        
        Convention:
        - PC stored as 32-bit array
        - Memory must support read_word() interface
        """
        self.memory = memory
        
        # Initialize PC (I/O BOUNDARY: convert initial value)
        self.pc = int_to_bits_unsigned(initial_pc, 32)
        
        # Validate PC alignment
        if not self._check_pc_alignment(self.pc):
            raise ValueError(f"Initial PC 0x{initial_pc:08X} is not word-aligned")
    
    def _check_pc_alignment(self, pc: List[int]) -> bool:
        """
        Check if PC is word-aligned (bits [1:0] = 00).
        
        Args:
            pc: 32-bit PC value
        
        Returns:
            True if aligned, False otherwise
        """
        return pc[-2] == 0 and pc[-1] == 0
    
    def fetch(self) -> List[int]:
        """
        Fetch instruction from memory at current PC.
        
        Returns:
            32-bit instruction [MSB at index 0]
        
        Raises:
            ValueError: If PC is not word-aligned or out of bounds
        
        Convention:
        - Reads word from memory at PC
        - Does NOT increment PC (use increment_pc() separately)
        """
        # Check PC alignment
        if not self._check_pc_alignment(self.pc):
            from riscsim.utils.bit_utils import bits_to_hex_string
            pc_hex = bits_to_hex_string(self.pc)
            raise ValueError(f"PC 0x{pc_hex} is not word-aligned")
        
        # Fetch instruction from memory
        try:
            instruction = self.memory.read_word(self.pc)
        except ValueError as e:
            from riscsim.utils.bit_utils import bits_to_hex_string
            pc_hex = bits_to_hex_string(self.pc)
            raise ValueError(f"Failed to fetch instruction at PC 0x{pc_hex}: {e}")
        
        return instruction
    
    def increment_pc(self) -> None:
        """
        Increment PC by 4 (next sequential instruction).
        
        Convention:
        - Uses ALU for addition (no host + operator)
        - PC_new = PC_old + 4
        
        Example:
            PC = 0x00000000
            increment_pc()
            PC = 0x00000004
        """
        # Create constant 4 as 32-bit value
        four = int_to_bits_unsigned(4, 32)
        
        # Add using ALU: PC = PC + 4
        # ALU control: [0, 0, 1, 0] = ADD operation
        new_pc, flags = alu(self.pc, four, [0, 0, 1, 0])
        
        # Update PC
        self.pc = new_pc
    
    def branch_to(self, target_addr: List[int]) -> None:
        """
        Branch/jump to target address.
        
        Args:
            target_addr: 32-bit target address [MSB at index 0]
        
        Raises:
            ValueError: If target address is not word-aligned
        
        Convention:
        - Sets PC to target address
        - Used for branches, jumps, exceptions
        """
        # Validate target is 32 bits
        if len(target_addr) != 32:
            raise ValueError(f"Target address must be 32 bits, got {len(target_addr)} bits")
        
        # Check alignment
        if not self._check_pc_alignment(target_addr):
            from riscsim.utils.bit_utils import bits_to_hex_string
            target_hex = bits_to_hex_string(target_addr)
            raise ValueError(f"Target address 0x{target_hex} is not word-aligned")
        
        # Set PC to target
        self.pc = target_addr.copy()
    
    def branch_relative(self, offset: List[int]) -> None:
        """
        Branch to PC + offset.
        
        Args:
            offset: 32-bit signed offset [MSB at index 0]
        
        Convention:
        - Uses ALU for addition: PC_new = PC_old + offset
        - Offset is sign-extended immediate from branch instruction
        
        Example:
            PC = 0x00000010
            offset = 0x00000008 (8 bytes forward)
            PC_new = 0x00000018
        """
        # Validate offset is 32 bits
        if len(offset) != 32:
            raise ValueError(f"Offset must be 32 bits, got {len(offset)} bits")
        
        # Add using ALU: PC_new = PC_old + offset
        # ALU control: [0, 0, 1, 0] = ADD operation
        new_pc, flags = alu(self.pc, offset, [0, 0, 1, 0])
        
        # Check alignment
        if not self._check_pc_alignment(new_pc):
            from riscsim.utils.bit_utils import bits_to_hex_string
            new_pc_hex = bits_to_hex_string(new_pc)
            raise ValueError(f"Computed PC 0x{new_pc_hex} is not word-aligned")
        
        # Update PC
        self.pc = new_pc
    
    def get_pc(self) -> List[int]:
        """
        Get current PC value.
        
        Returns:
            32-bit PC value [MSB at index 0]
        """
        return self.pc.copy()
    
    def set_pc(self, pc: List[int]) -> None:
        """
        Set PC to specific value.
        
        Args:
            pc: 32-bit PC value [MSB at index 0]
        
        Raises:
            ValueError: If PC is not word-aligned
        
        Convention:
        - Used for resets, exceptions, debugging
        """
        # Validate PC is 32 bits
        if len(pc) != 32:
            raise ValueError(f"PC must be 32 bits, got {len(pc)} bits")
        
        # Check alignment
        if not self._check_pc_alignment(pc):
            from riscsim.utils.bit_utils import bits_to_hex_string
            pc_hex = bits_to_hex_string(pc)
            raise ValueError(f"PC 0x{pc_hex} is not word-aligned")
        
        # Set PC
        self.pc = pc.copy()
    
    def get_next_pc(self) -> List[int]:
        """
        Calculate next sequential PC (PC + 4) without updating PC.
        
        Returns:
            32-bit next PC value [MSB at index 0]
        
        Convention:
        - Used for JAL/JALR return address (PC + 4)
        - Does not modify current PC
        """
        # Create constant 4
        four = int_to_bits_unsigned(4, 32)
        
        # Add using ALU: next_pc = PC + 4
        next_pc, flags = alu(self.pc, four, [0, 0, 1, 0])
        
        return next_pc

# AI-END
