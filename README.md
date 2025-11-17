# RISCSim - RISC-V CPU Simulator

A complete, hardware-accurate **single-cycle RISC-V CPU simulator** implementing the RV32I base instruction set with extensions for multiply/divide (M) and floating-point (F) operations.

## Overview

RISCSim is a **fully functional RISC-V CPU simulator** that executes real RISC-V machine code loaded from `.hex` files. It implements a single-cycle datapath with all five pipeline stages (fetch, decode, execute, memory, writeback) executing in one cycle. The simulator is built entirely from bit-level primitives without using host arithmetic operators, making it a true hardware simulation.

## Features

### Complete CPU Implementation ✅
- ✅ **Single-Cycle Datapath**: Five-stage execution in one cycle
- ✅ **Instruction Memory**: 64KB program storage, loads from .hex files
- ✅ **Data Memory**: 64KB data storage with word/byte access
- ✅ **Register File**: 32 integer registers (x0 hardwired to zero)
- ✅ **Program Counter**: PC management with branch/jump support
- ✅ **Control Unit**: FSM-based control signal generation

### Instruction Set Support (23 Instructions) ✅
- ✅ **Arithmetic**: ADD, SUB, ADDI
- ✅ **Logical**: AND, OR, XOR, ANDI, ORI, XORI
- ✅ **Shifts**: SLL, SRL, SRA, SLLI, SRLI, SRAI
- ✅ **Memory**: LW, SW (word-aligned access)
- ✅ **Branches**: BEQ, BNE (conditional branches)
- ✅ **Jumps**: JAL, JALR (with return address)
- ✅ **Upper Immediate**: LUI, AUIPC

### Hardware Components ✅
- ✅ **ALU**: 32-bit operations using 1-bit full adders (ADD, SUB, AND, OR, XOR)
- ✅ **Barrel Shifter**: 5-stage shifter (SLL, SRL, SRA)
- ✅ **MDU**: Multiply/Divide Unit with shift-add/restoring division algorithms
- ✅ **FPU**: IEEE-754 Float32 operations (FADD, FSUB, FMUL)
- ✅ **Instruction Decoder**: All 6 RISC-V formats (R, I, S, B, U, J)
- ✅ **Memory Unit**: Harvard architecture with separate I/D memory
- ✅ **Fetch Unit**: PC management with branch/jump handling

### Test Programs Included ✅
- ✅ `test_base.hex`: Provided reference program (11 instructions)
- ✅ `test_arithmetic.hex`: Arithmetic operations with overflow (19 instructions)
- ✅ `test_logical.hex`: Logical operations and bit patterns (25 instructions)
- ✅ `test_shifts.hex`: All shift variants (30 instructions)
- ✅ `test_memory.hex`: Memory operations with offsets (39 instructions)
- ✅ `test_branches.hex`: Branches, loops, control flow (41 instructions)
- ✅ `test_jumps.hex`: Jumps and returns (33 instructions)

## Quick Start

```python
from riscsim.cpu.cpu import CPU

# Create CPU and load program
cpu = CPU()
cpu.load_program('tests/programs/test_base.hex')

# Run program
result = cpu.run(max_cycles=1000)

# Check results
print(f"Executed {result.instructions} instructions")
print(f"Final state: x1={cpu.get_register(1)}, x3={cpu.get_register(3)}")
print(cpu.dump_registers())
```

## Project Structure

```
RISCSim/
├── riscsim/                   # Main package
│   ├── __init__.py
│   ├── cpu/                   # CPU components
│   │   ├── __init__.py
│   │   ├── alu.py             # Arithmetic Logic Unit (32-bit, bit-level)
│   │   ├── shifter.py         # Barrel shifter (SLL, SRL, SRA)
│   │   ├── mdu.py             # Multiply/Divide Unit (M extension)
│   │   ├── fpu.py             # Floating-Point Unit (F extension)
│   │   ├── registers.py       # Register file (32 int + 32 FP registers)
│   │   ├── control_signals.py # Control signal management
│   │   ├── control_unit.py    # Control FSM
│   │   ├── memory.py          # Instruction/Data memory (128KB)
│   │   ├── fetch.py           # Fetch unit with PC management
│   │   ├── decoder.py         # Instruction decoder (6 RISC-V formats)
│   │   ├── datapath.py        # Single-cycle datapath
│   │   └── cpu.py             # CPU top-level (main interface)
│   └── utils/                 # Utility modules
│       ├── __init__.py
│       ├── bit_utils.py       # Bit manipulation utilities
│       ├── components.py      # Hardware components (mux, demux)
│       ├── twos_complement.py # Two's complement operations
│       └── hex_loader.py      # .hex file loader
├── tests/                     # Comprehensive test suite (601 tests)
│   ├── test_*.py              # Component tests
│   ├── test_integration_comprehensive.py  # Phase 7 integration tests
│   └── programs/              # Test programs (.hex and .s files)
│       ├── test_base.s        # Assembly source file
│       ├── test_base.hex      # Provided reference program
│       ├── test_arithmetic.hex
│       ├── test_logical.hex
│       ├── test_shifts.hex
│       ├── test_memory.hex
│       ├── test_branches.hex
│       └── test_jumps.hex
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md        # System architecture details
│   ├── INSTRUCTION_SET.md     # Instruction reference
│   ├── USAGE.md               # Usage guide
│   └── diagrams/              # Architecture diagrams
├── examples/                  # Usage examples
│   ├── control_unit_demo.py
│   └── ... (component demos)
├── run_test_base.py           # Demo script to run test_base.hex
├── verify_hex.py              # Script to verify .hex matches .s source
├── encode_riscv.py            # Helper to create .hex files
├── pyproject.toml             # Modern Python packaging config
├── requirements.txt           # Dependencies
├── README.md                  # This file
├── RISCV_CPU_IMPLEMENTATION_PLAN.md  # Development roadmap
├── PROJECT_ARCHITECTURE.md    # Architecture compliance
└── AI_USAGE.md                # AI assistance disclosure
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (for cloning)

### For Development (Recommended)

```bash
# Clone the repository
git clone https://github.com/CPSC-440-CPU-Arch/RISCSim.git
cd RISCSim

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

### For Users

```bash
# Install directly from GitHub
pip install git+https://github.com/CPSC-440-CPU-Arch/RISCSim.git

# Or after cloning
cd RISCSim
pip install .
```

### Verify Installation

```bash
# Run full test suite (601 tests)
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_cpu.py -v

# Run Phase 7 integration tests
pytest tests/test_integration_comprehensive.py -v
```

## Usage Examples

### Basic Program Execution

```python
from riscsim.cpu.cpu import CPU

# Create CPU instance
cpu = CPU()

# Load a program from hex file
cpu.load_program('tests/programs/test_base.hex')

# Execute program (runs until halt)
result = cpu.run(max_cycles=1000)

# Print results
print(f"Executed {result.instructions} instructions in {result.cycles} cycles")
print(f"Halt reason: {result.halt_reason}")

# Inspect final register state
print("Final registers:")
for i in range(1, 8):
    print(f"  x{i} = {cpu.get_register(i)}")
```

### Single-Step Debugging

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_arithmetic.hex')

# Execute one instruction at a time
for i in range(10):
    cycle = cpu.step()
    print(f"Cycle {i+1}: PC=0x{cycle.pc_int:08X}, "
          f"Instr={cycle.decoded.mnemonic}, "
          f"Result=0x{cycle.alu_result_int:08X}")

# Dump registers
print(cpu.dump_registers())
```

### Creating Custom Programs

```python
from encode_riscv import *

# Create a simple program: x3 = (x1 + x2) * 2
program = [
    addi(1, 0, 10),         # x1 = 10
    addi(2, 0, 20),         # x2 = 20
    add(3, 1, 2),           # x3 = x1 + x2 = 30
    slli(3, 3, 1),          # x3 = x3 << 1 = 60
    jal(0, 0),              # halt (infinite loop)
]

write_hex_file('my_program.hex', program)

# Run the program
cpu = CPU()
cpu.load_program('my_program.hex')
cpu.run()
print(f"Result: x3 = {cpu.get_register(3)}")  # Should be 60
```

### Running Demonstration Scripts

The project includes ready-to-use demonstration scripts:

```bash
# Run the test_base.hex program with detailed output
python3 run_test_base.py

# Verify that test_base.hex matches test_base.s assembly source
python3 verify_hex.py
```

### Performance Analysis

```python
from riscsim.cpu.cpu import CPU

cpu = CPU()
cpu.load_program('tests/programs/test_branches.hex')
result = cpu.run()

# Get detailed statistics
stats = cpu.get_statistics()

print(f"Performance Statistics:")
print(f"  Instructions: {stats.instruction_count}")
print(f"  Cycles: {stats.cycle_count}")
print(f"  CPI: {stats.cpi:.2f}")
print(f"\nInstruction Mix:")
for instr, count in sorted(stats.instruction_mix.items()):
    percentage = (count / stats.instruction_count) * 100
    print(f"  {instr:<8}: {count:>4} ({percentage:>5.1f}%)")
```

## Testing

RISCSim includes a comprehensive test suite with **601 tests** covering all components:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=riscsim --cov-report=term-missing

# Run specific component tests
pytest tests/test_cpu.py -v                        # CPU tests (20 tests)
pytest tests/test_datapath.py -v                   # Datapath tests (28 tests)
pytest tests/test_decoder.py -v                    # Decoder tests (36 tests)
pytest tests/test_memory.py -v                     # Memory tests (26 tests)
pytest tests/test_fetch.py -v                      # Fetch tests (25 tests)

# Run test programs
pytest tests/test_programs.py -v                   # Program execution tests (10 tests)
pytest tests/test_integration_comprehensive.py -v  # Integration tests (15 tests)

# Run with output
pytest -v -s

# Run Test on test_base.hex in RISCIM/tests/programs/test_base.hex

python3 run_test_base.py # python file in RISCIM/run_test_base.py

```
### Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| **Phase 1: Memory & Fetch** | 81 | ✅ 100% |
| **Phase 2: Decoder** | 36 | ✅ 100% |
| **Phase 3: Datapath** | 28 | ✅ 100% |
| **Phase 4: CPU Top-Level** | 20 | ✅ 100% |
| **Phase 5: Test Programs** | 10 | ✅ 100% |
| **Existing Components** | 411 | ✅ 100% |
| **Total** | **586** | **✅ 100%** |

## Design Constraints

RISCSim follows strict **hardware-accurate implementation** rules to ensure it truly simulates hardware behavior:

### Implementation Modules (NO HOST OPERATORS)

- ❌ **No built-in numeric operators**: No `+`, `-`, `*`, `/`, `%`, `<<`, `>>` in core logic
- ❌ **No base conversion helpers**: No `int(..., base)`, `bin()`, `hex()`, `format()` in implementation
- ❌ **No float math**: All floating-point operations implemented at bit level
- ✅ **Bit-level operations only**: Boolean logic (`and`, `or`, `xor`, `not`), array indexing, slicing
- ✅ **Explicit bit vectors**: All data carried as arrays of 0/1 (e.g., `[1,0,1,1,0,0,1,0]`)

### Boundary Functions (Format Conversion Only)

I/O boundary functions are allowed for format conversion (like `struct.pack`/`unpack` in C):

```python
# Boundary function - converts Python int to bit array
def int_to_bits(value: int, width: int) -> List[int]:
    """Format conversion only, not used in arithmetic algorithms"""
    
# Boundary function - converts bit array to Python int  
def bits_to_int(bits: List[int]) -> int:
    """Format conversion only, for test verification"""
```

### How Arithmetic Works

All arithmetic is built from primitive operations:

1. **Addition**: Chain of 1-bit full adders
   ```python
   # Each bit computed using only boolean logic
   sum_bit = a_bit ^ b_bit ^ carry_in
   carry_out = (a_bit & b_bit) | (a_bit & carry_in) | (b_bit & carry_in)
   ```

2. **Subtraction**: Addition with two's complement
   ```python
   # a - b = a + (~b + 1)
   result = ALU(a, invert_bits(b), carry_in=1)
   ```

3. **Multiplication**: Shift-and-add algorithm
   ```python
   for each bit in multiplier:
       if bit == 1:
           result = ALU(result, multiplicand << i, ADD)
   ```

4. **Shifting**: Barrel shifter with array operations
   ```python
   # Shift left by 1: remove LSB, add 0 at MSB
   shifted = data[1:] + [0]
   ```

See [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) for detailed compliance documentation.

## Architecture Overview

RISCSim implements a **single-cycle RISC-V CPU** with Harvard architecture:

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│  Fetch     │────▶│  Decode    │────▶│  Execute   │
│  (PC, I$)  │     │  (Decoder) │     │  (ALU)     │
└────────────┘     └────────────┘     └────────────┘
                                            │
┌────────────┐     ┌────────────┐          │
│ Writeback  │◀────│  Memory    │◀─────────┘
│ (RegFile)  │     │  (D$)      │
└────────────┘     └────────────┘
```

**Key Features:**
- **Single-cycle execution**: All 5 stages complete in one cycle
- **Harvard architecture**: Separate instruction and data memory
- **Word-aligned memory**: 4-byte aligned access for LW/SW
- **32 registers**: x0-x31 (x0 hardwired to zero)
- **128KB memory**: 64KB instruction + 64KB data

For detailed architecture documentation, see:
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Complete system architecture
- [docs/INSTRUCTION_SET.md](docs/INSTRUCTION_SET.md) - Instruction reference
- [docs/USAGE.md](docs/USAGE.md) - Usage guide and examples

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: System overview, component descriptions, datapath diagrams, control signals, memory map
- **[INSTRUCTION_SET.md](docs/INSTRUCTION_SET.md)**: Complete instruction reference with encoding details and examples
- **[USAGE.md](docs/USAGE.md)**: Installation, usage examples, debugging, performance analysis
- **[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md)**: Design constraints and compliance verification
- **[RISCV_CPU_IMPLEMENTATION_PLAN.md](RISCV_CPU_IMPLEMENTATION_PLAN.md)**: Development roadmap and phase completion status

## Implementation Status

### ✅ Phase 1: Instruction Memory and Fetch Unit (COMPLETE)
- Memory unit with instruction/data regions
- Fetch unit with PC management
- Hex file loader
- **81 tests passing**

### ✅ Phase 2: Instruction Decoder (COMPLETE)
- Full RISC-V instruction decoder (6 formats)
- Immediate extraction with sign extension
- Control signal generation
- **36 tests passing**

### ✅ Phase 3: Single-Cycle Datapath (COMPLETE)
- Five-stage datapath integration
- Component interconnection
- Branch/jump logic
- **28 tests passing**

### ✅ Phase 4: CPU Simulator Top-Level (COMPLETE)
- CPU class with execution control
- Program loading and execution
- Debugging features
- Statistics tracking
- **20 tests passing**

### ✅ Phase 5: Test Program Execution (COMPLETE)
- 7 comprehensive test programs
- Arithmetic, logical, shifts, memory, branches, jumps
- Full instruction coverage
- **10 tests passing**

### ✅ Phase 6: Documentation and Diagrams (COMPLETE)
- Architecture documentation
- Instruction set reference
- Usage guide
- ASCII art diagrams

### ⏳ Phase 7: Integration Testing (Planned)
- Edge case testing
- Corner case validation
- Performance benchmarking

**Total: 586 tests passing (Phases 1-5 + existing components)**

## Project Timeline

- ✅ **Week 1**: Phases 1-2 (Memory, Fetch, Decoder) - COMPLETE
- ✅ **Week 2**: Phase 3 (Datapath Integration) - COMPLETE
- ✅ **Week 3**: Phases 4-5 (CPU Top-Level, Test Programs) - COMPLETE
- ✅ **Week 4**: Phase 6 (Documentation) - COMPLETE
- ⏳ **Future**: Phase 7 (Integration Testing) - Planned

## Contributing

This is an academic project for CPSC440 - Computer Architecture. See [AI_USAGE.md](AI_USAGE.md) for AI assistance disclosure and development guidelines.

### Development Guidelines

1. **Follow hardware-accurate constraints**: No host arithmetic operators in implementation
2. **Maintain test coverage**: Add tests for all new features
3. **Document thoroughly**: Include docstrings and usage examples
4. **Use consistent style**: Follow existing code patterns
5. **Commit frequently**: Clear commit messages describing changes

## License

Academic project for CPSC440 - Computer Architecture

## References

- [RISC-V ISA Specification](https://riscv.org/technical/specifications/)
- [RISC-V Reader: An Open Architecture Atlas](http://www.riscvbook.com/)
- [IEEE-754 Standard](https://standards.ieee.org/standard/754-2019.html)
- [Computer Organization and Design RISC-V Edition](https://www.elsevier.com/books/computer-organization-and-design-risc-v-edition/patterson/978-0-12-812275-4) (Patterson & Hennessy)

## Acknowledgments

- RISC-V Foundation for open ISA specification
- CPSC440 course staff for project guidance
- Open-source RISC-V community for reference implementations
