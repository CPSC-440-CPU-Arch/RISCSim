# RISCSim Datapath Diagram

This document provides detailed ASCII art diagrams of the RISCSim single-cycle datapath, showing all signal paths, multiplexers, and component connections.

## Complete Single-Cycle Datapath

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               RISCSim Single-Cycle Datapath                                       │
│                                  (All 5 stages in 1 cycle)                                        │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────────┐
                           ┌────────│  Program Counter│◀────────────┐
                           │        │    (PC) [32]    │             │
                           │        └─────────────────┘             │
                           │                                        │
                           │ PC [32]                                │ next_pc [32]
                           │                                        │
┌──────────────────────────┼────────────────────────────────────────┼──────────────────────────────┐
│  FETCH                   ▼                                        │                              │
│                   ┌─────────────┐                                 │                              │
│                   │ Instruction │                                 │                              │
│                   │   Memory    │                                 │                              │
│                   │ [I-Memory]  │                                 │                              │
│                   │ 0x00000000  │                                 │                              │
│                   └─────────────┘                                 │                              │
│                          │                                        │                              │
│                          │ instruction [32]                       │                              │
│                          │                                        │                              │
└──────────────────────────┼────────────────────────────────────────┼──────────────────────────────┘
                           │                                        │
                           ▼                                        │
┌──────────────────────────────────────────────────────────────────┼──────────────────────────────┐
│  DECODE                                                           │                              │
│                   ┌─────────────┐                                 │                              │
│                   │ Instruction │                                 │                              │
│                   │   Decoder   │                                 │                              │
│                   │             │                                 │                              │
│                   │ - opcode    │                                 │                              │
│                   │ - funct3/7  │                                 │                              │
│                   │ - rd/rs1/rs2│                                 │                              │
│                   │ - immediate │                                 │                              │
│                   └─────────────┘                                 │                              │
│                          │                                        │                              │
│         ┌────────────────┴────────────────┐                       │                              │
│         │                                 │                       │                              │
│         ▼                                 ▼                       │                              │
│    rd[5], rs1[5], rs2[5]            immediate[32]                │                              │
│         │                             (sign-extended)             │                              │
│         │                                 │                       │                              │
│         │                           ┌─────────────┐               │                              │
│         │                           │  Control    │               │                              │
│         │                           │  Signal     │               │                              │
│         │                           │ Generator   │               │                              │
│         │                           └─────────────┘               │                              │
│         │                                 │                       │                              │
│         │         control signals ────────┴───────────────────────┼──────────────────────┐      │
│         │                                                         │                       │      │
└─────────┼─────────────────────────────────────────────────────────┼───────────────────────┼──────┘
          │                                                         │                       │
          │                                                         │                       │
┌─────────┼─────────────────────────────────────────────────────────┼───────────────────────┼──────┐
│  EXECUTE│                                                         │                       │      │
│         │                                                         │                       │      │
│    ┌────┴─────────┐                                               │                       │      │
│    │  Register    │                                               │                       │      │
│    │    File      │                                               │                       │      │
│    │              │                                               │                       │      │
│    │  x0 = 0      │                                               │                       │      │
│    │  x1-x31      │                                               │                       │      │
│    │              │                                               │                       │      │
│    │ read(rs1)─┐  │                                               │                       │      │
│    │ read(rs2)─┼──┼──────────────────┐                            │                       │      │
│    │           │  │                  │                            │                       │      │
│    └───────────┼──┘                  │                            │                       │      │
│                │                     │                            │                       │      │
│                │ rs1_data[32]        │ rs2_data[32]               │                       │      │
│                │                     │                            │                       │      │
│                ▼                     │                            ▼                       │      │
│         ┌─────────────┐              │                      ┌─────────────┐              │      │
│    PC───│     MUX     │              │                      │     MUX     │──immediate   │      │
│   [32]  │  (alu_src_a)│              │                      │  (alu_src_b)│   [32]       │      │
│         │   0: rs1    │              │                      │   0: rs2    │              │      │
│         │   1: PC     │              │                      │   1: imm    │              │      │
│         └─────────────┘              │                      └─────────────┘              │      │
│                │                     │                            │                       │      │
│                │ operand_a[32]       │                            │ operand_b[32]         │      │
│                │                     │                            │                       │      │
│                └─────────────────────┼────────────────────────────┘                       │      │
│                                      │                                                    │      │
│                                      ▼                                                    │      │
│                         ┌────────────────────────────────┐                               │      │
│                         │                                │                               │      │
│                         │        ALU / Shifter           │                               │      │
│                         │                                │                               │      │
│                         │  ┌──────────────────────────┐  │                               │      │
│                         │  │   32-bit ALU             │  │                               │      │
│                         │  │   - Full-adder chain     │  │                               │      │
│                         │  │   - Operations:          │  │                               │      │
│                         │  │     ADD, SUB, AND,       │  │                               │      │
│                         │  │     OR, XOR              │  │                               │      │
│                         │  │   - Flags: N,Z,C,V       │  │                               │      │
│                         │  └──────────────────────────┘  │                               │      │
│                         │                                │                               │      │
│                         │  ┌──────────────────────────┐  │                               │      │
│                         │  │   Barrel Shifter         │  │                               │      │
│                         │  │   - 5-stage shifter      │  │                               │      │
│                         │  │   - SLL, SRL, SRA        │  │                               │      │
│                         │  │   - Shift 0-31 bits      │  │                               │      │
│                         │  └──────────────────────────┘  │                               │      │
│                         │                                │                               │      │
│                         └────────────────────────────────┘                               │      │
│                                      │                                                    │      │
│                                      │ alu_result[32]                                     │      │
│                                      │                                                    │      │
│                         ┌────────────┴────────────┐                                      │      │
│                         │                         │                                      │      │
│                         │ flags: N, Z, C, V       │                                      │      │
│                         │                         │                                      │      │
└─────────────────────────┼─────────────────────────┼──────────────────────────────────────┼──────┘
                          │                         │                                      │
                          │                         ▼                                      │
┌─────────────────────────┼──────────────────  ┌─────────────┐                            │      
│  MEMORY                 │                     │   Branch    │                            │      
│                         │                     │   Logic     │                            │      
│                         │                     │             │                            │      
│                         │                     │ BEQ: Z=1?   │                            │      
│                         │                     │ BNE: Z=0?   │                            │      
│                         │                     └─────────────┘                            │      
│                         │                           │                                    │      
│                         │                           │ branch_taken                       │      
│                         │                           └────────────────────────────────────┼──────┐
│                         │                                                                │      │
│                         ▼                                                                │      │
│                   ┌─────────────┐                                                        │      │
│                   │             │                                                        │      │
│             addr──│ Data Memory │                                                        │      │
│            [32]   │ [D-Memory]  │                                                        │      │
│                   │ 0x00010000  │                                                        │      │
│                   │             │                                                        │      │
│        rs2_data───│ write_data  │                                                        │      │
│          [32]     │             │                                                        │      │
│                   │ mem_read ───│─── mem_write                                           │      │
│                   │             │    (control signals)                                   │      │
│                   └─────────────┘                                                        │      │
│                         │                                                                │      │
│                         │ mem_data[32]                                                   │      │
│                         │ (if mem_read=1)                                                │      │
│                         │                                                                │      │
└─────────────────────────┼────────────────────────────────────────────────────────────────┼──────┘
                          │                                                                │      
                          │                                                                │      
┌─────────────────────────┼────────────────────────────────────────────────────────────────┼──────┐
│  WRITEBACK              │                                                                │      │
│                         │                                                                │      │
│                         ▼                                                                │      │
│                   ┌─────────────┐                                                        │      │
│                   │             │                                                        │      │
│        alu_result─│     MUX     │                                                        │      │
│           [32]    │ (result_src)│                                                        │      │
│                   │             │                                                        │      │
│         mem_data──│  0: ALU     │                                                        │      │
│           [32]    │  1: Memory  │                                                        │      │
│                   │  2: PC+4    │───PC+4 [32]                                            │      │
│                   │             │                                                        │      │
│                   └─────────────┘                                                        │      │
│                         │                                                                │      │
│                         │ writeback_data[32]                                             │      │
│                         │                                                                │      │
│                         ▼                                                                │      │
│                   ┌─────────────┐                                                        │      │
│                   │  Register   │                                                        │      │
│           rd[5]───│    File     │                                                        │      │
│                   │   Write     │                                                        │      │
│    writeback_data─│   (if       │                                                        │      │
│         [32]      │ reg_write=1)│                                                        │      │
│                   └─────────────┘                                                        │      │
│                                                                                          │      │
└──────────────────────────────────────────────────────────────────────────────────────────┼──────┘
                                                                                           │
                                                                                           │
┌──────────────────────────────────────────────────────────────────────────────────────────┼──────┐
│  PC UPDATE                                                                               │      │
│                                                                                          │      │
│                                                                                          ▼      │
│                                                                                    branch_taken │
│                                                                                          │      │
│                                                                                    ┌─────┴────┐ │
│           ┌────────────────────────────────────────────────────────────────────────│  Branch  │ │
│           │                                                                        │  Target  │ │
│           │                                                                        │  Calc    │ │
│           │                                                                        └──────────┘ │
│           │                                                                             │       │
│           │                                                                             │       │
│           │                         ┌───────────────────────────────────────────────────┘       │
│           │                         │                                                           │
│           │                         ▼                                                           │
│           │                   ┌─────────────┐                                                   │
│           │                   │             │                                                   │
│           │        PC+4 [32]──│     MUX     │                                                   │
│           │                   │  (pc_src)   │                                                   │
│           │                   │             │                                                   │
│           │   PC+imm_b [32]───│  0: PC+4    │                                                   │
│           │  (branch target)  │  1: branch  │                                                   │
│           │                   │  2: jump    │                                                   │
│           │  jump_target[32]──│             │                                                   │
│           │     (JAL/JALR)    └─────────────┘                                                   │
│           │                         │                                                           │
│           │                         │ next_pc[32]                                               │
│           │                         │                                                           │
│           └─────────────────────────┘                                                           │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Detailed Register File Connections

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          Register File Detail                                   │
└────────────────────────────────────────────────────────────────────────────────┘

                    Instruction Decode
                           │
                           ├──▶ rs1[5 bits] ─────────┐
                           ├──▶ rs2[5 bits] ────────┐│
                           └──▶ rd[5 bits] ────────┐││
                                                    │││
                                                    │││
                    ┌───────────────────────────────┘││
                    │                                ││
                    │            ┌───────────────────┘│
                    │            │                    │
                    │            │    ┌───────────────┘
                    ▼            ▼    ▼
          ┌──────────────────────────────────┐
          │       Register File              │
          │                                  │
          │  ┌────────────────────────────┐  │
          │  │  x0  = 0 (hardwired)       │  │
          │  │  x1  = ra (return address) │  │
          │  │  x2  = sp (stack pointer)  │  │
          │  │  x3  = gp (global pointer) │  │
          │  │  x4  = tp (thread pointer) │  │
          │  │  x5-x7 = t0-t2 (temps)     │  │
          │  │  x8  = s0/fp (saved/frame) │  │
          │  │  x9  = s1 (saved)          │  │
          │  │  x10-x17 = a0-a7 (args)    │  │
          │  │  x18-x27 = s2-s11 (saved)  │  │
          │  │  x28-x31 = t3-t6 (temps)   │  │
          │  └────────────────────────────┘  │
          │                                  │
          │  Read Ports:                     │
          │    - Port A: rs1 ──▶ data_a[32] ────▶ (to ALU MUX_A)
          │    - Port B: rs2 ──▶ data_b[32] ────▶ (to ALU MUX_B and Memory)
          │                                  │
          │  Write Port:                     │
          │    - rd ◀── writeback_data[32] ◀──── (from Writeback MUX)
          │    - enable: reg_write signal    │
          │    - Note: writes to x0 ignored  │
          │                                  │
          └──────────────────────────────────┘
```

## ALU and Shifter Detail

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          ALU and Shifter Detail                                 │
└────────────────────────────────────────────────────────────────────────────────┘

                operand_a[32]         operand_b[32]
                      │                     │
                      └──────────┬──────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │      Operation Select      │
                    │      (based on alu_op)     │
                    └────────────────────────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  │                             │
                  ▼                             ▼
        ┌──────────────────┐         ┌──────────────────┐
        │    32-bit ALU    │         │  Barrel Shifter  │
        │                  │         │                  │
        │  ┌────────────┐  │         │  ┌────────────┐  │
        │  │ Bit 31     │  │         │  │ Stage 1    │  │
        │  │ Full Adder │  │         │  │ (shift 16) │  │
        │  └────────────┘  │         │  └────────────┘  │
        │        ⋮         │         │        │         │
        │  ┌────────────┐  │         │  ┌────────────┐  │
        │  │ Bit 1      │  │         │  │ Stage 2    │  │
        │  │ Full Adder │  │         │  │ (shift 8)  │  │
        │  └────────────┘  │         │  └────────────┘  │
        │  ┌────────────┐  │         │        │         │
        │  │ Bit 0      │  │         │  ┌────────────┐  │
        │  │ Full Adder │  │         │  │ Stage 3    │  │
        │  └────────────┘  │         │  │ (shift 4)  │  │
        │                  │         │  └────────────┘  │
        │  Operations:     │         │        │         │
        │  - ADD [0010]    │         │  ┌────────────┐  │
        │  - SUB [0110]    │         │  │ Stage 4    │  │
        │  - AND [0000]    │         │  │ (shift 2)  │  │
        │  - OR  [0001]    │         │  └────────────┘  │
        │  - XOR [0100]    │         │        │         │
        │                  │         │  ┌────────────┐  │
        │  Flags:          │         │  │ Stage 5    │  │
        │  - N: result<0   │         │  │ (shift 1)  │  │
        │  - Z: result==0  │         │  └────────────┘  │
        │  - C: carry out  │         │                  │
        │  - V: overflow   │         │  Operations:     │
        │                  │         │  - SLL (left)    │
        └──────────────────┘         │  - SRL (right)   │
                  │                  │  - SRA (arith)   │
                  │                  │                  │
                  │                  └──────────────────┘
                  │                            │
                  └────────────┬───────────────┘
                               │
                               ▼
                       alu_result[32]
                               │
                               ├──▶ flags (N, Z, C, V)
                               │
                               └──▶ (to Memory stage)
```

## Memory Access Detail

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          Memory Access Detail                                   │
└────────────────────────────────────────────────────────────────────────────────┘

        alu_result[32]                    rs2_data[32]
        (address)                         (write data)
              │                                 │
              │                                 │
              └────────────┬────────────────────┘
                           │
                           ▼
              ┌────────────────────────────┐
              │    Address Alignment Check  │
              │    (must be 4-byte aligned) │
              │    addr[1:0] == 00?         │
              └────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────────┐
              │      Address Decode        │
              │                            │
              │  0x00000000 - 0x0000FFFF   │
              │    → Instruction Memory    │
              │                            │
              │  0x00010000 - 0x0001FFFF   │
              │    → Data Memory           │
              └────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────────┐
              │      Data Memory           │
              │      (64KB, 16K words)     │
              │                            │
              │  Base: 0x00010000          │
              │                            │
              │  Operations:               │
              │    if mem_read:            │
              │      mem_data = mem[addr]  │
              │                            │
              │    if mem_write:           │
              │      mem[addr] = rs2_data  │
              │                            │
              │  Byte Order:               │
              │    Little-endian           │
              │                            │
              └────────────────────────────┘
                           │
                           │ mem_data[32]
                           │ (if mem_read=1)
                           │
                           ▼
                    (to Writeback MUX)


Little-Endian Layout (word at address 0x00010000 = 0x12345678):

    Address     Byte Value
    0x00010000    0x78  (LSB)
    0x00010001    0x56
    0x00010002    0x34
    0x00010003    0x12  (MSB)
```

## PC Update and Branch Logic

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        PC Update and Branch Logic                               │
└────────────────────────────────────────────────────────────────────────────────┘

                        Current PC[32]
                             │
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        │                    │                    │
        ▼                    ▼                    ▼
  ┌──────────┐        ┌──────────┐        ┌──────────┐
  │  PC + 4  │        │ Branch   │        │  Jump    │
  │  (ALU)   │        │ Target   │        │ Target   │
  └──────────┘        └──────────┘        └──────────┘
        │                    │                    │
        │                    │ PC + imm_b         │ JAL: PC + imm_j
        │                    │                    │ JALR: (rs1+imm_i)&~1
        │                    │                    │
        └─────────┬──────────┴────────────────────┘
                  │
                  │
                  ▼
            ┌─────────────┐
            │   PC MUX    │
            │  (pc_src)   │          Branch Decision:
            │             │          ┌────────────────────┐
            │ 0: PC + 4   │◀─────────│ ALU Flags:         │
            │ 1: Branch   │          │   BEQ: Z flag = 1? │
            │ 2: Jump     │          │   BNE: Z flag = 0? │
            └─────────────┘          └────────────────────┘
                  │                            │
                  │                            │ branch_taken
                  │                            └────▶ sets pc_src
                  │
                  │ next_pc[32]
                  │
                  ▼
            ┌─────────────┐
            │     PC      │
            │  Register   │
            └─────────────┘
                  │
                  │ (next cycle)
                  │
                  └────▶ (back to Fetch)


PC Source Selection Logic:

Instruction Type    │  pc_src  │  Next PC Value
────────────────────┼──────────┼─────────────────────
Most instructions   │    0     │  PC + 4
BEQ (taken)         │    1     │  PC + imm_b
BNE (taken)         │    1     │  PC + imm_b
BEQ (not taken)     │    0     │  PC + 4
BNE (not taken)     │    0     │  PC + 4
JAL                 │    2     │  PC + imm_j
JALR                │    2     │  (rs1 + imm_i) & ~1
```

## Multiplexer Summary

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          All Multiplexers in Datapath                           │
└────────────────────────────────────────────────────────────────────────────────┘

MUX Name      │ Control Signal │ Inputs                    │ Output
──────────────┼────────────────┼───────────────────────────┼─────────────────
MUX_A         │ alu_src_a      │ 0: rs1_data[32]           │ operand_a[32]
(ALU input A) │                │ 1: PC[32]                 │
──────────────┼────────────────┼───────────────────────────┼─────────────────
MUX_B         │ alu_src_b      │ 0: rs2_data[32]           │ operand_b[32]
(ALU input B) │                │ 1: immediate[32]          │
──────────────┼────────────────┼───────────────────────────┼─────────────────
MUX_Result    │ result_src     │ 0: alu_result[32]         │ writeback_data[32]
(Writeback)   │                │ 1: mem_data[32]           │
              │                │ 2: PC + 4[32]             │
──────────────┼────────────────┼───────────────────────────┼─────────────────
MUX_PC        │ pc_src         │ 0: PC + 4[32]             │ next_pc[32]
(PC source)   │                │ 1: PC + imm_b[32]         │
              │                │ 2: jump_target[32]        │
──────────────┴────────────────┴───────────────────────────┴─────────────────

All multiplexers use simple bit-level selection - no arithmetic operations.
```

## Critical Path Analysis

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          Critical Path (Worst Case: LW)                         │
└────────────────────────────────────────────────────────────────────────────────┘

Cycle begins
     │
     ▼
┌─────────────────────────────┐  ← Fetch: Read instruction memory
│  T_fetch = T_mem_read       │     Time: ~5-10ns (memory access)
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐  ← Decode: Instruction decode + control
│  T_decode = T_decoder +     │     Time: ~2-3ns (combinational logic)
│             T_control       │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐  ← Execute: Register read + MUX + ALU
│  T_execute = T_reg_read +   │     Time: ~8-12ns (register + 32-bit add)
│              T_mux +        │
│              T_alu          │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐  ← Memory: Data memory access
│  T_memory = T_mem_read      │     Time: ~5-10ns (memory access)
└─────────────────────────────┘  ⚠️ LONGEST PATH (includes 2 memory accesses)
     │
     ▼
┌─────────────────────────────┐  ← Writeback: MUX + register write
│  T_writeback = T_mux +      │     Time: ~2-3ns (MUX + write)
│                T_reg_write  │
└─────────────────────────────┘
     │
     ▼
Cycle ends

Total Cycle Time = T_fetch + T_decode + T_execute + T_memory + T_writeback
                 ≈ 22-38ns for LW instruction (critical path)
                 ≈ 17-28ns for R-type instructions (no memory access)

Maximum Clock Frequency ≈ 1 / T_cycle
                       ≈ 26-45 MHz (limited by LW instruction)

Note: These are rough estimates. Actual timing depends on:
- Memory technology (SRAM vs DRAM)
- Process technology (wire delays, gate delays)
- Temperature and voltage
```

---

For complete system documentation, see:
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Full architecture description
- [cpu_block_diagram.md](cpu_block_diagram.md) - High-level block diagram
- [INSTRUCTION_SET.md](../INSTRUCTION_SET.md) - Instruction details
