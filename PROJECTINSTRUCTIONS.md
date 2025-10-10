# The Midterm Alternative Project: RISC‑V Numeric Ops Simulator

## 📋 Overview

Build a small, well‑tested numeric operations simulator that:

- ✅ converts integers to/from **two's‑complement** (multiple bit‑widths),
- ✅ simulates **RISC‑V M extension** integer multiply/divide instructions, and
- ✅ implements **IEEE‑754 single‑precision (float32)** representation + add, subtract, multiply.
- ⭐ **Extra credit**: support double‑precision (float64) and additional rounding modes.

**Your implementation must be in a high‑level language** (Python, Java, C/C++, Rust, Go, etc.), include clear step‑by‑step traces for multi‑step algorithms, and ship with a comprehensive unit test suite. The code should be **structured so it can be merged later** into a larger RISC‑V CPU simulator (unless your semester project is Verilog/Logisim Evo).

## 🎯 Learning Goals

1. Master **two's‑complement encoding/decoding** across common widths.
2. Understand and implement the semantics of **RISC‑V M** (integer multiply/divide) and **F** (float32 ops subset).
3. Manipulate **IEEE‑754 bitfields**, special values, normalization and rounding.
4. Design **traceable arithmetic algorithms** with correctness tests and corner‑case handling (overflow/underflow).

## 📦 Scope & Required Features

> **Note**: Function signatures, suggestions, and architectures below are only samples, but recommended.

### 1️⃣ Two's‑Complement Toolkit **(required)**

**Implement for width 32 only (RV32):**

```python
encode_twos_complement(value: int) -> {bin, hex, overflow_flag}  # fixed XLEN=32
decode_twos_complement(bits: str|int) -> {value: int}
```

**Overflow rule:** flag if value is outside the signed range `[-2^(width-1), 2^(width-1)-1]` (see FCSR later).

**Provide helpers** for sign‑extend / zero‑extend.

**Sample expectations (width=32):**

- `+13` → bin `00000000_00000000_00000000_00001101`; hex `0x0000000D`; overflow=0
- `-13` → bin `11111111_11111111_11111111_11110011`; hex `0xFFFFFFF3`; overflow=0
- `2^31` → overflow=1

### 2️⃣ Integer Addition/Subtraction (RV32I subset) **(required)**
Implement **ADD, SUB** (optionally ADDI for CLI convenience) on 32‑bit two's‑complement bit vectors using your ALU (**no host +/-**).

**Surface ALU flags:**
- **N** (negative)
- **Z** (zero)
- **C** (carry out of MSB in the adder)
- **V** (signed overflow)

**Overflow (V) rules (two's‑complement):**

- **ADD**: `V=1` iff `sign(rs1) == sign(rs2)` and `sign(result) != sign(rs1)`.
- **SUB**: implement as `rs1 + (~rs2 + 1)` and apply the ADD rule; equivalently, `V=1` iff `sign(rs1) != sign(rs2)` and `sign(result) != sign(rs1)`.

**Carry (C) convention:** carry‑out of the adder's Most Significant Bit (MSB). For subtraction via `rs1 + (~rs2 + 1)`, `C=1` implies no borrow.

**Edge expectations:**

- `0x7FFFFFFF + 0x00000001` → `0x80000000`; **V=1; C=0; N=1; Z=0**.
- `0x80000000 - 0x00000001` → `0x7FFFFFFF`; **V=1; C=1; N=0; Z=0**.
- `-1 + -1` → `-2`; **V=0; C=1; N=1; Z=0**.

**Traces** should show operand bits and final flags; per‑bit carry propagation table is optional for ADD/SUB.

### 3️⃣ RISC‑V Integer Multiply/Divide (M extension) **(required)**
Implement the following instructions (assume **RV32** for concreteness):

**Multiply family:**
- **Required:** `MUL` (low 32 bits)
- **Optional:** `MULH` (signed×signed high 32), `MULHU` (unsigned×unsigned high 32), `MULHSU` (signed×unsigned high 32)

**Divide/remainder family:**
- **Required:** `DIV`
- **Optional:** `DIVU`, `REM`, `REMU` with RISC‑V edge‑case semantics:
  - `DIV x / 0` → quotient = `-1` (`0xFFFFFFFF`), remainder = dividend.
  - `DIVU x / 0` → quotient = `0xFFFFFFFF`, remainder = dividend.
  - `DIV INT_MIN / -1` → quotient = `INT_MIN` (`0x80000000`), remainder = 0.
  - Quotient truncates toward zero; `REM` has the same sign as dividend.

**Overflow flagging for grading visibility:** even though RISC‑V M itself truncates, also compute an overflow flag for `MUL` if the true 64‑bit product is not representable as a signed 32‑bit result; and for `DIV` if the true mathematical quotient is outside signed 32‑bit (only possible at the `INT_MIN/−1` edge).

**Algorithm & Trace requirement (multi‑step):**

- For **MUL\***: implement shift‑add; trace each step (accumulator, multiplier, partial product, carry, step #). ⭐ _(Extra-credit: Booth's algorithm)_
- For **DIV\***: implement restoring or non‑restoring division; trace each iteration (remainder, quotient, subtract/restore decisions).

**Example unit expectations (RV32):**

- `MUL 12345678 * -87654321` → rd = `0xD91D0712` (low 32); overflow=1
- `MULH 12345678 * -87654321` → rd = `0xFFFC27C9`
- `DIV -7 / 3` → q = `-2` (`0xFFFFFFFE`); r = `-1` (`0xFFFFFFFF`)
- `DIVU 0x80000000 / 3` → q = `0x2AAAAAAA`; r = `0x00000002`

### 4️⃣ IEEE‑754 Float32 (F subset) **(required)**
Implement bit‑level encode/decode and arithmetic:

- `pack_f32(value: decimal)` → 32‑bit pattern `(s|exp|frac)` and `unpack_f32(bits)` → value.
- `fadd_f32(a,b)`, `fsub_f32(a,b)`, `fmul_f32(a,b)` that operate via IEEE‑754 steps (align, add/sub, normalize, round, repack). Use default rounding **RoundTiesToEven**.
- **Special values:** ±0, ±∞, NaN (signaling/quiet may be treated as NaN), _Optional: subnormals_.

**Flags:** (see FCSR later)
- **overflow** (result exponent overflows to ±∞ after rounding),
- **underflow** (final rounded result is subnormal or zero because magnitude < 2⁻¹²⁶),
- **invalid** (e.g., ∞−∞, 0·∞, NaN operand),
- **divide‑by‑zero** (not used here unless you optionally support division).

**Float32 sample expectations:**

- `1.5 + 2.25 = 3.75` → `0x40700000`
- `0.1 + 0.2 ≈ 0.3000000119` → `0x3E99999A` (ties‑to‑even)
- `1e38 * 10` → `+∞`; overflow=1
- `1e-38 * 1e-2` → subnormal; underflow=1

## ⭐ Extra credit (up to +10%)

- Add **float64 (D extension subset)**: pack/unpack + add/sub/mul with the same flags.
- Implement **selectable rounding modes** (RNE, RTZ, RDN, RUP).

## 🔧 Hardware‑Style Datapath & Control Requirements

To strengthen computer architecture understanding, model your simulator as a tiny **multi‑cycle datapath** with explicit bit‑level components.

⚠️ **All values must be carried as bit vectors** (arrays/lists of 0/1 or booleans). **Do not rely on host‑language integers** for arithmetic or shifting inside the implementation modules.

> **Note:** You don't have to implement the instructions (control) before the implementation of the whole CPU (which is introduced in Chapter 4).

### Required components

#### 📝 Registers
- `Reg(width)` with synchronous load and clear.
- **Register File** with 32 entries of width 32 (RV32). Implement `x0` hard‑wired to 0 (writes ignored). _(After chapter 4: expose read ports rs1, rs2, and one write port rd with write‑enable.)_
- **32 FP registers:** `f0` to `f31` (32-bit for single-precision/F extension, 64-bit for double-precision/D extension)
- **FCSR (Floating-Point Control and Status Register):**
  - `frm` (bits 7–5): Rounding mode (e.g., RNE, RTZ, RDN, RUP)
  - `fflags` (bits 4–0): Exception flags (e.g., overflow, underflow, invalid operation)

#### ➕ ALU
- Operates on **bit vectors**; implement via **full‑adder chains** and logic gates (ripple‑carry is fine).
- **Ops:** ADD, SUB, SLL, SRL, SRA (shifts implemented by your shifter module below). _(You can add these later: AND, OR, XOR, NOT, SLT/SLTU (compare via subtraction)._
- **Outputs:** result, flags **N** (negative), **Z** (zero), **C** (carry), **V** (signed overflow).

#### ↔️ Shifter
- SLL/SRL/SRA realized **without `<<`/`>>`**. Use **barrel‑shifter** or iterative shift‑register design. For SRA, replicate the sign bit.

#### ✖️➗ Multiply/Divide Unit (MDU) _(with internal registers as needed)_
- **Multiplier:** shift‑add or Booth; maintain accumulator, multiplicand, multiplier, and count registers.
- **Divider:** restoring or non‑restoring; maintain remainder, quotient, divisor, and count.

#### 🔢 Float Unit (FPU, float32)
- Bit‑level pack/unpack `(sign|exponent|fraction)`, alignment shifter, adder/subtracter on extended significands, normalization & RoundTiesToEven.
- **Status flags:** overflow, underflow, invalid, inexact (optional), divide_by_zero (if you add division).

#### 🎮 Control Unit (FSM) _(For your reference only; not required for this project)_
A simple **finite‑state machine** sequences multi‑cycle operations. Example states:
- **FPU:** IDLE → ALIGN → OP → NORMALIZE → ROUND → WRITEBACK
- **Divider:** IDLE → TESTBIT → SUB/RESTORE → SHIFT → WRITEBACK
- **Multiplier:** IDLE → ADD/SHIFT (×N cycles) → WRITEBACK

Expose control signals in traces: `alu_op`, `rf_we`, `rf_waddr`, `src_a_sel`, `src_b_sel`, `sh_op`, `md_start`, `md_busy`, `md_done`, `fpu_state`, `round_mode`.

### Bit‑accurate datapath representation

Represent data as **bit arrays**; provide utilities for:
- `from_decimal_string(s)` → bits and `to_decimal_string(bits)` using your own algorithms (e.g., double‑dabble for bin↔dec, but you can also use decimal numbers instead of strings),
- `from_hex_string`/`to_hex_string` via manual nibble lookup tables (**no `hex()`/`format()`**),
- sign/zero‑extend, two's‑complement negate (invert+add‑one using your adder).

### 📊 Traces (cycle‑by‑cycle)

- For **traced unit tests**, print out adequate information (snapshot at the start, at each iteration, and at the finish) to monitor the status of the components of the CPU (ALU, MDU, FPU, including internal/external registers and flags used/set).
- For **ADD/SUB**, if implemented as single‑cycle ALU ops, a single consolidated trace row is acceptable (include operands, result, and flags).

### 🔌 Suggested "hardware" Interfaces _(merge‑friendly to the semester project)_

```python
alu(bitsA, bitsB, op) -> {result, N, Z, C, V}
shifter(bits, shamt, op) -> bits
mdu_mul(op, rs1_bits, rs2_bits) -> {rd_bits, hi_bits?, flags, trace}
mdu_div(op, rs1_bits, rs2_bits) -> {q_bits, r_bits, flags, trace}
fpu_add/sub/mul(a_bits, b_bits) -> {res_bits, flags, trace}
```

## 🧪 Unit Tests (minimum set)

Provide a `tests/` folder with automated tests. Each test should assert **(a)** decimal results, **(b)** hex patterns, and **(c)** flags.

### Two's‑Complement

- Encode/Decode for **32‑bit only**; include boundary cases: `{-2^31, -1, -13, -7, 0, 13, 2^31-1}` and verify overflow for out‑of‑range values.

### RV32I Add/Sub

- `ADD 0x7FFFFFFF + 1` → `0x80000000`; V=1, C=0, N=1, Z=0
- `SUB 0x80000000 - 1` → `0x7FFFFFFF`; V=1, C=1, N=0, Z=0
- `ADD -1 + -1` → `-2`; V=0, C=1, N=1, Z=0
- `ADD 13 + -13` → `0`; V=0, C=1, N=0, Z=1

### RV32M

- Include the cases listed earlier (MUL/MULH/MULHU/MULHSU; DIV/DIVU/REM/REMU; divide‑by‑zero; INT_MIN/−1).
- Verify **cycle traces** match expected intermediate values for at least one multiply and one divide (e.g., accumulator/remainder evolution).

### Float32

- Pack/unpack known values (e.g., `3.75` → `0x40700000`), rounding edge cases (`0.1+0.2`), overflow/underflow, NaN/∞ propagation, sign of zero.

### Compliance tests

> **Note:** You may use host‑language numerics in tests only to compute expected values; **not in implementation**.

## 📦 Deliverables

1. **Make an Organization (org) on GitHub** for your individual or group projects for CPSC440, which includes your group members (if it is a group project for you), as well as my GitHub account **"2404s21"**.
   - Please make sure all of your group members have adequate (at least **"write"**) access to all repos of your org.
   - Please make sure **"2404s21"** can read all your org's repos.

2. **For group projects:** each group member should make commits related to her/his contributing area. One project leader can be selected for each project to coordinate code reviews, adjudicate merge conflicts / pull requests, etc.
   - ⚠️ This is important, as in principal, **all group members get the same points** for each project worked on together: if one member introduced a bug that's not found by code review before the deadline, **the whole team takes the hit.**

3. **Make a GitHub Repository** in your Organization for this project. Submit the repo's URL which includes the following items:
   - **Code** with README covering build/run instructions.
   - **AI usage disclosure:** `AI_USAGE.md` summarizing tools (e.g., ChatGPT, Copilot), prompts, where used, and `ai_report.json` with:
```json
{"total_lines":1234, "ai_tagged_lines":210, "percent":17.0, "tools":["ChatGPT"], "method":"count markers"}
```

   - Mark AI‑assisted regions with **AI-BEGIN/AI-END** comments so a simple counter script can verify.

## 🚫 Constraints & Style

**No built‑in numeric functions or operators in implementation modules.** Implement your own:
- ❌ Addition/subtraction via half/full adders (**no +/-**).
- ❌ Shifts/rotates via your shifter (**no <</>>**).
- ❌ Multiplication/division via MDU algorithms (**no \*/\//\%/divmod**).
- ❌ Base conversions (bin/hex/dec) with your own code (**no `int(..., base)`, `bin()`, `hex()`, `format()`, `std::stoi`, etc.**).
- ❌ Bit extraction/packing without host bitfields helpers.

**Data = bits.** Internals must operate on **explicit bit vectors**; host integers may be used only in tests to compute reference values (**not in implementation**).

### Language‑specific forbidden examples:

- **Python:** forbid `+ - * / % << >> **`, `int(.., base)`, `bin`, `hex`, `format`, f‑string numeric formatting, float math in impl. _(String concatenation is OK.)_
- **C/C++:** forbid `+ - * / % << >>` on numeric types in impl; no `<bitset>`, `std::stoi`, `std::bitset` helpers.
- **Java/Rust/Go:** analogous prohibitions on numeric ops and base‑conversion helpers in impl.

### ✅ Allowed:
- Boolean logic on single bits (`and`/`or`/`xor`/`not`)
- Array indexing/slicing
- Simple control flow
- String ops for printing

**Keep modules small, pure, and testable.** Pretty‑print binary with `_` nibble/byte grouping and zero‑padded hex built by your code.

## 📅 Suggested Timeline

- **T0 (now):** pick language, scaffold repo, define printing utilities.
- **T0 + 3 days:** finish two's‑complement + tests.
- **T0 + 1 week:** complete RV32M ops + traces.
- **T0 + 2 weeks:** finish float32 pack/unpack + arithmetic + flags; finalize tests.

## 🔗 Merge Guidance (for later CPU project)

- Keep a **NumericCore API** that exposes pure functions for each instruction.
- Use a simple `State{regs[32], fregs[32], flags}` structure so a CPU interpreter can wire them in.
- **Avoid global state**; make everything deterministic and side‑effect free.

## 🎓 Academic Integrity

Discuss high‑level ideas with peers, but **all code and tests must be your own**. Cite any external references in `README.md`.