# AI-BEGIN: Claude Code (Anthropic) - November 14, 2025
# Prompt: "Implement Phase 5: Test Program Execution with comprehensive testing"
"""
Phase 5: Test Program Execution

Comprehensive tests for executing complete RISC-V programs loaded from .hex files.
Tests verify correct execution of arithmetic, logical, shift, memory, branch, and jump operations.

Test Programs:
- test_base.hex: Basic program from specification
- test_arithmetic.hex: Arithmetic operations (ADD, SUB, ADDI, overflow)
- test_logical.hex: Logical operations (AND, OR, XOR and immediate variants)
- test_shifts.hex: Shift operations (SLL, SRL, SRA and immediate variants)
- test_memory.hex: Memory operations (LW, SW with various offsets)
- test_branches.hex: Branch operations (BEQ, BNE, forward/backward)
- test_jumps.hex: Jump operations (JAL, JALR, return addresses)

Each test verifies:
- Program loads correctly
- Instructions execute as expected
- Register state matches expected values
- Memory state matches expected values (for memory tests)
- Execution statistics are accurate

Convention: All bit arrays use MSB-at-index-0 convention.
"""

import pytest
import os
from riscsim.cpu.cpu import CPU


class TestBaseProgram:
    """Tests for the base test program (test_base.hex)."""
    
    def test_base_program_execution(self):
        """
        Test execution of test_base.hex program.
        
        Program flow:
        1. addi x1, x0, 5          # x1 = 5
        2. addi x2, x0, 10         # x2 = 10
        3. add x3, x1, x2          # x3 = 15
        4. sub x4, x2, x1          # x4 = 5
        5. lui x5, 0x00010         # x5 = 0x00010000
        6. sw x3, 0(x5)            # mem[0x00010000] = 15
        7. lw x4, 0(x5)            # x4 = 15
        8. beq x3, x4, label1      # branch forward (taken)
        9. addi x6, x0, 1          # skipped
        10. addi x6, x0, 2         # x6 = 2
        11. jal x0, 0              # infinite loop
        """
        cpu = CPU(memory_size=131072)  # 128KB to accommodate data region at 0x00010000
        hex_file = os.path.join(os.path.dirname(__file__), 'programs', 'test_base.hex')
        cpu.load_program(hex_file)
        
        # Run until halt (infinite loop detected)
        result = cpu.run(max_cycles=100)
        
        # Verify execution completed
        assert result.cycles > 0
        assert result.instructions > 0
        assert result.halt_reason in ["infinite_loop", "max_cycles"]
        
        # Verify register values
        assert cpu.get_register(1) == 5, "x1 should be 5"
        assert cpu.get_register(2) == 10, "x2 should be 10"
        assert cpu.get_register(3) == 15, "x3 should be 15"
        assert cpu.get_register(4) == 15, "x4 should be 15 (loaded from memory)"
        assert cpu.get_register(5) == 0x00010000, "x5 should be 0x00010000"
        assert cpu.get_register(6) == 2, "x6 should be 2 (branch taken, instruction 9 skipped)"
    
    def test_base_program_memory_state(self):
        """Test that test_base.hex correctly stores value to memory."""
        cpu = CPU(memory_size=131072)  # 128KB to accommodate data region
        hex_file = os.path.join(os.path.dirname(__file__), 'programs', 'test_base.hex')
        cpu.load_program(hex_file)
        
        # Run program
        cpu.run(max_cycles=100)
        
        # Verify memory at 0x00010000 contains 15 (stored by sw instruction)
        mem_value = cpu.get_memory_word(0x00010000)
        assert mem_value == 15, f"Memory at 0x00010000 should be 15, got {mem_value}"
    
    def test_base_program_register_state(self):
        """Test detailed register state after test_base.hex execution."""
        cpu = CPU(memory_size=131072)  # 128KB to accommodate data region
        hex_file = os.path.join(os.path.dirname(__file__), 'programs', 'test_base.hex')
        cpu.load_program(hex_file)
        
        result = cpu.run(max_cycles=100)
        
        # Verify all expected registers
        expected_registers = {
            0: 0,           # x0 is always 0
            1: 5,           # addi x1, x0, 5
            2: 10,          # addi x2, x0, 10
            3: 15,          # add x3, x1, x2
            4: 15,          # lw x4, 0(x5) - loaded from memory
            5: 0x00010000,  # lui x5, 0x00010
            6: 2,           # addi x6, x0, 2 (after branch)
        }
        
        for reg_num, expected_value in expected_registers.items():
            actual_value = cpu.get_register(reg_num)
            assert actual_value == expected_value, \
                f"x{reg_num} should be {expected_value}, got {actual_value}"


class TestArithmeticProgram:
    """Tests for arithmetic operations program."""
    
    def test_arithmetic_program(self):
        """
        Test execution of test_arithmetic.hex.
        
        Tests:
        - Basic ADD, SUB, ADDI
        - Overflow scenarios
        - Zero register behavior
        - Negative values
        """
        cpu = CPU(memory_size=131072)  # 128KB to accommodate data region
        hex_file = os.path.join(os.path.dirname(__file__), 'programs', 'test_arithmetic.hex')
        cpu.load_program(hex_file)
        
        result = cpu.run(max_cycles=100)
        
        # Verify basic operations
        assert cpu.get_register(1) == 5, "x1 should be 5"
        assert cpu.get_register(2) == 10, "x2 should be 10"
        assert cpu.get_register(3) == 15, "x3 should be 15 (5+10)"
        assert cpu.get_register(4) == 5, "x4 should be 5 (10-5)"
        
        # Verify larger values
        assert cpu.get_register(5) == 0x7FF, "x5 should be 0x7FF"
        assert cpu.get_register(6) == 0x800, "x6 should be 0x800 (0x7FF+1)"
        
        # Verify negative value handling
        assert cpu.get_register(7) == 0xFFFFFFFF, "x7 should be -1 (0xFFFFFFFF)"
        assert cpu.get_register(8) == 0, "x8 should be 0 (-1+1)"
        
        # Verify zero register behavior
        assert cpu.get_register(9) == 0, "x9 should be 0 (0+0)"
        assert cpu.get_register(10) == 0, "x10 should be 0"
        
        # Verify execution statistics
        stats = cpu.get_statistics()
        assert stats.instructions_executed > 0, "Should execute instructions"
        assert stats.total_cycles > 0, "Should have cycles"


class TestLogicalProgram:
    """Tests for logical operations program."""
    
    def test_logical_program(self):
        """
        Test execution of test_logical.hex.
        
        Tests:
        - AND, OR, XOR operations
        - Immediate variants (ANDI, ORI, XORI)
        - All ones/all zeros cases
        - Sign extension of immediates
        """
        cpu = CPU(memory_size=131072)  # 128KB to accommodate data region
        hex_file = os.path.join(os.path.dirname(__file__), 'programs', 'test_logical.hex')
        cpu.load_program(hex_file)
        
        result = cpu.run(max_cycles=100)
        
        # Verify setup values
        assert cpu.get_register(1) == 0x7FF, "x1 should be 0x7FF"
        assert cpu.get_register(2) == 0x555, "x2 should be 0x555"
        assert cpu.get_register(3) == 0x2AA, "x3 should be 0x2AA"
        assert cpu.get_register(4) == 0xFFFFFFFF, "x4 should be 0xFFFFFFFF (all 1s)"
        
        # Verify AND operations
        assert cpu.get_register(5) == 0x555, "x5 should be 0x555 (0x7FF & 0x555)"
        assert cpu.get_register(6) == 0x0FF, "x6 should be 0x0FF (0x7FF & 0x0FF)"
        assert cpu.get_register(8) == 0, "x8 should be 0 (0 & anything)"
        
        # Verify OR operations
        assert cpu.get_register(9) == 0x7FF, "x9 should be 0x7FF (0x7FF | 0x555)"
        assert cpu.get_register(11) == 0x7FF, "x11 should be 0x7FF (0 | 0x7FF)"
        
        # Verify XOR operations
        assert cpu.get_register(13) == 0x2AA, "x13 should be 0x2AA (0x7FF ^ 0x555)"
        assert cpu.get_register(15) == 0, "x15 should be 0 (same value XOR)"
        assert cpu.get_register(16) == 0x7FF, "x16 should be 0x7FF (0x7FF ^ 0)"
        
        # Verify all zeros
        assert cpu.get_register(17) == 0, "x17 should be 0 (0 & 0)"
        assert cpu.get_register(18) == 0, "x18 should be 0 (0 | 0)"
        assert cpu.get_register(19) == 0, "x19 should be 0 (0 ^ 0)"


class TestShiftsProgram:
    """Tests for shift operations program."""
    
    def test_shifts_program(self):
        """
        Test execution of test_shifts.hex.
        
        Tests:
        - SLL, SRL, SRA operations
        - Immediate variants (SLLI, SRLI, SRAI)
        - Various shift amounts (0, 1, 31)
        - Sign extension for SRA
        """
        cpu = CPU(memory_size=131072)  # 128KB to accommodate data region
        hex_file = os.path.join(os.path.dirname(__file__), 'programs', 'test_shifts.hex')
        cpu.load_program(hex_file)
        
        result = cpu.run(max_cycles=150)
        
        # Verify setup values
        assert cpu.get_register(1) == 1, "x1 should be 1"
        assert cpu.get_register(2) == 0x7FF, "x2 should be 0x7FF"
        assert cpu.get_register(3) == 0xFFFFFFFF, "x3 should be 0xFFFFFFFF"
        assert cpu.get_register(4) == 0x80000000, "x4 should be 0x80000000"
        
        # Verify SLL operations
        assert cpu.get_register(5) == 1, "x5 should be 1 (1<<0)"
        assert cpu.get_register(6) == 2, "x6 should be 2 (1<<1)"
        assert cpu.get_register(7) == 16, "x7 should be 16 (1<<4)"
        assert cpu.get_register(8) == 0x80000000, "x8 should be 0x80000000 (1<<31)"
        
        # Verify SRL operations (logical right shift - zero extension)
        assert cpu.get_register(10) == 0x40000000, "x10 should be 0x40000000 (0x80000000>>1)"
        assert cpu.get_register(11) == 1, "x11 should be 1 (0x80000000>>31)"
        assert cpu.get_register(12) == 0x7FFFFFFF, "x12 should be 0x7FFFFFFF (0xFFFFFFFF>>1)"
        
        # Verify SRA operations (arithmetic right shift - sign extension)
        assert cpu.get_register(14) == 0xC0000000, "x14 should be 0xC0000000 (0x80000000>>1 sign ext)"
        assert cpu.get_register(15) == 0xFFFFFFFF, "x15 should be 0xFFFFFFFF (0x80000000>>31 sign ext)"
        assert cpu.get_register(16) == 0x3FF, "x16 should be 0x3FF (0x7FF>>1, positive no sign ext)"
        
        # Verify variable shift
        assert cpu.get_register(17) == 8, "x17 should be 8 (shift amount)"
        assert cpu.get_register(18) == 256, "x18 should be 256 (1<<8)"


class TestMemoryProgram:
    """Tests for memory operations program."""
    
    def test_memory_program(self):
        """
        Test execution of test_memory.hex.
        
        Tests:
        - LW/SW operations
        - Various offsets (positive, negative, zero)
        - Different memory addresses
        - Data hazards (store then immediate load)
        - Sequential stores and loads
        """
        cpu = CPU(memory_size=131072)  # 128KB to accommodate data region
        hex_file = os.path.join(os.path.dirname(__file__), 'programs', 'test_memory.hex')
        cpu.load_program(hex_file)
        
        result = cpu.run(max_cycles=200)
        
        # Verify base address setup
        assert cpu.get_register(1) == 0x00010000, "x1 should be 0x00010000"
        
        # Verify basic store/load
        assert cpu.get_register(2) == 42, "x2 should be 42"
        assert cpu.get_register(5) == 42, "x5 should be 42 (loaded from memory)"
        assert cpu.get_memory_word(0x00010000) == 42, "mem[0x00010000] should be 42"
        
        assert cpu.get_register(3) == 100, "x3 should be 100"
        assert cpu.get_register(6) == 100, "x6 should be 100 (loaded from memory)"
        assert cpu.get_memory_word(0x00010004) == 100, "mem[0x00010004] should be 100"
        
        # Verify negative value storage
        assert cpu.get_register(4) == 0xFFFFFFFF, "x4 should be 0xFFFFFFFF"
        assert cpu.get_register(7) == 0xFFFFFFFF, "x7 should be 0xFFFFFFFF (loaded)"
        assert cpu.get_memory_word(0x00010008) == 0xFFFFFFFF, "mem[0x00010008] should be 0xFFFFFFFF"
        
        # Verify store with offset
        assert cpu.get_register(8) == 0x123, "x8 should be 0x123"
        assert cpu.get_register(9) == 0x123, "x9 should be 0x123 (loaded)"
        
        # Verify negative offset usage (overwrites previous value at 0x0001000C)
        assert cpu.get_register(11) == 55, "x11 should be 55"
        assert cpu.get_register(12) == 55, "x12 should be 55 (loaded with negative offset)"
        
        # Verify different memory region
        assert cpu.get_register(13) == 0x00011000, "x13 should be 0x00011000"
        assert cpu.get_register(14) == 77, "x14 should be 77"
        assert cpu.get_register(15) == 77, "x15 should be 77 (loaded)"
        assert cpu.get_memory_word(0x00011000) == 77, "mem[0x00011000] should be 77"
        
        # Verify sequential operations
        assert cpu.get_register(19) == 1, "x19 should be 1"
        assert cpu.get_register(20) == 2, "x20 should be 2"
        assert cpu.get_register(21) == 3, "x21 should be 3"
        
        # Verify data hazard handling
        assert cpu.get_register(22) == 99, "x22 should be 99"
        assert cpu.get_register(23) == 99, "x23 should be 99 (immediate load after store)"
        
        # Verify computed address
        assert cpu.get_register(26) == 88, "x26 should be 88"
        assert cpu.get_register(27) == 88, "x27 should be 88 (loaded from computed address)"


class TestBranchesProgram:
    """Tests for branch operations program."""
    
    def test_branches_program(self):
        """
        Test execution of test_branches.hex.
        
        Tests:
        - BEQ taken and not taken
        - BNE taken and not taken
        - Forward branches
        - Backward branches (loops)
        - Branch chaining
        """
        cpu = CPU(memory_size=131072)  # 128KB to accommodate data region
        hex_file = os.path.join(os.path.dirname(__file__), 'programs', 'test_branches.hex')
        cpu.load_program(hex_file)
        
        result = cpu.run(max_cycles=200)
        
        # Verify setup
        assert cpu.get_register(1) == 10, "x1 should be 10"
        assert cpu.get_register(2) == 10, "x2 should be 10"
        assert cpu.get_register(3) == 5, "x3 should be 5"
        
        # Verify BEQ taken (forward branch)
        assert cpu.get_register(4) == 0, "x4 should be 0 (instruction skipped by BEQ)"
        assert cpu.get_register(5) == 0, "x5 should be 0 (instruction skipped by BEQ)"
        assert cpu.get_register(6) == 3, "x6 should be 3 (branch target executed)"
        
        # Verify BEQ not taken
        assert cpu.get_register(7) == 4, "x7 should be 4 (BEQ not taken, executed)"
        assert cpu.get_register(8) == 5, "x8 should be 5 (BEQ not taken, executed)"
        
        # Verify BNE not taken
        assert cpu.get_register(9) == 6, "x9 should be 6 (BNE not taken, executed)"
        assert cpu.get_register(10) == 7, "x10 should be 7 (BNE not taken, executed)"
        
        # Verify BNE taken
        assert cpu.get_register(11) == 0, "x11 should be 0 (skipped by BNE)"
        assert cpu.get_register(12) == 0, "x12 should be 0 (skipped by BNE)"
        assert cpu.get_register(13) == 10, "x13 should be 10 (BNE branch target)"
        
        # Verify forward branch over multiple instructions
        assert cpu.get_register(14) == 20, "x14 should be 20"
        assert cpu.get_register(15) == 0, "x15 should be 0 (skipped)"
        assert cpu.get_register(16) == 0, "x16 should be 0 (skipped)"
        assert cpu.get_register(17) == 0, "x17 should be 0 (skipped)"
        assert cpu.get_register(18) == 0, "x18 should be 0 (skipped)"
        assert cpu.get_register(19) == 15, "x19 should be 15 (executed after branch)"
        
        # Verify backward branch (loop)
        # Loop should execute until x20 == 3
        # Loop body does: x21 = x20 + 1, x20++, check if x20 != 3
        # Iterations: x20=0,x21=1; x20=1,x21=2; x20=2,x21=3; x20=3,exit
        assert cpu.get_register(20) == 3, "x20 should be 3 (loop counter)"
        assert cpu.get_register(21) == 3, "x21 should be 3 (last value x20+1 = 2+1)"
        assert cpu.get_register(22) == 3, "x22 should be 3 (loop limit)"
        assert cpu.get_register(23) == 200, "x23 should be 200 (after loop)"


class TestJumpsProgram:
    """Tests for jump operations program."""
    
    def test_jumps_program(self):
        """
        Test execution of test_jumps.hex.
        
        Tests:
        - JAL with various offsets
        - Return address storage
        - JALR register indirect jump
        - JALR with offset
        """
        cpu = CPU(memory_size=131072)  # 128KB to accommodate data region
        hex_file = os.path.join(os.path.dirname(__file__), 'programs', 'test_jumps.hex')
        cpu.load_program(hex_file)
        
        result = cpu.run(max_cycles=200)
        
        # Verify JAL forward jump
        # First JAL jumps over 4 instructions, stores return address in x1
        assert cpu.get_register(1) == 4, "x1 should be 4 (return address = PC+4)"
        assert cpu.get_register(2) == 0, "x2 should be 0 (skipped by JAL)"
        assert cpu.get_register(3) == 0, "x3 should be 0 (skipped by JAL)"
        assert cpu.get_register(4) == 0, "x4 should be 0 (skipped by JAL)"
        assert cpu.get_register(5) == 10, "x5 should be 10 (JAL target executed)"
        
        # Verify return address copied
        assert cpu.get_register(6) == cpu.get_register(1), "x6 should equal x1 (return address)"
        
        # Verify second JAL with longer offset
        assert cpu.get_register(7) != 0, "x7 should have return address from second JAL"
        assert cpu.get_register(8) == 0, "x8 should be 0 (skipped by JAL)"
        assert cpu.get_register(16) == 30, "x16 should be 30 (second JAL target)"
        
        # Verify JALR executed
        assert cpu.get_register(18) != 0, "x18 should have return address from JALR"
        assert cpu.get_register(24) == 100, "x24 should be 100 (JALR target)"
        
        # Statistics check
        stats = cpu.get_statistics()
        assert stats.instructions_executed > 0, "Should have executed instructions"
        assert 'JAL' in stats.instruction_mix or 'JALR' in stats.instruction_mix, \
            "Should have JAL or JALR in instruction mix"


class TestProgramStatistics:
    """Tests for execution statistics across all programs."""
    
    def test_program_statistics(self):
        """
        Test that CPU statistics are correctly tracked across program execution.
        
        Verifies:
        - Cycle counting
        - Instruction counting
        - CPI calculation
        - Instruction mix tracking
        - Branch statistics
        """
        cpu = CPU(memory_size=131072)  # 128KB to accommodate data region
        hex_file = os.path.join(os.path.dirname(__file__), 'programs', 'test_base.hex')
        cpu.load_program(hex_file)
        
        result = cpu.run(max_cycles=100)
        stats = cpu.get_statistics()
        
        # Verify basic statistics
        assert stats.total_cycles > 0, "Should have executed cycles"
        assert stats.instructions_executed > 0, "Should have executed instructions"
        assert stats.cpi >= 1.0, "CPI should be at least 1.0 (single-cycle)"
        assert stats.cpi == stats.total_cycles / stats.instructions_executed, \
            "CPI calculation should be correct"
        
        # Verify instruction mix is populated
        assert len(stats.instruction_mix) > 0, "Instruction mix should have entries"
        assert 'ADDI' in stats.instruction_mix, "Should have ADDI in mix"
        assert stats.instruction_mix['ADDI'] > 0, "ADDI count should be > 0"
        
        # Verify branch statistics
        # test_base.hex has one BEQ that is taken
        assert stats.branch_taken_count >= 0, "Branch taken count should be non-negative"
        assert stats.branch_not_taken_count >= 0, "Branch not taken count should be non-negative"
        
        # Test with branch-heavy program
        cpu2 = CPU()
        hex_file2 = os.path.join(os.path.dirname(__file__), 'programs', 'test_branches.hex')
        cpu2.load_program(hex_file2)
        result2 = cpu2.run(max_cycles=200)
        stats2 = cpu2.get_statistics()
        
        # Branch program should have more branch activity
        total_branches = stats2.branch_taken_count + stats2.branch_not_taken_count
        assert total_branches > 0, "Branch program should have branch statistics"
        
        # Verify instruction mix includes branches
        assert 'BEQ' in stats2.instruction_mix or 'BNE' in stats2.instruction_mix, \
            "Branch program should have branch instructions in mix"

# AI-END
# AI-END
