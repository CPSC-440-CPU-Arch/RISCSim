# Control Unit FSM Development Plan
## Building a Cycle-Accurate FSM-Based Control Unit

**Date Started**: November 13, 2025  
**Last Updated**: November 14, 2025  
**Status**: Phase 7 Partial (Tasks 2 & 4) Complete - 390 tests passing (100%)  
**Goal**: Build a full FSM-based control unit that sequences multi-cycle operations with cycle-accurate behavior

### Progress Summary
- ✅ **Phase 1 COMPLETE**: Data Path Infrastructure (8 tests)
- ✅ **Phase 2 COMPLETE**: ALU Integration (8 tests)
- ✅ **Phase 3 COMPLETE**: Shifter Integration (6 tests)
- ✅ **Phase 4 COMPLETE**: MDU Multi-Cycle Integration (8 tests)
- ✅ **Phase 5 COMPLETE**: FPU Multi-Cycle Integration (10 tests)
- ✅ **Phase 6 COMPLETE**: Complete Instruction Execution (15 tests)
- ⏳ **Phase 7 IN PROGRESS**: Performance Counters ✅ (20 tests) + Documentation ✅
- ⏳ Phase 8: Pending (System Integration)

---

## Current State Analysis

### ✅ What We Have

1. **`control_signals.py`** - Complete control signal definitions
   - All required signals: `alu_op`, `rf_we`, `rf_waddr`, `src_a_sel`, `src_b_sel`, `sh_op`, `md_start`, `md_busy`, `md_done`, `fpu_state`, `round_mode`
   - State constants for FPU and MDU FSMs
   - Helper functions for signal formatting and decoding

2. **`control_unit.py`** - FSM infrastructure (118 control unit tests passing)
   - Main FSM states: IDLE → EXECUTE → WRITEBACK
   - Sub-FSMs for MDU and FPU
   - Start methods for all operation types
   - Basic `tick()` method for cycle advancement
   - Trace generation capabilities
   - **Phase 6 unified interface**: `execute_instruction()` with automatic routing to all functional units
   - **Phase 7 performance monitoring**: Comprehensive performance counters and statistics
   - **Phase 7 documentation**: Enhanced module documentation with architecture overview

3. **Component Integration** (272 tests passing)
   - `alu_with_control()`, `shifter_with_control()`
   - `mdu_with_control()`, `fpu_with_control()`
   - `register_with_control()`
   - All synchronous wrappers working

4. **Integration Tests** (12 tests passing)
   - 12 end-to-end tests verifying component cooperation
   - Trace verification tests

5. **Comprehensive Tests** (6 tests passing)
   - All functional units validated through unified interface
   - Register isolation and x0 immutability verified

### ✅ What We Have Built (Phases 1-6 Complete)

1. **Data Path Simulation**
   - Actual operand values flowing through pipeline
   - Multiplexer selection based on `src_a_sel`, `src_b_sel`
   - Intermediate result storage during multi-cycle ops
   - Unified instruction execution interface

2. **Register File Integration**
   - Connect control unit to actual RegisterFile instance
   - Read/write operations controlled by FSM signals

3. **Component Integration**
   - Connect ALU, Shifter, MDU, FPU to control unit
   - Data flow between components based on control signals

4. **Full Execution Method**
   - High-level method to execute complete instructions
   - Automatic cycling until operation completes

5. **Advanced Testing**
   - Cycle-by-cycle verification
   - State transition validation
   - Signal timing tests
   - Data correctness throughout pipeline

---

## Development Phases

### Phase 1: Data Path Infrastructure (Est: 2-3 hours) ✅ COMPLETE

**Goal**: Add data storage and flow capabilities to the Control Unit

**Status**: ✅ **COMPLETED** - All 8 tests passing (317 total tests passing)

**Completed Tasks**:
1. ✅ Added data registers to ControlUnit:
   - `operand_a`, `operand_b` - Source operand storage
   - `alu_result`, `shifter_result`, `mdu_result`, `fpu_result`
   - `writeback_data` - Final result to write
   - `immediate` - Immediate value storage

2. ✅ Added multiplexer logic:
   - Implemented `_select_operand_a()` method (register vs immediate vs PC)
   - Implemented `_select_operand_b()` method (register vs immediate vs constant)
   - Result mux for different functional units via `_select_result()`

3. ✅ Created RegisterFile connection:
   - Added `self.register_file` attribute with optional injection
   - Implemented `_read_registers()` method
   - Implemented `_write_register()` method
   - **BONUS**: Enhanced RegisterFile to accept bit arrays directly (meeting strict requirements)

**Files Modified**:
- ✅ `riscsim/cpu/control_unit.py` - Added data path infrastructure
- ✅ `riscsim/cpu/registers.py` - Enhanced to accept bit arrays (5-bit addresses)

**Tests Added** (`tests/test_control_unit_datapath.py`): ✅ 8/8 passing
- ✅ test_operand_storage
- ✅ test_src_a_multiplexer
- ✅ test_src_b_multiplexer  
- ✅ test_register_read_integration
- ✅ test_register_write_integration
- ✅ test_result_multiplexer
- ✅ test_immediate_value_setting
- ✅ test_data_path_with_register_file_integration

**Success Criteria**: ✅ All met - 8 new tests passing, data flows through control unit, 317 total tests passing

---

### Phase 2: ALU Integration (Est: 2 hours) ✅ COMPLETE

**Goal**: Connect ALU to control unit with cycle-accurate execution

**Status**: ✅ **COMPLETED** - All 8 tests passing (325 total tests passing)

**Completed Tasks**:
1. ✅ Integrated ALU into control unit:
   - Imported and instantiated ALU operations
   - Call ALU during EXECUTE state with actual operands
   - Store ALU result for writeback

2. ✅ Updated `_tick_alu()` method:
   - Reads registers into operands
   - Performs actual ALU operation using stored operands
   - Generates correct control signals at each cycle
   - Handles result writeback to register file

3. ✅ Created execute helper:
   - `execute_alu_instruction()` - Complete ALU instruction execution with automatic cycling

**Files Modified**:
- ✅ `riscsim/cpu/control_unit.py` - Integrated ALU execution

**Tests Added** (`tests/test_control_unit_alu.py`): ✅ 8/8 passing
- ✅ test_alu_add_cycle_by_cycle
- ✅ test_alu_sub_with_trace
- ✅ test_alu_and_or_xor_sequence
- ✅ test_alu_result_writeback
- ✅ test_alu_control_signals_each_cycle
- ✅ test_alu_with_different_registers
- ✅ test_alu_x0_hardwired_to_zero
- ✅ test_alu_operation_isolation

**Success Criteria**: ✅ All met - 8 new tests passing, ALU operations execute correctly cycle-by-cycle, 325 total tests passing

---

### Phase 3: Shifter Integration (Est: 2 hours) ✅ COMPLETE

**Goal**: Connect Shifter to control unit with cycle-accurate execution

**Status**: ✅ **COMPLETED** - All 6 tests passing (331 total tests passing)

**Completed Tasks**:
1. ✅ Integrated Shifter into control unit:
   - Imported shifter module
   - Calls shifter during EXECUTE state with actual operands
   - Stores shifter result for writeback

2. ✅ Updated `_tick_shifter()` method:
   - Reads registers into operands
   - Performs actual shift operation using stored operands
   - **FIXED**: Converts 3-bit control signal op to 2-bit shifter op
   - Generates correct control signals at each cycle
   - Handles result writeback to register file

3. ✅ Created execute helper:
   - `execute_shifter_instruction()` - Complete shifter instruction execution with automatic cycling

**Files Modified**:
- ✅ `riscsim/cpu/control_unit.py` - Integrated Shifter execution with op code conversion

**Tests Added** (`tests/test_control_unit_shifter.py`): ✅ 6/6 passing
- ✅ test_shifter_sll_cycle_by_cycle
- ✅ test_shifter_srl_with_trace
- ✅ test_shifter_sra_execution
- ✅ test_shifter_result_writeback
- ✅ test_shifter_control_signals
- ✅ test_shifter_variable_amounts

**Success Criteria**: ✅ All met - 6 new tests passing, Shifter operations execute correctly cycle-by-cycle, 331 total tests passing

---

### Phase 4: MDU Multi-Cycle Integration (Est: 3-4 hours) ✅ COMPLETE

**Goal**: Implement cycle-accurate MDU operations with visible state transitions

**Status**: ✅ **COMPLETED** - All 8 tests passing (339 total tests passing)

**Completed Tasks**:
1. ✅ Integrated MDU into control unit:
   - Imported `mdu_mul` and `mdu_div` functions
   - Calls MDU functions during first cycle of operation
   - Stores results and intermediate values (quotient, remainder, partial products)

2. ✅ Enhanced `_tick_mdu_multiply()`:
   - Performs actual multiplication on cycle 1
   - Cycles through 32 iterations with SHIFT ↔ ADD state transitions
   - Updates `md_busy` and `md_done` signals correctly
   - Handles writeback with `rf_we` signal

3. ✅ Enhanced `_tick_mdu_divide()`:
   - Performs actual division on cycle 1
   - Cycles through 32 iterations with TESTBIT → SUB → RESTORE → SHIFT transitions
   - Correctly returns quotient (DIV/DIVU) or remainder (REM/REMU)
   - Handles writeback with `rf_we` signal

4. ✅ Created execute helper:
   - `execute_mdu_instruction()` - Complete MDU instruction with all cycles
   - Returns quotient, remainder, and partial product data

**Files Modified**:
- ✅ `riscsim/cpu/control_unit.py` - Integrated MDU multiply and divide with cycle-accurate execution

**Tests Added** (`tests/test_control_unit_mdu.py`): ✅ 8/8 passing
- ✅ test_mul_32_cycles
- ✅ test_mul_partial_products
- ✅ test_mul_busy_done_signals
- ✅ test_div_cycle_by_cycle
- ✅ test_div_testbit_sub_restore_transitions
- ✅ test_div_quotient_remainder_building
- ✅ test_mdu_state_trace
- ✅ test_mdu_writeback

**Success Criteria**: ✅ All met - 8 new tests passing, MDU shows all 32+ cycles with correct state transitions, 339 total tests passing

---

### Phase 5: FPU Multi-Cycle Integration (Est: 3-4 hours) ✅ COMPLETE

**Goal**: Implement cycle-accurate FPU operations with pipeline stages

**Status**: ✅ **COMPLETED** - All 10 tests passing (349 total tests passing)

**Completed Tasks**:
1. ✅ Integrated FPU into control unit:
   - Imported `fadd_f32` and `fmul_f32` functions
   - Calls FPU functions during ALIGN stage
   - Stores results and exception flags

2. ✅ Enhanced `_tick_fpu()`:
   - Performs actual FP computation in ALIGN state
   - Handles FSUB by negating operand B's sign bit
   - Cycles through ALIGN → OP → NORMALIZE → ROUND → WRITEBACK stages
   - Updates `fpu_state` signal at each stage
   - Handles writeback with `rf_we` signal

3. ✅ Fixed register file access:
   - Updated `_read_registers()` to use FP registers for FPU operations
   - Updated `_write_register()` to use FP registers for FPU operations
   - Integer operations still use integer register file

4. ✅ Created execute helper:
   - `execute_fpu_instruction()` - Complete FPU instruction through all pipeline stages
   - Accepts rounding mode parameter
   - Returns exception flags

**Files Modified**:
- ✅ `riscsim/cpu/control_unit.py` - Integrated FPU with 5-stage pipeline and FP register support

**Tests Added** (`tests/test_control_unit_fpu.py`): ✅ 10/10 passing
- ✅ test_fadd_align_stage
- ✅ test_fadd_op_stage
- ✅ test_fadd_normalize_stage
- ✅ test_fadd_round_stage
- ✅ test_fadd_complete_pipeline
- ✅ test_fmul_pipeline_stages
- ✅ test_fpu_state_transitions
- ✅ test_fpu_rounding_modes
- ✅ test_fsub_operation
- ✅ test_fpu_writeback_to_register

**Success Criteria**: ✅ All met - 10 new tests passing, FPU shows all pipeline stages with correct state, 349 total tests passing

---

### Phase 6: Complete Instruction Execution (Est: 2-3 hours) ✅ COMPLETE

**Goal**: High-level instruction execution with automatic routing to functional units

**Status**: ✅ **COMPLETED** - All 15 tests passing (364 total tests passing)

**Completed Tasks**:
1. ✅ Created unified execution interface:
   - `execute_instruction(op_type, operation, rs1, rs2, rd, **kwargs)` method
   - Validates idle state before execution
   - Decodes `op_type` ('ALU', 'SHIFTER', 'MDU', 'FPU')
   - Routes to appropriate functional unit
   - Returns unified result dict with trace, cycles, success, etc.

2. ✅ Added instruction decoding:
   - Type-based routing (ALU/Shifter/MDU/FPU)
   - Flexible kwargs for unit-specific parameters (shamt, immediate, rounding_mode)
   - Explicit error messages for invalid types
   - Parameter validation (e.g., shifter requires shamt)

3. ✅ Created convenience methods:
   - `execute_and_get_result()` - Returns only 32-bit result value, raises RuntimeError on failure
   - `execute_and_get_trace()` - Returns cycle-by-cycle trace list
   - `execute_with_timeout()` - Safety wrapper with configurable timeout and 'timed_out' flag

**Files Modified**:
- ✅ `riscsim/cpu/control_unit.py` - Added ~170 lines of Phase 6 code (4 new methods)

**Tests Added** (`tests/test_control_unit_execution.py`): ✅ 15/15 passing
- ✅ test_execute_alu_add_instruction
- ✅ test_execute_shifter_sll_instruction
- ✅ test_execute_mdu_mul_instruction
- ✅ test_execute_mdu_div_instruction
- ✅ test_execute_fpu_fadd_instruction
- ✅ test_execute_with_trace
- ✅ test_mixed_instruction_sequence
- ✅ test_execute_and_get_result
- ✅ test_execute_and_get_result_failure
- ✅ test_execute_and_get_trace
- ✅ test_execute_with_timeout
- ✅ test_execute_with_timeout_exceeded
- ✅ test_invalid_operation_type
- ✅ test_shifter_requires_shamt
- ✅ test_must_be_idle_before_execute

**Success Criteria**: ✅ All met - 15 new tests passing, unified interface working for all instruction types, 364 total tests passing

---

### Phase 7: Advanced Features & Polish (Est: 2-3 hours) ⏳ IN PROGRESS

**Goal**: Add advanced features and comprehensive testing

**Status**: **Tasks 2 & 4 COMPLETED** - Performance counters and documentation done (20 tests passing)

**Tasks**:
1. ⏳ Implement hazard detection (NOT STARTED):
   - RAW (Read After Write) hazard detection
   - Forwarding logic simulation
   - Stall detection

2. ✅ **Add performance counters (COMPLETE)**:
   - ✅ Total cycles counter
   - ✅ Instruction count
   - ✅ CPI (Cycles Per Instruction) calculation
   - ✅ IPC (Instructions Per Cycle) calculation
   - ✅ Functional unit utilization (ALU, Shifter, MDU, FPU, Idle)
   - ✅ Per-unit cycle counters
   - ✅ get_performance_stats() method
   - ✅ print_performance_stats() method
   - ✅ reset_performance_counters() method

3. ⏳ Enhanced trace visualization (NOT STARTED):
   - Pretty-print traces with timing diagrams
   - Export traces to JSON/CSV
   - Cycle-by-cycle signal viewer

4. ✅ **Documentation (COMPLETE)**:
   - ✅ Enhanced module-level docstring with architecture overview
   - ✅ State machine documentation for all units
   - ✅ Data path description
   - ✅ Performance monitoring documentation
   - ✅ Comprehensive usage examples
   - ✅ Testing and validation guide
   - ✅ Phase development history
   - ✅ All methods already have complete docstrings

**Files Modified**:
- ✅ `riscsim/cpu/control_unit.py` - Added performance counters and enhanced documentation (~140 lines added)

**Tests Added** (`tests/test_control_unit_performance.py`): ✅ 20/20 passing
- ✅ TestPerformanceCounters (8 tests):
  * test_counters_initialized_to_zero
  * test_total_cycles_increment
  * test_instruction_count_increment
  * test_alu_cycles_tracking
  * test_shifter_cycles_tracking
  * test_mdu_cycles_tracking
  * test_fpu_cycles_tracking
  * test_mixed_operation_cycles
- ✅ TestPerformanceStats (5 tests):
  * test_get_performance_stats_structure
  * test_cpi_calculation
  * test_utilization_percentages
  * test_mdu_high_utilization
  * test_stats_with_no_operations
- ✅ TestPerformanceReset (3 tests):
  * test_reset_performance_counters
  * test_reset_doesnt_affect_state
  * test_counters_work_after_reset
- ✅ TestPerformancePrinting (2 tests):
  * test_print_performance_stats_no_crash
  * test_print_stats_with_zero_operations
- ✅ TestComplexScenarios (2 tests):
  * test_long_program_sequence
  * test_mixed_program_with_all_units

**Success Criteria**: 
- ✅ Performance counters: 20 tests passing, all metrics working
- ✅ Documentation: Comprehensive module docs added
- ⏳ Hazard detection: Not started
- ⏳ Trace visualization: Not started
- **Current Status**: 390 total tests passing (118 control unit tests)

---

### Phase 8: Full System Integration & Validation (Est: 2 hours)

**Goal**: Verify complete system works together

**Tasks**:
1. Create comprehensive integration tests:
   - Run complete programs through control unit
   - Verify all signals at every cycle
   - Check data correctness throughout

2. Performance validation:
   - Measure execution time
   - Verify cycle counts match expectations
   - Compare against reference implementations

3. Create example programs:
   - Fibonacci calculation
   - Factorial computation
   - Floating-point calculations
   - Mixed integer/FP programs

**Files to Create**:
- `examples/control_unit_programs.py`
- `tests/test_control_unit_programs.py`

**Tests to Add**:
- test_fibonacci_program
- test_factorial_program
- test_fp_calculation_program
- test_mixed_program
- test_cycle_accuracy

**Success Criteria**: 5 new tests passing, example programs run correctly

---

## Testing Strategy

### Unit Tests
- Each phase has dedicated test file
- Test individual FSM state transitions
- Verify control signal generation
- Check data correctness at each stage

### Integration Tests
- Test complete instruction execution
- Verify multi-cycle operations
- Check component interactions
- Validate trace output

### Regression Tests
- Ensure all 309 existing tests still pass
- No breaking changes to component interfaces
- Backward compatibility maintained

### Acceptance Tests
- Run reference instruction sequences
- Compare against expected behavior
- Verify cycle-accurate execution
- Validate all control signals

---

## Expected Test Count Progression

| Phase | New Tests | Cumulative | Description | Status |
|-------|-----------|------------|-------------|--------|
| Current | 0 | 309 | Starting point (25 CU + 284 components) | ✅ |
| Phase 1 | 8 | 317 | Data path infrastructure | ✅ COMPLETE |
| Phase 2 | 8 | 325 | ALU integration | ✅ COMPLETE |
| Phase 3 | 6 | 331 | Shifter integration | ✅ COMPLETE |
| Phase 4 | 8 | 339 | MDU multi-cycle | ✅ COMPLETE |
| Phase 5 | 10 | 349 | FPU multi-cycle | ✅ COMPLETE |
| Phase 6 | 15 | 364 | Unified instruction execution | ✅ COMPLETE |
| Phase 7 | 20 | 384 | Performance counters (tasks 2 & 4) | ✅ PARTIAL COMPLETE |
| Phase 8 | TBD | TBD | System integration | ⏳ PENDING |

**Target**: ~390+ total tests, 100% passing
**Current Progress**: 390 tests (100% passing, Phases 1-6 complete + Phase 7 partial)
**Breakdown**: 118 control unit tests + 272 component tests

---

## Implementation Notes

### Key Design Principles

1. **Separation of Concerns**:
   - FSM logic separate from data operations
   - Control signals drive behavior
   - Components remain independent

2. **Cycle Accuracy**:
   - Each `tick()` represents one clock cycle
   - State changes happen on cycle boundaries
   - Signals visible at each cycle

3. **Traceability**:
   - Full trace of every cycle
   - All control signals captured
   - Easy debugging and verification

4. **Extensibility**:
   - Easy to add new instructions
   - New functional units can integrate
   - Flexible state machine design

### Potential Challenges

1. **Complexity Management**:
   - Many state variables to track
   - Complex state transitions
   - Solution: Clear state diagrams, good comments

2. **Cycle Timing**:
   - Ensuring correct cycle counts
   - Synchronizing multiple FSMs
   - Solution: Comprehensive cycle-by-cycle tests

3. **Data Handling**:
   - Managing intermediate values
   - Proper multiplexer selection
   - Solution: Clear data flow documentation

4. **Test Coverage**:
   - Many edge cases to cover
   - Complex multi-cycle sequences
   - Solution: Systematic test generation

---

## Success Metrics

### Functionality
- ✅ All instruction types execute correctly
- ✅ Cycle-accurate behavior verified
- ✅ All control signals generated properly
- ✅ Complete traces available

### Quality
- ✅ 100% test pass rate
- ✅ All FSM states tested
- ✅ Edge cases covered
- ✅ Clean code architecture

### Performance
- ✅ Fast test execution (< 1 second)
- ✅ Efficient state management
- ✅ Reasonable memory usage

### Documentation
- ✅ Complete docstrings
- ✅ Usage examples
- ✅ Architecture diagrams
- ✅ State transition documentation

---

## Timeline Estimate

**Total Estimated Time**: 18-23 hours

- Phase 1: 2-3 hours
- Phase 2: 2 hours
- Phase 3: 2 hours
- Phase 4: 3-4 hours
- Phase 5: 3-4 hours
- Phase 6: 2-3 hours
- Phase 7: 2-3 hours
- Phase 8: 2 hours

**Recommended Schedule**: 2-3 weeks at 8-10 hours/week

---

## Next Steps

1. Review and approve this plan
2. Begin Phase 1: Data Path Infrastructure
3. Implement phase-by-phase with testing at each step
4. Document progress as we go
5. Iterate and refine based on findings

---

## Notes

- This plan builds on our existing 309 passing tests
- Each phase is independent and testable
- Backward compatibility maintained throughout
- Focus on cycle-accurate, educational implementation
- All phases follow test-driven development

**Status**: Ready to begin Phase 1
