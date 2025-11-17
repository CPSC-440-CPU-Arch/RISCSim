# RISCSim Usage Guide

**Authors:** Joshua Castaneda and Ivan Flores

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Running Test Programs](#running-test-programs)
4. [Creating Custom Programs](#creating-custom-programs)
5. [Debugging Features](#debugging-features)
6. [Performance Analysis](#performance-analysis)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- **Python 3.8+** required
- **pip** package manager
- **Git** for cloning repository

### Development Installation (Recommended)

For development work where you want changes to reflect immediately:

```bash
# Clone the repository
git clone https://github.com/CPSC-440-CPU-Arch/RISCSim.git
cd RISCSim

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

### User Installation

For users who just want to use the simulator:

```bash
# Install directly from GitHub
pip install git+https://github.com/CPSC-440-CPU-Arch/RISCSim.git

# Or after cloning
cd RISCSim
pip install .
```

### Verify Installation

```bash
# Run test suite to verify installation
pytest

# Or run specific tests
pytest tests/test_cpu.py -v
```

Expected output: All tests should pass (586 tests as of Phase 5).

---

## Quick Start

### Example 1: Simple Program Execution

```python
from riscsim.cpu.cpu import CPU

# Create CPU instance
cpu = CPU()

# Load a program from hex file
cpu.load_program('tests/programs/test_base.hex')

# Run the program (executes until halt)
result = cpu.run(max_cycles=1000)

# Print results
print(f"Executed {result.instruction_count} instructions in {result.cycle_count} cycles")
print(f"Halt reason: {result.halt_reason}")
print(f"Final register state:")
print(cpu.dump_registers())
```

### Example 2: Step-by-Step Execution

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_arithmetic.hex')

# Execute one instruction at a time
for i in range(10):
    cycle_result = cpu.step()
    print(f"Cycle {i+1}:")
    print(f"  PC: 0x{cycle_result.pc_int:08X}")
    print(f"  Instruction: 0x{cycle_result.instruction_int:08X}")
    print(f"  Mnemonic: {cycle_result.decoded.mnemonic}")
    print(f"  ALU Result: 0x{cycle_result.alu_result_int:08X}")
```

### Example 3: Inspect Registers and Memory

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_memory.hex')
cpu.run()

# Read individual registers
x1_value = cpu.get_register(1)
x2_value = cpu.get_register(2)
print(f"x1 = {x1_value}, x2 = {x2_value}")

# Read memory
mem_value = cpu.get_memory_word(0x00010000)
print(f"Memory at 0x00010000: {mem_value}")

# Dump registers
print(cpu.dump_registers())

# Dump memory region
print(cpu.dump_memory(0x00010000, 8))  # 8 words starting at 0x00010000
```

---

## Running Test Programs

RISCSim includes 6 comprehensive test programs that demonstrate all supported instructions.

### Available Test Programs

| Program | File | Description | Instructions |
|---------|------|-------------|--------------|
| **Base** | `test_base.hex` | Provided test program | 11 |
| **Arithmetic** | `test_arithmetic.hex` | ADD, SUB, ADDI, overflow | 19 |
| **Logical** | `test_logical.hex` | AND, OR, XOR variants | 25 |
| **Shifts** | `test_shifts.hex` | SLL, SRL, SRA variants | 30 |
| **Memory** | `test_memory.hex` | LW, SW with offsets | 39 |
| **Branches** | `test_branches.hex` | BEQ, BNE, loops | 41 |
| **Jumps** | `test_jumps.hex` | JAL, JALR, returns | 33 |

### Running Test Programs

#### Using Python API

```python
from riscsim.cpu.cpu import CPU

# Run test_base.hex
cpu = CPU()
cpu.load_program('tests/programs/test_base.hex')
result = cpu.run(max_cycles=1000)

print(f"Program completed:")
print(f"  Instructions: {result.instruction_count}")
print(f"  Cycles: {result.cycle_count}")
print(f"  CPI: {result.cycle_count / result.instruction_count:.2f}")
print(f"  Halt reason: {result.halt_reason}")

# Check final state
print(f"\nFinal registers:")
for i in range(1, 8):
    print(f"  x{i} = {cpu.get_register(i)}")
```

#### Using Test Suite

```bash
# Run all test programs
pytest tests/test_programs.py -v

# Run specific test program
pytest tests/test_programs.py::TestArithmeticProgram -v

# Run with output
pytest tests/test_programs.py::TestBaseProgram -v -s
```

### Expected Results: test_base.hex

```
Program: tests/programs/test_base.hex
Expected final state:
  x1 = 5
  x2 = 10
  x3 = 15
  x4 = 15 (loaded from memory)
  x5 = 0x00010000
  x6 = 2
  mem[0x00010000] = 15
  PC = 0x00000028 (infinite loop)
  Halt reason: Infinite loop detected
```

---

## Creating Custom Programs

### Method 1: Write Assembly and Encode to Hex

Use the provided `encode_riscv.py` utility to create hex files.

#### Step 1: Write Assembly Code

Create a file `my_program.asm`:

```assembly
# my_program.asm - Calculate factorial of 5

# x1 = n (input, n=5)
# x2 = result (output)
# x3 = counter

addi x1, x0, 5      # n = 5
addi x2, x0, 1      # result = 1
addi x3, x0, 1      # counter = 1

loop:
    beq x3, x1, done    # if counter == n, done
    addi x3, x3, 1      # counter++
    mul x2, x2, x3      # result *= counter (using shifts/adds)
    jal x0, loop        # repeat

done:
    jal x0, 0           # infinite loop (halt)
```

#### Step 2: Encode to Hex

```python
from encode_riscv import *

instructions = [
    addi(1, 0, 5),          # x1 = 5
    addi(2, 0, 1),          # x2 = 1
    addi(3, 0, 1),          # x3 = 1
    # loop:
    beq(3, 1, 16),          # if x3 == x1, skip to done (4 instructions * 4 = 16 bytes)
    addi(3, 3, 1),          # x3++
    # Multiply x2 by x3 (simplified: assume multiply instruction)
    # For actual implementation, use shift-add algorithm
    add(2, 2, 3),           # Simplified: result += counter
    jal(0, -12),            # jump back to loop (-3 instructions * 4 = -12 bytes)
    # done:
    jal(0, 0),              # infinite loop
]

write_hex_file('my_program.hex', instructions)
print("Created my_program.hex")
```

#### Step 3: Run Your Program

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('my_program.hex')
result = cpu.run(max_cycles=1000)

print(f"Result in x2: {cpu.get_register(2)}")
print(f"Instructions executed: {result.instruction_count}")
```

### Method 2: Direct Encoding

For simple programs, directly create hex file:

```python
from encode_riscv import *

# Calculate: x3 = (x1 + x2) * 2
program = [
    addi(1, 0, 10),         # x1 = 10
    addi(2, 0, 20),         # x2 = 20
    add(3, 1, 2),           # x3 = x1 + x2 = 30
    slli(3, 3, 1),          # x3 = x3 << 1 = 60 (multiply by 2)
    jal(0, 0),              # halt
]

write_hex_file('simple.hex', program)
```

### Method 3: Load Data into Memory

```python
from riscsim.cpu.cpu import CPU
from encode_riscv import *

cpu = CPU()

# Create program that accesses data
program = [
    lui(5, 0x10),           # x5 = 0x00010000 (data region)
    lw(1, 5, 0),            # x1 = mem[0x00010000]
    lw(2, 5, 4),            # x2 = mem[0x00010004]
    add(3, 1, 2),           # x3 = x1 + x2
    sw(3, 5, 8),            # mem[0x00010008] = x3
    jal(0, 0),              # halt
]

write_hex_file('data_program.hex', program)

# Load program
cpu.load_program('data_program.hex')

# Pre-load data into memory
cpu.set_memory_word(0x00010000, 100)
cpu.set_memory_word(0x00010004, 200)

# Run
cpu.run()

# Check result
result = cpu.get_memory_word(0x00010008)
print(f"Result: {result}")  # Should be 300
```

---

## Debugging Features

### Single-Step Execution

Execute one instruction at a time and inspect state:

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_branches.hex')

while True:
    # Execute one instruction
    cycle = cpu.step()
    
    # Print detailed info
    print(f"\n{'='*60}")
    print(f"Cycle {cycle.cycle_num}:")
    print(f"  PC: 0x{cycle.pc_int:08X}")
    print(f"  Instruction: 0x{cycle.instruction_int:08X}")
    print(f"  Mnemonic: {cycle.decoded.mnemonic}")
    print(f"  Type: {cycle.decoded.instr_type}")
    print(f"  rd={cycle.decoded.rd_int}, rs1={cycle.decoded.rs1_int}, rs2={cycle.decoded.rs2_int}")
    print(f"  ALU Result: 0x{cycle.alu_result_int:08X}")
    
    if cycle.decoded.mnemonic in ['LW', 'SW'] and cycle.mem_data is not None:
        print(f"  Memory Data: 0x{cycle.mem_data_int:08X}")
    
    if cycle.branch_taken:
        print(f"  Branch TAKEN")
    
    # Check for halt (infinite loop)
    if cycle.decoded.mnemonic == 'JAL' and cycle.decoded.rd_int == 0:
        if cycle.decoded.immediate_int == 0:
            print(f"\nInfinite loop detected - halting")
            break
    
    # Manual break after N instructions
    if cycle.cycle_num >= 50:
        print(f"\nMax cycles reached")
        break
```

### Breakpoints (Run Until PC)

Run until a specific PC address is reached:

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_branches.hex')

# Run until PC reaches 0x00000020
result = cpu.run_until_pc(0x00000020, max_cycles=1000)

print(f"Stopped at PC: 0x{result.final_pc:08X}")
print(f"Instructions executed: {result.instruction_count}")
print(cpu.dump_registers())
```

### Trace Execution

Enable detailed trace for debugging:

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_arithmetic.hex')

print("Execution Trace:")
print("="*80)
print(f"{'Cycle':<6} {'PC':<10} {'Instruction':<12} {'Mnemonic':<8} {'Result':<10}")
print("="*80)

for i in range(20):
    cycle = cpu.step()
    print(f"{cycle.cycle_num:<6} "
          f"0x{cycle.pc_int:08X}  "
          f"0x{cycle.instruction_int:08X}  "
          f"{cycle.decoded.mnemonic:<8} "
          f"0x{cycle.alu_result_int:08X}")
```

### Register Watch

Monitor specific registers during execution:

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_arithmetic.hex')

watch_regs = [1, 2, 3, 4]  # Watch x1, x2, x3, x4

print(f"{'Cycle':<6} " + " ".join([f"x{r}:<10" for r in watch_regs]))

for i in range(20):
    cpu.step()
    values = [cpu.get_register(r) for r in watch_regs]
    print(f"{i+1:<6} " + " ".join([f"{v:<10}" for v in values]))
```

### Memory Dump

Inspect memory contents:

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_memory.hex')
cpu.run()

# Dump instruction memory (first 16 words)
print("Instruction Memory:")
print(cpu.dump_memory(0x00000000, 16))

# Dump data memory (first 16 words)
print("\nData Memory:")
print(cpu.dump_memory(0x00010000, 16))
```

Output format:
```
Address      Hex          Decimal      
0x00000000   0x00500093   5243027      
0x00000004   0x00A00113   10485011     
...
```

### Register Dump

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_base.hex')
cpu.run()

# Dump all registers
print(cpu.dump_registers())
```

Output format:
```
Register File:
x0  (zero) = 0x00000000 (0)
x1  (ra)   = 0x00000005 (5)
x2  (sp)   = 0x0000000A (10)
x3  (gp)   = 0x0000000F (15)
...
```

---

## Performance Analysis

### CPU Statistics

Get detailed performance statistics:

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_branches.hex')
result = cpu.run()

# Get statistics
stats = cpu.get_statistics()

print(f"Performance Statistics:")
print(f"  Total Instructions: {stats.instruction_count}")
print(f"  Total Cycles: {stats.cycle_count}")
print(f"  CPI: {stats.cpi:.2f}")
print(f"\nInstruction Mix:")
for instr, count in sorted(stats.instruction_mix.items()):
    percentage = (count / stats.instruction_count) * 100
    print(f"  {instr:<8}: {count:>4} ({percentage:>5.1f}%)")

print(f"\nBranch Statistics:")
print(f"  Total Branches: {stats.branch_count}")
print(f"  Branches Taken: {stats.branches_taken}")
print(f"  Branch Taken Rate: {stats.branch_taken_rate:.2%}")

print(f"\nMemory Statistics:")
print(f"  Memory Reads: {stats.memory_reads}")
print(f"  Memory Writes: {stats.memory_writes}")
```

### Execution Time Estimation

Estimate execution time for different clock frequencies:

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_arithmetic.hex')
result = cpu.run()

cycles = result.cycle_count

# Estimate time for different frequencies
frequencies = [1e6, 10e6, 100e6, 1e9]  # 1 MHz, 10 MHz, 100 MHz, 1 GHz

print(f"Execution time estimates ({cycles} cycles):")
for freq in frequencies:
    time_seconds = cycles / freq
    if time_seconds < 1e-6:
        print(f"  {freq/1e6:>6.0f} MHz: {time_seconds*1e9:>8.2f} ns")
    elif time_seconds < 1e-3:
        print(f"  {freq/1e6:>6.0f} MHz: {time_seconds*1e6:>8.2f} µs")
    elif time_seconds < 1:
        print(f"  {freq/1e6:>6.0f} MHz: {time_seconds*1e3:>8.2f} ms")
    else:
        print(f"  {freq/1e6:>6.0f} MHz: {time_seconds:>8.2f} s")
```

### Profiling Instruction Types

Analyze which instruction types dominate:

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_branches.hex')
result = cpu.run()

stats = cpu.get_statistics()

# Categorize instructions
categories = {
    'Arithmetic': ['ADD', 'SUB', 'ADDI'],
    'Logical': ['AND', 'OR', 'XOR', 'ANDI', 'ORI', 'XORI'],
    'Shift': ['SLL', 'SRL', 'SRA', 'SLLI', 'SRLI', 'SRAI'],
    'Memory': ['LW', 'SW'],
    'Branch': ['BEQ', 'BNE'],
    'Jump': ['JAL', 'JALR'],
    'Upper': ['LUI', 'AUIPC'],
}

category_counts = {cat: 0 for cat in categories}

for instr, count in stats.instruction_mix.items():
    for cat, instrs in categories.items():
        if instr in instrs:
            category_counts[cat] += count
            break

print("Instruction Categories:")
for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
    if count > 0:
        percentage = (count / stats.instruction_count) * 100
        print(f"  {cat:<12}: {count:>4} ({percentage:>5.1f}%)")
```

---

## Advanced Features

### Custom Memory Configuration

Create CPU with custom memory size:

```python
from riscsim.cpu.cpu import CPU

# Create CPU with 256KB memory (default is 128KB)
cpu = CPU(memory_size=256*1024)

cpu.load_program('my_program.hex')
cpu.run()
```

### Reset CPU State

Reset CPU without reloading program:

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_arithmetic.hex')

# Run first time
result1 = cpu.run()
print(f"Run 1: {cpu.get_register(3)}")

# Reset and run again
cpu.reset()
result2 = cpu.run()
print(f"Run 2: {cpu.get_register(3)}")  # Should be same
```

### Modify State During Execution

Inject values during execution:

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_arithmetic.hex')

# Execute first 5 instructions
for i in range(5):
    cpu.step()

# Modify register
cpu.set_register(1, 999)

# Continue execution
for i in range(10):
    cpu.step()

print(f"Modified result: {cpu.get_register(3)}")
```

### Compare Execution Results

Run multiple programs and compare:

```python
from riscsim.cpu.cpu import CPU

programs = [
    'tests/programs/test_arithmetic.hex',
    'tests/programs/test_logical.hex',
    'tests/programs/test_shifts.hex',
]

results = []

for prog in programs:
    cpu = CPU()
    cpu.load_program(prog)
    result = cpu.run()
    stats = cpu.get_statistics()
    
    results.append({
        'program': prog.split('/')[-1],
        'instructions': result.instruction_count,
        'cycles': result.cycle_count,
        'cpi': stats.cpi,
    })

# Print comparison
print(f"{'Program':<30} {'Instructions':<12} {'Cycles':<8} {'CPI':<6}")
print("="*60)
for r in results:
    print(f"{r['program']:<30} {r['instructions']:<12} {r['cycles']:<8} {r['cpi']:<6.2f}")
```

---

## Troubleshooting

### Common Issues

#### Issue 1: "Address not aligned" Error

**Problem**: Trying to access memory at non-aligned address.

```python
cpu.set_memory_word(0x00010001, 100)  # ERROR: address not aligned
```

**Solution**: Ensure addresses are 4-byte aligned (multiples of 4).

```python
cpu.set_memory_word(0x00010000, 100)  # OK
cpu.set_memory_word(0x00010004, 100)  # OK
```

---

#### Issue 2: "Address out of range" Error

**Problem**: Accessing memory outside valid range.

```python
cpu.set_memory_word(0x00100000, 100)  # ERROR: out of range
```

**Solution**: Use valid memory ranges:
- Instruction memory: 0x00000000 - 0x0000FFFF
- Data memory: 0x00010000 - 0x0001FFFF

---

#### Issue 3: Program Doesn't Halt

**Problem**: Program runs forever (no infinite loop detection).

```python
result = cpu.run(max_cycles=10000)  # Times out
```

**Solution 1**: Add proper halt instruction (infinite loop):
```assembly
jal x0, 0  # Jump to self - detected as halt
```

**Solution 2**: Use `max_cycles` parameter:
```python
result = cpu.run(max_cycles=1000)  # Limit execution
```

**Solution 3**: Use `run_until_pc()` with target:
```python
result = cpu.run_until_pc(target_pc, max_cycles=1000)
```

---

#### Issue 4: Invalid Instruction

**Problem**: Program contains invalid opcode.

```python
# Invalid instruction in hex file
cpu.load_program('bad_program.hex')
result = cpu.run()  # Halts with "Invalid instruction"
```

**Solution**: Verify hex file encoding using decoder:

```python
from riscsim.cpu.decoder import InstructionDecoder
from riscsim.utils.bit_utils import int_to_bits

decoder = InstructionDecoder()
instruction_int = 0xFFFFFFFF  # Suspicious instruction
instruction_bits = int_to_bits(instruction_int, 32)
decoded = decoder.decode(instruction_bits)

print(f"Mnemonic: {decoded.mnemonic}")  # Will show "UNKNOWN" if invalid
```

---

#### Issue 5: Incorrect Results

**Problem**: Program produces wrong output.

**Debug Steps**:

1. **Single-step through program**:
```python
cpu = CPU()
cpu.load_program('my_program.hex')

for i in range(20):
    cycle = cpu.step()
    print(f"Cycle {i+1}: PC=0x{cycle.pc_int:08X}, "
          f"Instr={cycle.decoded.mnemonic}, "
          f"ALU={cycle.alu_result_int}")
```

2. **Check instruction encoding**:
```python
# Verify your encoding matches expected
from encode_riscv import addi, add
print(f"ADDI x1, x0, 5: 0x{addi(1, 0, 5):08X}")
print(f"Expected:       0x00500093")
```

3. **Verify memory layout**:
```python
# Check if data is at expected addresses
print(cpu.dump_memory(0x00010000, 8))
```

4. **Check register values**:
```python
# Verify intermediate values
print(cpu.dump_registers())
```

---

### Getting Help

If you encounter issues not covered here:

1. **Check documentation**:
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [INSTRUCTION_SET.md](INSTRUCTION_SET.md) - Instruction details
   - [README.md](../README.md) - Project overview

2. **Run test suite**:
```bash
pytest tests/ -v  # Should all pass
```

3. **Check examples**:
```python
# Look at working examples
import tests.test_programs as examples
# Read source code for test programs
```

4. **Enable verbose output**:
```python
cpu = CPU()
cpu.load_program('my_program.hex')

# Step through with full details
for i in range(100):
    cycle = cpu.step()
    print(f"\nCycle {i+1}:")
    print(f"  PC: 0x{cycle.pc_int:08X}")
    print(f"  Instruction: 0x{cycle.instruction_int:08X}")
    print(f"  {cycle.decoded}")
    print(f"  Signals: {cycle.signals}")
    print(f"  Registers: {[cpu.get_register(j) for j in range(8)]}")
```

---

## Summary

This usage guide covers:

✅ **Installation** - Development and user installation  
✅ **Quick Start** - Basic usage examples  
✅ **Test Programs** - Running provided test programs  
✅ **Custom Programs** - Creating your own programs  
✅ **Debugging** - Single-step, breakpoints, traces  
✅ **Performance** - Statistics and profiling  
✅ **Advanced** - Custom configurations  
✅ **Troubleshooting** - Common issues and solutions  

For more details:
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Instructions: [INSTRUCTION_SET.md](INSTRUCTION_SET.md)
- Project Info: [README.md](../README.md)

---

## Examples Directory

Check the `examples/` directory for additional usage examples:

```bash
examples/
├── control_unit_demo.py           # Control unit demonstration
├── control_unit_programs.py       # Example programs
├── alu_control_integration.py     # ALU integration
├── register_control_integration.py # Register integration
└── ... (other component demos)
```

Run examples:
```bash
cd examples
python control_unit_demo.py
```
