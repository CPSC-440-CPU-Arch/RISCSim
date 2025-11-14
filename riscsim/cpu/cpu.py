# AI-BEGIN: Claude Code (Anthropic) - November 14, 2025
# Prompt: "Implement Phase 4 CPU Simulator Top-Level with program execution capabilities"
"""
Top-Level RISC-V CPU Simulator

This module implements the top-level CPU class that coordinates all components
and provides a high-level interface for program execution and debugging.

Features:
- Program loading from .hex files
- Single-step execution
- Continuous execution with halt detection
- Register and memory access
- Execution statistics tracking
- Debug output (register/memory dumps)

The CPU class integrates:
- Memory (instruction and data)
- Register File (integer and FP registers)
- Datapath (5-stage single-cycle execution)
- Program loader

Convention: All bit arrays use MSB-at-index-0 convention.
"""

from typing import Dict, List, Optional
from riscsim.cpu.memory import Memory
from riscsim.cpu.registers import RegisterFile
from riscsim.cpu.datapath import Datapath, CycleResult
from riscsim.utils.bit_utils import (
    bits_to_int_unsigned,
    int_to_bits_unsigned
)
from riscsim.utils.twos_complement import decode_twos_complement


class ExecutionResult:
    """Result of program execution.
    
    Captures comprehensive information about program execution including
    cycle count, instruction count, final state, and execution trace.
    
    Attributes:
        cycles: Total number of cycles executed
        instructions: Total number of instructions executed
        final_pc: Program counter value at halt (32-bit unsigned)
        halt_reason: Reason for halting ("max_cycles", "infinite_loop", "target_reached", "invalid_instruction")
        register_state: Dictionary of register values at halt {reg_num: value}
        trace: List of CycleResult objects for execution trace
    """
    
    def __init__(self):
        self.cycles: int = 0
        self.instructions: int = 0
        self.final_pc: int = 0
        self.halt_reason: str = ""
        self.register_state: Dict[int, int] = {}
        self.trace: List[CycleResult] = []
        
    def __repr__(self):
        return (f"ExecutionResult(cycles={self.cycles}, instructions={self.instructions}, "
                f"final_pc=0x{self.final_pc:08x}, halt_reason='{self.halt_reason}')")


class CPUStatistics:
    """CPU execution statistics.
    
    Tracks various metrics about CPU execution including instruction counts,
    CPI (cycles per instruction), instruction mix, branch statistics, and
    memory access patterns.
    
    Attributes:
        total_cycles: Total cycles executed
        instructions_executed: Total instructions executed
        cpi: Cycles per instruction (float)
        instruction_mix: Count of each instruction type {mnemonic: count}
        branch_taken_count: Number of branches taken
        branch_not_taken_count: Number of branches not taken
        memory_accesses: Total memory read/write operations
    """
    
    def __init__(self):
        self.total_cycles: int = 0
        self.instructions_executed: int = 0
        self.cpi: float = 0.0
        self.instruction_mix: Dict[str, int] = {}
        self.branch_taken_count: int = 0
        self.branch_not_taken_count: int = 0
        self.memory_accesses: int = 0
        
    def __repr__(self):
        return (f"CPUStatistics(cycles={self.total_cycles}, instructions={self.instructions_executed}, "
                f"cpi={self.cpi:.2f}, branches_taken={self.branch_taken_count}, "
                f"branches_not_taken={self.branch_not_taken_count})")


class CPU:
    """
    Top-level RISC-V CPU simulator.
    
    Coordinates all components and provides high-level execution interface
    for running RISC-V programs loaded from .hex files.
    
    Features:
    - Program loading from .hex files
    - Single-step execution (step method)
    - Continuous execution (run method)
    - Execution until specific PC (run_until_pc method)
    - Halt detection (infinite loops, invalid instructions)
    - Register/memory access for debugging
    - Execution statistics tracking
    - Register and memory dumps
    
    Halt Conditions:
    - Infinite loop detected: JAL x0, 0 (jump to self)
    - Max cycle limit reached
    - Invalid instruction encountered
    - Target PC reached (for run_until_pc)
    
    Convention:
    - All bit arrays use MSB-at-index-0
    - PC is 32-bit unsigned
    - Memory addresses are 32-bit unsigned
    """
    
    def __init__(self, memory_size: int = 65536, pc_start: int = 0x00000000):
        """
        Initialize CPU simulator.
        
        Args:
            memory_size: Size of memory in bytes (default 64KB)
            pc_start: Initial program counter value (default 0x00000000)
        """
        # Create components
        self.memory = Memory(size_bytes=memory_size, base_addr=0x00000000)
        self.register_file = RegisterFile()
        self.datapath = Datapath(self.memory, self.register_file)
        
        # Set initial PC
        self.pc_start = pc_start
        pc_bits = int_to_bits_unsigned(pc_start, 32)
        self.datapath.fetch_unit.set_pc(pc_bits)
        
        # Statistics tracking
        self._instruction_mix: Dict[str, int] = {}
        self._branch_taken_count: int = 0
        self._branch_not_taken_count: int = 0
        self._memory_accesses: int = 0
        
        # Execution trace
        self._execution_trace: List[CycleResult] = []
        
        # Previous PC for loop detection
        self._prev_pc: Optional[int] = None
        
    def load_program(self, hex_file_path: str) -> None:
        """
        Load program from .hex file into instruction memory.
        
        The .hex file should contain 32-bit instructions in hexadecimal format,
        one instruction per line (8 hex digits per line).
        
        Args:
            hex_file_path: Path to .hex file to load
            
        Raises:
            FileNotFoundError: If hex file does not exist
            ValueError: If hex file format is invalid
        """
        self.memory.load_program(hex_file_path)
        
    def reset(self) -> None:
        """
        Reset CPU to initial state.
        
        Resets:
        - Program counter to pc_start
        - All registers to zero
        - Datapath cycle count to zero
        - All statistics counters
        - Execution trace
        
        Does NOT clear memory (program remains loaded).
        """
        # Reset PC
        pc_bits = int_to_bits_unsigned(self.pc_start, 32)
        self.datapath.fetch_unit.set_pc(pc_bits)
        
        # Reset registers
        zero_bits = [0] * 32
        for i in range(32):
            if i != 0:  # x0 is hardwired to zero, no need to reset
                self.register_file.write_int_reg(i, zero_bits)
                self.register_file.write_fp_reg(i, zero_bits)
        
        # Reset datapath cycle count
        self.datapath.cycle_count = 0
        
        # Reset statistics
        self._instruction_mix = {}
        self._branch_taken_count = 0
        self._branch_not_taken_count = 0
        self._memory_accesses = 0
        self._execution_trace = []
        
    def step(self) -> CycleResult:
        """
        Execute one instruction (single cycle).
        
        Performs one complete cycle of the datapath:
        1. Fetch instruction from memory
        2. Decode instruction
        3. Execute operation
        4. Memory access (if needed)
        5. Writeback to register file
        
        Returns:
            CycleResult containing information about executed cycle
        """
        # Execute one cycle
        result = self.datapath.execute_cycle()
        
        # Update statistics
        if result.decoded:
            mnemonic = result.decoded.mnemonic
            self._instruction_mix[mnemonic] = self._instruction_mix.get(mnemonic, 0) + 1
            
            # Track branch statistics
            if result.decoded.instr_type == 'B':
                if result.branch_taken:
                    self._branch_taken_count += 1
                else:
                    self._branch_not_taken_count += 1
            
            # Track memory accesses
            if result.signals:
                if result.signals.mem_read or result.signals.mem_write:
                    self._memory_accesses += 1
        
        # Add to execution trace
        self._execution_trace.append(result)
        
        return result
        
    def run(self, max_cycles: int = 10000) -> ExecutionResult:
        """
        Run program until halt condition is met.
        
        Executes instructions continuously until one of the halt conditions:
        - Infinite loop detected (JAL x0, 0 - jump to self)
        - Max cycle limit reached
        - Invalid instruction encountered
        
        Args:
            max_cycles: Maximum number of cycles to execute (default 10000)
            
        Returns:
            ExecutionResult containing execution summary
        """
        result = ExecutionResult()
        result.trace = []
        
        for cycle_num in range(max_cycles):
            # Get current PC before executing
            current_pc_bits = self.datapath.fetch_unit.get_pc()
            current_pc = bits_to_int_unsigned(current_pc_bits)
            
            # Execute one cycle
            cycle_result = self.step()
            result.trace.append(cycle_result)
            result.instructions += 1
            
            # Check for invalid instruction
            if cycle_result.decoded and cycle_result.decoded.mnemonic == "UNKNOWN":
                result.cycles = cycle_num + 1
                result.final_pc = current_pc
                result.halt_reason = "invalid_instruction"
                result.register_state = self._get_register_state()
                return result
            
            # Check for infinite loop: PC didn't change after JAL/JALR with rd=x0
            next_pc_bits = self.datapath.fetch_unit.get_pc()
            next_pc = bits_to_int_unsigned(next_pc_bits)
            
            # Detect JAL x0, 0 (jump to same address, infinite loop)
            if next_pc == current_pc and cycle_result.decoded:
                if cycle_result.decoded.mnemonic in ["JAL", "JALR"]:
                    # JAL/JALR with rd=x0 (no return address) jumping to same PC = infinite loop
                    if cycle_result.decoded.rd == 0:
                        result.cycles = cycle_num + 1
                        result.final_pc = current_pc
                        result.halt_reason = "infinite_loop"
                        result.register_state = self._get_register_state()
                        return result
        
        # Max cycles reached
        final_pc_bits = self.datapath.fetch_unit.get_pc()
        result.cycles = max_cycles
        result.final_pc = bits_to_int_unsigned(final_pc_bits)
        result.halt_reason = "max_cycles"
        result.register_state = self._get_register_state()
        return result
        
    def run_until_pc(self, target_pc: int, max_cycles: int = 10000) -> ExecutionResult:
        """
        Run program until PC reaches target address.
        
        Executes instructions until the program counter reaches the specified
        target address, or a halt condition is met (infinite loop, invalid
        instruction, max cycles).
        
        Args:
            target_pc: Target program counter value (32-bit unsigned)
            max_cycles: Maximum number of cycles to execute (default 10000)
            
        Returns:
            ExecutionResult containing execution summary
        """
        result = ExecutionResult()
        result.trace = []
        
        for cycle_num in range(max_cycles):
            # Get current PC
            current_pc_bits = self.datapath.fetch_unit.get_pc()
            current_pc = bits_to_int_unsigned(current_pc_bits)
            
            # Check if we've reached target
            if current_pc == target_pc:
                result.cycles = cycle_num
                result.instructions = cycle_num
                result.final_pc = current_pc
                result.halt_reason = "target_reached"
                result.register_state = self._get_register_state()
                return result
            
            # Execute one cycle
            cycle_result = self.step()
            result.trace.append(cycle_result)
            result.instructions += 1
            
            # Check for invalid instruction
            if cycle_result.decoded and cycle_result.decoded.mnemonic == "UNKNOWN":
                next_pc_bits = self.datapath.fetch_unit.get_pc()
                result.cycles = cycle_num + 1
                result.final_pc = bits_to_int_unsigned(next_pc_bits)
                result.halt_reason = "invalid_instruction"
                result.register_state = self._get_register_state()
                return result
            
            # Check for infinite loop
            next_pc_bits = self.datapath.fetch_unit.get_pc()
            next_pc = bits_to_int_unsigned(next_pc_bits)
            
            if next_pc == current_pc:
                if cycle_result.decoded and cycle_result.decoded.mnemonic == "JAL":
                    if cycle_result.decoded.rd == 0:
                        result.cycles = cycle_num + 1
                        result.final_pc = current_pc
                        result.halt_reason = "infinite_loop"
                        result.register_state = self._get_register_state()
                        return result
        
        # Max cycles reached without hitting target
        final_pc_bits = self.datapath.fetch_unit.get_pc()
        result.cycles = max_cycles
        result.final_pc = bits_to_int_unsigned(final_pc_bits)
        result.halt_reason = "max_cycles"
        result.register_state = self._get_register_state()
        return result
        
    def get_register(self, reg_num: int) -> int:
        """
        Get value of integer register.
        
        Args:
            reg_num: Register number (0-31)
            
        Returns:
            Register value as unsigned 32-bit integer
            
        Raises:
            ValueError: If register number is out of range
        """
        if not (0 <= reg_num < 32):
            raise ValueError(f"Register number must be 0-31, got {reg_num}")
        
        reg_bits = self.register_file.read_int_reg(reg_num)
        return bits_to_int_unsigned(reg_bits)
        
    def set_register(self, reg_num: int, value: int) -> None:
        """
        Set value of integer register.
        
        Note: Writing to x0 has no effect (x0 is hardwired to zero).
        
        Args:
            reg_num: Register number (0-31)
            value: 32-bit unsigned value to write
            
        Raises:
            ValueError: If register number is out of range
        """
        if not (0 <= reg_num < 32):
            raise ValueError(f"Register number must be 0-31, got {reg_num}")
        
        value_bits = int_to_bits_unsigned(value, 32)
        self.register_file.write_int_reg(reg_num, value_bits)
        
    def get_memory_word(self, addr: int) -> int:
        """
        Read 32-bit word from memory.
        
        Args:
            addr: Memory address (must be word-aligned)
            
        Returns:
            32-bit word value as unsigned integer
            
        Raises:
            ValueError: If address is not word-aligned or out of range
        """
        addr_bits = int_to_bits_unsigned(addr, 32)
        word_bits = self.memory.read_word(addr_bits)
        return bits_to_int_unsigned(word_bits)
        
    def set_memory_word(self, addr: int, value: int) -> None:
        """
        Write 32-bit word to memory.
        
        Args:
            addr: Memory address (must be word-aligned)
            value: 32-bit unsigned value to write
            
        Raises:
            ValueError: If address is not word-aligned or out of range
        """
        addr_bits = int_to_bits_unsigned(addr, 32)
        value_bits = int_to_bits_unsigned(value, 32)
        self.memory.write_word(addr_bits, value_bits)
        
    def dump_registers(self) -> str:
        """
        Generate formatted dump of all integer registers.
        
        Returns:
            String containing formatted register dump with hex and decimal values
        """
        lines = []
        lines.append("=" * 60)
        lines.append("Integer Registers:")
        lines.append("=" * 60)
        
        for i in range(32):
            reg_bits = self.register_file.read_int_reg(i)
            unsigned_val = bits_to_int_unsigned(reg_bits)
            signed_val = decode_twos_complement(reg_bits)['value']
            
            # Format register name
            reg_name = f"x{i}"
            if i == 0:
                reg_name = "x0 (zero)"
            elif i == 1:
                reg_name = "x1 (ra)  "
            elif i == 2:
                reg_name = "x2 (sp)  "
            else:
                reg_name = f"x{i:2d}      "
            
            lines.append(f"{reg_name}: 0x{unsigned_val:08x} ({signed_val:11d})")
        
        lines.append("=" * 60)
        return "\n".join(lines)
        
    def dump_memory(self, start: int, end: int) -> str:
        """
        Generate formatted dump of memory region.
        
        Args:
            start: Start address (must be word-aligned)
            end: End address (exclusive, must be word-aligned)
            
        Returns:
            String containing formatted memory dump
            
        Raises:
            ValueError: If addresses are not word-aligned
        """
        if start % 4 != 0 or end % 4 != 0:
            raise ValueError("Start and end addresses must be word-aligned")
        
        lines = []
        lines.append("=" * 60)
        lines.append(f"Memory Dump: 0x{start:08x} to 0x{end:08x}")
        lines.append("=" * 60)
        lines.append("Address     | Value      | Decimal")
        lines.append("-" * 60)
        
        addr = start
        while addr < end:
            try:
                addr_bits = int_to_bits_unsigned(addr, 32)
                word_bits = self.memory.read_word(addr_bits)
                unsigned_val = bits_to_int_unsigned(word_bits)
                signed_val = decode_twos_complement(word_bits)['value']
                lines.append(f"0x{addr:08x} | 0x{unsigned_val:08x} | {signed_val:11d}")
            except ValueError:
                lines.append(f"0x{addr:08x} | <invalid>  |")
            addr += 4
        
        lines.append("=" * 60)
        return "\n".join(lines)
        
    def get_statistics(self) -> CPUStatistics:
        """
        Get current CPU execution statistics.
        
        Returns:
            CPUStatistics object containing execution metrics
        """
        stats = CPUStatistics()
        stats.total_cycles = self.datapath.cycle_count
        stats.instructions_executed = len(self._execution_trace)
        
        # Calculate CPI (cycles per instruction)
        if stats.instructions_executed > 0:
            stats.cpi = stats.total_cycles / stats.instructions_executed
        else:
            stats.cpi = 0.0
        
        # Copy instruction mix
        stats.instruction_mix = self._instruction_mix.copy()
        
        # Copy branch statistics
        stats.branch_taken_count = self._branch_taken_count
        stats.branch_not_taken_count = self._branch_not_taken_count
        
        # Copy memory accesses
        stats.memory_accesses = self._memory_accesses
        
        return stats
        
    def _get_register_state(self) -> Dict[int, int]:
        """
        Get current state of all integer registers.
        
        Returns:
            Dictionary mapping register number to unsigned value
        """
        state = {}
        for i in range(32):
            reg_bits = self.register_file.read_int_reg(i)
            state[i] = bits_to_int_unsigned(reg_bits)
        return state
        
    def get_pc(self) -> int:
        """
        Get current program counter value.
        
        Returns:
            PC value as unsigned 32-bit integer
        """
        pc_bits = self.datapath.fetch_unit.get_pc()
        return bits_to_int_unsigned(pc_bits)
        
    def set_pc(self, pc: int) -> None:
        """
        Set program counter value.
        
        Args:
            pc: New PC value as unsigned 32-bit integer
        """
        pc_bits = int_to_bits_unsigned(pc, 32)
        self.datapath.fetch_unit.set_pc(pc_bits)


# AI-END: Claude Code (Anthropic) - November 14, 2025
