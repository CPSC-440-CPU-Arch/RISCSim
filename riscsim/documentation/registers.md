# Register File Documentation

## Overview

The `registers.py` module implements the RISC-V Register File, which is the central storage component for the CPU's general-purpose registers and floating-point registers. This implementation follows the RISC-V RV32 specification with the F (single-precision floating-point) extension.

**Module:** `riscsim.cpu.registers`
**Main Class:** `RegisterFile`

---

## Architecture Components

The register file manages three main storage components:

### 1. Integer Registers (x0-x31)
- **Count:** 32 registers
- **Width:** 32 bits (XLEN=32 for RV32)
- **Special Behavior:** x0 is hardwired to zero (reads always return 0, writes are ignored)
- **Naming Convention:**
  - x0: Zero register (hardwired to 0)
  - x1-x31: General-purpose integer registers

### 2. Floating-Point Registers (f0-f31)
- **Count:** 32 registers
- **Width:** 32 bits (FLEN=32 for F extension)
- **Purpose:** Store single-precision floating-point values
- **Naming Convention:** f0-f31

### 3. FCSR (Floating-Point Control and Status Register)
- **Width:** 8 bits
- **Fields:**
  - **Bits 7-5:** `frm` (Rounding Mode) - 3 bits
  - **Bits 4-0:** `fflags` (Exception Flags) - 5 bits

---

## Bit Convention

**All values use MSB-first convention:**
- Index 0 = Most Significant Bit (MSB)
- Index 31 = Least Significant Bit (LSB)

**Example:**
```python
# Binary: 0000...0001 (decimal 1)
value = [0]*31 + [1]
# index 0 is the MSB, index 31 is the LSB
```

---

## Class: RegisterFile

### Constructor

```python
rf = RegisterFile()
```

Initializes a new register file with all registers set to zero:
- All 32 integer registers initialized to `[0]*32`
- All 32 floating-point registers initialized to `[0]*32`
- FCSR register initialized to `[0]*8`

---

## Integer Register Operations

### read_int_reg(reg_num)

Read an integer register value.

**Parameters:**
- `reg_num` (int): Register number (0-31)

**Returns:**
- List of 32 bits representing the register value
- x0 always returns `[0]*32` regardless of previous writes

**Raises:**
- `ValueError`: If reg_num is out of range (not 0-31)

**Example:**
```python
rf = RegisterFile()
value = rf.read_int_reg(5)  # Read x5
# Returns: [0, 0, 0, ..., 0] (32 zeros)

zero = rf.read_int_reg(0)   # Read x0 (always zero)
# Returns: [0, 0, 0, ..., 0]
```

**Implementation Note:** Returns a copy of the internal state to prevent external modification.

---

### write_int_reg(reg_num, value)

Write a value to an integer register.

**Parameters:**
- `reg_num` (int): Register number (0-31)
- `value` (list): 32-bit array to write

**Raises:**
- `ValueError`: If reg_num is out of range or value is not 32 bits

**Special Behavior:**
- Writes to x0 are **silently ignored** (x0 is hardwired to zero)

**Example:**
```python
rf = RegisterFile()

# Write value 42 to x5
value_42 = [0]*27 + [1,0,1,0,1,0]  # Binary: 101010 = 42
rf.write_int_reg(5, value_42)

# Try to write to x0 (ignored)
rf.write_int_reg(0, [1]*32)
x0_value = rf.read_int_reg(0)  # Still returns [0]*32
```

**Implementation Note:** Stores a copy of the value to prevent external modification.

---

## Floating-Point Register Operations

### read_fp_reg(reg_num)

Read a floating-point register value.

**Parameters:**
- `reg_num` (int): Register number (0-31)

**Returns:**
- List of 32 bits representing the register value

**Raises:**
- `ValueError`: If reg_num is out of range (not 0-31)

**Example:**
```python
rf = RegisterFile()
fp_value = rf.read_fp_reg(10)  # Read f10
```

---

### write_fp_reg(reg_num, value)

Write a value to a floating-point register.

**Parameters:**
- `reg_num` (int): Register number (0-31)
- `value` (list): 32-bit array to write

**Raises:**
- `ValueError`: If reg_num is out of range or value is not 32 bits

**Example:**
```python
rf = RegisterFile()

# Write a pattern to f10
pattern = [1,0,1,0] * 8  # Alternating pattern
rf.write_fp_reg(10, pattern)

# Read it back
result = rf.read_fp_reg(10)
# Returns: [1,0,1,0,1,0,1,0, ...]
```

---

## FCSR Operations

The FCSR (Floating-Point Control and Status Register) manages floating-point operation modes and tracks exceptions.

### FCSR Structure

```
Bit Position:  7  6  5  |  4  3  2  1  0
Field:        [ frm  ]  |  [   fflags   ]
              Rounding  |   Exception
              Mode      |   Flags
```

**Rounding Mode (frm) - Bits 7-5:**
- `[0,0,0]` - RNE (Round to Nearest, ties to Even) - **Default**
- `[0,0,1]` - RTZ (Round Toward Zero)
- `[0,1,0]` - RDN (Round Down, toward -∞)
- `[0,1,1]` - RUP (Round Up, toward +∞)
- `[1,0,0]` - RMM (Round to Nearest, ties to Max Magnitude)

**Exception Flags (fflags) - Bits 4-0:**
- **Bit 4:** NV (Invalid Operation)
- **Bit 3:** DZ (Divide by Zero)
- **Bit 2:** OF (Overflow)
- **Bit 1:** UF (Underflow)
- **Bit 0:** NX (Inexact)

---

### read_fcsr()

Read the entire FCSR register.

**Returns:**
- 8-bit array representing the complete FCSR value

**Example:**
```python
rf = RegisterFile()
fcsr = rf.read_fcsr()
# Returns: [0,0,0,0,0,0,0,0]
```

---

### write_fcsr(value)

Write the entire FCSR register.

**Parameters:**
- `value` (list): 8-bit array to write

**Raises:**
- `ValueError`: If value is not 8 bits

**Example:**
```python
rf = RegisterFile()
# Set rounding mode to RTZ and set NX flag
fcsr_value = [0,0,1,0,0,0,0,1]  # RTZ mode, NX=1
rf.write_fcsr(fcsr_value)
```

---

### get_rounding_mode()

Get the rounding mode field from FCSR.

**Returns:**
- 3-bit array representing frm (bits 7-5 of FCSR)

**Example:**
```python
rf = RegisterFile()
rf.set_rounding_mode([0,0,1])  # Set to RTZ
mode = rf.get_rounding_mode()
# Returns: [0,0,1]
```

---

### set_rounding_mode(mode)

Set the rounding mode field in FCSR.

**Parameters:**
- `mode` (list): 3-bit array representing the rounding mode

**Raises:**
- `ValueError`: If mode is not 3 bits

**Example:**
```python
rf = RegisterFile()
rf.set_rounding_mode([0,1,0])  # Set to RDN (Round Down)
```

---

### get_fflags()

Get all exception flags from FCSR.

**Returns:**
- 5-bit array representing fflags (bits 4-0 of FCSR)

**Example:**
```python
rf = RegisterFile()
flags = rf.get_fflags()
# Returns: [0,0,0,0,0]  (no exceptions)
```

---

### set_fflags(flags)

Set all exception flags in FCSR.

**Parameters:**
- `flags` (list): 5-bit array representing the exception flags

**Raises:**
- `ValueError`: If flags is not 5 bits

**Example:**
```python
rf = RegisterFile()
# Set overflow and inexact flags
rf.set_fflags([0,0,1,0,1])  # OF=1, NX=1
```

---

## Individual Flag Operations

### Setting Individual Flags

**Methods:**
- `set_flag_nv(value)` - Set Invalid Operation flag
- `set_flag_dz(value)` - Set Divide by Zero flag
- `set_flag_of(value)` - Set Overflow flag
- `set_flag_uf(value)` - Set Underflow flag
- `set_flag_nx(value)` - Set Inexact flag

**Parameters:**
- `value` (int): 0 or 1

**Example:**
```python
rf = RegisterFile()
rf.set_flag_of(1)  # Set overflow flag
rf.set_flag_nx(1)  # Set inexact flag
```

---

### Reading Individual Flags

**Methods:**
- `get_flag_nv()` - Get Invalid Operation flag
- `get_flag_dz()` - Get Divide by Zero flag
- `get_flag_of()` - Get Overflow flag
- `get_flag_uf()` - Get Underflow flag
- `get_flag_nx()` - Get Inexact flag

**Returns:**
- int: 0 or 1

**Example:**
```python
rf = RegisterFile()
rf.set_flag_of(1)

if rf.get_flag_of():
    print("Overflow occurred")
# Output: Overflow occurred
```

---

## Complete Usage Example

```python
from riscsim.cpu.registers import RegisterFile

# Create register file
rf = RegisterFile()

# === Integer Register Operations ===

# Write to x5
value = [0]*27 + [1,0,1,0,1,0]  # 42 in binary
rf.write_int_reg(5, value)

# Read from x5
result = rf.read_int_reg(5)
print(f"x5 = {result}")

# Try to modify x0 (will be ignored)
rf.write_int_reg(0, [1]*32)
zero = rf.read_int_reg(0)
# zero is still [0]*32

# === Floating-Point Register Operations ===

# Write to f10
fp_data = [0,1,0,0,0,0,0,0] + [0]*24  # Some FP pattern
rf.write_fp_reg(10, fp_data)

# Read from f10
fp_result = rf.read_fp_reg(10)

# === FCSR Operations ===

# Set rounding mode to Round Toward Zero (RTZ)
rf.set_rounding_mode([0,0,1])

# Set some exception flags
rf.set_flag_of(1)  # Overflow
rf.set_flag_nx(1)  # Inexact

# Read flags
flags = rf.get_fflags()
print(f"Flags: {flags}")  # [0,0,1,0,1]

# Check specific flag
if rf.get_flag_of():
    print("Overflow flag is set")
```

---

## Implementation Details

### Memory Safety
- All read operations return **copies** of internal state
- All write operations store **copies** of input values
- This prevents external code from accidentally modifying internal register state

### x0 Hardwiring
The RISC-V specification requires x0 to always read as zero:
```python
# Implementation ensures x0 is always zero
if reg_num == 0:
    return [0] * XLEN  # Always return zeros

# Writes to x0 are silently ignored
if reg_num == 0:
    return  # No-op
```

### Bit Indexing
The module uses **MSB-first** indexing consistently:
- Bit 7 of FCSR (MSB) is at index 0
- Bit 0 of FCSR (LSB) is at index 7
- This applies to all registers (integer, FP, and FCSR)

---

## Constants

```python
XLEN = 32           # Integer register width (RV32)
FLEN = 32           # Floating-point register width (F extension)
FCSR_WIDTH = 8      # FCSR register width
NUM_INT_REGS = 32   # Number of integer registers
NUM_FP_REGS = 32    # Number of floating-point registers
```

---

## Dependencies

```python
from riscsim.utils.bit_utils import slice_bits, set_bit, get_bit
```

The register file uses utility functions for bit manipulation operations.

---

## RISC-V Compliance

This implementation follows the RISC-V specification:
- **RV32I Base Integer Instruction Set** (32-bit integer registers)
- **RV32F Standard Extension** (32-bit floating-point registers)
- **FCSR specification** for floating-point control and status

---

## Testing

Comprehensive tests are available in `tests/test_registers.py` covering:
- Integer register read/write operations
- x0 hardwiring behavior
- Floating-point register operations
- FCSR read/write operations
- Rounding mode management
- Exception flag operations
- Boundary conditions and error handling

---

## See Also

- RISC-V Instruction Set Manual: https://riscv.org/technical/specifications/
- Related modules:
  - `riscsim.cpu.alu` - Arithmetic Logic Unit
  - `riscsim.cpu.shifter` - Barrel Shifter
  - `riscsim.utils.bit_utils` - Bit manipulation utilities
