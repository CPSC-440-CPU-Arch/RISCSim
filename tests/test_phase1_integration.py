"""
Integration test for Phase 1: Memory and Fetch Unit

Verifies that memory and fetch unit work together correctly.

Author: RISCSim Team
Date: November 2025
"""

# AI-BEGIN: Claude Code (Anthropic) - November 14, 2025
# Prompt: "Create integration test for Phase 1 memory and fetch functionality"

import pytest
from riscsim.cpu.memory import Memory
from riscsim.cpu.fetch import FetchUnit
from riscsim.utils.bit_utils import bits_to_int_unsigned, int_to_bits_unsigned
import os


class TestPhase1Integration:
    """Integration tests for Phase 1 components."""
    
    def test_load_and_fetch_test_base_program(self):
        """Test loading test_base.hex and fetching instructions."""
        # Get path to test_base.hex
        test_dir = os.path.dirname(__file__)
        hex_file = os.path.join(test_dir, 'programs', 'test_base.hex')
        
        # Skip if file doesn't exist
        if not os.path.exists(hex_file):
            pytest.skip(f"test_base.hex not found at {hex_file}")
        
        # Create memory and load program
        mem = Memory()
        mem.load_program(hex_file)
        
        # Create fetch unit
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        # Expected instructions from test_base.s
        expected_instructions = [
            0x00500093,  # addi x1, x0, 5
            0x00A00113,  # addi x2, x0, 10
            0x002081B3,  # add x3, x1, x2
            0x40110233,  # sub x4, x2, x1
            0x000102B7,  # lui x5, 0x00010
            0x0032A023,  # sw x3, 0(x5)
            0x0002A203,  # lw x4, 0(x5)
            0x00418463,  # beq x3, x4, label1
            0x00100313,  # addi x6, x0, 1 (skipped)
            0x00200313,  # addi x6, x0, 2
            0x0000006F,  # jal x0, 0 (infinite loop)
        ]
        
        # Fetch and verify each instruction
        for i, expected in enumerate(expected_instructions):
            # Fetch instruction
            instr = fetch.fetch()
            instr_int = bits_to_int_unsigned(instr)
            
            # Verify
            assert instr_int == expected, \
                f"Instruction {i} mismatch: got 0x{instr_int:08X}, expected 0x{expected:08X}"
            
            # Increment PC for next instruction
            fetch.increment_pc()
        
        # Verify final PC
        final_pc = bits_to_int_unsigned(fetch.get_pc())
        assert final_pc == 0x0000002C  # 11 instructions * 4 bytes
    
    def test_memory_fetch_integration(self):
        """Test basic memory and fetch integration."""
        mem = Memory()
        
        # Write some instructions manually
        instructions = [
            (0x00000000, 0x12345678),
            (0x00000004, 0xABCDEF00),
            (0x00000008, 0xDEADBEEF),
        ]
        
        for addr_int, instr_int in instructions:
            addr = int_to_bits_unsigned(addr_int, 32)
            instr = int_to_bits_unsigned(instr_int, 32)
            mem.write_word(addr, instr)
        
        # Create fetch unit and fetch instructions
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        for addr_int, expected_instr in instructions:
            # Verify PC
            assert bits_to_int_unsigned(fetch.get_pc()) == addr_int
            
            # Fetch
            instr = fetch.fetch()
            assert bits_to_int_unsigned(instr) == expected_instr
            
            # Next
            fetch.increment_pc()
    
    def test_fetch_from_data_region(self):
        """Test that fetch can access data memory region (for data loads)."""
        mem = Memory()
        
        # Write word to data region
        data_addr = int_to_bits_unsigned(0x00010000, 32)
        data_word = int_to_bits_unsigned(0xCAFEBABE, 32)
        mem.write_word(data_addr, data_word)
        
        # Create fetch unit starting at data region
        fetch = FetchUnit(mem, initial_pc=0x00010000)
        
        # Fetch should work (even though this is data region)
        word = fetch.fetch()
        assert bits_to_int_unsigned(word) == 0xCAFEBABE
    
    def test_branch_and_fetch(self):
        """Test branching and then fetching from new location."""
        mem = Memory()
        
        # Write instructions at different locations
        mem.write_word(
            int_to_bits_unsigned(0x00000000, 32),
            int_to_bits_unsigned(0x11111111, 32)
        )
        mem.write_word(
            int_to_bits_unsigned(0x00000100, 32),
            int_to_bits_unsigned(0x22222222, 32)
        )
        
        # Start at 0x00000000
        fetch = FetchUnit(mem, initial_pc=0x00000000)
        
        # Fetch first instruction
        instr1 = fetch.fetch()
        assert bits_to_int_unsigned(instr1) == 0x11111111
        
        # Branch to 0x00000100
        fetch.branch_to(int_to_bits_unsigned(0x00000100, 32))
        
        # Fetch from new location
        instr2 = fetch.fetch()
        assert bits_to_int_unsigned(instr2) == 0x22222222
    
    def test_sequential_fetch_pattern(self):
        """Test typical sequential fetch pattern."""
        mem = Memory()
        
        # Load a sequence of instructions
        base_addr = 0x00000000
        num_instructions = 10
        
        for i in range(num_instructions):
            addr = int_to_bits_unsigned(base_addr + i * 4, 32)
            # Use i as the instruction value for easy verification
            instr = int_to_bits_unsigned(i * 0x01010101, 32)
            mem.write_word(addr, instr)
        
        # Fetch all instructions sequentially
        fetch = FetchUnit(mem, initial_pc=base_addr)
        
        for i in range(num_instructions):
            # Verify PC
            expected_pc = base_addr + i * 4
            assert bits_to_int_unsigned(fetch.get_pc()) == expected_pc
            
            # Fetch
            instr = fetch.fetch()
            expected_instr = i * 0x01010101
            assert bits_to_int_unsigned(instr) == expected_instr
            
            # Increment
            fetch.increment_pc()


class TestPhase1Summary:
    """Summary test to verify Phase 1 completion."""
    
    def test_phase1_components_exist(self):
        """Verify all Phase 1 components are implemented."""
        # Check Memory module
        from riscsim.cpu.memory import Memory
        mem = Memory()
        assert hasattr(mem, 'read_word')
        assert hasattr(mem, 'write_word')
        assert hasattr(mem, 'read_byte')
        assert hasattr(mem, 'write_byte')
        assert hasattr(mem, 'load_program')
        
        # Check FetchUnit module
        from riscsim.cpu.fetch import FetchUnit
        fetch = FetchUnit(mem)
        assert hasattr(fetch, 'fetch')
        assert hasattr(fetch, 'increment_pc')
        assert hasattr(fetch, 'branch_to')
        assert hasattr(fetch, 'get_pc')
        assert hasattr(fetch, 'set_pc')
        
        # Check hex_loader module
        from riscsim.utils.hex_loader import load_hex_file, parse_hex_line, validate_hex_file
        assert callable(load_hex_file)
        assert callable(parse_hex_line)
        assert callable(validate_hex_file)
    
    def test_phase1_test_coverage(self):
        """Verify Phase 1 has comprehensive test coverage."""
        import os
        test_dir = os.path.dirname(__file__)
        
        # Check test files exist
        assert os.path.exists(os.path.join(test_dir, 'test_memory.py'))
        assert os.path.exists(os.path.join(test_dir, 'test_fetch.py'))
        assert os.path.exists(os.path.join(test_dir, 'test_hex_loader.py'))


# AI-END
