# RISCSim Instruction Set Documentation

**Authors:** Joshua Castaneda and Ivan Flores

## Table of Contents
1. [Overview](#overview)
2. [Instruction Formats](#instruction-formats)
3. [Instruction Encodings](#instruction-encodings)
4. [Arithmetic Instructions](#arithmetic-instructions)
5. [Logical Instructions](#logical-instructions)
6. [Shift Instructions](#shift-instructions)
7. [Memory Instructions](#memory-instructions)
8. [Branch Instructions](#branch-instructions)
9. [Jump Instructions](#jump-instructions)
10. [Upper Immediate Instructions](#upper-immediate-instructions)
11. [Edge Cases and Special Behavior](#edge-cases-and-special-behavior)
12. [Instruction Encoding Examples](#instruction-encoding-examples)

---

## Overview

RISCSim implements the **RV32I base integer instruction set** with support for 23 instructions across 7 categories. All instructions are 32 bits wide and follow the RISC-V instruction format specifications.

### Supported Instructions Summary

| Category | Instructions | Count |
|----------|-------------|-------|
| **Arithmetic** | ADD, SUB, ADDI | 3 |
| **Logical** | AND, OR, XOR, ANDI, ORI, XORI | 6 |
| **Shifts** | SLL, SRL, SRA, SLLI, SRLI, SRAI | 6 |
| **Memory** | LW, SW | 2 |
| **Branch** | BEQ, BNE | 2 |
| **Jump** | JAL, JALR | 2 |
| **Upper Imm** | LUI, AUIPC | 2 |
| **Total** | | **23** |

### Register Convention

- **x0**: Hardwired to zero (writes ignored, always reads 0)
- **x1-x31**: General-purpose registers (32 bits each)
- Common aliases: x1=ra (return address), x2=sp (stack pointer), x8=s0/fp (frame pointer)

---

## Instruction Formats

RISC-V defines 6 base instruction formats. All are 32 bits wide.

### R-Type (Register-Register)

Used for register-to-register operations.

```
 31        25 24    20 19    15 14    12 11     7 6       0
┌───────────┬────────┬────────┬────────┬────────┬─────────┐
│  funct7   │  rs2   │  rs1   │ funct3 │   rd   │ opcode  │
│  [7 bits] │[5 bits]│[5 bits]│[3 bits]│[5 bits]│ [7 bits]│
└───────────┴────────┴────────┴────────┴────────┴─────────┘
```

**Instructions**: ADD, SUB, AND, OR, XOR, SLL, SRL, SRA

---

### I-Type (Immediate)

Used for operations with immediate values and loads.

```
 31                 20 19    15 14    12 11     7 6       0
┌────────────────────┬────────┬────────┬────────┬─────────┐
│     imm[11:0]      │  rs1   │ funct3 │   rd   │ opcode  │
│     [12 bits]      │[5 bits]│[3 bits]│[5 bits]│ [7 bits]│
└────────────────────┴────────┴────────┴────────┴─────────┘
```

**Immediate**: Sign-extended to 32 bits

**Instructions**: ADDI, ANDI, ORI, XORI, SLLI, SRLI, SRAI, LW, JALR

---

### S-Type (Store)

Used for store operations.

```
 31        25 24    20 19    15 14    12 11     7 6       0
┌───────────┬────────┬────────┬────────┬────────┬─────────┐
│ imm[11:5] │  rs2   │  rs1   │ funct3 │imm[4:0]│ opcode  │
│  [7 bits] │[5 bits]│[5 bits]│[3 bits]│[5 bits]│ [7 bits]│
└───────────┴────────┴────────┴────────┴────────┴─────────┘
```

**Immediate**: `{imm[11:5], imm[4:0]}` sign-extended to 32 bits

**Instructions**: SW

---

### B-Type (Branch)

Used for conditional branches.

```
 31    30        25 24    20 19    15 14    12 11    8 7        6       0
┌──────┬───────────┬────────┬────────┬────────┬──────┬─────────┬─────────┐
│imm[12]│ imm[10:5] │  rs2   │  rs1   │ funct3 │imm[4:1]│imm[11]│ opcode  │
│[1 bit]│  [6 bits] │[5 bits]│[5 bits]│[3 bits]│[4 bits]│[1 bit]│ [7 bits]│
└──────┴───────────┴────────┴────────┴────────┴──────┴─────────┴─────────┘
```

**Immediate**: `{imm[12], imm[11], imm[10:5], imm[4:1], 0}` sign-extended to 32 bits
- Note: LSB (bit 0) is always 0, so offset is always even (2-byte aligned)

**Instructions**: BEQ, BNE

---

### U-Type (Upper Immediate)

Used for loading upper immediate values.

```
 31                             12 11     7 6       0
┌─────────────────────────────────┬────────┬─────────┐
│          imm[31:12]             │   rd   │ opcode  │
│          [20 bits]              │[5 bits]│ [7 bits]│
└─────────────────────────────────┴────────┴─────────┘
```

**Immediate**: `{imm[31:12], 12'b0}` - upper 20 bits, lower 12 bits zero

**Instructions**: LUI, AUIPC

---

### J-Type (Jump)

Used for unconditional jumps.

```
 31    30        21 20    19          12 11     7 6       0
┌──────┬───────────┬──────┬─────────────┬────────┬─────────┐
│imm[20]│ imm[10:1] │imm[11]│  imm[19:12] │   rd   │ opcode  │
│[1 bit]│ [10 bits] │[1 bit]│  [8 bits]   │[5 bits]│ [7 bits]│
└──────┴───────────┴──────┴─────────────┴────────┴─────────┘
```

**Immediate**: `{imm[20], imm[19:12], imm[11], imm[10:1], 0}` sign-extended to 32 bits
- Note: LSB (bit 0) is always 0, so offset is always even (2-byte aligned)

**Instructions**: JAL

---

## Instruction Encodings

### Opcode Table

| Opcode  | Format | Instruction Type |
|---------|--------|------------------|
| 0110011 | R      | Integer register-register |
| 0010011 | I      | Integer immediate |
| 0000011 | I      | Load |
| 0100011 | S      | Store |
| 1100011 | B      | Branch |
| 1101111 | J      | JAL |
| 1100111 | I      | JALR |
| 0110111 | U      | LUI |
| 0010111 | U      | AUIPC |

### Funct3 Table

| funct3 | R-Type | I-Type ALU | Branch | Load/Store | Shift |
|--------|--------|------------|--------|------------|-------|
| 000    | ADD/SUB| ADDI       | BEQ    | LB/SB      |       |
| 001    | SLL    | SLLI       | BNE    | LH/SH      |       |
| 010    | SLT    | SLTI       |        | LW/SW      |       |
| 011    | SLTU   | SLTIU      |        |            |       |
| 100    | XOR    | XORI       | BLT    | LBU        |       |
| 101    | SRL/SRA| SRLI/SRAI  | BGE    | LHU        |       |
| 110    | OR     | ORI        | BLTU   |            |       |
| 111    | AND    | ANDI       | BGEU   |            |       |

### Funct7 Table

| funct7  | Operation | Notes |
|---------|-----------|-------|
| 0000000 | ADD, SLL, SRL, AND, OR, XOR | Standard ops |
| 0100000 | SUB, SRA | Alternate ops |

---

## Arithmetic Instructions

### ADD - Add

**Format**: R-Type  
**Syntax**: `ADD rd, rs1, rs2`  
**Operation**: `rd = rs1 + rs2`  
**Encoding**: `0000000 rs2 rs1 000 rd 0110011`

**Description**: Adds the values in registers rs1 and rs2, stores result in rd.

**Example**:
```assembly
ADD x3, x1, x2      # x3 = x1 + x2
```

**Machine Code**: `0x002081B3` (if rs1=1, rs2=2, rd=3)

**ALU Operation**: 32-bit addition using full-adder chain

**Flags**: Sets N (negative), Z (zero), C (carry), V (overflow)

---

### SUB - Subtract

**Format**: R-Type  
**Syntax**: `SUB rd, rs1, rs2`  
**Operation**: `rd = rs1 - rs2`  
**Encoding**: `0100000 rs2 rs1 000 rd 0110011`

**Description**: Subtracts rs2 from rs1, stores result in rd.

**Example**:
```assembly
SUB x4, x2, x1      # x4 = x2 - x1
```

**Machine Code**: `0x40110233` (if rs1=2, rs2=1, rd=4)

**ALU Operation**: Two's complement subtraction (rs1 + ~rs2 + 1)

**Flags**: Sets N, Z, C, V

---

### ADDI - Add Immediate

**Format**: I-Type  
**Syntax**: `ADDI rd, rs1, imm`  
**Operation**: `rd = rs1 + sign_extend(imm)`  
**Encoding**: `imm[11:0] rs1 000 rd 0010011`

**Description**: Adds sign-extended 12-bit immediate to rs1, stores in rd.

**Example**:
```assembly
ADDI x1, x0, 5      # x1 = 0 + 5 = 5
ADDI x2, x1, -3     # x2 = x1 - 3
```

**Machine Code**: 
- `0x00500093` (ADDI x1, x0, 5)
- `0xFFD08113` (ADDI x2, x1, -3)

**Special Uses**:
- `ADDI rd, rs1, 0` → MV (move/copy register)
- `ADDI rd, x0, imm` → LI (load immediate)

---

## Logical Instructions

### AND - Logical AND

**Format**: R-Type  
**Syntax**: `AND rd, rs1, rs2`  
**Operation**: `rd = rs1 & rs2` (bitwise)  
**Encoding**: `0000000 rs2 rs1 111 rd 0110011`

**Description**: Performs bitwise AND on rs1 and rs2.

**Example**:
```assembly
AND x5, x3, x4      # x5 = x3 & x4
```

---

### ANDI - AND Immediate

**Format**: I-Type  
**Syntax**: `ANDI rd, rs1, imm`  
**Operation**: `rd = rs1 & sign_extend(imm)`  
**Encoding**: `imm[11:0] rs1 111 rd 0010011`

**Example**:
```assembly
ANDI x5, x3, 0xFF   # x5 = x3 & 0x000000FF (mask lower byte)
```

---

### OR - Logical OR

**Format**: R-Type  
**Syntax**: `OR rd, rs1, rs2`  
**Operation**: `rd = rs1 | rs2` (bitwise)  
**Encoding**: `0000000 rs2 rs1 110 rd 0110011`

**Description**: Performs bitwise OR on rs1 and rs2.

**Example**:
```assembly
OR x5, x3, x4       # x5 = x3 | x4
```

---

### ORI - OR Immediate

**Format**: I-Type  
**Syntax**: `ORI rd, rs1, imm`  
**Operation**: `rd = rs1 | sign_extend(imm)`  
**Encoding**: `imm[11:0] rs1 110 rd 0010011`

**Example**:
```assembly
ORI x5, x3, 0x100   # x5 = x3 | 0x00000100 (set bit 8)
```

---

### XOR - Logical XOR

**Format**: R-Type  
**Syntax**: `XOR rd, rs1, rs2`  
**Operation**: `rd = rs1 ^ rs2` (bitwise)  
**Encoding**: `0000000 rs2 rs1 100 rd 0110011`

**Description**: Performs bitwise XOR on rs1 and rs2.

**Example**:
```assembly
XOR x5, x3, x4      # x5 = x3 ^ x4
```

**Special Use**:
- `XOR rd, rs1, rs1` → Clear register (rd = 0)

---

### XORI - XOR Immediate

**Format**: I-Type  
**Syntax**: `XORI rd, rs1, imm`  
**Operation**: `rd = rs1 ^ sign_extend(imm)`  
**Encoding**: `imm[11:0] rs1 100 rd 0010011`

**Example**:
```assembly
XORI x5, x3, -1     # x5 = ~x3 (invert all bits)
```

---

## Shift Instructions

All shift amounts are taken from the lower 5 bits of rs2 (or shamt field), so valid range is 0-31.

### SLL - Shift Left Logical

**Format**: R-Type  
**Syntax**: `SLL rd, rs1, rs2`  
**Operation**: `rd = rs1 << (rs2[4:0])`  
**Encoding**: `0000000 rs2 rs1 001 rd 0110011`

**Description**: Shifts rs1 left by amount in rs2[4:0], fills with zeros.

**Example**:
```assembly
SLL x5, x3, x4      # x5 = x3 << (x4 & 0x1F)
```

**Implementation**: 5-stage barrel shifter

---

### SLLI - Shift Left Logical Immediate

**Format**: I-Type  
**Syntax**: `SLLI rd, rs1, shamt`  
**Operation**: `rd = rs1 << shamt`  
**Encoding**: `0000000 shamt rs1 001 rd 0010011`

**Description**: Shifts rs1 left by immediate amount (0-31).

**Example**:
```assembly
SLLI x5, x3, 4      # x5 = x3 << 4 (multiply by 16)
```

---

### SRL - Shift Right Logical

**Format**: R-Type  
**Syntax**: `SRL rd, rs1, rs2`  
**Operation**: `rd = rs1 >> (rs2[4:0])` (unsigned)  
**Encoding**: `0000000 rs2 rs1 101 rd 0110011`

**Description**: Shifts rs1 right by amount in rs2[4:0], fills with zeros.

**Example**:
```assembly
SRL x5, x3, x4      # x5 = x3 >> (x4 & 0x1F) (logical)
```

---

### SRLI - Shift Right Logical Immediate

**Format**: I-Type  
**Syntax**: `SRLI rd, rs1, shamt`  
**Operation**: `rd = rs1 >> shamt` (unsigned)  
**Encoding**: `0000000 shamt rs1 101 rd 0010011`

**Example**:
```assembly
SRLI x5, x3, 4      # x5 = x3 >> 4 (divide by 16, unsigned)
```

---

### SRA - Shift Right Arithmetic

**Format**: R-Type  
**Syntax**: `SRA rd, rs1, rs2`  
**Operation**: `rd = rs1 >>> (rs2[4:0])` (sign-extended)  
**Encoding**: `0100000 rs2 rs1 101 rd 0110011`

**Description**: Shifts rs1 right, fills with sign bit (arithmetic shift).

**Example**:
```assembly
SRA x5, x3, x4      # x5 = x3 >>> (x4 & 0x1F) (arithmetic)
```

---

### SRAI - Shift Right Arithmetic Immediate

**Format**: I-Type  
**Syntax**: `SRAI rd, rs1, shamt`  
**Operation**: `rd = rs1 >>> shamt` (sign-extended)  
**Encoding**: `0100000 shamt rs1 101 rd 0010011`

**Example**:
```assembly
SRAI x5, x3, 4      # x5 = x3 >>> 4 (divide by 16, signed)
```

---

## Memory Instructions

All memory operations must use **4-byte aligned addresses** for word access.

### LW - Load Word

**Format**: I-Type  
**Syntax**: `LW rd, offset(rs1)`  
**Operation**: `rd = memory[rs1 + sign_extend(offset)]`  
**Encoding**: `offset[11:0] rs1 010 rd 0000011`

**Description**: Loads 32-bit word from memory address (rs1 + offset).

**Example**:
```assembly
LW x4, 0(x5)        # x4 = mem[x5 + 0]
LW x6, 8(x5)        # x6 = mem[x5 + 8]
LW x7, -4(x5)       # x7 = mem[x5 - 4]
```

**Machine Code**:
- `0x0002A203` (LW x4, 0(x5))

**Memory Access**: Little-endian byte order

**Requirements**:
- Address must be 4-byte aligned (addr[1:0] = 0)
- Address must be in valid range (0x00000000-0x0001FFFF)

---

### SW - Store Word

**Format**: S-Type  
**Syntax**: `SW rs2, offset(rs1)`  
**Operation**: `memory[rs1 + sign_extend(offset)] = rs2`  
**Encoding**: `offset[11:5] rs2 rs1 010 offset[4:0] 0100011`

**Description**: Stores 32-bit word from rs2 to memory address (rs1 + offset).

**Example**:
```assembly
SW x3, 0(x5)        # mem[x5 + 0] = x3
SW x4, 8(x5)        # mem[x5 + 8] = x4
SW x6, -4(x5)       # mem[x5 - 4] = x6
```

**Machine Code**:
- `0x0032A023` (SW x3, 0(x5))

**Memory Access**: Little-endian byte order

**Requirements**:
- Address must be 4-byte aligned
- Address must be in valid range

---

## Branch Instructions

All branch offsets are **PC-relative** and must be **2-byte aligned** (even).

### BEQ - Branch if Equal

**Format**: B-Type  
**Syntax**: `BEQ rs1, rs2, offset`  
**Operation**: `if (rs1 == rs2) PC = PC + sign_extend(offset)`  
**Encoding**: `offset[12|10:5] rs2 rs1 000 offset[4:1|11] 1100011`

**Description**: Branches to PC + offset if rs1 equals rs2.

**Example**:
```assembly
BEQ x3, x4, label   # if (x3 == x4) goto label
BEQ x0, x0, loop    # Unconditional branch (always taken)
```

**Machine Code**:
- `0x00418463` (BEQ x3, x4, 8) - branch forward 8 bytes

**Branch Calculation**:
1. Compare rs1 and rs2 using ALU (SUB operation)
2. If Z flag set (result == 0), branch taken
3. Target = PC + sign_extend(offset)

**Offset Range**: -4096 to +4094 bytes (±2KB)

---

### BNE - Branch if Not Equal

**Format**: B-Type  
**Syntax**: `BNE rs1, rs2, offset`  
**Operation**: `if (rs1 != rs2) PC = PC + sign_extend(offset)`  
**Encoding**: `offset[12|10:5] rs2 rs1 001 offset[4:1|11] 1100011`

**Description**: Branches to PC + offset if rs1 not equal to rs2.

**Example**:
```assembly
BNE x3, x4, label   # if (x3 != x4) goto label
```

**Branch Calculation**:
1. Compare rs1 and rs2 using ALU (SUB operation)
2. If Z flag clear (result != 0), branch taken
3. Target = PC + sign_extend(offset)

---

## Jump Instructions

### JAL - Jump and Link

**Format**: J-Type  
**Syntax**: `JAL rd, offset`  
**Operation**: `rd = PC + 4; PC = PC + sign_extend(offset)`  
**Encoding**: `offset[20|10:1|11|19:12] rd 1101111`

**Description**: Jumps to PC + offset, stores return address (PC+4) in rd.

**Example**:
```assembly
JAL x1, function    # Call function, return address in x1 (ra)
JAL x0, label       # Jump without saving return address
```

**Machine Code**:
- `0x010000EF` (JAL x1, 16) - jump forward 16 bytes

**Usage**:
- Function calls: `JAL x1, func` (save return address)
- Unconditional jumps: `JAL x0, label` (discard return address)

**Offset Range**: -1MB to +1MB

---

### JALR - Jump and Link Register

**Format**: I-Type  
**Syntax**: `JALR rd, offset(rs1)`  
**Operation**: `rd = PC + 4; PC = (rs1 + sign_extend(offset)) & ~1`  
**Encoding**: `offset[11:0] rs1 000 rd 1100111`

**Description**: Jumps to (rs1 + offset), stores return address in rd. LSB is cleared.

**Example**:
```assembly
JALR x0, 0(x1)      # Return from function (PC = x1)
JALR x1, 0(x5)      # Indirect call through x5
```

**Machine Code**:
- `0x00008067` (JALR x0, 0(x1)) - return instruction

**Usage**:
- Function return: `JALR x0, 0(x1)` or `RET` pseudo-instruction
- Indirect jumps: `JALR x0, 0(rs1)`
- Indirect calls: `JALR x1, 0(rs1)`

**Note**: LSB of target is always cleared to ensure alignment

---

## Upper Immediate Instructions

### LUI - Load Upper Immediate

**Format**: U-Type  
**Syntax**: `LUI rd, imm`  
**Operation**: `rd = imm << 12` (upper 20 bits)  
**Encoding**: `imm[31:12] rd 0110111`

**Description**: Loads 20-bit immediate into upper 20 bits of rd, lower 12 bits set to 0.

**Example**:
```assembly
LUI x5, 0x12345     # x5 = 0x12345000
```

**Machine Code**:
- `0x123452B7` (LUI x5, 0x12345)

**Usage**:
- Load 32-bit constants:
  ```assembly
  LUI x5, 0x12345   # x5 = 0x12345000
  ADDI x5, x5, 0x678 # x5 = 0x12345678
  ```

---

### AUIPC - Add Upper Immediate to PC

**Format**: U-Type  
**Syntax**: `AUIPC rd, imm`  
**Operation**: `rd = PC + (imm << 12)`  
**Encoding**: `imm[31:12] rd 0010111`

**Description**: Adds 20-bit immediate (shifted left 12) to PC, stores in rd.

**Example**:
```assembly
AUIPC x5, 0x1       # x5 = PC + 0x1000
```

**Machine Code**:
- `0x00001297` (AUIPC x5, 0x1)

**Usage**:
- PC-relative addressing:
  ```assembly
  AUIPC x5, 0x1     # x5 = PC + 0x1000
  LW x6, 0x234(x5)  # Load from PC + 0x1234
  ```
- Position-independent code (PIC)

---

## Edge Cases and Special Behavior

### x0 Register Behavior

**Writing to x0**: All writes are **ignored**. x0 always reads as 0.

```assembly
ADDI x0, x0, 100    # No effect, x0 remains 0
ADD x0, x1, x2      # No effect, x0 remains 0
```

**Reading from x0**: Always returns 0.

```assembly
ADD x3, x0, x5      # x3 = 0 + x5 = x5 (move)
ADDI x4, x0, 10     # x4 = 0 + 10 = 10 (load immediate)
```

---

### Arithmetic Overflow/Underflow

RISC-V **does not trap on overflow**. Results wrap around using two's complement arithmetic.

**Overflow Example**:
```assembly
LUI x1, 0x7FFFF     # x1 = 0x7FFFF000
ADDI x1, x1, 0x7FF  # x1 = 0x7FFFFFFF (max positive)
ADDI x2, x1, 1      # x2 = 0x80000000 (wraps to min negative)
```

**Underflow Example**:
```assembly
LUI x1, 0x80000     # x1 = 0x80000000 (min negative)
ADDI x2, x1, -1     # x2 = 0x7FFFFFFF (wraps to max positive)
```

**Detection**: Use ALU flags (V flag) to detect overflow if needed.

---

### Branch Offset Calculation

Branch offsets are **relative to current PC**, not next PC.

**Example**:
```assembly
0x00: ADDI x1, x0, 5
0x04: BEQ x1, x2, 8      # If equal, branch to 0x04 + 8 = 0x0C
0x08: ADDI x3, x0, 1     # Skipped if branch taken
0x0C: ADDI x4, x0, 2     # Branch target
```

**Forward Branch**: Positive offset
**Backward Branch** (loops): Negative offset

```assembly
loop:
    ADDI x1, x1, 1
    BNE x1, x2, loop     # Branch backward to loop
```

---

### Jump Offset Calculation

Jump offsets are **relative to current PC**.

**Example**:
```assembly
0x00: JAL x1, 16         # Jump to 0x00 + 16 = 0x10, x1 = 0x04
0x04: ADDI x2, x0, 1     # Skipped
...
0x10: ADDI x3, x0, 2     # Jump target
```

---

### JALR Alignment

JALR **clears the LSB** of the target address to ensure alignment.

**Example**:
```assembly
LUI x5, 0x1000          # x5 = 0x10000000
ADDI x5, x5, 0x123      # x5 = 0x10000123 (odd address)
JALR x0, 0(x5)          # PC = 0x10000122 (LSB cleared)
```

---

### Memory Alignment

**Word Access** (LW/SW): Address must be 4-byte aligned.

**Valid Addresses**: 0x0, 0x4, 0x8, 0xC, ...  
**Invalid Addresses**: 0x1, 0x2, 0x3, 0x5, ... (causes error)

**Example**:
```assembly
LUI x5, 0x10            # x5 = 0x10000
LW x4, 0(x5)            # OK: 0x10000 is aligned
LW x4, 1(x5)            # ERROR: 0x10001 is not aligned
LW x4, 4(x5)            # OK: 0x10004 is aligned
```

---

### Sign Extension

**I-Type, S-Type, B-Type**: 12-bit immediates are **sign-extended** to 32 bits.

**Positive Immediate** (bit 11 = 0):
```
imm = 0x123 (0001 0010 0011)
→ 0x00000123 (0000...0001 0010 0011)
```

**Negative Immediate** (bit 11 = 1):
```
imm = 0xFFF (1111 1111 1111) = -1
→ 0xFFFFFFFF (1111...1111 1111 1111)
```

**U-Type**: 20-bit immediates are **zero-extended** in lower 12 bits.

```
LUI x5, 0x12345
→ x5 = 0x12345000 (not sign-extended)
```

---

### Invalid Instructions

If an instruction has an **unknown opcode** or **invalid encoding**, behavior is:

1. Decoder returns `mnemonic = "UNKNOWN"`
2. CPU halts with `halt_reason = "Invalid instruction"`
3. No state changes occur

**Example**:
```
0xFFFFFFFF → Likely invalid opcode → CPU halts
```

---

## Instruction Encoding Examples

### Example 1: ADDI x1, x0, 5

```
Instruction: ADDI x1, x0, 5
Format: I-Type
Fields:
  - imm[11:0] = 5 = 0x005
  - rs1 = 0
  - funct3 = 000 (ADDI)
  - rd = 1
  - opcode = 0010011

Encoding:
  imm[11:0]  rs1 funct3 rd  opcode
  000000000101 00000 000 00001 0010011
  
Machine Code: 0x00500093
```

---

### Example 2: ADD x3, x1, x2

```
Instruction: ADD x3, x1, x2
Format: R-Type
Fields:
  - funct7 = 0000000 (ADD)
  - rs2 = 2
  - rs1 = 1
  - funct3 = 000 (ADD)
  - rd = 3
  - opcode = 0110011

Encoding:
  funct7   rs2  rs1 funct3 rd  opcode
  0000000 00010 00001 000 00011 0110011
  
Machine Code: 0x002081B3
```

---

### Example 3: LW x4, 0(x5)

```
Instruction: LW x4, 0(x5)
Format: I-Type
Fields:
  - imm[11:0] = 0
  - rs1 = 5
  - funct3 = 010 (LW)
  - rd = 4
  - opcode = 0000011

Encoding:
  imm[11:0]    rs1 funct3 rd  opcode
  000000000000 00101 010 00100 0000011
  
Machine Code: 0x0002A203
```

---

### Example 4: BEQ x3, x4, 8

```
Instruction: BEQ x3, x4, 8 (branch forward 8 bytes)
Format: B-Type
Fields:
  - offset = 8 = 0b0000 0000 1000
  - imm[12] = 0, imm[11] = 0, imm[10:5] = 000010, imm[4:1] = 0000
  - rs2 = 4
  - rs1 = 3
  - funct3 = 000 (BEQ)
  - opcode = 1100011

Encoding:
  imm[12] imm[10:5] rs2  rs1 funct3 imm[4:1] imm[11] opcode
  0       000010    00100 00011 000  0000    0      1100011
  
Machine Code: 0x00418463
```

---

### Example 5: JAL x1, 16

```
Instruction: JAL x1, 16 (jump forward 16 bytes)
Format: J-Type
Fields:
  - offset = 16 = 0b0000 0000 0001 0000
  - imm[20] = 0, imm[19:12] = 00000000, imm[11] = 0, imm[10:1] = 0000010000
  - rd = 1
  - opcode = 1101111

Encoding:
  imm[20] imm[10:1]  imm[11] imm[19:12] rd  opcode
  0       0000001000 0       00000000   00001 1101111
  
Machine Code: 0x010000EF
```

---

### Example 6: LUI x5, 0x12345

```
Instruction: LUI x5, 0x12345
Format: U-Type
Fields:
  - imm[31:12] = 0x12345
  - rd = 5
  - opcode = 0110111

Encoding:
  imm[31:12]            rd  opcode
  00010010001101000101 00101 0110111
  
Machine Code: 0x123452B7
```

---

## Pseudo-Instructions

RISC-V assemblers support **pseudo-instructions** that map to real instructions:

| Pseudo | Real Instruction | Description |
|--------|------------------|-------------|
| `NOP` | `ADDI x0, x0, 0` | No operation |
| `MV rd, rs` | `ADDI rd, rs, 0` | Copy register |
| `LI rd, imm` | `ADDI rd, x0, imm` | Load immediate (small) |
| `NOT rd, rs` | `XORI rd, rs, -1` | Bitwise NOT |
| `NEG rd, rs` | `SUB rd, x0, rs` | Negate |
| `J offset` | `JAL x0, offset` | Jump |
| `JR rs` | `JALR x0, 0(rs)` | Jump register |
| `RET` | `JALR x0, 0(x1)` | Return from function |
| `CALL offset` | `JAL x1, offset` | Call function |

---

## Summary

RISCSim implements **23 core RISC-V instructions** with full bit-accurate behavior:

✅ **Arithmetic**: ADD, SUB, ADDI  
✅ **Logical**: AND, OR, XOR, ANDI, ORI, XORI  
✅ **Shifts**: SLL, SRL, SRA, SLLI, SRLI, SRAI  
✅ **Memory**: LW, SW (word-aligned)  
✅ **Branches**: BEQ, BNE (PC-relative)  
✅ **Jumps**: JAL, JALR (with return address)  
✅ **Upper Imm**: LUI, AUIPC  

All instructions follow RISC-V specifications with proper edge case handling:
- x0 always reads as zero
- Overflow wraps around (no traps)
- Memory must be word-aligned
- Branch/jump offsets are 2-byte aligned
- Sign extension for I/S/B-type immediates

For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md).  
For usage examples, see [USAGE.md](USAGE.md).
