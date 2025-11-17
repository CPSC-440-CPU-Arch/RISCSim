# RISCSim Project Architecture

**Authors:** Joshua Castaneda and Ivan Flores

## Compliance with "No Host Operators" Requirement

This document explains how RISCSim meets the strict requirement: **"No built-in numeric operators in implementation modules"**.

---

## Architecture Overview

RISCSim is built on a **layered architecture** that separates:
1. **Pure bit-level implementation modules** (ALU, MDU, FPU, shifter)
2. **I/O boundary functions** (format conversion only)
3. **Test utilities** (for reference value computation)

---

## Implementation Modules (NO HOST OPERATORS)

These modules implement all arithmetic using ONLY bit-level operations:

### ✅ ALU (`riscsim/cpu/alu.py`)
- Hand-stitched from 32 1-bit ALUs
- Uses ONLY boolean logic: `and`, `or`, `xor`, `not`
- **NO** `+`, `-`, or any arithmetic operators

### ✅ MDU (`riscsim/cpu/mdu.py`)
- Multiplication: shift-add algorithm using ALU and shifter
- Division: restoring division using ALU and shifter
- **NO** `*`, `/`, `%`, or any arithmetic operators

### ✅ Shifter (`riscsim/cpu/shifter.py`)
- 5-stage barrel shifter (shifts by 16, 8, 4, 2, 1)
- Uses ONLY array slicing and concatenation
- **NO** `<<`, `>>` operators in core logic
- Lookup table for shift amount conversion (test convenience)

### ✅ Registers (`riscsim/cpu/registers.py`)
- Bit array storage only
- NO arithmetic operators

---

## I/O Boundary Functions (FORMAT CONVERSION ONLY)

These functions convert between Python's native types and bit arrays.
They use minimal operators for **format conversion**, NOT for implementing arithmetic.

### Analogous to C's `struct.pack` / `struct.unpack`

Just as C code might use `struct.pack()` to convert a float to bytes, we use I/O boundary functions to convert between representations.

#### In `riscsim/utils/twos_complement.py`:
```python
def _int_to_bits_boundary(value, width):
    """
    I/O BOUNDARY FUNCTION
    Converts Python int to bit array (format conversion only)
    Uses %, // for conversion (like struct.pack for format conversion)
    """
```

#### In `riscsim/cpu/fpu.py`:
```python
def pack_f32(value):
    """
    I/O BOUNDARY FUNCTION
    Converts Python float to IEEE-754 bits using struct.pack()
    Format conversion only - NOT for arithmetic
    """

def unpack_f32(bits):
    """
    I/O BOUNDARY FUNCTION
    Converts IEEE-754 bits to Python float using struct.unpack()
    Format conversion only - NOT for arithmetic
    """
```

#### In `riscsim/utils/bit_utils.py`:
```python
def int_to_bits_unsigned(value, width):
    """
    ***** TEST-ONLY FUNCTION *****
    Uses %, // for test data generation
    DO NOT use in implementation modules!
    """

def bits_to_int_unsigned(bits):
    """
    ***** TEST-ONLY FUNCTION *****
    Uses + for test verification
    DO NOT use in implementation modules!
    """
```

---

## Where Arithmetic Happens

### ❌ WRONG (uses host operators):
```python
# BAD: Using Python arithmetic in implementation
result_val = val_a + val_b  # Uses host + operator
```

### ✅ RIGHT (uses bit-level ALU):
```python
# GOOD: Using ALU for arithmetic
sig_a_32 = zero_extend(sig_a, 32)
sig_b_32 = zero_extend(sig_b, 32)
result_sig, flags = alu(sig_a_32, sig_b_32, [0, 0, 1, 0])  # ADD operation
```

---

## FPU Implementation

The FPU (`riscsim/cpu/fpu.py`) demonstrates full bit-level arithmetic:

### `fadd_f32()` - IEEE-754 Addition
1. ✅ Extract fields using bit slicing
2. ✅ Align exponents using `compare_exponents()` (ALU-based)
3. ✅ Shift significands using `shifter()`
4. ✅ Add/subtract using `alu()`
5. ✅ Normalize using `normalize_significand()` (shifter + ALU)
6. ✅ Pack result using bit concatenation

### `fmul_f32()` - IEEE-754 Multiplication
1. ✅ Extract significands
2. ✅ Multiply using shift-add algorithm (ALU)
3. ✅ Add exponents using ALU
4. ✅ Normalize using shifter
5. ✅ Pack result

### What About `pack_f32`/`unpack_f32`?

These are **I/O boundary functions** (like `struct.pack`), used ONLY for:
- Test data generation
- Converting initial values
- **NOT** for arithmetic within algorithms

All arithmetic operations (fadd, fmul, fsub) use bit-level ALU/shifter operations.

---

## Test Utilities

Test files can use:
- `int_to_bits_unsigned()` - to create test data
- `bits_to_int_unsigned()` - to verify results
- Python arithmetic - to compute expected values

**These are NOT used in implementation modules!**

---

## Verification

### Check Implementation Purity:
```bash
# ALU: should find NO +, -, *, / operators
grep -E '(\+|-|\*|/|%|<<|>>)' riscsim/cpu/alu.py

# MDU: should find NO *, /, % operators
grep -E '(\*|/|%)' riscsim/cpu/mdu.py

# Shifter: should find NO <<, >> in core logic
grep -E '(<<|>>)' riscsim/cpu/shifter.py
```

---

## Summary

**Implementation modules** (ALU, MDU, FPU, shifter):
- ✅ Use ONLY: boolean logic, array operations, ALU, shifter
- ❌ NO: +, -, *, /, %, <<, >>, arithmetic operators

**I/O boundary functions** (pack/unpack, int_to_bits, etc.):
- ✅ Convert between Python types and bit arrays
- ✅ Analogous to struct.pack/unpack (format conversion)
- ❌ NOT used for arithmetic in algorithms

**Test files**:
- ✅ Can use Python arithmetic for reference values
- ✅ Use I/O boundary functions to create test data

This architecture provides a clean separation between:
1. **Pure bit-level implementation** (the CPU components)
2. **Format conversion** (I/O boundaries)
3. **Test infrastructure** (reference value computation)
