# RISCSim CPU Architecture Documentation

**Authors:** Joshua Castaneda and Ivan Flores

## Table of Contents
1. [System Overview](#system-overview)
2. [Component Descriptions](#component-descriptions)
3. [Datapath Architecture](#datapath-architecture)
4. [Control Signal Flow](#control-signal-flow)
5. [Memory Map](#memory-map)
6. [Instruction Execution Flow](#instruction-execution-flow)
7. [Design Constraints](#design-constraints)

---

## System Overview

RISCSim is a **single-cycle RISC-V CPU simulator** implementing the RV32I base instruction set. The design follows a classic five-stage datapath architecture executed in a single cycle:

1. **Instruction Fetch (IF)**: Fetch instruction from memory
2. **Instruction Decode (ID)**: Decode instruction and generate control signals
3. **Execute (EX)**: Perform ALU/Shifter/MDU/FPU operations
4. **Memory Access (MEM)**: Read/write data memory
5. **Write Back (WB)**: Update register file

### Key Features
- ✅ **Single-cycle execution**: Each instruction completes in one cycle
- ✅ **Harvard architecture**: Separate instruction and data memory
- ✅ **32-bit word size**: RV32I integer base
- ✅ **32 integer registers**: x0-x31 (x0 hardwired to zero)
- ✅ **32 floating-point registers**: f0-f31 (for future extensions)
- ✅ **Bit-accurate implementation**: No host arithmetic operators
- ✅ **Comprehensive ALU**: ADD, SUB, AND, OR, XOR with flags
- ✅ **Barrel shifter**: SLL, SRL, SRA operations
- ✅ **MDU**: Multiply/divide unit (M extension)
- ✅ **FPU**: Floating-point unit (F extension)

### Supported Instruction Set (Minimum Viable)

| Category | Instructions | Count |
|----------|-------------|-------|
| Arithmetic | ADD, SUB, ADDI | 3 |
| Logical | AND, OR, XOR, ANDI, ORI, XORI | 6 |
| Shifts | SLL, SRL, SRA, SLLI, SRLI, SRAI | 6 |
| Memory | LW, SW | 2 |
| Branch | BEQ, BNE | 2 |
| Jump | JAL, JALR | 2 |
| Upper Imm | LUI, AUIPC | 2 |
| **Total** | | **23 instructions** |

---

## Component Descriptions

### 1. Memory Unit (`riscsim/cpu/memory.py`)

**Purpose**: Unified memory system with separate instruction and data regions.

**Features**:
- Word-addressable (32-bit) and byte-addressable
- Little-endian byte ordering
- Address alignment checking for word access
- Separate regions for instructions (0x00000000+) and data (0x00010000+)
- Program loading from .hex files

**Interface**:
```python
class Memory:
    def __init__(self, size_bytes=128*1024, base_addr=0x00000000)
    def read_word(self, addr: List[int]) -> List[int]  # [32 bits] -> [32 bits]
    def write_word(self, addr: List[int], data: List[int])
    def read_byte(self, addr: List[int]) -> List[int]  # [32 bits] -> [8 bits]
    def write_byte(self, addr: List[int], data: List[int])
    def load_program(self, hex_file_path: str)
```

**Constraints**:
- Address must be 4-byte aligned for word access
- Address must be within bounds (0x00000000 to 0x00020000)
- Data region starts at 0x00010000

---

### 2. Fetch Unit (`riscsim/cpu/fetch.py`)

**Purpose**: Manage program counter (PC) and fetch instructions from memory.

**Features**:
- PC management with alignment checking
- Instruction fetch from memory
- PC increment using ALU (no host operators)
- Branch target calculation
- Jump target calculation

**Interface**:
```python
class FetchUnit:
    def __init__(self, memory: Memory, initial_pc: int = 0)
    def fetch(self) -> List[int]  # Returns [32 bits] instruction
    def increment_pc(self)  # PC = PC + 4 (using ALU)
    def branch_to(self, target_addr: List[int])  # PC = target
    def branch_relative(self, offset: List[int])  # PC = PC + offset
    def get_pc(self) -> List[int]  # Returns [32 bits]
    def get_next_pc(self) -> List[int]  # Returns PC + 4 for JAL/JALR
```

**PC Update Logic**:
- Sequential: `PC = PC + 4`
- Branch taken: `PC = PC + imm_b`
- Jump (JAL): `PC = PC + imm_j`
- Jump (JALR): `PC = (rs1 + imm_i) & ~1`

---

### 3. Instruction Decoder (`riscsim/cpu/decoder.py`)

**Purpose**: Decode 32-bit RISC-V instructions into control signals and operands.

**Features**:
- Support for all 6 RISC-V instruction formats (R, I, S, B, U, J)
- Field extraction (opcode, funct3, funct7, rd, rs1, rs2)
- Immediate extraction with proper sign extension
- Mnemonic generation for debugging
- Invalid instruction detection

**Interface**:
```python
class InstructionDecoder:
    def decode(self, instruction: List[int]) -> DecodedInstruction
    
class DecodedInstruction:
    instr_type: str        # 'R', 'I', 'S', 'B', 'U', 'J'
    opcode: List[int]      # [7 bits]
    funct3: List[int]      # [3 bits]
    funct7: List[int]      # [7 bits]
    rd: List[int]          # [5 bits]
    rs1: List[int]         # [5 bits]
    rs2: List[int]         # [5 bits]
    immediate: List[int]   # [32 bits] sign-extended
    mnemonic: str          # "ADD", "ADDI", etc.
```

**Instruction Formats**:
```
R-type: [funct7(7) | rs2(5) | rs1(5) | funct3(3) | rd(5) | opcode(7)]
I-type: [imm(12) | rs1(5) | funct3(3) | rd(5) | opcode(7)]
S-type: [imm[11:5](7) | rs2(5) | rs1(5) | funct3(3) | imm[4:0](5) | opcode(7)]
B-type: [imm[12|10:5](7) | rs2(5) | rs1(5) | funct3(3) | imm[4:1|11](5) | opcode(7)]
U-type: [imm[31:12](20) | rd(5) | opcode(7)]
J-type: [imm[20|10:1|11|19:12](20) | rd(5) | opcode(7)]
```

---

### 4. ALU (Arithmetic Logic Unit) (`riscsim/cpu/alu.py`)

**Purpose**: Perform bit-level arithmetic and logical operations.

**Features**:
- 32-bit operations using 1-bit full adders
- Operations: ADD, SUB, AND, OR, XOR, NOT
- ALU flags: N (negative), Z (zero), C (carry), V (overflow)
- No host arithmetic operators (uses only boolean logic)

**Interface**:
```python
def alu(a: List[int], b: List[int], control: List[int]) -> Tuple[List[int], ALUFlags]:
    # a, b: [32 bits]
    # control: [4 bits] operation select
    # Returns: (result[32 bits], flags)
```

**Control Signals**:
- `[0,0,0,0]`: AND
- `[0,0,0,1]`: OR
- `[0,0,1,0]`: ADD
- `[0,1,1,0]`: SUB
- `[1,1,0,0]`: NOR

---

### 5. Shifter (`riscsim/cpu/shifter.py`)

**Purpose**: Perform barrel shift operations.

**Features**:
- 5-stage barrel shifter (shift by 16, 8, 4, 2, 1)
- Operations: SLL (logical left), SRL (logical right), SRA (arithmetic right)
- No host shift operators (uses array slicing)

**Interface**:
```python
def shift(data: List[int], shamt: List[int], shift_type: str) -> List[int]:
    # data: [32 bits]
    # shamt: [5 bits] shift amount (0-31)
    # shift_type: 'SLL', 'SRL', 'SRA'
    # Returns: [32 bits] shifted result
```

---

### 6. Register File (`riscsim/cpu/registers.py`)

**Purpose**: Store and manage register state.

**Features**:
- 32 integer registers (x0-x31), x0 always reads as zero
- 32 floating-point registers (f0-f31)
- FCSR (Floating-point Control and Status Register)

**Interface**:
```python
class RegisterFile:
    def read(self, reg_num: List[int]) -> List[int]  # [5 bits] -> [32 bits]
    def write(self, reg_num: List[int], data: List[int])
    def reset(self)
```

**Special Registers**:
- `x0`: Always reads as 0, writes are ignored
- `x1-x31`: General-purpose registers

---

### 7. Control Unit (`riscsim/cpu/control_signals.py`)

**Purpose**: Generate control signals for datapath components.

**Control Signals**:
```python
class ControlSignals:
    # Register control
    reg_write: int         # Write to register file
    
    # ALU control
    alu_op: List[int]      # [4 bits] ALU operation
    alu_src_a: int         # ALU source A (0=rs1, 1=PC)
    alu_src_b: int         # ALU source B (0=rs2, 1=immediate)
    
    # Memory control
    mem_read: int          # Read from memory
    mem_write: int         # Write to memory
    
    # Branch/Jump control
    branch: int            # Branch instruction
    jump: int              # Jump instruction
    
    # Writeback control
    result_src: int        # Result source (0=ALU, 1=memory, 2=PC+4)
    
    # PC control
    pc_src: int            # PC source (0=PC+4, 1=branch, 2=jump)
```

---

### 8. Datapath (`riscsim/cpu/datapath.py`)

**Purpose**: Connect all components and orchestrate single-cycle execution.

**Features**:
- Five-stage execution in single cycle
- Multiplexer selection for data routing
- Branch/jump target calculation
- Writeback data selection

**Interface**:
```python
class Datapath:
    def __init__(self, memory: Memory, register_file: RegisterFile)
    def execute_cycle(self) -> CycleResult
    def get_pc(self) -> List[int]
    def set_pc(self, addr: List[int])
    def get_cycle_count(self) -> int

class CycleResult:
    pc: List[int]              # [32 bits] current PC
    instruction: List[int]      # [32 bits] fetched instruction
    decoded: DecodedInstruction
    signals: ControlSignals
    alu_result: List[int]      # [32 bits]
    mem_data: Optional[List[int]]  # [32 bits] if memory accessed
    writeback_data: List[int]  # [32 bits]
    branch_taken: bool
    cycle_num: int
```

---

### 9. CPU Top-Level (`riscsim/cpu/cpu.py`)

**Purpose**: Provide user interface for program execution and debugging.

**Features**:
- Program loading from .hex files
- Single-step execution
- Run until halt
- Run until specific PC
- Register/memory inspection
- Statistics tracking (CPI, instruction mix, etc.)

**Interface**:
```python
class CPU:
    def __init__(self, memory_size: int = 128*1024)
    def load_program(self, hex_file_path: str)
    def reset(self)
    def step(self) -> CycleResult
    def run(self, max_cycles: int = 10000) -> ExecutionResult
    def run_until_pc(self, target_pc: int, max_cycles: int = 10000) -> ExecutionResult
    def get_register(self, reg_num: int) -> int
    def set_register(self, reg_num: int, value: int)
    def get_memory_word(self, addr: int) -> int
    def set_memory_word(self, addr: int, value: int)
    def dump_registers(self) -> str
    def dump_memory(self, start_addr: int, num_words: int) -> str
    def get_statistics(self) -> CPUStatistics
```

**Halt Conditions**:
1. Infinite loop detected (JAL x0, 0)
2. Max cycle limit reached
3. Invalid instruction encountered
4. Target PC reached (for run_until_pc)

---

## Datapath Architecture

### Single-Cycle Datapath Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RISC-V Single-Cycle Datapath                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Fetch      │
│   Unit       │──────┐
│              │      │
│   PC ────────┼──────┼────────────────────────────────────────────┐
│   [32]       │      │                                            │
└──────────────┘      │                                            │
       │              │                                            │
       │ fetch()      │ PC [32]                                    │
       ▼              │                                            │
┌──────────────┐      │                                            │
│ Instruction  │      │                                            │
│   Memory     │      │                                            │
│ [0x00000000] │      │                                            │
└──────────────┘      │                                            │
       │              │                                            │
       │ instruction  │                                            │
       │ [32]         │                                            │
       ▼              │                                            │
┌──────────────┐      │                                            │
│  Instruction │      │                                            │
│   Decoder    │      │                                            │
│              │      │                                            │
│  - opcode    │      │                                            │
│  - funct3/7  │      │                                            │
│  - rd/rs1/rs2│      │                                            │
│  - immediate │      │                                            │
└──────────────┘      │                                            │
       │              │                                            │
       │ decoded      │                                            │
       │              │                                            │
       ▼              │                                            │
┌──────────────┐      │                                            │
│   Control    │      │                                            │
│   Signal     │      │                                            │
│  Generator   │      │                                            │
└──────────────┘      │                                            │
       │              │                                            │
       │ control_signals                                          │
       │              │                                            │
       ├──────────────┼────────────────────────┐                  │
       │              │                        │                  │
       ▼              ▼                        ▼                  │
┌──────────────┐   ┌─────────┐         ┌──────────────┐          │
│  Register    │   │   MUX   │         │     MUX      │          │
│    File      │   │ alu_src │         │  alu_src_b   │          │
│              │   │    _a   │         │              │          │
│ x0 = 0       │   │ (rs1/PC)│         │ (rs2/imm)    │          │
│ x1-x31       │   └─────────┘         └──────────────┘          │
└──────────────┘        │                      │                 │
   │        │            ▼                      ▼                 │
   │ rs1    │ rs2   ┌────────────────────────────────┐           │
   │ [32]   │ [32]  │         ALU / Shifter          │           │
   ▼        ▼       │                                │           │
   │        │       │  Operations:                   │           │
   │        │       │  - ADD, SUB (full adder)       │           │
   │        │       │  - AND, OR, XOR (boolean)      │           │
   │        └───────┼─▶- SLL, SRL, SRA (barrel)      │           │
   │                │                                │           │
   │                │  Output: result[32], flags     │           │
   │                └────────────────────────────────┘           │
   │                            │                                │
   │                            │ alu_result [32]                │
   │                            │                                │
   │                            ├─────────────┐                  │
   │                            │             │                  │
   │                            ▼             ▼                  │
   │                    ┌──────────────┐  ┌─────────┐           │
   │                    │  Data Memory │  │  Branch │           │
   │                    │  [0x00010000]│  │  Logic  │           │
   │                    │              │  │         │           │
   │                    │  LW / SW     │  │ BEQ/BNE │           │
   │                    └──────────────┘  │ taken?  │           │
   │                            │         └─────────┘           │
   │                            │             │                  │
   │                            │ mem_data    │ branch_taken     │
   │                            │ [32]        │                  │
   │                            │             │                  │
   │                            ▼             ▼                  │
   │                    ┌─────────────────────────┐             │
   │                    │     MUX (result_src)    │             │
   │                    │  0: ALU result          │             │
   │                    │  1: Memory data         │             │
   │                    │  2: PC + 4 (JAL/JALR)   │             │
   │                    └─────────────────────────┘             │
   │                               │                             │
   │                               │ writeback_data [32]         │
   │                               │                             │
   └───────────────────────────────┘                             │
                                                                 │
                        ┌──────────────────────────┐             │
                        │   MUX (pc_src)           │◀────────────┘
                        │  0: PC + 4               │
                        │  1: PC + branch_offset   │
                        │  2: jump_target          │
                        └──────────────────────────┘
                                   │
                                   │ next_pc [32]
                                   │
                                   └─────────▶ (back to PC)
```

### Key Datapath Paths

1. **Instruction Fetch Path**:
   - PC → Instruction Memory → Instruction Register

2. **Register Read Path**:
   - Instruction[rs1] → Register File → ALU input A
   - Instruction[rs2] → Register File → ALU input B / Memory data

3. **Execute Path**:
   - ALU inputs → ALU/Shifter → ALU result
   - Branch comparison → Branch taken flag

4. **Memory Path**:
   - ALU result (address) → Data Memory → Memory data
   - Register[rs2] → Data Memory (for SW)

5. **Writeback Path**:
   - ALU result / Memory data / PC+4 → Register File[rd]

6. **PC Update Path**:
   - PC+4 / Branch target / Jump target → PC

---

## Control Signal Flow

### Control Signal Generation

The decoder generates control signals based on opcode and funct fields:

```
Instruction → Decoder → Control Signals → Datapath Components
```

### Control Signal Truth Table

| Instruction | Type | reg_write | alu_src_a | alu_src_b | mem_read | mem_write | branch | jump | result_src | pc_src |
|-------------|------|-----------|-----------|-----------|----------|-----------|--------|------|------------|--------|
| ADD         | R    | 1         | 0 (rs1)   | 0 (rs2)   | 0        | 0         | 0      | 0    | 0 (ALU)    | 0      |
| ADDI        | I    | 1         | 0 (rs1)   | 1 (imm)   | 0        | 0         | 0      | 0    | 0 (ALU)    | 0      |
| LW          | I    | 1         | 0 (rs1)   | 1 (imm)   | 1        | 0         | 0      | 0    | 1 (mem)    | 0      |
| SW          | S    | 0         | 0 (rs1)   | 1 (imm)   | 0        | 1         | 0      | 0    | X          | 0      |
| BEQ         | B    | 0         | 0 (rs1)   | 0 (rs2)   | 0        | 0         | 1      | 0    | X          | 0/1    |
| JAL         | J    | 1         | 1 (PC)    | 1 (imm)   | 0        | 0         | 0      | 1    | 2 (PC+4)   | 2      |
| JALR        | I    | 1         | 0 (rs1)   | 1 (imm)   | 0        | 0         | 0      | 1    | 2 (PC+4)   | 2      |
| LUI         | U    | 1         | X         | 1 (imm)   | 0        | 0         | 0      | 0    | 0 (ALU)    | 0      |
| AUIPC       | U    | 1         | 1 (PC)    | 1 (imm)   | 0        | 0         | 0      | 0    | 0 (ALU)    | 0      |

### ALU Operation Control

| Instruction | ALU Control | Operation |
|-------------|-------------|-----------|
| ADD, ADDI, LW, SW | [0,0,1,0] | ADD |
| SUB         | [0,1,1,0] | SUB |
| AND, ANDI   | [0,0,0,0] | AND |
| OR, ORI     | [0,0,0,1] | OR |
| XOR, XORI   | [0,1,0,0] | XOR |

### Branch Control Logic

```
BEQ: branch_taken = (rs1 == rs2)
BNE: branch_taken = (rs1 != rs2)

If branch_taken:
    next_pc = PC + imm_b
Else:
    next_pc = PC + 4
```

### Jump Control Logic

```
JAL:  next_pc = PC + imm_j
      rd = PC + 4

JALR: next_pc = (rs1 + imm_i) & ~1  # Clear LSB
      rd = PC + 4
```

---

## Memory Map

### Address Space Layout

```
┌─────────────────────────────────────┐ 0xFFFFFFFF
│                                     │
│         Unused / Reserved           │
│                                     │
├─────────────────────────────────────┤ 0x00020000
│                                     │
│        Data Memory Region           │
│     (Stack, Heap, Global Data)      │
│                                     │
│         Base: 0x00010000            │
│         Size: 64 KB                 │
│                                     │
├─────────────────────────────────────┤ 0x00010000
│                                     │
│      Instruction Memory Region      │
│         (Program Code)              │
│                                     │
│         Base: 0x00000000            │
│         Size: 64 KB                 │
│                                     │
└─────────────────────────────────────┘ 0x00000000
```

### Memory Regions

1. **Instruction Memory** (0x00000000 - 0x0000FFFF):
   - Read-only during execution
   - Loaded from .hex files
   - Word-aligned access required
   - 64 KB capacity (16,384 instructions)

2. **Data Memory** (0x00010000 - 0x0001FFFF):
   - Read/write during execution
   - Word and byte access supported
   - Used for stack, heap, global variables
   - 64 KB capacity

3. **Reserved** (0x00020000 - 0xFFFFFFFF):
   - Future expansion
   - Memory-mapped I/O (future)
   - Peripheral devices (future)

### Memory Access

**Word Access** (LW/SW):
- Address must be 4-byte aligned (addr[1:0] = 00)
- Transfers 32 bits
- Little-endian byte order

**Byte Access** (LB/SB - future):
- Any address
- Transfers 8 bits
- Sign extension for LB

### Memory Layout Example

```
Program loaded at 0x00000000:
    0x00000000: 00500093  # addi x1, x0, 5
    0x00000004: 00A00113  # addi x2, x0, 10
    0x00000008: 002081B3  # add x3, x1, x2
    ...

Data region at 0x00010000:
    0x00010000: 00000000  # Initialized to 0
    0x00010004: 00000000
    ...
    
Stack pointer (x2/sp) typically starts at 0x0001FFFC (top of data memory)
```

---

## Instruction Execution Flow

### Single-Cycle Execution Sequence

For each instruction, all five stages execute in one cycle:

#### 1. Fetch Stage
```
1. Read instruction from memory at address PC
2. instruction = memory[PC]
```

#### 2. Decode Stage
```
1. Extract instruction fields:
   - opcode = instruction[6:0]
   - rd = instruction[11:7]
   - rs1 = instruction[19:15]
   - rs2 = instruction[24:20]
   - funct3 = instruction[14:12]
   - funct7 = instruction[31:25]
   
2. Extract immediate (format-dependent):
   - I-type: imm = sign_extend(instruction[31:20])
   - S-type: imm = sign_extend({instruction[31:25], instruction[11:7]})
   - B-type: imm = sign_extend({instruction[31], instruction[7], instruction[30:25], instruction[11:8], 1'b0})
   - U-type: imm = {instruction[31:12], 12'b0}
   - J-type: imm = sign_extend({instruction[31], instruction[19:12], instruction[20], instruction[30:21], 1'b0})
   
3. Generate control signals based on opcode/funct
```

#### 3. Execute Stage
```
1. Read operands:
   - operand_a = (alu_src_a == 0) ? reg[rs1] : PC
   - operand_b = (alu_src_b == 0) ? reg[rs2] : immediate
   
2. Perform operation:
   - alu_result = ALU(operand_a, operand_b, alu_control)
   
3. Branch decision:
   - If branch instruction:
     - Compare rs1 and rs2
     - branch_taken = (condition met)
```

#### 4. Memory Stage
```
1. If mem_read:
   - mem_data = memory[alu_result]
   
2. If mem_write:
   - memory[alu_result] = reg[rs2]
```

#### 5. Writeback Stage
```
1. Select writeback data:
   - writeback_data = (result_src == 0) ? alu_result :
                      (result_src == 1) ? mem_data :
                      (result_src == 2) ? PC + 4 : 0
   
2. If reg_write and (rd != 0):
   - reg[rd] = writeback_data
   
3. Update PC:
   - next_pc = (pc_src == 0) ? PC + 4 :
               (pc_src == 1) ? PC + imm_b :  # Branch taken
               (pc_src == 2) ? jump_target : PC + 4
   - PC = next_pc
```

### Example Instruction Execution

#### Example 1: ADD x3, x1, x2

```
Fetch:    instruction = memory[PC] = 0x002081B3
Decode:   opcode=0x33 (R-type), rd=3, rs1=1, rs2=2, funct3=0, funct7=0
          → ADD operation
          → reg_write=1, alu_src_a=0, alu_src_b=0, result_src=0
Execute:  operand_a = reg[1] = 5
          operand_b = reg[2] = 10
          alu_result = 5 + 10 = 15 (using ALU with ADD control)
Memory:   (no memory access)
Writeback: reg[3] = 15
          PC = PC + 4
```

#### Example 2: LW x4, 0(x5)

```
Fetch:    instruction = memory[PC] = 0x0002A203
Decode:   opcode=0x03 (I-type), rd=4, rs1=5, imm=0
          → LW operation
          → reg_write=1, alu_src_a=0, alu_src_b=1, mem_read=1, result_src=1
Execute:  operand_a = reg[5] = 0x00010000
          operand_b = 0 (immediate)
          alu_result = 0x00010000 + 0 = 0x00010000
Memory:   mem_data = memory[0x00010000] = 15
Writeback: reg[4] = 15
          PC = PC + 4
```

#### Example 3: BEQ x3, x4, 8 (offset = 8 bytes forward)

```
Fetch:    instruction = memory[PC] = 0x00418463
Decode:   opcode=0x63 (B-type), rs1=3, rs2=4, imm=8
          → BEQ operation
          → branch=1, alu_src_a=0, alu_src_b=0
Execute:  operand_a = reg[3] = 15
          operand_b = reg[4] = 15
          alu_result = 15 - 15 = 0 (using ALU with SUB control)
          Z_flag = 1 (zero)
          branch_taken = (Z_flag == 1) = true
Memory:   (no memory access)
Writeback: (no register write)
          PC = PC + 8 (branch taken)
```

#### Example 4: JAL x1, 16 (offset = 16 bytes forward)

```
Fetch:    instruction = memory[PC] = 0x010000EF
Decode:   opcode=0x6F (J-type), rd=1, imm=16
          → JAL operation
          → reg_write=1, jump=1, result_src=2, pc_src=2
Execute:  operand_a = PC
          operand_b = 16 (immediate)
          jump_target = PC + 16
Memory:   (no memory access)
Writeback: reg[1] = PC + 4 (return address)
          PC = PC + 16 (jump taken)
```

---

## Design Constraints

### Hardware-Accurate Implementation

RISCSim follows strict constraints to ensure bit-accurate hardware simulation:

#### ❌ Prohibited Operations (in implementation modules)
- **No arithmetic operators**: `+`, `-`, `*`, `/`, `%`
- **No shift operators**: `<<`, `>>`
- **No comparison operators**: `<`, `>`, `<=`, `>=`
- **No base conversion**: `int(..., base)`, `bin()`, `hex()`, `format()`
- **No floating-point math**: All FP operations at bit level

#### ✅ Allowed Operations
- **Boolean logic**: `and`, `or`, `xor`, `not`
- **Array operations**: indexing, slicing, concatenation
- **Control flow**: `if`, `for`, `while`
- **Bit vectors**: All data as arrays of 0/1

### Implementation Strategy

All arithmetic operations are built from primitive operations:

1. **Addition**: Chain of 1-bit full adders
   ```python
   sum_bit = a_bit ^ b_bit ^ carry_in
   carry_out = (a_bit & b_bit) | (a_bit & carry_in) | (b_bit & carry_in)
   ```

2. **Subtraction**: Addition with two's complement
   ```python
   # a - b = a + (~b + 1)
   result = ALU(a, invert_bits(b), carry_in=1)
   ```

3. **Shifting**: Barrel shifter with array operations
   ```python
   # Shift left by 1: remove LSB, add 0 at MSB
   shifted = data[1:] + [0]
   ```

4. **Multiplication**: Shift-and-add algorithm using ALU
   ```python
   for each bit in multiplier:
       if bit == 1:
           result = ALU(result, multiplicand << i, ADD)
   ```

### Boundary Functions

**I/O boundary functions** are allowed for format conversion only (not arithmetic):

```python
def int_to_bits(value: int, width: int) -> List[int]:
    """Convert Python int to bit array (boundary function)"""
    # Uses % and // for format conversion only
    
def bits_to_int(bits: List[int]) -> int:
    """Convert bit array to Python int (boundary function)"""
    # Uses + for format conversion only
```

These are analogous to `struct.pack`/`struct.unpack` in C - used only at the interface between Python types and bit representations.

### Testing Strategy

Tests may use Python arithmetic for **reference value computation**:

```python
def test_add():
    a_bits = int_to_bits(5, 32)
    b_bits = int_to_bits(10, 32)
    result, flags = alu(a_bits, b_bits, ADD_CONTROL)
    
    # Python arithmetic OK in tests for verification
    expected = 5 + 10
    actual = bits_to_int(result)
    assert actual == expected
```

---

## Performance Characteristics

### Single-Cycle Timing

**Cycle Time**: Determined by longest path through all five stages

```
T_cycle = T_fetch + T_decode + T_execute + T_memory + T_writeback
```

**CPI (Cycles Per Instruction)**: Always 1 (single-cycle design)

```
CPI = Total Cycles / Total Instructions = N / N = 1
```

**Program Execution Time**:
```
Execution Time = Instruction Count × CPI × Cycle Time
               = Instruction Count × 1 × T_cycle
               = Instruction Count × T_cycle
```

### Critical Path Analysis

Longest path for different instruction types:

1. **R-type (ADD, SUB, etc.)**:
   ```
   Fetch → Decode → RegRead → ALU → Writeback
   ```

2. **Load (LW)**:
   ```
   Fetch → Decode → RegRead → ALU (addr) → Memory → Writeback
   ```
   ⚠️ **Longest path** - includes memory access

3. **Store (SW)**:
   ```
   Fetch → Decode → RegRead → ALU (addr) → Memory
   ```

4. **Branch (BEQ, BNE)**:
   ```
   Fetch → Decode → RegRead → ALU (compare) → PC Update
   ```

5. **Jump (JAL, JALR)**:
   ```
   Fetch → Decode → ALU (target) → PC Update + Writeback
   ```

### Optimization Opportunities (Future)

To improve performance, consider:

1. **Pipelining**: Break into 5 pipeline stages (CPI → ~1 with hazards)
2. **Caching**: Add instruction/data caches
3. **Branch Prediction**: Reduce branch penalty
4. **Forwarding**: Reduce data hazards in pipeline

---

## Conclusion

This architecture document provides a comprehensive overview of the RISCSim CPU implementation. Key takeaways:

- ✅ **Single-cycle design**: Simple, deterministic execution
- ✅ **Bit-accurate**: No host arithmetic operators
- ✅ **Modular**: Each component is independent and testable
- ✅ **Complete**: Supports minimum viable RV32I instruction set
- ✅ **Extensible**: Ready for pipelining, caching, extended ISA

For usage instructions, see [USAGE.md](USAGE.md).
For instruction set details, see [INSTRUCTION_SET.md](INSTRUCTION_SET.md).
