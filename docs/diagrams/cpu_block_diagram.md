# RISCSim CPU Block Diagram

This document provides ASCII art diagrams of the RISCSim CPU architecture.

## High-Level CPU Block Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          RISCSim CPU Architecture                                │
│                         Single-Cycle RISC-V Processor                           │
└─────────────────────────────────────────────────────────────────────────────────┘

                                ┌─────────────────┐
                                │   Program       │
                                │   Counter (PC)  │
                                │   [32 bits]     │
                                └────────┬────────┘
                                         │
                                         ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                              FETCH STAGE                                        │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────────────────────┐                                 │
│  │     Instruction Memory (I-Memory)        │                                 │
│  │     Base Address: 0x00000000             │                                 │
│  │     Size: 64KB                           │                                 │
│  │     - Read instruction at PC             │                                 │
│  │     - Word-aligned access                │                                 │
│  └──────────────────────────────────────────┘                                 │
│                    │                                                           │
│                    ▼                                                           │
│           [32-bit instruction]                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                            DECODE STAGE                                         │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────────────────────┐                                 │
│  │     Instruction Decoder                  │                                 │
│  │     - Extract opcode, funct3, funct7     │                                 │
│  │     - Extract rd, rs1, rs2               │                                 │
│  │     - Extract immediate (sign-extended)  │                                 │
│  │     - Identify instruction type          │                                 │
│  │     - Generate mnemonic                  │                                 │
│  └──────────────────────────────────────────┘                                 │
│                    │                                                           │
│                    ▼                                                           │
│  ┌──────────────────────────────────────────┐                                 │
│  │     Control Signal Generator             │                                 │
│  │     - reg_write, mem_read, mem_write     │                                 │
│  │     - alu_op, alu_src_a, alu_src_b       │                                 │
│  │     - branch, jump, result_src, pc_src   │                                 │
│  └──────────────────────────────────────────┘                                 │
│            │                                                                   │
│            │ [control signals]                                                 │
│            ▼                                                                   │
└────────────────────────────────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                            EXECUTE STAGE                                        │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────┐           ┌────────────────────────┐            │
│  │   Register File          │           │    Immediate           │            │
│  │   - 32 registers (x0-x31)│           │    (sign-extended)     │            │
│  │   - x0 = 0 (hardwired)   │           └────────────────────────┘            │
│  │   - Read rs1, rs2        │                      │                          │
│  └──────────────────────────┘                      │                          │
│       │             │                               │                          │
│       │ rs1_data    │ rs2_data                      │                          │
│       ▼             ▼                               ▼                          │
│  ┌─────────┐   ┌─────────┐                    ┌─────────┐                    │
│  │  MUX    │   │  MUX    │                    │  MUX    │                    │
│  │ alu_src │   │         │                    │ alu_src │                    │
│  │    _a   │   │         │                    │    _b   │                    │
│  │(rs1/PC) │   │         │                    │(rs2/imm)│                    │
│  └─────────┘   └─────────┘                    └─────────┘                    │
│       │             │                               │                          │
│       └─────────────┼───────────────────────────────┘                          │
│                     ▼                                                          │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │                    ALU / Shifter / MDU / FPU               │               │
│  │                                                            │               │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │               │
│  │  │     ALU      │  │   Shifter    │  │     MDU      │   │               │
│  │  │  - ADD/SUB   │  │  - SLL       │  │  - MUL       │   │               │
│  │  │  - AND/OR    │  │  - SRL       │  │  - DIV       │   │               │
│  │  │  - XOR       │  │  - SRA       │  │  - REM       │   │               │
│  │  │  - Flags:    │  │  - 5-stage   │  │  - Shift-add │   │               │
│  │  │    N,Z,C,V   │  │    barrel    │  │    algorithm │   │               │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │               │
│  │                                                            │               │
│  │  ┌──────────────┐                                         │               │
│  │  │     FPU      │                                         │               │
│  │  │  - FADD      │                                         │               │
│  │  │  - FSUB      │                                         │               │
│  │  │  - FMUL      │                                         │               │
│  │  │  - IEEE-754  │                                         │               │
│  │  └──────────────┘                                         │               │
│  │                                                            │               │
│  └────────────────────────────────────────────────────────────┘               │
│                              │                                                 │
│                              ▼                                                 │
│                    [ALU result - 32 bits]                                     │
│                              │                                                 │
└──────────────────────────────┼─────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────┼─────────────────────────────────────────────────┐
│                            MEMORY STAGE                                         │
├──────────────────────────────┼─────────────────────────────────────────────────┤
│                              │                                                  │
│                              ▼                                                  │
│  ┌──────────────────────────────────────────┐                                 │
│  │     Data Memory (D-Memory)               │                                 │
│  │     Base Address: 0x00010000             │                                 │
│  │     Size: 64KB                           │                                 │
│  │     - Address from ALU result            │                                 │
│  │     - Write data from rs2                │                                 │
│  │     - LW: Read word                      │                                 │
│  │     - SW: Write word                     │                                 │
│  │     - Word-aligned access required       │                                 │
│  └──────────────────────────────────────────┘                                 │
│                    │                                                           │
│                    ▼                                                           │
│           [Memory data - 32 bits]                                             │
│             (if mem_read = 1)                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                          WRITEBACK STAGE                                        │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────┐                                  │
│  │     Writeback Multiplexer (Result Src)  │                                  │
│  │                                          │                                  │
│  │     Select based on result_src:         │                                  │
│  │     0: ALU result                        │                                  │
│  │     1: Memory data (LW)                  │                                  │
│  │     2: PC + 4 (JAL/JALR)                 │                                  │
│  └─────────────────────────────────────────┘                                  │
│                    │                                                           │
│                    ▼                                                           │
│           [Writeback data - 32 bits]                                          │
│                    │                                                           │
│                    ▼                                                           │
│  ┌──────────────────────────────────────────┐                                 │
│  │     Register File Write                  │                                 │
│  │     - Write to rd if reg_write = 1       │                                 │
│  │     - Ignore writes to x0 (hardwired 0)  │                                 │
│  └──────────────────────────────────────────┘                                 │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│                          PC UPDATE LOGIC                                        │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────┐                                  │
│  │     PC Update Multiplexer (PC Src)      │                                  │
│  │                                          │                                  │
│  │     Select next PC based on pc_src:     │                                  │
│  │     0: PC + 4 (sequential)               │                                  │
│  │     1: PC + imm_b (branch taken)         │                                  │
│  │     2: jump_target (JAL/JALR)            │                                  │
│  │                                          │                                  │
│  │     Branch decision:                     │                                  │
│  │     - BEQ: branch if Z flag set          │                                  │
│  │     - BNE: branch if Z flag clear        │                                  │
│  └─────────────────────────────────────────┘                                  │
│                    │                                                           │
│                    ▼                                                           │
│              [Next PC - 32 bits]                                              │
│                    │                                                           │
│                    └───────────────────────────▶ (back to PC register)        │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Component Interconnection Details

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                     Component-Level Connections                                 │
└────────────────────────────────────────────────────────────────────────────────┘

PC ──────────────┐
                 │
                 ▼
            FetchUnit
                 │
                 ├──▶ Memory (read instruction)
                 │
                 ▼
            Instruction [32]
                 │
                 ▼
         InstructionDecoder
                 │
                 ├──▶ opcode, funct3, funct7
                 ├──▶ rd, rs1, rs2
                 ├──▶ immediate (sign-extended)
                 │
                 ▼
      ControlSignalGenerator
                 │
                 ├──▶ reg_write, mem_read, mem_write
                 ├──▶ alu_op, alu_src_a, alu_src_b
                 ├──▶ branch, jump, result_src, pc_src
                 │
                 ▼
          RegisterFile
                 │
                 ├──▶ read rs1 ────────────┐
                 ├──▶ read rs2 ──────┐     │
                 │                   │     │
                 │                   ▼     ▼
                 │              MUX_A   MUX_B
                 │                │       │
                 │                └───┬───┘
                 │                    │
                 │                    ▼
                 │                  ALU / Shifter
                 │                    │
                 │                    ├──▶ alu_result [32]
                 │                    ├──▶ flags (N,Z,C,V)
                 │                    │
                 │                    ▼
                 │               Memory (D-Memory)
                 │                    │
                 │                    ├──▶ mem_data [32] (if LW)
                 │                    │
                 │                    ▼
                 │                MUX_Result
                 │                    │
                 │                    ▼
                 ◀────────────── writeback_data [32]
                 │
                 ▼
         (write to rd if reg_write=1)


Branch/Jump Logic:
                 
  ALU flags ──────┐
                  │
  branch signal ──┼──▶ Branch Decision Logic
                  │         │
  BEQ/BNE ────────┘         ├──▶ branch_taken
                            │
                            ▼
                        PC MUX
                            │
                            ├──▶ 0: PC + 4
                            ├──▶ 1: PC + imm_b (branch)
                            ├──▶ 2: jump_target (JAL/JALR)
                            │
                            ▼
                        Next PC ──▶ (update PC register)
```

## Memory Map

```
┌─────────────────────────────────────┐ 0xFFFFFFFF
│                                     │
│         Unused / Reserved           │
│                                     │
├─────────────────────────────────────┤ 0x00020000 (128KB)
│                                     │
│        Data Memory Region           │
│     (Stack, Heap, Global Data)      │
│                                     │
│         Base: 0x00010000            │
│         Size: 64 KB                 │
│         Access: LW/SW               │
│         Alignment: 4-byte           │
│                                     │
├─────────────────────────────────────┤ 0x00010000 (64KB)
│                                     │
│      Instruction Memory Region      │
│         (Program Code)              │
│                                     │
│         Base: 0x00000000            │
│         Size: 64 KB                 │
│         Access: Fetch only          │
│         Alignment: 4-byte           │
│                                     │
└─────────────────────────────────────┘ 0x00000000

Memory Access Rules:
- Word access (LW/SW): Address must be 4-byte aligned (addr[1:0] = 00)
- Little-endian byte ordering
- Instruction memory: Read-only during execution
- Data memory: Read/write during execution
```

## Control Signal Flow

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        Control Signal Generation                                │
└────────────────────────────────────────────────────────────────────────────────┘

Instruction ──▶ Decoder ──▶ opcode, funct3, funct7
                              │
                              ▼
                    ┌───────────────────┐
                    │  Control Logic    │
                    └───────────────────┘
                              │
                              ├──▶ To Register File:
                              │    - reg_write (enable write)
                              │
                              ├──▶ To ALU:
                              │    - alu_op [4 bits] (ADD/SUB/AND/OR/XOR)
                              │
                              ├──▶ To Multiplexers:
                              │    - alu_src_a (0=rs1, 1=PC)
                              │    - alu_src_b (0=rs2, 1=immediate)
                              │    - result_src (0=ALU, 1=mem, 2=PC+4)
                              │    - pc_src (0=PC+4, 1=branch, 2=jump)
                              │
                              ├──▶ To Memory:
                              │    - mem_read (enable read for LW)
                              │    - mem_write (enable write for SW)
                              │
                              └──▶ To Branch Logic:
                                   - branch (is branch instruction)
                                   - jump (is jump instruction)

Example Control Signals by Instruction:

ADD:  reg_write=1, alu_op=ADD, alu_src_a=0, alu_src_b=0, result_src=0
ADDI: reg_write=1, alu_op=ADD, alu_src_a=0, alu_src_b=1, result_src=0
LW:   reg_write=1, alu_op=ADD, alu_src_a=0, alu_src_b=1, result_src=1, mem_read=1
SW:   reg_write=0, alu_op=ADD, alu_src_a=0, alu_src_b=1, mem_write=1
BEQ:  reg_write=0, alu_op=SUB, alu_src_a=0, alu_src_b=0, branch=1, pc_src=0/1
JAL:  reg_write=1, jump=1, result_src=2, pc_src=2
```

## Data Flow for Common Instructions

### ADD x3, x1, x2

```
PC ──▶ I-Mem ──▶ [ADD instruction]
                        │
                        ▼
                    Decoder: opcode=0x33, rd=3, rs1=1, rs2=2
                        │
                        ▼
                    Control: reg_write=1, alu_op=ADD, alu_src_a=0, alu_src_b=0
                        │
                        ▼
    RegFile[1] ────▶ MUX_A ──┐
    (x1)                      │
                              ├──▶ ALU (ADD) ──▶ result
    RegFile[2] ────▶ MUX_B ──┘                    │
    (x2)                                          ▼
                                            MUX_Result ──▶ RegFile[3]
                                                              (x3)
```

### LW x4, 0(x5)

```
PC ──▶ I-Mem ──▶ [LW instruction]
                        │
                        ▼
                    Decoder: opcode=0x03, rd=4, rs1=5, imm=0
                        │
                        ▼
                    Control: reg_write=1, alu_op=ADD, alu_src_b=1, 
                             mem_read=1, result_src=1
                        │
                        ▼
    RegFile[5] ────▶ MUX_A ──┐
    (x5)                      │
                              ├──▶ ALU (ADD) ──▶ address
    Immediate(0) ───▶ MUX_B ──┘                    │
                                                   ▼
                                            D-Mem (read) ──▶ mem_data
                                                              │
                                                              ▼
                                                        MUX_Result ──▶ RegFile[4]
                                                                         (x4)
```

### BEQ x3, x4, 8

```
PC ──▶ I-Mem ──▶ [BEQ instruction]
                        │
                        ▼
                    Decoder: opcode=0x63, rs1=3, rs2=4, imm=8
                        │
                        ▼
                    Control: branch=1, alu_op=SUB
                        │
                        ▼
    RegFile[3] ────▶ MUX_A ──┐
    (x3)                      │
                              ├──▶ ALU (SUB) ──▶ result, Z flag
    RegFile[4] ────▶ MUX_B ──┘                    │
    (x4)                                          ▼
                                            Branch Logic
                                              (if Z=1, taken)
                                                   │
                                                   ▼
                                            PC MUX ──▶ Next PC
                                              (PC+4 or PC+8)
```

---

For more detailed information, see:
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Complete architecture documentation
- [INSTRUCTION_SET.md](../INSTRUCTION_SET.md) - Instruction details
- [USAGE.md](../USAGE.md) - Usage examples
