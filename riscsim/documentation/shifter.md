# Barrel Shifter Documentation

## Overview

The `shifter.py` module implements a **barrel shifter** for RISC-V shift operations. A barrel shifter is a digital circuit that can shift data by any number of bit positions in a single clock cycle using a multi-stage approach, avoiding the need for iterative shifting or built-in shift operators.

This implementation strictly adheres to hardware-like behavior by using only bit-level manipulation operations, without relying on Python's built-in `<<` or `>>` shift operators.

**Module:** `riscsim.cpu.shifter`
**Main Function:** `shifter(bits, shamt, op)`

---

## Supported Operations

The barrel shifter implements three RISC-V shift operations:

### 1. SLL (Shift Left Logical)
- **Operation:** Shift bits to the left
- **Fill:** Zeros on the right (LSB side)
- **Use Case:** Multiplication by powers of 2, bit manipulation
- **Example:** `0x00000001` << 3 = `0x00000008`

### 2. SRL (Shift Right Logical)
- **Operation:** Shift bits to the right
- **Fill:** Zeros on the left (MSB side)
- **Use Case:** Unsigned division by powers of 2, bit extraction
- **Example:** `0x80000000` >> 4 = `0x08000000`

### 3. SRA (Shift Right Arithmetic)
- **Operation:** Shift bits to the right
- **Fill:** Sign bit replicated on the left (MSB side)
- **Use Case:** Signed division by powers of 2, preserving sign in two's complement
- **Example:** `0x80000000` >> 4 = `0xF8000000` (sign-extended)

---

## Barrel Shifter Architecture

### Multi-Stage Design

The barrel shifter uses a **5-stage pipeline** where each stage can shift by a power of 2:

```
Stage 1: Shift by 0 or 16 bits (controlled by shamt[0])
Stage 2: Shift by 0 or 8 bits  (controlled by shamt[1])
Stage 3: Shift by 0 or 4 bits  (controlled by shamt[2])
Stage 4: Shift by 0 or 2 bits  (controlled by shamt[3])
Stage 5: Shift by 0 or 1 bit   (controlled by shamt[4])
```

**Why 5 stages?** With 5 bits in the shift amount, we can represent values 0-31, which is perfect for shifting 32-bit values.

### How It Works

Each stage conditionally shifts the data based on the corresponding bit in the shift amount:

```
Example: Shift left by 7 positions
- 7 in binary: 00111
- Stage 1 (bit 4=0): No shift by 16
- Stage 2 (bit 3=0): No shift by 8
- Stage 3 (bit 2=1): Shift by 4
- Stage 4 (bit 1=1): Shift by 2
- Stage 5 (bit 0=1): Shift by 1
- Total shift: 4 + 2 + 1 = 7 ✓
```

This allows any shift amount from 0 to 31 in just 5 stages!

---

## Function Reference

### shifter(bits, shamt, op)

Performs a shift operation on a 32-bit value using barrel shifter architecture.

**Parameters:**

- **bits** (list): 32-bit array to shift (MSB at index 0, LSB at index 31)
- **shamt** (int or list): Shift amount
  - As integer: 0-31 (or any value - automatically masked to 5 bits)
  - As list: 5-bit array `[b4, b3, b2, b1, b0]`
- **op** (str or list): Operation code
  - As string: `"SLL"`, `"SRL"`, or `"SRA"` (case-insensitive)
  - As list: 2-bit array
    - `[0, 0]` = SLL
    - `[0, 1]` = SRL
    - `[1, 1]` = SRA

**Returns:**
- list: 32-bit array with the shifted result (MSB at index 0)

**Raises:**
- `AssertionError`: If bits is not 32-bit array
- `AssertionError`: If shamt is not valid (integer or 5-bit array)
- `AssertionError`: If op is not valid operation code
- `ValueError`: If op bit pattern is not recognized

---

## Usage Examples

### Example 1: Basic Shift Left Logical (SLL)

```python
from riscsim.cpu.shifter import shifter

# Shift 0x00000001 left by 4 positions
bits = [0]*31 + [1]  # Binary: 0000...0001
result = shifter(bits, 4, "SLL")

# Result: [0]*27 + [1,0,0,0,0]  (Binary: 0000...00010000 = 0x00000010)
```

### Example 2: Shift Right Logical (SRL)

```python
from riscsim.cpu.shifter import shifter

# Shift 0x80000000 right by 4 positions (logical)
bits = [1] + [0]*31  # Binary: 1000...0000
result = shifter(bits, 4, "SRL")

# Result: [0]*4 + [1] + [0]*27  (Binary: 0000 1000...0000 = 0x08000000)
# Note: Filled with zeros on the left
```

### Example 3: Shift Right Arithmetic (SRA)

```python
from riscsim.cpu.shifter import shifter

# Shift 0x80000000 right by 4 positions (arithmetic)
bits = [1] + [0]*31  # Binary: 1000...0000 (negative in two's complement)
result = shifter(bits, 4, "SRA")

# Result: [1]*5 + [0]*27  (Binary: 1111 1000...0000 = 0xF8000000)
# Note: Filled with sign bit (1) on the left
```

### Example 4: Using Bit Array for Shift Amount

```python
from riscsim.cpu.shifter import shifter

# Shift left by 7 (binary: 00111)
bits = [0]*31 + [1]
shamt = [0, 0, 1, 1, 1]  # 5-bit representation of 7
result = shifter(bits, shamt, "SLL")

# Result: 0x00000080 (shifted left by 7)
```

### Example 5: Using Bit Array for Operation

```python
from riscsim.cpu.shifter import shifter

# Use operation codes as bit arrays
bits = [0]*28 + [1,1,1,1]  # 0x0000000F

result_sll = shifter(bits, 4, [0, 0])  # SLL
# Result: 0x000000F0

result_srl = shifter(bits, 1, [0, 1])  # SRL
# Result: 0x00000007

result_sra = shifter(bits, 1, [1, 1])  # SRA
# Result: 0x00000007 (same as SRL for positive numbers)
```

### Example 6: Shift Amount Masking

```python
from riscsim.cpu.shifter import shifter

# RISC-V specification: only lower 5 bits of shamt are used
bits = [0]*31 + [1]

# 32 in binary: 100000 (6 bits)
# Lower 5 bits: 00000 = 0
result = shifter(bits, 32, "SLL")
# Result: 0x00000001 (no shift, because 32 & 0x1F = 0)

# 33 in binary: 100001
# Lower 5 bits: 00001 = 1
result = shifter(bits, 33, "SLL")
# Result: 0x00000002 (shifted by 1)
```

---

## Detailed Operation Behavior

### SLL (Shift Left Logical)

**Algorithm:**
1. For each stage (16, 8, 4, 2, 1):
   - If corresponding shamt bit is 1:
     - Take bits from position `shift_amount` to end
     - Concatenate with `shift_amount` zeros on the right
   - Otherwise: keep current bits unchanged

**Visual Example (shift by 3):**
```
Original:  0000 0000 0000 0000 0000 0000 0000 0001
           ↓
Stage 3:   (shamt[2]=1) shift by 4
           0000 0000 0000 0000 0000 0000 0001 0000
           ↓
Stage 4:   (shamt[3]=0) no shift
           0000 0000 0000 0000 0000 0000 0001 0000
           ↓
Stage 5:   (shamt[4]=1) shift by 1
Result:    0000 0000 0000 0000 0000 0000 0010 0000
```

---

### SRL (Shift Right Logical)

**Algorithm:**
1. For each stage (16, 8, 4, 2, 1):
   - If corresponding shamt bit is 1:
     - Add `shift_amount` zeros on the left
     - Concatenate with bits from position 0 to `32 - shift_amount`
   - Otherwise: keep current bits unchanged

**Visual Example (shift by 3):**
```
Original:  1000 0000 0000 0000 0000 0000 0000 0000
           ↓
Stage 3:   (shamt[2]=1) shift by 4
           0000 1000 0000 0000 0000 0000 0000 0000
           ↓
Stage 4:   (shamt[3]=0) no shift
           0000 1000 0000 0000 0000 0000 0000 0000
           ↓
Stage 5:   (shamt[4]=1) shift by 1
Result:    0000 0100 0000 0000 0000 0000 0000 0000
```

---

### SRA (Shift Right Arithmetic)

**Algorithm:**
1. Extract sign bit (MSB, index 0)
2. For each stage (16, 8, 4, 2, 1):
   - If corresponding shamt bit is 1:
     - Add `shift_amount` **sign bits** on the left (instead of zeros)
     - Concatenate with bits from position 0 to `32 - shift_amount`
   - Otherwise: keep current bits unchanged

**Visual Example - Negative Number (shift by 3):**
```
Original:  1000 0000 0000 0000 0000 0000 0000 0000  (sign bit = 1)
           ↓
Stage 3:   (shamt[2]=1) shift by 4, fill with sign bit
           1111 1000 0000 0000 0000 0000 0000 0000
           ↓
Stage 4:   (shamt[3]=0) no shift
           1111 1000 0000 0000 0000 0000 0000 0000
           ↓
Stage 5:   (shamt[4]=1) shift by 1, fill with sign bit
Result:    1111 1100 0000 0000 0000 0000 0000 0000
```

**Visual Example - Positive Number (shift by 3):**
```
Original:  0111 1111 1111 1111 1111 1111 1111 1111  (sign bit = 0)
           ↓
Stage 3:   (shamt[2]=1) shift by 4, fill with sign bit (0)
           0000 0111 1111 1111 1111 1111 1111 1111
           ↓
Stage 4:   (shamt[3]=0) no shift
           0000 0111 1111 1111 1111 1111 1111 1111
           ↓
Stage 5:   (shamt[4]=1) shift by 1, fill with sign bit (0)
Result:    0000 0011 1111 1111 1111 1111 1111 1111
```

**Key Insight:** For positive numbers (sign bit = 0), SRA behaves identically to SRL!

---

## Bit Convention

**All values use MSB-first convention:**
- Index 0 = Most Significant Bit (MSB)
- Index 31 = Least Significant Bit (LSB)

This convention is consistent across the entire RISCSim project.

---

## Implementation Details

### No Built-in Shift Operators

The implementation strictly avoids Python's `<<` and `>>` operators to simulate hardware behavior:

```python
# ❌ NOT ALLOWED (would violate hardware simulation)
result = value << shift_amount
result = value >> shift_amount

# ✅ ALLOWED (uses barrel shifter stages)
if shamt_bits[0] == 1:
    current = concat_bits(slice_bits(current, 16, 32), [0]*16)
```

### Stage-by-Stage Processing

Each stage is implemented explicitly without loops for clarity and hardware accuracy:

```python
# Stage 1: Shift by 16 if shamt_bits[0] == 1
if shamt_bits[0] == 1:
    current = concat_bits(slice_bits(current, 16, 32), [0]*16)

# Stage 2: Shift by 8 if shamt_bits[1] == 1
if shamt_bits[1] == 1:
    current = concat_bits(slice_bits(current, 8, 32), [0]*8)

# ... and so on for stages 3, 4, 5
```

### Utility Functions Used

```python
from riscsim.utils.bit_utils import slice_bits, concat_bits

# slice_bits(bits, start, end) - Extract bit range (Python slice semantics)
# concat_bits(*arrays) - Concatenate multiple bit arrays
```

---

## Edge Cases and Special Behaviors

### 1. Shift by Zero
```python
bits = [0]*28 + [1,0,1,0]  # Some value
result = shifter(bits, 0, "SLL")
# Result: identical to input (no shift)
```

### 2. Maximum Shift (31 bits)
```python
# SLL: All bits shifted out except possibly one
bits = [0]*31 + [1]
result = shifter(bits, 31, "SLL")
# Result: [1] + [0]*31  (0x80000000)

# SRA: Fills with sign bit
bits = [1] + [0]*31  # Negative number
result = shifter(bits, 31, "SRA")
# Result: [1]*32  (0xFFFFFFFF - all ones)
```

### 3. Shift Amount Greater Than 31
```python
# RISC-V spec: only lower 5 bits are used
bits = [0]*31 + [1]

# 35 & 0x1F = 3
result = shifter(bits, 35, "SLL")
# Equivalent to: shifter(bits, 3, "SLL")
```

### 4. All Zeros Input
```python
bits = [0]*32
# Any shift operation returns all zeros
result_sll = shifter(bits, 10, "SLL")  # [0]*32
result_srl = shifter(bits, 10, "SRL")  # [0]*32
result_sra = shifter(bits, 10, "SRA")  # [0]*32
```

### 5. All Ones Input
```python
bits = [1]*32

result_sll = shifter(bits, 4, "SLL")
# Result: [1]*28 + [0]*4  (0xFFFFFFF0)

result_srl = shifter(bits, 4, "SRL")
# Result: [0]*4 + [1]*28  (0x0FFFFFFF)

result_sra = shifter(bits, 4, "SRA")
# Result: [1]*32  (0xFFFFFFFF - sign extended)
```

---

## Performance Characteristics

### Time Complexity
- **O(1)** - Constant time
- All operations complete in exactly 5 stages regardless of shift amount
- No loops over shift amount (unlike iterative shifters)

### Space Complexity
- **O(1)** - Constant space
- Only a fixed number of intermediate arrays needed for 5 stages

### Hardware Equivalence
The barrel shifter mimics hardware behavior:
- Single-cycle operation (in hardware)
- No iterative shifting required
- Predictable timing regardless of shift amount

---

## Testing

Comprehensive tests are available in `tests/test_shifter.py` covering:

- **40 test cases** across 5 test classes:
  - `TestShiftLeftLogical` (9 tests)
  - `TestShiftRightLogical` (10 tests)
  - `TestShiftRightArithmetic` (10 tests)
  - `TestEdgeCases` (7 tests)
  - `TestComprehensive` (4 tests)

**Test Coverage:**
- All three operations (SLL, SRL, SRA)
- Various shift amounts (0, 1, 4, 8, 16, 31)
- Edge cases (all zeros, all ones, alternating patterns)
- Shift amount masking (values > 31)
- Different input formats (strings, bit arrays)
- Sign preservation for SRA
- Symmetry and operation comparisons

**Test Results:** All 40 tests pass ✓

---

## Common Patterns and Recipes

### Multiply by Power of 2
```python
# Multiply by 8 (2^3)
value = [0]*29 + [1,0,1]  # 5 in binary
result = shifter(value, 3, "SLL")
# Result: 40 (5 * 8)
```

### Divide Unsigned by Power of 2
```python
# Divide by 4 (2^2)
value = [0]*26 + [1,0,1,0,0,0]  # 40 in binary
result = shifter(value, 2, "SRL")
# Result: 10 (40 / 4)
```

### Divide Signed by Power of 2
```python
# Divide -40 by 4 (two's complement)
value = int_to_bin32(-40)  # Helper function from tests
result = shifter(value, 2, "SRA")
# Result: -10 (sign preserved)
```

### Extract Bits
```python
# Extract upper 8 bits
value = [0,1,0,1,0,1,0,1] + [1,1,1,1,0,0,0,0] + [0]*16
upper_8 = shifter(value, 24, "SRL")
# Shifts right 24 positions, zeros fill left
```

---

## Comparison: SRL vs SRA

The critical difference between SRL and SRA is the fill bit:

| Operation | Fill Bit | Use Case | Example (0x80000000 >> 4) |
|-----------|----------|----------|---------------------------|
| **SRL** | Always 0 | Unsigned division | `0x08000000` |
| **SRA** | Sign bit | Signed division | `0xF8000000` |

```python
bits = [1] + [0]*31  # 0x80000000 (negative in two's complement)

# Logical shift: fills with zeros
srl_result = shifter(bits, 4, "SRL")
# Result: 0x08000000

# Arithmetic shift: fills with sign bit (1)
sra_result = shifter(bits, 4, "SRA")
# Result: 0xF8000000

# For positive numbers (sign bit = 0), SRL and SRA are identical!
```

---

## Dependencies

```python
from riscsim.utils.bit_utils import slice_bits, concat_bits
```

The shifter uses utility functions for bit manipulation:
- `slice_bits(bits, start, end)` - Extract a range of bits
- `concat_bits(*arrays)` - Concatenate multiple bit arrays

---

## RISC-V Compliance

This implementation follows the RISC-V specification:
- **RV32I Base Integer Instruction Set**
  - SLL instruction (Shift Left Logical)
  - SRL instruction (Shift Right Logical)
  - SRA instruction (Shift Right Arithmetic)
- **Shift amount masking:** Only lower 5 bits of shamt are used (RISC-V spec requirement)
- **Two's complement preservation:** SRA correctly preserves sign for negative numbers

---

## See Also

- RISC-V Instruction Set Manual: https://riscv.org/technical/specifications/
- Barrel Shifter: https://en.wikipedia.org/wiki/Barrel_shifter
- Related modules:
  - `riscsim.cpu.alu` - Arithmetic Logic Unit
  - `riscsim.cpu.registers` - Register File
  - `riscsim.utils.bit_utils` - Bit manipulation utilities

---

## Quick Reference Card

```python
from riscsim.cpu.shifter import shifter

# Basic usage
result = shifter(bits, shift_amount, operation)

# Operations:
# "SLL" - Shift Left Logical (fill right with 0)
# "SRL" - Shift Right Logical (fill left with 0)
# "SRA" - Shift Right Arithmetic (fill left with sign bit)

# Examples:
shifter([0]*31 + [1], 3, "SLL")      # 0x00000008
shifter([1] + [0]*31, 4, "SRL")      # 0x08000000
shifter([1] + [0]*31, 4, "SRA")      # 0xF8000000
```
