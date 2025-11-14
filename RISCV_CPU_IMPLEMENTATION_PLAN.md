# RISC-V CPU Implementation Plan

## Project Overview

Transform the existing RISCSim numeric operations simulator into a complete single-cycle RISC-V CPU simulator implementing the RV32I ISA subset. This project targets 100 base points with opportunities for up to 40 extra credit points.

**Current Status:**
- ✅ ALU (32-bit arithmetic/logic operations with flags)
- ✅ Shifter (barrel shifter: SLL, SRL, SRA)
- ✅ MDU (Multiply/Divide Unit: MUL, DIV family)
- ✅ FPU (Floating-Point Unit: FADD, FSUB, FMUL)
- ✅ Register File (32 integer + 32 FP registers)
- ✅ Control Unit (FSM for multi-cycle operations)
- ✅ Control Signals (centralized signal management)
- ✅ Comprehensive test suite (390+ tests passing)

**Required:**
- Instruction fetch and decode logic
- Data and instruction memory
- Full datapath integration
- Support for minimum viable instruction set
- Program loader for .hex files
- Test program execution

---

## Phase 1: Instruction Memory and Fetch Unit (Week 1)

### Objective
Implement instruction memory and basic instruction fetch mechanism.

### Components to Create/Modify

#### 1.1 Create `riscsim/cpu/memory.py`
```python
class Memory:
    """
    Memory unit supporting both instruction and data memory.
    - Word-addressable (32-bit words)
    - Byte-addressable with alignment checking
    - Separate I-memory and D-memory regions
    - Load/store operations
    """
    - __init__(size_bytes, base_addr)
    - read_word(addr) -> [32 bits]
    - write_word(addr, data[32 bits])
    - read_byte(addr) -> [8 bits]
    - write_byte(addr, data[8 bits])
    - load_program(hex_file_path)
```

**Key Features:**
- Support for little-endian byte ordering
- Address range checking
- Alignment verification for word accesses
- Separate instruction (0x00000000+) and data (0x00010000+) regions

**Testing Requirements:**
- `tests/test_memory.py`:
  - test_memory_initialization
  - test_word_read_write
  - test_byte_read_write
  - test_little_endian_ordering
  - test_address_alignment
  - test_address_range_checking
  - test_load_program_from_hex
  - test_instruction_data_separation
  - test_unaligned_access_error
  - test_boundary_addresses
  - **Target: 15 tests, 100% coverage**

#### 1.2 Create `riscsim/cpu/fetch.py`
```python
class FetchUnit:
    """
    Instruction fetch unit.
    - PC management
    - Instruction fetch from memory
    - PC increment logic
    """
    - __init__(memory, initial_pc)
    - fetch() -> instruction[32 bits]
    - increment_pc()
    - branch_to(target_addr[32 bits])
    - get_pc() -> [32 bits]
```

**Testing Requirements:**
- `tests/test_fetch.py`:
  - test_fetch_sequential
  - test_pc_increment
  - test_branch_absolute
  - test_branch_relative
  - test_fetch_from_different_addresses
  - test_pc_overflow
  - test_pc_alignment
  - **Target: 10 tests, 100% coverage**

#### 1.3 Create `riscsim/utils/hex_loader.py`
```python
def load_hex_file(filepath) -> List[int]:
    """
    Load .hex file into memory.
    Format: 8 hex digits per line (32-bit word)
    Returns list of 32-bit words as integers
    """

def parse_hex_line(line) -> int:
    """Parse single hex line to integer"""

def validate_hex_file(filepath) -> bool:
    """Validate hex file format"""
```

**Testing Requirements:**
- `tests/test_hex_loader.py`:
  - test_load_valid_hex_file
  - test_parse_hex_line
  - test_blank_lines_ignored
  - test_invalid_hex_format
  - test_line_length_validation
  - test_uppercase_lowercase_hex
  - test_empty_file
  - test_test_base_hex_provided
  - **Target: 10 tests, 100% coverage**

---

## Phase 2: Instruction Decoder (Week 1-2)

### Objective
Implement RISC-V instruction decoding for RV32I base instruction set.

### Components to Create/Modify

#### 2.1 Create `riscsim/cpu/decoder.py`
```python
class InstructionDecoder:
    """
    Decode 32-bit RISC-V instructions into control signals.
    Supports R-type, I-type, S-type, B-type, U-type, J-type formats.
    """
    - decode(instruction[32 bits]) -> DecodedInstruction
    - extract_opcode(instruction) -> [7 bits]
    - extract_funct3(instruction) -> [3 bits]
    - extract_funct7(instruction) -> [7 bits]
    - extract_rd(instruction) -> [5 bits]
    - extract_rs1(instruction) -> [5 bits]
    - extract_rs2(instruction) -> [5 bits]
    - extract_imm_i(instruction) -> [32 bits sign-extended]
    - extract_imm_s(instruction) -> [32 bits sign-extended]
    - extract_imm_b(instruction) -> [32 bits sign-extended]
    - extract_imm_u(instruction) -> [32 bits]
    - extract_imm_j(instruction) -> [32 bits sign-extended]
    - generate_control_signals(decoded) -> ControlSignals

class DecodedInstruction:
    """Container for decoded instruction fields"""
    - instr_type: str  # R, I, S, B, U, J
    - opcode: [7 bits]
    - funct3: [3 bits]
    - funct7: [7 bits]
    - rd: [5 bits]
    - rs1: [5 bits]
    - rs2: [5 bits]
    - immediate: [32 bits]
    - mnemonic: str
```

**RISC-V Instruction Formats:**

```
R-type: funct7[7] | rs2[5] | rs1[5] | funct3[3] | rd[5] | opcode[7]
I-type: imm[12] | rs1[5] | funct3[3] | rd[5] | opcode[7]
S-type: imm[11:5][7] | rs2[5] | rs1[5] | funct3[3] | imm[4:0][5] | opcode[7]
B-type: imm[12|10:5][7] | rs2[5] | rs1[5] | funct3[3] | imm[4:1|11][5] | opcode[7]
U-type: imm[31:12][20] | rd[5] | opcode[7]
J-type: imm[20|10:1|11|19:12][20] | rd[5] | opcode[7]
```

**Minimum Viable Instruction Set:**

| Category | Instructions |
|----------|-------------|
| Arithmetic | ADD, SUB, ADDI |
| Logical | AND, OR, XOR, ANDI, ORI, XORI |
| Shifts | SLL, SRL, SRA, SLLI, SRLI, SRAI |
| Memory | LW, SW |
| Branch | BEQ, BNE |
| Jump | JAL, JALR |
| Upper Imm | LUI, AUIPC |

**Testing Requirements:**
- `tests/test_decoder.py`:
  - **R-type tests (8 tests):**
    - test_decode_add
    - test_decode_sub
    - test_decode_and
    - test_decode_or
    - test_decode_xor
    - test_decode_sll
    - test_decode_srl
    - test_decode_sra
  - **I-type tests (8 tests):**
    - test_decode_addi
    - test_decode_andi
    - test_decode_ori
    - test_decode_xori
    - test_decode_slli
    - test_decode_srli
    - test_decode_srai
    - test_decode_lw
  - **S-type tests (1 test):**
    - test_decode_sw
  - **B-type tests (2 tests):**
    - test_decode_beq
    - test_decode_bne
  - **U-type tests (2 tests):**
    - test_decode_lui
    - test_decode_auipc
  - **J-type tests (2 tests):**
    - test_decode_jal
    - test_decode_jalr
  - **Edge cases (5 tests):**
    - test_immediate_sign_extension
    - test_immediate_zero_extension
    - test_invalid_opcode
    - test_all_zero_instruction
    - test_all_one_instruction
  - **Target: 28 tests, 100% coverage**

#### 2.2 Update `riscsim/cpu/control_signals.py`
```python
# Add RISC-V specific control signals
class ControlSignals:
    # Existing fields...
    
    # Add instruction decode signals
    - mem_read: int          # Memory read enable
    - mem_write: int         # Memory write enable
    - branch: int            # Branch instruction flag
    - jump: int              # Jump instruction flag
    - result_src: int        # Result source select (0=ALU, 1=memory, 2=PC+4)
    - pc_src: int            # PC source (0=PC+4, 1=branch target, 2=jump target)
    - alu_src_a: int         # ALU source A (0=rs1, 1=PC)
    - alu_src_b: int         # ALU source B (0=rs2, 1=immediate)
```

---

## Phase 3: Single-Cycle Datapath Integration (Week 2)

### Objective
Connect all components into a single-cycle execution pipeline.

### Components to Create/Modify

#### 3.1 Create `riscsim/cpu/datapath.py`
```python
class Datapath:
    """
    Single-cycle RISC-V datapath.
    Connects fetch, decode, execute, memory, writeback stages.
    """
    - __init__(memory, register_file)
    - execute_cycle() -> CycleResult
    - _fetch_stage() -> instruction[32 bits]
    - _decode_stage(instruction) -> DecodedInstruction, ControlSignals
    - _execute_stage(decoded, signals) -> alu_result, branch_taken
    - _memory_stage(signals, alu_result) -> mem_data
    - _writeback_stage(signals, alu_result, mem_data)
    - get_pc() -> [32 bits]
    - set_pc(addr[32 bits])
    - get_cycle_count() -> int

class CycleResult:
    """Result of single cycle execution"""
    - pc: [32 bits]
    - instruction: [32 bits]
    - decoded: DecodedInstruction
    - signals: ControlSignals
    - alu_result: [32 bits]
    - mem_data: Optional[[32 bits]]
    - writeback_data: [32 bits]
    - branch_taken: bool
    - cycle_num: int
```

**Datapath Flow:**
1. **Fetch:** Read instruction from memory at PC
2. **Decode:** Extract fields and generate control signals
3. **Execute:** Perform ALU/Shifter/MDU/FPU operation
4. **Memory:** Read/write data memory if needed
5. **Writeback:** Write result to register file

**Testing Requirements:**
- `tests/test_datapath.py`:
  - **Arithmetic tests (5 tests):**
    - test_add_instruction
    - test_addi_instruction
    - test_sub_instruction
    - test_arithmetic_with_zero_register
    - test_arithmetic_overflow
  - **Logical tests (3 tests):**
    - test_and_instruction
    - test_or_instruction
    - test_xor_instruction
  - **Shift tests (3 tests):**
    - test_sll_instruction
    - test_srl_instruction
    - test_sra_instruction
  - **Memory tests (4 tests):**
    - test_lw_instruction
    - test_sw_instruction
    - test_lw_sw_sequence
    - test_memory_alignment
  - **Branch tests (4 tests):**
    - test_beq_taken
    - test_beq_not_taken
    - test_bne_taken
    - test_bne_not_taken
  - **Jump tests (2 tests):**
    - test_jal_instruction
    - test_jalr_instruction
  - **Upper immediate tests (2 tests):**
    - test_lui_instruction
    - test_auipc_instruction
  - **Integration tests (5 tests):**
    - test_sequential_execution
    - test_register_dependencies
    - test_pc_increment
    - test_invalid_instruction
    - test_halt_detection
  - **Target: 28 tests, 100% coverage**

---

## Phase 4: CPU Simulator Top-Level (Week 3)

### Objective
Create top-level CPU simulator with program execution capabilities.

### Components to Create/Modify

#### 4.1 Create `riscsim/cpu/cpu.py`
```python
class CPU:
    """
    Top-level RISC-V CPU simulator.
    Coordinates all components and provides high-level execution interface.
    """
    - __init__(memory_size=65536, pc_start=0x00000000)
    - load_program(hex_file_path)
    - reset()
    - step() -> CycleResult  # Execute one instruction
    - run(max_cycles=10000) -> ExecutionResult  # Run until halt
    - run_until_pc(target_pc, max_cycles=10000) -> ExecutionResult
    - get_register(reg_num) -> [32 bits]
    - set_register(reg_num, value[32 bits])
    - get_memory_word(addr) -> [32 bits]
    - set_memory_word(addr, value[32 bits])
    - dump_registers() -> str
    - dump_memory(start, end) -> str
    - get_statistics() -> CPUStatistics

class ExecutionResult:
    """Result of program execution"""
    - cycles: int
    - instructions: int
    - final_pc: [32 bits]
    - halt_reason: str  # "max_cycles", "infinite_loop", "target_reached"
    - register_state: Dict
    - trace: List[CycleResult]

class CPUStatistics:
    """CPU execution statistics"""
    - total_cycles: int
    - instructions_executed: int
    - cpi: float
    - instruction_mix: Dict[str, int]  # Count per instruction type
    - branch_taken_count: int
    - branch_not_taken_count: int
    - memory_accesses: int
```

**Halt Detection:**
- Detect infinite loop: `JAL x0, 0` (jump to self)
- Max cycle limit reached
- Invalid instruction encountered

**Testing Requirements:**
- `tests/test_cpu.py`:
  - **Basic execution (5 tests):**
    - test_cpu_initialization
    - test_load_program
    - test_single_step
    - test_reset
    - test_register_access
  - **Program execution (10 tests):**
    - test_run_simple_program
    - test_run_with_branches
    - test_run_with_loops
    - test_halt_detection
    - test_max_cycles_limit
    - test_run_until_pc
    - test_infinite_loop_detection
    - test_register_writeback
    - test_memory_operations
    - test_sequential_instructions
  - **Statistics (3 tests):**
    - test_instruction_count
    - test_cpi_calculation
    - test_instruction_mix
  - **Debugging (2 tests):**
    - test_dump_registers
    - test_dump_memory
  - **Target: 20 tests, 100% coverage**

---

## Phase 5: Test Program Execution (Week 3)

### Objective
Execute and verify the provided test_base.s program and create additional test programs.

### Test Programs to Create

#### 5.1 Create `tests/programs/test_base.hex`
Provided test program:
```asm
addi x1, x0, 5          # x1 = 5
addi x2, x0, 10         # x2 = 10
add x3, x1, x2          # x3 = 15
sub x4, x2, x1          # x4 = 5
lui x5, 0x00010         # x5 = 0x00010000
sw x3, 0(x5)            # mem[0x00010000] = 15
lw x4, 0(x5)            # x4 = 15
beq x3, x4, label1      # branch forward
addi x6, x0, 1          # skipped
label1:
addi x6, x0, 2          # x6 = 2
jal x0, 0               # infinite loop
```

Expected machine code (test_base.hex):
```
00500093
00A00113
002081B3
40110233
000102B7
0032A023
0002A203
00418463
00100313
00200313
0000006F
```

#### 5.2 Create Additional Test Programs

**`tests/programs/test_arithmetic.hex`:**
- All arithmetic operations (ADD, SUB, ADDI)
- Overflow cases
- Zero register behavior

**`tests/programs/test_logical.hex`:**
- All logical operations (AND, OR, XOR, ANDI, ORI, XORI)
- All ones/all zeros cases

**`tests/programs/test_shifts.hex`:**
- All shift operations
- Shift by 0, 31, various amounts
- Sign extension verification

**`tests/programs/test_memory.hex`:**
- LW/SW with various offsets
- Memory at different addresses
- Data hazards

**`tests/programs/test_branches.hex`:**
- BEQ/BNE taken and not taken
- Forward and backward branches
- Branch prediction scenarios

**`tests/programs/test_jumps.hex`:**
- JAL with various offsets
- JALR register indirect
- Return address verification

**Testing Requirements:**
- `tests/test_programs.py`:
  - test_base_program_execution
  - test_base_program_memory_state
  - test_base_program_register_state
  - test_arithmetic_program
  - test_logical_program
  - test_shifts_program
  - test_memory_program
  - test_branches_program
  - test_jumps_program
  - test_program_statistics
  - **Target: 10 tests, execute all test programs**

---

## Phase 6: Documentation and Diagrams (Week 4)

### Objective
Create comprehensive documentation including block diagrams, datapath diagrams, and usage instructions.

### Documentation to Create/Update

#### 6.1 Create `docs/ARCHITECTURE.md`
- System overview
- Component descriptions
- Datapath diagram
- Control signal flow
- Memory map

#### 6.2 Create `docs/INSTRUCTION_SET.md`
- Supported instructions with opcodes
- Instruction format details
- Encoding examples
- Edge case behavior

#### 6.3 Create `docs/USAGE.md`
- Installation instructions
- Running test programs
- Creating custom programs
- Debugging features
- Performance analysis

#### 6.4 Update `README.md`
- Project overview
- Quick start guide
- Feature list
- Testing instructions
- GitHub repository structure

#### 6.5 Create Block Diagram
Create `docs/diagrams/cpu_block_diagram.png`:
- Shows all major components
- Signal connections
- Data flow
- Control flow

#### 6.6 Create Datapath Diagram
Create `docs/diagrams/datapath_diagram.png`:
- Five-stage pipeline view (even though single-cycle)
- Register file connections
- ALU/Memory/PC connections
- Multiplexer locations

---

## Phase 7: Integration Testing and Validation (Week 4)

### Objective
Comprehensive end-to-end testing with edge cases and corner cases.

### Testing Requirements

#### 7.1 Create `tests/test_integration_comprehensive.py`
- **Edge cases (15 tests):**
  - test_all_zeros_program
  - test_all_ones_values
  - test_max_positive_int
  - test_max_negative_int
  - test_overflow_detection
  - test_underflow_detection
  - test_unaligned_memory_access
  - test_invalid_opcode_handling
  - test_branch_to_invalid_address
  - test_jump_to_invalid_address
  - test_write_to_x0
  - test_memory_boundary_access
  - test_pc_overflow
  - test_nested_branches
  - test_chained_jumps

#### 7.2 Create `tests/test_corner_cases.py`
- **Corner cases (10 tests):**
  - test_immediate_sign_extension_edge_cases
  - test_shift_by_zero
  - test_shift_by_31
  - test_branch_backward_forward
  - test_lui_all_combinations
  - test_auipc_with_branches
  - test_jalr_with_offsets
  - test_memory_write_read_same_cycle
  - test_register_dependencies
  - test_data_forwarding_simulation

#### 7.3 Performance Testing
Create `tests/test_performance.py`:
- test_execution_speed
- test_memory_throughput
- test_cpi_calculation_accuracy
- test_large_program_execution
- test_statistics_accuracy

---

## Testing Summary

### Total Test Coverage Target

| Phase | Component | Tests | Coverage |
|-------|-----------|-------|----------|
| 1 | Memory | 15 | 100% |
| 1 | Fetch | 10 | 100% |
| 1 | Hex Loader | 10 | 100% |
| 2 | Decoder | 28 | 100% |
| 3 | Datapath | 28 | 100% |
| 4 | CPU Top-Level | 20 | 100% |
| 5 | Test Programs | 10 | N/A |
| 7 | Integration | 15 | N/A |
| 7 | Corner Cases | 10 | N/A |
| 7 | Performance | 5 | N/A |
| **Total** | | **151 new tests** | **100%** |

### Existing Tests (Keep Passing)
- ALU tests: 15 ✅
- Shifter tests: 20 ✅
- MDU tests: 25 ✅
- FPU tests: 30 ✅
- Register tests: 25 ✅
- Control Unit tests: 118 ✅
- Bit utils tests: 40 ✅
- Component tests: 15 ✅
- Integration tests: 15 ✅
- **Total existing: 303 tests ✅**

### Grand Total: 454 tests

---

## Extra Credit Opportunities (Optional)

### Pipelining (5-stage) - +15 points
**Phase 8a: Implement 5-stage pipeline**
- Create `riscsim/cpu/pipeline.py`
- Stages: IF, ID, EX, MEM, WB
- Pipeline registers between stages
- Proper stage separation

**Testing:** 20 tests covering:
- Pipeline initialization
- Register forwarding simulation
- Stage progression
- Instruction throughput

### Data/Control Hazard Management - +10-15 points
**Phase 8b: Implement hazard detection and handling**
- Data hazards (RAW, WAR, WAW)
- Control hazards (branch prediction)
- Forwarding/bypass network
- Stall logic

**Testing:** 25 tests covering:
- Hazard detection
- Forwarding paths
- Stall insertion
- Branch prediction accuracy

### Instruction Set Coverage - +5-15 points
**Phase 8c: Extend instruction set**
- Complete RV32I (all 40+ instructions)
- RV32M extension (if not already complete)
- RV32A extension (atomics)
- RV32F extension (more FP ops)

**Testing:** 30 tests for additional instructions

### Simple I/O - +5-10 points
**Phase 8d: Add I/O simulation**
- Memory-mapped I/O
- Console output
- Simple input handling
- LED/switch simulation

**Testing:** 10 tests for I/O operations

### Branch Prediction - +5-10 points
**Phase 8e: Implement branch predictor**
- Static prediction (always taken/not taken)
- Dynamic prediction (1-bit, 2-bit)
- Branch target buffer
- Prediction accuracy tracking

**Testing:** 15 tests for prediction accuracy

---

## File Structure (After Completion)

```
RISCSim/
├── riscsim/
│   ├── __init__.py
│   ├── cpu/
│   │   ├── __init__.py
│   │   ├── alu.py                    ✅ Existing
│   │   ├── shifter.py                ✅ Existing
│   │   ├── mdu.py                    ✅ Existing
│   │   ├── fpu.py                    ✅ Existing
│   │   ├── registers.py              ✅ Existing
│   │   ├── control_signals.py        ⚠️  Update
│   │   ├── control_unit.py           ✅ Existing
│   │   ├── memory.py                 🆕 Phase 1
│   │   ├── fetch.py                  🆕 Phase 1
│   │   ├── decoder.py                🆕 Phase 2
│   │   ├── datapath.py               🆕 Phase 3
│   │   ├── cpu.py                    🆕 Phase 4
│   │   └── pipeline.py               🆕 Phase 8 (Extra Credit)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── bit_utils.py              ✅ Existing
│   │   ├── components.py             ✅ Existing
│   │   ├── twos_complement.py        ✅ Existing
│   │   └── hex_loader.py             🆕 Phase 1
│   └── documentation/
│       ├── registers.md              ✅ Existing
│       └── shifter.md                ✅ Existing
├── tests/
│   ├── test_*.py                     ✅ Existing (303 tests)
│   ├── test_memory.py                🆕 Phase 1
│   ├── test_fetch.py                 🆕 Phase 1
│   ├── test_hex_loader.py            🆕 Phase 1
│   ├── test_decoder.py               🆕 Phase 2
│   ├── test_datapath.py              🆕 Phase 3
│   ├── test_cpu.py                   🆕 Phase 4
│   ├── test_programs.py              🆕 Phase 5
│   ├── test_integration_comprehensive.py 🆕 Phase 7
│   ├── test_corner_cases.py          🆕 Phase 7
│   ├── test_performance.py           🆕 Phase 7
│   └── programs/
│       ├── test_base.hex             🆕 Phase 5
│       ├── test_arithmetic.hex       🆕 Phase 5
│       ├── test_logical.hex          🆕 Phase 5
│       ├── test_shifts.hex           🆕 Phase 5
│       ├── test_memory.hex           🆕 Phase 5
│       ├── test_branches.hex         🆕 Phase 5
│       └── test_jumps.hex            🆕 Phase 5
├── docs/
│   ├── ARCHITECTURE.md               🆕 Phase 6
│   ├── INSTRUCTION_SET.md            🆕 Phase 6
│   ├── USAGE.md                      🆕 Phase 6
│   └── diagrams/
│       ├── cpu_block_diagram.png     🆕 Phase 6
│       └── datapath_diagram.png      🆕 Phase 6
├── examples/
│   ├── *.py                          ✅ Existing
│   ├── simple_program.py             🆕 Phase 5
│   └── custom_program_loader.py      🆕 Phase 5
├── README.md                         ⚠️  Update
├── PROJECTINSTRUCTIONS.md            ✅ Existing
├── PROJECT_ARCHITECTURE.md           ✅ Existing
├── AI_USAGE.md                       ✅ Existing
├── RISCV_CPU_IMPLEMENTATION_PLAN.md  🆕 This file
├── pyproject.toml                    ✅ Existing
└── requirements.txt                  ✅ Existing
```

---

## Implementation Guidelines

### Code Quality Standards

1. **Follow existing patterns:**
   - Use bit arrays [0/1] for all data
   - MSB at index 0 convention
   - No host arithmetic operators in implementation
   - Boundary functions only for I/O conversion

2. **Documentation:**
   - Comprehensive docstrings for all functions/classes
   - Type hints where applicable
   - Usage examples in docstrings
   - Trace generation for debugging

3. **Testing:**
   - 100% code coverage for new components
   - Edge cases and corner cases
   - Integration tests
   - Performance benchmarks

4. **Git workflow:**
   - Feature branches for each phase
   - Descriptive commit messages
   - Pull requests with review
   - Merge to main after testing

### Constraints Compliance

**Strict "No Host Operators" Rule:**
- ✅ Use existing ALU for all arithmetic
- ✅ Use existing Shifter for all shifts
- ✅ Use bit_utils functions for bit manipulation
- ❌ Never use +, -, *, /, %, <<, >> in implementation
- ✅ I/O boundary functions OK for format conversion only

**Memory Representation:**
- All data as bit arrays [0/1]
- Little-endian byte ordering
- Word-aligned access validation
- Address bounds checking

---

## Timeline (4-Week Plan)

### Week 1: Memory and Fetch
- **Days 1-2:** Memory implementation and testing
- **Days 3-4:** Fetch unit and PC management
- **Days 5-7:** Hex loader and integration

### Week 2: Decoder and Datapath
- **Days 8-10:** Instruction decoder
- **Days 11-13:** Datapath integration
- **Day 14:** Integration testing

### Week 3: CPU and Programs
- **Days 15-16:** CPU top-level
- **Days 17-19:** Test program execution
- **Days 20-21:** Additional test programs

### Week 4: Documentation and Testing
- **Days 22-23:** Documentation and diagrams
- **Days 24-25:** Comprehensive integration testing
- **Days 26-27:** Corner cases and performance
- **Day 28:** Final review and submission prep

---

## Success Criteria

### Minimum for 100 Base Points
- ✅ All phases 1-7 completed
- ✅ 151+ new tests passing
- ✅ All existing 303 tests still passing
- ✅ test_base.hex executes correctly
- ✅ Comprehensive documentation
- ✅ Block and datapath diagrams
- ✅ GitHub repository with clear history

### Extra Credit (Up to 40 Points)
- Phase 8a: Pipelining (+15)
- Phase 8b: Hazard management (+10-15)
- Phase 8c: Extended ISA (+5-15)
- Phase 8d: I/O simulation (+5-10)
- Phase 8e: Branch prediction (+5-10)

---

## AI Usage Documentation

All AI assistance must be documented in `AI_USAGE.md` including:
- What AI tool was used (GitHub Copilot, ChatGPT, etc.)
- What it was used for
- Representative prompts and responses
- Code generation vs. debugging vs. explanation

---

## Deliverables Checklist

- [ ] Phase 1: Memory and Fetch (15 + 10 + 10 = 35 tests)
- [ ] Phase 2: Decoder (28 tests)
- [ ] Phase 3: Datapath (28 tests)
- [ ] Phase 4: CPU Top-Level (20 tests)
- [ ] Phase 5: Test Programs (10 test programs)
- [ ] Phase 6: Documentation (4 docs + 2 diagrams)
- [ ] Phase 7: Integration Testing (30 tests)
- [ ] README.md updated
- [ ] GitHub repository with branches
- [ ] test_base.hex executes correctly
- [ ] All 454 tests passing
- [ ] AI usage documented
- [ ] Final submission on Canvas

---

## Contact and Support

For questions or issues during implementation:
- Review existing code patterns in riscsim/cpu/
- Check test files for usage examples
- Consult PROJECT_ARCHITECTURE.md for design principles
- Follow PROJECTINSTRUCTIONS.md for constraints

---

**Last Updated:** December 2024  
**Status:** Planning Complete - Ready for Implementation
