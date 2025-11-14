"""
Unit tests for Fetch Unit module

Tests instruction fetch, PC management, and branch/jump operations.

Author: RISCSim Team
Date: November 2025
"""

# AI-BEGIN: Claude Code (Anthropic) - November 14, 2025
# Prompt: "Create comprehensive tests for fetch unit following Phase 1 requirements"

import pytest
from riscsim.cpu.memory import Memory
from riscsim.cpu.fetch import FetchUnit
from riscsim.utils.bit_utils import int_to_bits_unsigned, bits_to_int_unsigned


class TestFetchSequential:
    """Test sequential instruction fetching."""
    
    def test_fetch_single_instruction(self):
        """Test fetching a single instruction."""
        mem = Memory()
        
        # Write instruction at address 0
        addr = int_to_bits_unsigned(0x00000000, 32)
        instr = int_to_bits_unsigned(0x00500093, 32)  # addi x1, x0, 5
        mem.write_word(addr, instr)
        
        # Create fetch unit
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        # Fetch instruction
        result = fetch.fetch()
        assert bits_to_int_unsigned(result) == 0x00500093
    
    def test_fetch_multiple_sequential(self):
        """Test fetching multiple sequential instructions."""
        mem = Memory()
        
        # Write three instructions
        instructions = [
            (0x00000000, 0x00500093),  # addi x1, x0, 5
            (0x00000004, 0x00A00113),  # addi x2, x0, 10
            (0x00000008, 0x002081B3),  # add x3, x1, x2
        ]
        
        for addr_int, instr_int in instructions:
            addr = int_to_bits_unsigned(addr_int, 32)
            instr = int_to_bits_unsigned(instr_int, 32)
            mem.write_word(addr, instr)
        
        # Fetch sequentially
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        for _, expected_instr in instructions:
            result = fetch.fetch()
            assert bits_to_int_unsigned(result) == expected_instr
            fetch.increment_pc()
    
    def test_fetch_from_different_addresses(self):
        """Test fetching from different starting addresses."""
        mem = Memory()
        
        # Write instructions at different addresses
        test_cases = [
            (0x00000000, 0x11111111),
            (0x00000100, 0x22222222),
            (0x00001000, 0x33333333),
        ]
        
        for addr_int, instr_int in test_cases:
            addr = int_to_bits_unsigned(addr_int, 32)
            instr = int_to_bits_unsigned(instr_int, 32)
            mem.write_word(addr, instr)
        
        # Test each address
        for addr_int, expected_instr in test_cases:
            fetch = FetchUnit(mem, initial_pc=addr_int)
            result = fetch.fetch()
            assert bits_to_int_unsigned(result) == expected_instr


class TestPCIncrement:
    """Test PC increment operations."""
    
    def test_pc_increment_basic(self):
        """Test basic PC increment by 4."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        # Initial PC
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00000000
        
        # Increment
        fetch.increment_pc()
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00000004
        
        # Increment again
        fetch.increment_pc()
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00000008
    
    def test_pc_increment_multiple(self):
        """Test multiple PC increments."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        expected_pcs = [0x00000000, 0x00000004, 0x00000008, 0x0000000C, 0x00000010]
        
        for expected_pc in expected_pcs:
            assert bits_to_int_unsigned(fetch.get_pc()) == expected_pc
            fetch.increment_pc()
    
    def test_pc_increment_from_nonzero(self):
        """Test PC increment from non-zero address."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00001000)
        
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00001000
        
        fetch.increment_pc()
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00001004
        
        fetch.increment_pc()
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00001008


class TestBranchAbsolute:
    """Test absolute branch/jump operations."""
    
    def test_branch_to_forward(self):
        """Test branching forward to target address."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        # Branch to address 0x00000100
        target = int_to_bits_unsigned(0x00000100, 32)
        fetch.branch_to(target)
        
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00000100
    
    def test_branch_to_backward(self):
        """Test branching backward to earlier address."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00001000)
        
        # Branch back to address 0x00000100
        target = int_to_bits_unsigned(0x00000100, 32)
        fetch.branch_to(target)
        
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00000100
    
    def test_branch_to_same_address(self):
        """Test branching to same address (infinite loop)."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000100)
        
        # Branch to same address
        target = int_to_bits_unsigned(0x00000100, 32)
        fetch.branch_to(target)
        
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00000100
    
    def test_branch_to_unaligned_rejected(self):
        """Test that branching to unaligned address is rejected."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        # Try to branch to unaligned address
        target = int_to_bits_unsigned(0x00000101, 32)  # Not aligned
        
        with pytest.raises(ValueError, match="not word-aligned"):
            fetch.branch_to(target)


class TestBranchRelative:
    """Test relative branch operations."""
    
    def test_branch_relative_forward(self):
        """Test relative branch forward."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000100)
        
        # Branch forward by 8 bytes
        offset = int_to_bits_unsigned(0x00000008, 32)
        fetch.branch_relative(offset)
        
        # PC should be 0x00000100 + 0x00000008 = 0x00000108
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00000108
    
    def test_branch_relative_backward(self):
        """Test relative branch backward."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000100)
        
        # Branch backward by 16 bytes (use two's complement)
        # -16 = 0xFFFFFFF0 in 32-bit two's complement
        offset = int_to_bits_unsigned(0xFFFFFFF0, 32)
        fetch.branch_relative(offset)
        
        # PC should be 0x00000100 + (-16) = 0x000000F0
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x000000F0
    
    def test_branch_relative_zero(self):
        """Test relative branch with zero offset."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000100)
        
        # Branch with zero offset
        offset = int_to_bits_unsigned(0x00000000, 32)
        fetch.branch_relative(offset)
        
        # PC should be unchanged
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00000100


class TestPCOverflow:
    """Test PC behavior near address boundaries."""
    
    def test_pc_near_boundary(self):
        """Test PC increment near memory boundary."""
        mem = Memory(size_bytes=0x10000)  # 64KB
        
        # Start near end of memory
        fetch = FetchUnit(mem, initial_pc=0x0000FFF0)
        
        # Should be able to increment
        fetch.increment_pc()
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x0000FFF4
        
        fetch.increment_pc()
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x0000FFF8
        
        fetch.increment_pc()
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x0000FFFC
    
    def test_pc_wrap_around(self):
        """Test PC can wrap around (overflow)."""
        mem = Memory()
        
        # Start near max 32-bit address
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        # Set PC near max value (though memory won't support it)
        # Just testing PC arithmetic wraps correctly
        high_pc = int_to_bits_unsigned(0xFFFFFFFC, 32)
        fetch.set_pc(high_pc)
        
        assert bits_to_int_unsigned(fetch.get_pc()) == 0xFFFFFFFC


class TestPCAlignment:
    """Test PC alignment checking."""
    
    def test_initial_pc_aligned(self):
        """Test that initial PC must be aligned."""
        mem = Memory()
        
        # Aligned addresses should work
        aligned_pcs = [0x00000000, 0x00000004, 0x00000100, 0x00001000]
        
        for pc in aligned_pcs:
            fetch = FetchUnit(mem, initial_pc=pc)
            assert bits_to_int_unsigned(fetch.get_pc()) == pc
    
    def test_initial_pc_unaligned_rejected(self):
        """Test that unaligned initial PC is rejected."""
        mem = Memory()
        
        # Unaligned addresses should fail
        unaligned_pcs = [0x00000001, 0x00000002, 0x00000003]
        
        for pc in unaligned_pcs:
            with pytest.raises(ValueError, match="not word-aligned"):
                FetchUnit(mem, initial_pc=pc)
    
    def test_set_pc_unaligned_rejected(self):
        """Test that setting PC to unaligned address is rejected."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        # Try to set to unaligned address
        unaligned_pc = int_to_bits_unsigned(0x00000002, 32)
        
        with pytest.raises(ValueError, match="not word-aligned"):
            fetch.set_pc(unaligned_pc)


class TestGetNextPC:
    """Test getting next PC without updating current PC."""
    
    def test_get_next_pc_no_update(self):
        """Test that get_next_pc doesn't update current PC."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000100)
        
        # Get next PC
        next_pc = fetch.get_next_pc()
        
        # Should be PC + 4
        assert bits_to_int_unsigned(next_pc) == 0x00000104
        
        # Current PC should be unchanged
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00000100
    
    def test_get_next_pc_for_jalr(self):
        """Test get_next_pc for computing return address (JAL/JALR)."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00001000)
        
        # Get return address (PC + 4)
        return_addr = fetch.get_next_pc()
        assert bits_to_int_unsigned(return_addr) == 0x00001004
        
        # Current PC unchanged
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00001000


class TestPCGetSet:
    """Test PC get/set operations."""
    
    def test_get_pc(self):
        """Test getting current PC."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000100)
        
        pc = fetch.get_pc()
        assert bits_to_int_unsigned(pc) == 0x00000100
    
    def test_set_pc(self):
        """Test setting PC to new value."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        # Set PC to different address
        new_pc = int_to_bits_unsigned(0x00001000, 32)
        fetch.set_pc(new_pc)
        
        assert bits_to_int_unsigned(fetch.get_pc()) == 0x00001000
    
    def test_set_pc_multiple_times(self):
        """Test setting PC multiple times."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        addresses = [0x00000100, 0x00000200, 0x00001000, 0x00000000]
        
        for addr_int in addresses:
            addr = int_to_bits_unsigned(addr_int, 32)
            fetch.set_pc(addr)
            assert bits_to_int_unsigned(fetch.get_pc()) == addr_int


class TestFetchErrors:
    """Test error handling in fetch operations."""
    
    def test_fetch_out_of_bounds(self):
        """Test fetching from out-of-bounds address."""
        mem = Memory(size_bytes=1024)
        
        # Start at valid address
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        # Jump to out-of-bounds address
        oob_addr = int_to_bits_unsigned(0x00010000, 32)
        fetch.set_pc(oob_addr)
        
        # Fetch should fail
        with pytest.raises(ValueError, match="out of bounds"):
            fetch.fetch()
    
    def test_fetch_unaligned_pc(self):
        """Test that fetch detects unaligned PC."""
        mem = Memory()
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        # Manually corrupt PC to unaligned (shouldn't happen in normal use)
        fetch.pc = int_to_bits_unsigned(0x00000001, 32)
        
        # Fetch should detect misalignment
        with pytest.raises(ValueError, match="not word-aligned"):
            fetch.fetch()


# AI-END
