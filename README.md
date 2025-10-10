# RISCSim - RISC-V Numeric Operations Simulator

A hardware-accurate simulator for RISC-V numeric operations, implementing two's-complement arithmetic, integer multiply/divide (M extension), and IEEE-754 floating-point operations (F extension).

## Overview

This project is a **midterm alternative project** that will later be merged into a full RISC-V CPU simulator. It focuses on bit-level implementations of numeric operations without using host language numeric operators.

## Features

### Implemented
- **Two's-Complement Toolkit** (32-bit RV32)
  - Encode/decode with overflow detection
  - Sign-extend and zero-extend helpers

- **RV32I Integer Operations**
  - ADD, SUB with ALU flags (N, Z, C, V)
  - Bit-level full adder implementation

- **RV32M Integer Multiply/Divide**
  - MUL, MULH, MULHU, MULHSU (shift-add algorithm with traces)
  - DIV, DIVU, REM, REMU (restoring division with traces)
  - RISC-V edge-case semantics (div-by-zero, INT_MIN/-1)

- **IEEE-754 Float32 (F Extension)**
  - Pack/unpack with special values (±0, ±∞, NaN)
  - FADD, FSUB, FMUL with RoundTiesToEven
  - Exception flags (overflow, underflow, invalid)

### Hardware Components
- **ALU**: Full-adder chains, bit-level operations
- **Shifter**: Barrel-shifter implementation (SLL/SRL/SRA)
- **MDU**: Multiply/Divide unit with internal registers
- **FPU**: Float32 unit with normalization and rounding
- **Registers**: 32 integer registers (x0-x31), 32 FP registers (f0-f31), FCSR

## Project Structure

```
RISCSim/
├── riscsim/                   # Main package (renamed from src/)
│   ├── __init__.py
│   ├── cpu/                   # CPU components
│   │   ├── __init__.py
│   │   ├── alu.py             # Arithmetic Logic Unit
│   │   ├── shifter.py         # Barrel shifter
│   │   ├── mdu.py             # Multiply/Divide Unit
│   │   ├── fpu.py             # Floating-Point Unit
│   │   └── registers.py       # Register file and FCSR
│   └── utils/                 # Utility modules
│       ├── __init__.py
│       └── bit_utils.py       # Bit manipulation utilities
├── tests/                     # Test suite
│   ├── test_bit_utils.py
│   ├── test_alu.py
│   └── ...
├── pyproject.toml             # Modern Python packaging config
├── README.md
└── PROJECTINSTRUCTIONS.md
```

## Installation

### For Development (Recommended)

```bash
# Clone the repository
git clone https://github.com/CPSC-440-CPU-Arch/RISCSim.git
cd RISCSim

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode (changes reflect immediately)
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### For Users

```bash
# Install directly from repository
pip install git+https://github.com/CPSC-440-CPU-Arch/RISCSim.git

# Or after cloning
pip install .
```

## Usage

```python
from riscsim.utils.bit_utils import bits_and, bits_to_hex_string
from riscsim.cpu.alu import alu

# Use bit utilities
result = bits_and([1,0,1,0], [1,1,0,0])
print(bits_to_hex_string(result))  # Output: 0x8

# Use CPU components
alu()  # Will be expanded with actual ALU operations
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_bit_utils.py

# Run with verbose output
pytest -v

# Run with print statements visible
pytest -v -s
```

## Design Constraints

This simulator follows strict hardware-accurate implementation rules:

- ❌ **No built-in numeric operators**: No `+`, `-`, `*`, `/`, `%`, `<<`, `>>` in implementation
- ❌ **No base conversion helpers**: No `int(..., base)`, `bin()`, `hex()`, `format()`
- ❌ **No float math**: All floating-point operations implemented at bit level
- ✅ **Bit-level operations only**: Boolean logic, array indexing, control flow
- ✅ **Explicit bit vectors**: All data carried as arrays of 0/1

## Architecture Principles

To facilitate merging with the future CPU simulator:

1. **Pure functions**: Stateless operations that return results
2. **Explicit state**: `State{regs[32], fregs[32], flags}` structure
3. **Modular design**: Each component (ALU, MDU, FPU) is independent
4. **Traceable execution**: All multi-step operations provide cycle-by-cycle traces
5. **Deterministic**: No global state or side effects

## Development Timeline

- ✅ T0: Project structure and bit utilities
- 🔄 T0+3 days: Two's-complement and ALU with tests
- ⏳ T0+1 week: RV32M multiply/divide with traces
- ⏳ T0+2 weeks: Float32 operations and comprehensive tests

## Contributing

See `AI_USAGE.md` for AI assistance disclosure and contribution guidelines.

## License

Academic project for CPSC440 - Computer Architecture

## References

- [RISC-V ISA Specification](https://riscv.org/technical/specifications/)
- [IEEE-754 Standard](https://standards.ieee.org/standard/754-2019.html)
- Computer Organization and Design RISC-V Edition (Patterson & Hennessy)
