"""
Memory Unit for RISC-V CPU Simulator

Implements word-addressable and byte-addressable memory with:
- Separate instruction and data memory regions
- Little-endian byte ordering
- Address alignment checking
- Load/store operations

Memory Map:
- Instruction Memory: 0x00000000 - 0x0000FFFF (64KB)
- Data Memory:        0x00010000 - 0x0001FFFF (64KB)

Author: RISCSim Team
Date: November 2025
"""

# AI-BEGIN: Claude Code (Anthropic) - November 14, 2025
# Prompt: "Implement Phase 1 of RISC-V CPU - Memory unit with word/byte access,
#         little-endian, alignment checking, following no-host-operators constraint"

from typing import List, Optional
from riscsim.utils.bit_utils import (
    bits_to_int_unsigned,
    int_to_bits_unsigned,
    slice_bits,
    concat_bits,
    bits_to_hex_string
)


class Memory:
    """
    Memory unit supporting both instruction and data memory.
    
    Features:
    - Word-addressable (32-bit words, 4-byte aligned)
    - Byte-addressable with alignment checking
    - Separate I-memory (0x00000000+) and D-memory (0x00010000+) regions
    - Little-endian byte ordering
    - Load/store operations with bounds checking
    
    Convention:
    - All data stored as bit arrays [0/1]
    - Addresses are 32-bit values
    - MSB at index 0
    """
    
    # Memory region boundaries (using boundary function for initialization only)
    INSTRUCTION_BASE = 0x00000000
    INSTRUCTION_SIZE = 0x00010000  # 64KB
    DATA_BASE = 0x00010000
    DATA_SIZE = 0x00010000  # 64KB
    
    def __init__(self, size_bytes: int = 128 * 1024, base_addr: int = 0x00000000):
        """
        Initialize memory unit.
        
        Args:
            size_bytes: Total memory size in bytes (default 128KB)
            base_addr: Base address for memory (default 0x00000000)
        
        Convention:
        - Memory stored as list of 8-bit bytes [each byte is list of 8 bits]
        - Each address holds one byte
        """
        self.size_bytes = size_bytes
        self.base_addr = base_addr
        
        # Initialize memory as list of bytes (each byte is 8-bit array)
        # I/O BOUNDARY: Using host arithmetic for initialization only
        self.memory: List[List[int]] = [[0] * 8 for _ in range(size_bytes)]
        
        # Track loaded program bounds
        self.program_start = None
        self.program_end = None
    
    def _check_address_bounds(self, addr: List[int]) -> bool:
        """
        Check if address is within valid memory range.
        
        Args:
            addr: 32-bit address [MSB at index 0]
        
        Returns:
            True if address is valid, False otherwise
        
        Convention:
        - Uses boundary function for address comparison
        """
        # I/O BOUNDARY: Convert address to int for bounds check
        addr_int = bits_to_int_unsigned(addr)
        
        # Check if address is within memory bounds
        if addr_int < self.base_addr:
            return False
        if addr_int >= self.base_addr + self.size_bytes:
            return False
        
        return True
    
    def _check_word_alignment(self, addr: List[int]) -> bool:
        """
        Check if address is word-aligned (multiple of 4).
        
        Args:
            addr: 32-bit address
        
        Returns:
            True if word-aligned, False otherwise
        
        Convention:
        - Word addresses must have bits [1:0] = 00
        """
        # Check if last 2 bits are zero
        return addr[-2] == 0 and addr[-1] == 0
    
    def _addr_to_offset(self, addr: List[int]) -> int:
        """
        Convert absolute address to memory array offset.
        
        Args:
            addr: 32-bit address
        
        Returns:
            Offset into memory array
        
        Convention:
        - I/O BOUNDARY FUNCTION (address arithmetic for array indexing)
        """
        addr_int = bits_to_int_unsigned(addr)
        return addr_int - self.base_addr
    
    def read_word(self, addr: List[int]) -> List[int]:
        """
        Read 32-bit word from memory (little-endian).
        
        Args:
            addr: 32-bit word-aligned address
        
        Returns:
            32-bit word [MSB at index 0]
        
        Raises:
            ValueError: If address is out of bounds or not word-aligned
        
        Convention:
        - Little-endian: byte0 (lowest address) is LSB of word
        - Word at addr consists of bytes [addr, addr+1, addr+2, addr+3]
        - Result: [byte3[7:0], byte2[7:0], byte1[7:0], byte0[7:0]] in MSB-first
        """
        # Check bounds
        if not self._check_address_bounds(addr):
            addr_hex = bits_to_hex_string(addr)
            raise ValueError(f"Address 0x{addr_hex} out of bounds")
        
        # Check alignment
        if not self._check_word_alignment(addr):
            addr_hex = bits_to_hex_string(addr)
            raise ValueError(f"Address 0x{addr_hex} is not word-aligned")
        
        # Get offset
        offset = self._addr_to_offset(addr)
        
        # Read 4 bytes (little-endian)
        # I/O BOUNDARY: Using host arithmetic for array indexing
        byte0 = self.memory[offset]      # LSB
        byte1 = self.memory[offset + 1]
        byte2 = self.memory[offset + 2]
        byte3 = self.memory[offset + 3]  # MSB
        
        # Concatenate bytes in big-endian order (MSB first)
        # Word = [byte3, byte2, byte1, byte0] for MSB-first convention
        word = concat_bits(byte3, byte2, byte1, byte0)
        
        return word
    
    def write_word(self, addr: List[int], data: List[int]) -> None:
        """
        Write 32-bit word to memory (little-endian).
        
        Args:
            addr: 32-bit word-aligned address
            data: 32-bit word to write [MSB at index 0]
        
        Raises:
            ValueError: If address is out of bounds or not word-aligned
        
        Convention:
        - Little-endian: data[31:24] goes to addr+3, data[7:0] goes to addr
        - Splits 32-bit word into 4 bytes and stores them
        """
        # Check bounds
        if not self._check_address_bounds(addr):
            addr_hex = bits_to_hex_string(addr)
            raise ValueError(f"Address 0x{addr_hex} out of bounds")
        
        # Check alignment
        if not self._check_word_alignment(addr):
            addr_hex = bits_to_hex_string(addr)
            raise ValueError(f"Address 0x{addr_hex} is not word-aligned")
        
        # Validate data is 32 bits
        if len(data) != 32:
            raise ValueError(f"Data must be 32 bits, got {len(data)} bits")
        
        # Get offset
        offset = self._addr_to_offset(addr)
        
        # Split 32-bit word into 4 bytes
        # data = [31:24 (byte3), 23:16 (byte2), 15:8 (byte1), 7:0 (byte0)]
        byte3 = slice_bits(data, 0, 8)    # MSB [31:24]
        byte2 = slice_bits(data, 8, 16)   # [23:16]
        byte1 = slice_bits(data, 16, 24)  # [15:8]
        byte0 = slice_bits(data, 24, 32)  # LSB [7:0]
        
        # Write bytes in little-endian order
        # I/O BOUNDARY: Using host arithmetic for array indexing
        self.memory[offset] = byte0      # LSB at lowest address
        self.memory[offset + 1] = byte1
        self.memory[offset + 2] = byte2
        self.memory[offset + 3] = byte3  # MSB at highest address
    
    def read_byte(self, addr: List[int]) -> List[int]:
        """
        Read 8-bit byte from memory.
        
        Args:
            addr: 32-bit byte address
        
        Returns:
            8-bit byte [MSB at index 0]
        
        Raises:
            ValueError: If address is out of bounds
        """
        # Check bounds
        if not self._check_address_bounds(addr):
            addr_hex = bits_to_hex_string(addr)
            raise ValueError(f"Address 0x{addr_hex} out of bounds")
        
        # Get offset
        offset = self._addr_to_offset(addr)
        
        # Return byte
        return self.memory[offset].copy()
    
    def write_byte(self, addr: List[int], data: List[int]) -> None:
        """
        Write 8-bit byte to memory.
        
        Args:
            addr: 32-bit byte address
            data: 8-bit byte to write [MSB at index 0]
        
        Raises:
            ValueError: If address is out of bounds or data is not 8 bits
        """
        # Check bounds
        if not self._check_address_bounds(addr):
            addr_hex = bits_to_hex_string(addr)
            raise ValueError(f"Address 0x{addr_hex} out of bounds")
        
        # Validate data is 8 bits
        if len(data) != 8:
            raise ValueError(f"Data must be 8 bits, got {len(data)} bits")
        
        # Get offset
        offset = self._addr_to_offset(addr)
        
        # Write byte
        self.memory[offset] = data.copy()
    
    def load_program(self, hex_file_path: str) -> None:
        """
        Load program from .hex file into instruction memory.
        
        Args:
            hex_file_path: Path to .hex file containing 32-bit words
        
        Convention:
        - Each line in .hex file is 8 hex digits (32 bits)
        - Words loaded starting at INSTRUCTION_BASE (0x00000000)
        - Sequential word addresses (0x00000000, 0x00000004, 0x00000008, ...)
        
        Raises:
            FileNotFoundError: If hex file doesn't exist
            ValueError: If hex file format is invalid
        """
        from riscsim.utils.hex_loader import load_hex_file
        
        # Load words from hex file
        words = load_hex_file(hex_file_path)
        
        # Convert starting address to bits
        addr = int_to_bits_unsigned(self.INSTRUCTION_BASE, 32)
        
        # Track program bounds
        self.program_start = self.INSTRUCTION_BASE
        
        # Write each word to memory
        for word in words:
            # Convert word to 32-bit array
            word_bits = int_to_bits_unsigned(word, 32)
            
            # Write word
            self.write_word(addr, word_bits)
            
            # Increment address by 4 (I/O BOUNDARY: address arithmetic)
            addr_int = bits_to_int_unsigned(addr)
            addr_int += 4
            addr = int_to_bits_unsigned(addr_int, 32)
        
        # Set program end
        self.program_end = self.program_start + (len(words) * 4)
    
    def dump_memory(self, start_addr: int, end_addr: int) -> str:
        """
        Dump memory contents as hex string for debugging.
        
        Args:
            start_addr: Start address (int)
            end_addr: End address (int)
        
        Returns:
            String representation of memory contents
        
        Convention:
        - I/O BOUNDARY FUNCTION (for debugging/display only)
        """
        lines = []
        lines.append(f"Memory Dump: 0x{start_addr:08X} - 0x{end_addr:08X}")
        lines.append("-" * 60)
        
        # Align to word boundary
        start_addr = (start_addr // 4) * 4
        
        addr = start_addr
        while addr < end_addr:
            try:
                addr_bits = int_to_bits_unsigned(addr, 32)
                word_bits = self.read_word(addr_bits)
                word_hex = bits_to_hex_string(word_bits)
                lines.append(f"0x{addr:08X}: 0x{word_hex}")
                addr += 4
            except ValueError:
                break
        
        return "\n".join(lines)
    
    def get_instruction_region(self) -> tuple:
        """
        Get instruction memory region bounds.
        
        Returns:
            Tuple of (base_addr, size_bytes)
        """
        return (self.INSTRUCTION_BASE, self.INSTRUCTION_SIZE)
    
    def get_data_region(self) -> tuple:
        """
        Get data memory region bounds.
        
        Returns:
            Tuple of (base_addr, size_bytes)
        """
        return (self.DATA_BASE, self.DATA_SIZE)

# AI-END
