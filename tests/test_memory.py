"""
Unit tests for Memory module

Tests word/byte read/write, alignment, bounds checking, and program loading.

Author: RISCSim Team
Date: November 2025
"""

# AI-BEGIN: Claude Code (Anthropic) - November 14, 2025
# Prompt: "Create comprehensive tests for memory module following Phase 1 requirements"

import pytest
from riscsim.cpu.memory import Memory
from riscsim.utils.bit_utils import int_to_bits_unsigned, bits_to_int_unsigned, bits_to_hex_string
import tempfile
import os


class TestMemoryInitialization:
    """Test memory initialization and configuration."""
    
    def test_memory_initialization(self):
        """Test memory creates with correct size."""
        mem = Memory(size_bytes=1024, base_addr=0x00000000)
        assert mem.size_bytes == 1024
        assert mem.base_addr == 0x00000000
        assert len(mem.memory) == 1024
    
    def test_memory_default_initialization(self):
        """Test default memory size (128KB)."""
        mem = Memory()
        assert mem.size_bytes == 128 * 1024
        assert mem.base_addr == 0x00000000
    
    def test_memory_regions(self):
        """Test instruction and data memory regions."""
        mem = Memory()
        
        # Check instruction region
        i_base, i_size = mem.get_instruction_region()
        assert i_base == 0x00000000
        assert i_size == 0x00010000
        
        # Check data region
        d_base, d_size = mem.get_data_region()
        assert d_base == 0x00010000
        assert d_size == 0x00010000


class TestWordReadWrite:
    """Test word-aligned read/write operations."""
    
    def test_word_write_and_read(self):
        """Test basic word write followed by read."""
        mem = Memory()
        
        # Write word at address 0x00000000
        addr = int_to_bits_unsigned(0x00000000, 32)
        data = int_to_bits_unsigned(0x12345678, 32)
        mem.write_word(addr, data)
        
        # Read it back
        result = mem.read_word(addr)
        assert result == data
        assert bits_to_int_unsigned(result) == 0x12345678
    
    def test_word_write_multiple_addresses(self):
        """Test writing to multiple addresses."""
        mem = Memory()
        
        # Write three words
        test_data = [
            (0x00000000, 0xAAAAAAAA),
            (0x00000004, 0xBBBBBBBB),
            (0x00000008, 0xCCCCCCCC),
        ]
        
        for addr_int, data_int in test_data:
            addr = int_to_bits_unsigned(addr_int, 32)
            data = int_to_bits_unsigned(data_int, 32)
            mem.write_word(addr, data)
        
        # Read them back
        for addr_int, expected_int in test_data:
            addr = int_to_bits_unsigned(addr_int, 32)
            result = mem.read_word(addr)
            assert bits_to_int_unsigned(result) == expected_int
    
    def test_word_overwrite(self):
        """Test overwriting existing word."""
        mem = Memory()
        
        addr = int_to_bits_unsigned(0x00000000, 32)
        
        # Write first value
        data1 = int_to_bits_unsigned(0x11111111, 32)
        mem.write_word(addr, data1)
        assert bits_to_int_unsigned(mem.read_word(addr)) == 0x11111111
        
        # Overwrite with second value
        data2 = int_to_bits_unsigned(0x22222222, 32)
        mem.write_word(addr, data2)
        assert bits_to_int_unsigned(mem.read_word(addr)) == 0x22222222


class TestByteReadWrite:
    """Test byte-level read/write operations."""
    
    def test_byte_write_and_read(self):
        """Test basic byte write followed by read."""
        mem = Memory()
        
        # Write byte at address 0x00000000
        addr = int_to_bits_unsigned(0x00000000, 32)
        data = int_to_bits_unsigned(0xAB, 8)
        mem.write_byte(addr, data)
        
        # Read it back
        result = mem.read_byte(addr)
        assert result == data
        assert bits_to_int_unsigned(result) == 0xAB
    
    def test_byte_write_multiple_addresses(self):
        """Test writing to sequential byte addresses."""
        mem = Memory()
        
        # Write four bytes
        test_data = [
            (0x00000000, 0x12),
            (0x00000001, 0x34),
            (0x00000002, 0x56),
            (0x00000003, 0x78),
        ]
        
        for addr_int, data_int in test_data:
            addr = int_to_bits_unsigned(addr_int, 32)
            data = int_to_bits_unsigned(data_int, 8)
            mem.write_byte(addr, data)
        
        # Read them back
        for addr_int, expected_int in test_data:
            addr = int_to_bits_unsigned(addr_int, 32)
            result = mem.read_byte(addr)
            assert bits_to_int_unsigned(result) == expected_int


class TestLittleEndianOrdering:
    """Test little-endian byte ordering for word operations."""
    
    def test_little_endian_word_storage(self):
        """Test that words are stored in little-endian byte order."""
        mem = Memory()
        
        # Write word 0x12345678 at address 0
        addr = int_to_bits_unsigned(0x00000000, 32)
        word = int_to_bits_unsigned(0x12345678, 32)
        mem.write_word(addr, word)
        
        # Read individual bytes
        # Little-endian: LSB at lowest address
        # Address 0x00: 0x78 (LSB)
        # Address 0x01: 0x56
        # Address 0x02: 0x34
        # Address 0x03: 0x12 (MSB)
        
        byte0 = mem.read_byte(int_to_bits_unsigned(0x00000000, 32))
        byte1 = mem.read_byte(int_to_bits_unsigned(0x00000001, 32))
        byte2 = mem.read_byte(int_to_bits_unsigned(0x00000002, 32))
        byte3 = mem.read_byte(int_to_bits_unsigned(0x00000003, 32))
        
        assert bits_to_int_unsigned(byte0) == 0x78
        assert bits_to_int_unsigned(byte1) == 0x56
        assert bits_to_int_unsigned(byte2) == 0x34
        assert bits_to_int_unsigned(byte3) == 0x12
    
    def test_little_endian_byte_to_word(self):
        """Test that bytes written individually form correct word."""
        mem = Memory()
        
        # Write bytes individually
        mem.write_byte(int_to_bits_unsigned(0x00000000, 32), int_to_bits_unsigned(0x78, 8))
        mem.write_byte(int_to_bits_unsigned(0x00000001, 32), int_to_bits_unsigned(0x56, 8))
        mem.write_byte(int_to_bits_unsigned(0x00000002, 32), int_to_bits_unsigned(0x34, 8))
        mem.write_byte(int_to_bits_unsigned(0x00000003, 32), int_to_bits_unsigned(0x12, 8))
        
        # Read as word
        word = mem.read_word(int_to_bits_unsigned(0x00000000, 32))
        assert bits_to_int_unsigned(word) == 0x12345678


class TestAddressAlignment:
    """Test word address alignment checking."""
    
    def test_aligned_addresses_accepted(self):
        """Test that word-aligned addresses work."""
        mem = Memory()
        data = int_to_bits_unsigned(0xAAAAAAAA, 32)
        
        # Test aligned addresses (multiples of 4)
        aligned_addrs = [0x00000000, 0x00000004, 0x00000008, 0x0000000C, 0x00000010]
        
        for addr_int in aligned_addrs:
            addr = int_to_bits_unsigned(addr_int, 32)
            mem.write_word(addr, data)
            result = mem.read_word(addr)
            assert result == data
    
    def test_unaligned_write_rejected(self):
        """Test that unaligned word writes are rejected."""
        mem = Memory()
        data = int_to_bits_unsigned(0xAAAAAAAA, 32)
        
        # Test unaligned addresses
        unaligned_addrs = [0x00000001, 0x00000002, 0x00000003, 0x00000005]
        
        for addr_int in unaligned_addrs:
            addr = int_to_bits_unsigned(addr_int, 32)
            with pytest.raises(ValueError, match="not word-aligned"):
                mem.write_word(addr, data)
    
    def test_unaligned_read_rejected(self):
        """Test that unaligned word reads are rejected."""
        mem = Memory()
        
        # Test unaligned addresses
        unaligned_addrs = [0x00000001, 0x00000002, 0x00000003]
        
        for addr_int in unaligned_addrs:
            addr = int_to_bits_unsigned(addr_int, 32)
            with pytest.raises(ValueError, match="not word-aligned"):
                mem.read_word(addr)


class TestAddressRangeChecking:
    """Test memory bounds checking."""
    
    def test_valid_addresses_accepted(self):
        """Test that addresses within bounds work."""
        mem = Memory(size_bytes=1024, base_addr=0x00000000)
        
        # First word
        addr = int_to_bits_unsigned(0x00000000, 32)
        data = int_to_bits_unsigned(0x12345678, 32)
        mem.write_word(addr, data)
        assert bits_to_int_unsigned(mem.read_word(addr)) == 0x12345678
        
        # Last word (1024 - 4 = 1020 = 0x3FC)
        addr = int_to_bits_unsigned(0x000003FC, 32)
        mem.write_word(addr, data)
        assert bits_to_int_unsigned(mem.read_word(addr)) == 0x12345678
    
    def test_out_of_bounds_write_rejected(self):
        """Test that out-of-bounds writes are rejected."""
        mem = Memory(size_bytes=1024, base_addr=0x00000000)
        data = int_to_bits_unsigned(0xAAAAAAAA, 32)
        
        # Beyond end of memory
        addr = int_to_bits_unsigned(0x00000400, 32)  # 1024 bytes
        with pytest.raises(ValueError, match="out of bounds"):
            mem.write_word(addr, data)
    
    def test_out_of_bounds_read_rejected(self):
        """Test that out-of-bounds reads are rejected."""
        mem = Memory(size_bytes=1024, base_addr=0x00000000)
        
        # Beyond end of memory
        addr = int_to_bits_unsigned(0x00000400, 32)
        with pytest.raises(ValueError, match="out of bounds"):
            mem.read_word(addr)
    
    def test_byte_bounds_checking(self):
        """Test bounds checking for byte access."""
        mem = Memory(size_bytes=1024, base_addr=0x00000000)
        data = int_to_bits_unsigned(0xAB, 8)
        
        # Last valid byte
        addr = int_to_bits_unsigned(0x000003FF, 32)  # 1023
        mem.write_byte(addr, data)
        assert bits_to_int_unsigned(mem.read_byte(addr)) == 0xAB
        
        # First invalid byte
        addr = int_to_bits_unsigned(0x00000400, 32)  # 1024
        with pytest.raises(ValueError, match="out of bounds"):
            mem.write_byte(addr, data)


class TestLoadProgramFromHex:
    """Test loading programs from .hex files."""
    
    def test_load_simple_program(self):
        """Test loading a simple program."""
        # Create temporary hex file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            f.write("00500093\n")  # addi x1, x0, 5
            f.write("00A00113\n")  # addi x2, x0, 10
            f.write("002081B3\n")  # add x3, x1, x2
            hex_file = f.name
        
        try:
            mem = Memory()
            mem.load_program(hex_file)
            
            # Verify instructions loaded
            instr0 = mem.read_word(int_to_bits_unsigned(0x00000000, 32))
            instr1 = mem.read_word(int_to_bits_unsigned(0x00000004, 32))
            instr2 = mem.read_word(int_to_bits_unsigned(0x00000008, 32))
            
            assert bits_to_int_unsigned(instr0) == 0x00500093
            assert bits_to_int_unsigned(instr1) == 0x00A00113
            assert bits_to_int_unsigned(instr2) == 0x002081B3
            
            # Check program bounds
            assert mem.program_start == 0x00000000
            assert mem.program_end == 0x0000000C  # 3 words * 4 bytes
        
        finally:
            os.unlink(hex_file)
    
    def test_load_program_with_blank_lines(self):
        """Test loading program with blank lines."""
        # Create temporary hex file with blank lines
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            f.write("00500093\n")
            f.write("\n")  # Blank line
            f.write("00A00113\n")
            f.write("\n")
            f.write("002081B3\n")
            hex_file = f.name
        
        try:
            mem = Memory()
            mem.load_program(hex_file)
            
            # Verify instructions loaded (blank lines ignored)
            instr0 = mem.read_word(int_to_bits_unsigned(0x00000000, 32))
            instr1 = mem.read_word(int_to_bits_unsigned(0x00000004, 32))
            instr2 = mem.read_word(int_to_bits_unsigned(0x00000008, 32))
            
            assert bits_to_int_unsigned(instr0) == 0x00500093
            assert bits_to_int_unsigned(instr1) == 0x00A00113
            assert bits_to_int_unsigned(instr2) == 0x002081B3
        
        finally:
            os.unlink(hex_file)


class TestInstructionDataSeparation:
    """Test separation of instruction and data memory regions."""
    
    def test_instruction_region_access(self):
        """Test accessing instruction memory region."""
        mem = Memory()
        
        # Write to instruction region
        addr = int_to_bits_unsigned(0x00000000, 32)
        data = int_to_bits_unsigned(0x12345678, 32)
        mem.write_word(addr, data)
        
        result = mem.read_word(addr)
        assert bits_to_int_unsigned(result) == 0x12345678
    
    def test_data_region_access(self):
        """Test accessing data memory region."""
        mem = Memory()
        
        # Write to data region
        addr = int_to_bits_unsigned(0x00010000, 32)
        data = int_to_bits_unsigned(0xABCDEF00, 32)
        mem.write_word(addr, data)
        
        result = mem.read_word(addr)
        assert bits_to_int_unsigned(result) == 0xABCDEF00
    
    def test_both_regions_independent(self):
        """Test that instruction and data regions are independent."""
        mem = Memory()
        
        # Write to instruction region
        i_addr = int_to_bits_unsigned(0x00000000, 32)
        i_data = int_to_bits_unsigned(0x11111111, 32)
        mem.write_word(i_addr, i_data)
        
        # Write to data region
        d_addr = int_to_bits_unsigned(0x00010000, 32)
        d_data = int_to_bits_unsigned(0x22222222, 32)
        mem.write_word(d_addr, d_data)
        
        # Verify both are preserved
        assert bits_to_int_unsigned(mem.read_word(i_addr)) == 0x11111111
        assert bits_to_int_unsigned(mem.read_word(d_addr)) == 0x22222222


class TestBoundaryAddresses:
    """Test edge cases at memory boundaries."""
    
    def test_first_address(self):
        """Test accessing first memory address."""
        mem = Memory()
        
        addr = int_to_bits_unsigned(0x00000000, 32)
        data = int_to_bits_unsigned(0xFFFFFFFF, 32)
        mem.write_word(addr, data)
        
        result = mem.read_word(addr)
        assert bits_to_int_unsigned(result) == 0xFFFFFFFF
    
    def test_last_valid_word_address(self):
        """Test accessing last valid word address."""
        mem = Memory(size_bytes=1024)
        
        # Last word at offset 1020 (1024 - 4)
        addr = int_to_bits_unsigned(0x000003FC, 32)
        data = int_to_bits_unsigned(0xDEADBEEF, 32)
        mem.write_word(addr, data)
        
        result = mem.read_word(addr)
        assert bits_to_int_unsigned(result) == 0xDEADBEEF
    
    def test_cross_region_boundary(self):
        """Test accessing addresses near region boundary."""
        mem = Memory()
        
        # Near end of instruction region
        addr1 = int_to_bits_unsigned(0x0000FFFC, 32)
        data1 = int_to_bits_unsigned(0x11111111, 32)
        mem.write_word(addr1, data1)
        
        # Start of data region
        addr2 = int_to_bits_unsigned(0x00010000, 32)
        data2 = int_to_bits_unsigned(0x22222222, 32)
        mem.write_word(addr2, data2)
        
        # Verify both
        assert bits_to_int_unsigned(mem.read_word(addr1)) == 0x11111111
        assert bits_to_int_unsigned(mem.read_word(addr2)) == 0x22222222


class TestMemoryDump:
    """Test memory dump functionality for debugging."""
    
    def test_dump_memory(self):
        """Test dumping memory contents."""
        mem = Memory()
        
        # Write some data
        mem.write_word(int_to_bits_unsigned(0x00000000, 32), int_to_bits_unsigned(0x12345678, 32))
        mem.write_word(int_to_bits_unsigned(0x00000004, 32), int_to_bits_unsigned(0xABCDEF00, 32))
        
        # Dump memory
        dump = mem.dump_memory(0x00000000, 0x00000008)
        
        # Verify format
        assert "Memory Dump" in dump
        assert "0x00000000" in dump
        assert "12345678" in dump
        assert "ABCDEF00" in dump


# AI-END
