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

## Initial Project Structure (Subject to Refactoring)

```
RISCSim/
├── src/
│   ├── bit_utils.py           # Bit array operations and conversions
│   ├── twos_complement.py     # Two's-complement encode/decode
│   ├── alu.py                 # Arithmetic Logic Unit (ADD/SUB)
│   ├── shifter.py             # Barrel shifter (SLL/SRL/SRA)
│   ├── mdu.py                 # Multiply/Divide Unit
│   ├── fpu.py                 # Floating-Point Unit (Float32)
│   ├── registers.py           # Register file and FCSR
│   └── simulator.py           # Main simulator interface
├── tests/
│   ├── test_bit_utils.py
│   ├── test_twos_complement.py
│   ├── test_alu.py
│   ├── test_shifter.py
│   ├── test_mdu.py
│   └── test_fpu.py
├── README.md
├── AI_USAGE.md                # AI usage disclosure
├── ai_report.json             # AI contribution metrics
└── PROJECTINSTRUCTIONS.md     # Original project specification
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd RISCSim

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```python
from src.simulator import RISCSimulator

# Create simulator instance
sim = RISCSimulator()

# Example: Two's-complement encoding
result = sim.encode_twos_complement(13)
print(f"Binary: {result['bin']}, Hex: {result['hex']}")

# Example: Integer multiply
result = sim.mul(12345678, -87654321)
print(f"Result: {result['rd']}, Overflow: {result['overflow']}")

# Example: Float32 addition
result = sim.fadd_f32(1.5, 2.25)
print(f"Result: {result['value']}, Bits: {result['bits']}")
```

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_alu.py

# Run with verbose output and traces
pytest tests/ -v --tb=short
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
