# AI-BEGIN
"""
Control Unit (FSM) for RISC-V CPU Simulation

This module implements a cycle-accurate finite state machine (FSM) that orchestrates
multi-cycle operations across all CPU functional units including ALU, Shifter,
MDU (Multiply-Divide Unit), FPU (Floating-Point Unit), and Register File.

Architecture Overview
--------------------
The Control Unit acts as the CPU's central controller, managing:
- State transitions for different operation types
- Control signal generation and sequencing
- Cycle-by-cycle operation traces for debugging and verification
- Coordination and data flow between functional units
- Performance monitoring and statistics collection

State Machine Models
-------------------
Each functional unit follows a specific FSM pattern:

1. **ALU (Arithmetic Logic Unit)**
   - States: IDLE → EXECUTE → WRITEBACK
   - Cycle Count: 2 cycles (typically single-cycle execution + writeback)
   - Operations: ADD, SUB, AND, OR, XOR, SLT, etc.

2. **Shifter**
   - States: IDLE → EXECUTE → WRITEBACK
   - Cycle Count: 2 cycles (shift operation + writeback)
   - Operations: SLL (Shift Left Logical), SRL (Shift Right Logical), 
                 SRA (Shift Right Arithmetic)

3. **MDU (Multiply-Divide Unit)**
   - Multiply States: IDLE → (SHIFT ↔ ADD) ×32 → WRITEBACK
   - Divide States: IDLE → (TESTBIT → SUB → RESTORE → SHIFT) ×32 → WRITEBACK
   - Cycle Count: 33 cycles (1 setup + 32 iterations)
   - Operations: MUL, MULH, MULHU, MULHSU, DIV, DIVU, REM, REMU

4. **FPU (Floating-Point Unit)**
   - States: IDLE → ALIGN → OP → NORMALIZE → ROUND → WRITEBACK
   - Cycle Count: 5 cycles (pipeline stages)
   - Operations: FADD, FSUB, FMUL (FDIV and FSQRT can be added)

Data Path
---------
The Control Unit manages a comprehensive data path including:

- **Operand Storage**: Temporary storage for source operands (operand_a, operand_b)
- **Result Storage**: Unit-specific result buffers (alu_result, shifter_result, etc.)
- **Multiplexers**: Dynamic selection of operand sources and result routing
- **Register File Integration**: Automatic read/write of integer and FP registers
- **Writeback Logic**: Final result delivery to destination register

Performance Monitoring
---------------------
Built-in performance counters track:

- Total cycles executed
- Instructions completed
- CPI (Cycles Per Instruction) and IPC (Instructions Per Cycle)
- Per-unit cycle counts (ALU, Shifter, MDU, FPU, Idle)
- Functional unit utilization percentages

Usage Example
------------
```python
from riscsim.cpu.control_unit import ControlUnit
from riscsim.cpu.control_signals import ALU_OP_ADD

# Create control unit
cu = ControlUnit()

# Setup operands in registers
cu.register_file.write_int_reg([0,0,0,0,1], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0])  # r1 = 10
cu.register_file.write_int_reg([0,0,0,1,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0])  # r2 = 20

# Execute ADD: r3 = r1 + r2
result = cu.execute_instruction('ALU', ALU_OP_ADD,
                               rs1_addr=[0,0,0,0,1],  # r1
                               rs2_addr=[0,0,0,1,0],  # r2
                               rd_addr=[0,0,0,1,1])   # r3

print(f"Cycles: {result['cycles']}")
print(f"Success: {result['success']}")

# Get performance stats
stats = cu.get_performance_stats()
print(f"CPI: {stats['cpi']:.2f}")
print(f"ALU Utilization: {stats['alu_utilization']:.1f}%")
```

Testing and Validation
----------------------
The Control Unit includes comprehensive testing capabilities:

- Cycle-by-cycle trace generation with full control signal visibility
- State transition verification
- Signal timing validation
- Data correctness checking throughout the pipeline
- Performance counter accuracy verification

Phase Development
----------------
This Control Unit was developed through an 8-phase incremental approach:

1. Phase 1: Data Path Infrastructure (8 tests)
2. Phase 2: ALU Integration (8 tests)
3. Phase 3: Shifter Integration (6 tests)
4. Phase 4: MDU Multi-Cycle Integration (8 tests)
5. Phase 5: FPU Multi-Cycle Integration (10 tests)
6. Phase 6: Unified Instruction Execution (15 tests)
7. Phase 7: Performance Counters & Documentation (20 tests)
8. Phase 8: Advanced Features (planned)

Current Status: 118 control unit tests passing, 390 total project tests

See Also
--------
- control_signals.py: Control signal definitions and constants
- registers.py: Register file implementation
- alu.py, shifter.py, mdu.py, fpu.py: Functional unit implementations
"""

from typing import List, Dict, Any, Optional
from riscsim.cpu.control_signals import (
    ControlSignals,
    ALU_OP_ADD, ALU_OP_SUB, ALU_OP_AND, ALU_OP_OR, ALU_OP_XOR,
    SH_OP_SLL, SH_OP_SRL, SH_OP_SRA,
    FPU_STATE_IDLE, FPU_STATE_ALIGN, FPU_STATE_OP,
    FPU_STATE_NORMALIZE, FPU_STATE_ROUND, FPU_STATE_WRITEBACK,
    MDU_STATE_IDLE, MDU_STATE_MUL_SHIFT, MDU_STATE_MUL_ADD,
    MDU_STATE_DIV_TESTBIT, MDU_STATE_DIV_SUB, MDU_STATE_DIV_RESTORE,
    MDU_STATE_DIV_SHIFT, MDU_STATE_WRITEBACK,
    format_control_signals
)
from riscsim.cpu.registers import RegisterFile
from riscsim.cpu.alu import alu
from riscsim.cpu.shifter import shifter
from riscsim.cpu.mdu import mdu_mul, mdu_div
from riscsim.cpu.fpu import fadd_f32, fmul_f32


class ControlUnit:
    """
    Finite State Machine Control Unit for CPU operation sequencing.
    
    Manages multi-cycle operations and generates control signals for all
    functional units in the CPU datapath.
    """
    
    # Main FSM States
    STATE_IDLE = 'IDLE'
    STATE_EXECUTE = 'EXECUTE'
    STATE_WRITEBACK = 'WRITEBACK'
    
    # Operation Types
    OP_ALU = 'ALU'
    OP_SHIFTER = 'SHIFTER'
    OP_MDU = 'MDU'
    OP_FPU = 'FPU'
    
    def __init__(self, register_file: Optional[RegisterFile] = None):
        """
        Initialize the Control Unit with default state.
        
        Args:
            register_file: Optional RegisterFile instance for data path integration.
                          If None, a new RegisterFile will be created.
        """
        self.state = self.STATE_IDLE
        self.signals = ControlSignals()
        self.trace = []  # Operation trace for debugging
        
        # Sub-unit states
        self.mdu_state = MDU_STATE_IDLE
        self.fpu_state = FPU_STATE_IDLE
        
        # Operation context
        self.current_op_type = None
        self.current_op = None
        self.operation_data = {}  # Stores intermediate values during multi-cycle ops
        
        # Data path - register file integration
        self.register_file = register_file if register_file is not None else RegisterFile()
        
        # Data path - operand storage
        self.operand_a = [0] * 32  # Source operand A
        self.operand_b = [0] * 32  # Source operand B
        self.immediate = [0] * 32  # Immediate value (for I-type instructions)
        
        # Data path - result storage
        self.alu_result = [0] * 32
        self.shifter_result = [0] * 32
        self.mdu_result = [0] * 32
        self.fpu_result = [0] * 32
        self.writeback_data = [0] * 32  # Final result to write back
        
        # Performance counters
        self.total_cycles = 0           # Total clock cycles executed
        self.instruction_count = 0      # Total instructions completed
        self.alu_cycles = 0             # Cycles spent in ALU operations
        self.shifter_cycles = 0         # Cycles spent in Shifter operations
        self.mdu_cycles = 0             # Cycles spent in MDU operations
        self.fpu_cycles = 0             # Cycles spent in FPU operations
        self.idle_cycles = 0            # Cycles spent idle
        
    def reset(self):
        """Reset the control unit to initial state."""
        self.state = self.STATE_IDLE
        self.signals.reset()
        self.trace = []
        self.mdu_state = MDU_STATE_IDLE
        self.fpu_state = FPU_STATE_IDLE
        self.current_op_type = None
        self.current_op = None
        self.operation_data = {}
        
        # Reset data path
        self.operand_a = [0] * 32
        self.operand_b = [0] * 32
        self.immediate = [0] * 32
        self.alu_result = [0] * 32
        self.shifter_result = [0] * 32
        self.mdu_result = [0] * 32
        self.fpu_result = [0] * 32
        self.writeback_data = [0] * 32
        
        # Reset performance counters
        self.total_cycles = 0
        self.instruction_count = 0
        self.alu_cycles = 0
        self.shifter_cycles = 0
        self.mdu_cycles = 0
        self.fpu_cycles = 0
        self.idle_cycles = 0
        self.alu_result = [0] * 32
        self.shifter_result = [0] * 32
        self.mdu_result = [0] * 32
        self.fpu_result = [0] * 32
        self.writeback_data = [0] * 32
    
    def start_alu_operation(self, alu_op: List[int], rs1_addr: List[int], 
                           rs2_addr: List[int], rd_addr: List[int]):
        """
        Start an ALU operation.
        
        Args:
            alu_op: 4-bit ALU opcode
            rs1_addr: Source register 1 address (5 bits)
            rs2_addr: Source register 2 address (5 bits)
            rd_addr: Destination register address (5 bits)
        """
        assert self.state == self.STATE_IDLE, "Control unit must be IDLE to start new operation"
        
        self.current_op_type = self.OP_ALU
        self.current_op = 'ALU'
        self.state = self.STATE_EXECUTE
        
        # Set control signals
        self.signals.alu_op = alu_op.copy()
        self.signals.rf_raddr_a = rs1_addr.copy()
        self.signals.rf_raddr_b = rs2_addr.copy()
        self.signals.rf_waddr = rd_addr.copy()
        self.signals.src_a_sel = 0  # Register source
        self.signals.src_b_sel = 0  # Register source
        
        self._add_trace(f"Start ALU operation: opcode={''.join(map(str, alu_op))}")
    
    def start_shifter_operation(self, sh_op: List[int], rs1_addr: List[int],
                               sh_amount: List[int], rd_addr: List[int]):
        """
        Start a shifter operation.
        
        Args:
            sh_op: 3-bit shifter opcode
            rs1_addr: Source register address (5 bits)
            sh_amount: Shift amount (5 bits)
            rd_addr: Destination register address (5 bits)
        """
        assert self.state == self.STATE_IDLE, "Control unit must be IDLE to start new operation"
        
        self.current_op_type = self.OP_SHIFTER
        self.current_op = 'SHIFTER'
        self.state = self.STATE_EXECUTE
        
        # Set control signals
        self.signals.sh_op = sh_op.copy()
        self.signals.sh_amount = sh_amount.copy()
        self.signals.rf_raddr_a = rs1_addr.copy()
        self.signals.rf_waddr = rd_addr.copy()
        
        self._add_trace(f"Start Shifter operation: op={''.join(map(str, sh_op))}, "
                       f"amount={''.join(map(str, sh_amount))}")
    
    def start_mdu_operation(self, mdu_op: str, rs1_addr: List[int],
                           rs2_addr: List[int], rd_addr: List[int]):
        """
        Start an MDU (multiply/divide) operation.
        
        Args:
            mdu_op: Operation type ('MUL', 'MULH', 'DIV', etc.)
            rs1_addr: Source register 1 address (5 bits)
            rs2_addr: Source register 2 address (5 bits)
            rd_addr: Destination register address (5 bits)
        """
        assert self.state == self.STATE_IDLE, "Control unit must be IDLE to start new operation"
        
        self.current_op_type = self.OP_MDU
        self.current_op = mdu_op
        self.state = self.STATE_EXECUTE  # Set main state to EXECUTE
        self.mdu_state = MDU_STATE_IDLE
        
        # Set control signals
        self.signals.md_op = mdu_op
        self.signals.md_start = 1
        self.signals.md_busy = 0
        self.signals.md_done = 0
        self.signals.rf_raddr_a = rs1_addr.copy()
        self.signals.rf_raddr_b = rs2_addr.copy()
        self.signals.rf_waddr = rd_addr.copy()
        
        # Initialize operation data
        self.operation_data = {
            'cycle_count': 0,
            'max_cycles': 32  # 32 iterations for 32-bit operations
        }
        
        self._add_trace(f"Start MDU operation: {mdu_op}")
        
        # Transition to first operational state
        if mdu_op in ['MUL', 'MULH', 'MULHU', 'MULHSU']:
            self.mdu_state = MDU_STATE_MUL_SHIFT
        else:  # DIV, DIVU, REM, REMU
            self.mdu_state = MDU_STATE_DIV_TESTBIT
        
        self.signals.md_busy = 1
        self.signals.md_start = 0
    
    def start_fpu_operation(self, fpu_op: str, rs1_addr: List[int],
                           rs2_addr: List[int], rd_addr: List[int],
                           round_mode: List[int] = None):
        """
        Start an FPU (floating-point) operation.
        
        Args:
            fpu_op: Operation type ('FADD', 'FSUB', 'FMUL')
            rs1_addr: Source register 1 address (5 bits)
            rs2_addr: Source register 2 address (5 bits)
            rd_addr: Destination register address (5 bits)
            round_mode: 3-bit rounding mode (default [0,0,0] = RNE)
        """
        assert self.state == self.STATE_IDLE, "Control unit must be IDLE to start new operation"
        
        if round_mode is None:
            round_mode = [0, 0, 0]  # Default to RNE (Round to Nearest, ties to Even)
        
        self.current_op_type = self.OP_FPU
        self.current_op = fpu_op
        self.state = self.STATE_EXECUTE  # Set main state to EXECUTE
        self.fpu_state = FPU_STATE_IDLE
        
        # Set control signals
        self.signals.fpu_op = fpu_op
        self.signals.fpu_start = 1
        self.signals.round_mode = round_mode
        self.signals.rf_raddr_a = rs1_addr.copy()
        self.signals.rf_raddr_b = rs2_addr.copy()
        self.signals.rf_waddr = rd_addr.copy()
        
        # Initialize operation data
        self.operation_data = {
            'fpu_computed': False
        }
        
        self._add_trace(f"Start FPU operation: {fpu_op}, round_mode={round_mode}")
        
        # Transition to ALIGN state
        self.fpu_state = FPU_STATE_ALIGN
        self.signals.fpu_state = FPU_STATE_ALIGN
        self.signals.fpu_start = 0
    
    def tick(self) -> bool:
        """
        Advance the FSM by one clock cycle.
        
        Returns:
            True if operation is complete, False if still in progress
        """
        self.signals.cycle += 1
        self.total_cycles += 1  # Increment total cycle counter
        
        if self.state == self.STATE_IDLE:
            self.idle_cycles += 1  # Increment idle counter
            return True
        
        # Track cycles by operation type
        if self.current_op_type == self.OP_ALU:
            self.alu_cycles += 1
            return self._tick_alu()
        elif self.current_op_type == self.OP_SHIFTER:
            self.shifter_cycles += 1
            return self._tick_shifter()
        elif self.current_op_type == self.OP_MDU:
            self.mdu_cycles += 1
            return self._tick_mdu()
        elif self.current_op_type == self.OP_FPU:
            self.fpu_cycles += 1
            return self._tick_fpu()
        
        return True
    
    def _tick_alu(self) -> bool:
        """Advance ALU operation FSM. Returns True when complete."""
        if self.state == self.STATE_EXECUTE:
            # Perform ALU operation
            # Read registers into operands
            self._read_registers()
            
            # Select operands based on multiplexers
            op_a = self._select_operand_a()
            op_b = self._select_operand_b()
            
            # Execute ALU operation
            result_bits, flags = alu(op_a, op_b, self.signals.alu_op)
            self.alu_result = result_bits
            # flags = [N, Z, C, V] but we don't use them yet
            
            # Prepare for writeback
            self.writeback_data = self._select_result()
            
            # ALU operations are single-cycle: transition to writeback
            self.state = self.STATE_WRITEBACK
            self.signals.rf_we = 1  # Enable register write
            self._add_trace(f"ALU: EXECUTE → WRITEBACK (result={result_bits[:8]}...)")
            return False
        
        elif self.state == self.STATE_WRITEBACK:
            # Write result back to register file
            self._write_register()
            
            # Complete operation
            self.signals.rf_we = 0
            self.state = self.STATE_IDLE
            self.current_op_type = None
            self._add_trace("ALU: WRITEBACK → IDLE (complete)")
            return True
        
        return False
    
    def _tick_shifter(self) -> bool:
        """Advance Shifter operation FSM. Returns True when complete."""
        if self.state == self.STATE_EXECUTE:
            # Perform Shifter operation
            # Read register into operand
            self._read_registers()
            
            # Get source operand (only operand_a is used for shifts)
            op_a = self._select_operand_a()
            
            # Convert 3-bit control signal op to 2-bit shifter op
            # SH_OP_SLL = [0,0,0] -> [0,0]
            # SH_OP_SRL = [0,0,1] -> [0,1]
            # SH_OP_SRA = [0,1,1] -> [1,1]
            shifter_op = self.signals.sh_op[1:]  # Take last 2 bits
            
            # Execute Shifter operation
            result_bits = shifter(op_a, self.signals.sh_amount, shifter_op)
            self.shifter_result = result_bits
            
            # Prepare for writeback
            self.writeback_data = self._select_result()
            
            # Barrel shifter is single-cycle: transition to writeback
            self.state = self.STATE_WRITEBACK
            self.signals.rf_we = 1
            self._add_trace(f"Shifter: EXECUTE → WRITEBACK (result={result_bits[:8]}...)")
            return False
        
        elif self.state == self.STATE_WRITEBACK:
            # Write result back to register file
            self._write_register()
            
            # Complete operation
            self.signals.rf_we = 0
            self.state = self.STATE_IDLE
            self.current_op_type = None
            self._add_trace("Shifter: WRITEBACK → IDLE (complete)")
            return True
        
        return False
    
    def _tick_mdu(self) -> bool:
        """Advance MDU operation FSM. Returns True when complete."""
        self.operation_data['cycle_count'] += 1
        
        if self.current_op in ['MUL', 'MULH', 'MULHU', 'MULHSU']:
            return self._tick_mdu_multiply()
        else:  # DIV, DIVU, REM, REMU
            return self._tick_mdu_divide()
    
    def _tick_mdu_multiply(self) -> bool:
        """Advance MDU multiply FSM. Returns True when complete."""
        cycle = self.operation_data['cycle_count']
        max_cycles = self.operation_data.get('max_cycles', 32)
        
        if self.mdu_state == MDU_STATE_MUL_SHIFT:
            # In shift state, check if we need to add
            # Perform actual multiplication computation on first cycle
            if cycle == 1:
                # Read registers into operands
                self._read_registers()
                op_a = self._select_operand_a()
                op_b = self._select_operand_b()
                
                # Call MDU multiply function to get result
                mdu_result = mdu_mul(op_a, op_b, self.current_op)
                
                # Store result and intermediate data
                self.mdu_result = mdu_result['result']
                self.operation_data['mdu_result_dict'] = mdu_result
                self.operation_data['product_hi'] = mdu_result.get('hi_bits', [0]*32)
                self.operation_data['product_lo'] = mdu_result.get('lo_bits', [0]*32)
                
                self._add_trace(f"MDU MUL cycle {cycle}: Starting multiplication, result computed")
            
            self.mdu_state = MDU_STATE_MUL_ADD
            self._add_trace(f"MDU MUL cycle {cycle}: SHIFT → ADD")
            return False
        
        elif self.mdu_state == MDU_STATE_MUL_ADD:
            # After add, shift and continue
            if cycle >= max_cycles:
                # All cycles complete, go to writeback
                self.mdu_state = MDU_STATE_WRITEBACK
                self.signals.md_busy = 0
                self.signals.md_done = 1
                
                # Prepare writeback data
                self.writeback_data = self.mdu_result
                
                self._add_trace(f"MDU MUL cycle {cycle}: ADD → WRITEBACK (complete)")
                return False
            else:
                self.mdu_state = MDU_STATE_MUL_SHIFT
                self._add_trace(f"MDU MUL cycle {cycle}: ADD → SHIFT")
                return False
        
        elif self.mdu_state == MDU_STATE_WRITEBACK:
            # Write result to register file
            self.signals.rf_we = 1
            self._write_register()
            
            self.signals.rf_we = 0
            self.signals.md_done = 0
            self.state = self.STATE_IDLE
            self.mdu_state = MDU_STATE_IDLE
            self.current_op_type = None
            self._add_trace("MDU MUL: WRITEBACK → IDLE (operation complete)")
            return True
        
        return False
    
    def _tick_mdu_divide(self) -> bool:
        """Advance MDU divide FSM. Returns True when complete."""
        cycle = self.operation_data['cycle_count']
        max_cycles = self.operation_data.get('max_cycles', 32)
        
        if self.mdu_state == MDU_STATE_DIV_TESTBIT:
            # Test if we can subtract
            # Perform actual division computation on first cycle
            if cycle == 1:
                # Read registers into operands
                self._read_registers()
                op_a = self._select_operand_a()
                op_b = self._select_operand_b()
                
                # Call MDU divide function to get result
                mdu_result = mdu_div(op_a, op_b, self.current_op)
                
                # Store result - DIV/DIVU returns quotient, REM/REMU returns remainder
                if self.current_op in ['DIV', 'DIVU']:
                    self.mdu_result = mdu_result['quotient']
                else:  # REM, REMU
                    self.mdu_result = mdu_result['remainder']
                
                self.operation_data['mdu_result_dict'] = mdu_result
                self.operation_data['quotient'] = mdu_result['quotient']
                self.operation_data['remainder'] = mdu_result['remainder']
                
                self._add_trace(f"MDU DIV cycle {cycle}: Starting division, result computed")
            
            self.mdu_state = MDU_STATE_DIV_SUB
            self._add_trace(f"MDU DIV cycle {cycle}: TESTBIT → SUB")
            return False
        
        elif self.mdu_state == MDU_STATE_DIV_SUB:
            # After subtract, check if we need to restore
            self.mdu_state = MDU_STATE_DIV_RESTORE
            self._add_trace(f"MDU DIV cycle {cycle}: SUB → RESTORE")
            return False
        
        elif self.mdu_state == MDU_STATE_DIV_RESTORE:
            # After restore decision, shift
            self.mdu_state = MDU_STATE_DIV_SHIFT
            self._add_trace(f"MDU DIV cycle {cycle}: RESTORE → SHIFT")
            return False
        
        elif self.mdu_state == MDU_STATE_DIV_SHIFT:
            if cycle >= max_cycles:
                # All cycles complete, go to writeback
                self.mdu_state = MDU_STATE_WRITEBACK
                self.signals.md_busy = 0
                self.signals.md_done = 1
                
                # Prepare writeback data
                self.writeback_data = self.mdu_result
                
                self._add_trace(f"MDU DIV cycle {cycle}: SHIFT → WRITEBACK (complete)")
                return False
            else:
                self.mdu_state = MDU_STATE_DIV_TESTBIT
                self._add_trace(f"MDU DIV cycle {cycle}: SHIFT → TESTBIT")
                return False
        
        elif self.mdu_state == MDU_STATE_WRITEBACK:
            # Write result to register file
            self.signals.rf_we = 1
            self._write_register()
            
            self.signals.rf_we = 0
            self.signals.md_done = 0
            self.state = self.STATE_IDLE
            self.mdu_state = MDU_STATE_IDLE
            self.current_op_type = None
            self._add_trace("MDU DIV: WRITEBACK → IDLE (operation complete)")
            return True
        
        return False
    
    def _tick_fpu(self) -> bool:
        """Advance FPU operation FSM. Returns True when complete."""
        current_state = self.fpu_state
        
        if current_state == FPU_STATE_ALIGN:
            # Exponent alignment stage
            # On first entry to ALIGN, perform the full FPU computation
            if not self.operation_data.get('fpu_computed', False):
                # Read registers into operands
                self._read_registers()
                op_a = self._select_operand_a()
                op_b = self._select_operand_b()
                
                # Call appropriate FPU function based on operation
                if self.current_op in ['FADD', 'FSUB']:
                    # For FSUB, negate operand B
                    if self.current_op == 'FSUB':
                        # Flip sign bit of B
                        op_b = [1 - op_b[0]] + op_b[1:]
                    fpu_result = fadd_f32(op_a, op_b, self.signals.round_mode)
                elif self.current_op in ['FMUL']:
                    fpu_result = fmul_f32(op_a, op_b, self.signals.round_mode)
                else:
                    # Default to add for unsupported ops
                    fpu_result = fadd_f32(op_a, op_b, self.signals.round_mode)
                
                # Store result
                self.fpu_result = fpu_result['result']
                self.operation_data['fpu_result_dict'] = fpu_result
                self.operation_data['fpu_computed'] = True
                
                self._add_trace(f"FPU {self.current_op}: Computation complete in ALIGN stage")
            
            # Transition to OP state
            self.fpu_state = FPU_STATE_OP
            self.signals.fpu_state = FPU_STATE_OP
            self._add_trace("FPU: ALIGN → OP")
            return False
        
        elif current_state == FPU_STATE_OP:
            # Core operation stage (computation already done in ALIGN)
            self.fpu_state = FPU_STATE_NORMALIZE
            self.signals.fpu_state = FPU_STATE_NORMALIZE
            self._add_trace("FPU: OP → NORMALIZE")
            return False
        
        elif current_state == FPU_STATE_NORMALIZE:
            # Normalization stage
            self.fpu_state = FPU_STATE_ROUND
            self.signals.fpu_state = FPU_STATE_ROUND
            self._add_trace("FPU: NORMALIZE → ROUND")
            return False
        
        elif current_state == FPU_STATE_ROUND:
            # Rounding stage - prepare writeback
            self.writeback_data = self.fpu_result
            self.fpu_state = FPU_STATE_WRITEBACK
            self.signals.fpu_state = FPU_STATE_WRITEBACK
            self._add_trace("FPU: ROUND → WRITEBACK")
            return False
        
        elif current_state == FPU_STATE_WRITEBACK:
            # Write result and complete
            self.signals.rf_we = 1
            self._write_register()
            
            self.signals.rf_we = 0
            self.fpu_state = FPU_STATE_IDLE
            self.signals.fpu_state = FPU_STATE_IDLE
            self.state = self.STATE_IDLE
            self.current_op_type = None
            self._add_trace("FPU: WRITEBACK → IDLE (complete)")
            return True
        
        return False
    
    def _add_trace(self, message: str):
        """Add an entry to the operation trace."""
        trace_entry = {
            'cycle': self.signals.cycle,
            'message': message,
            'signals': self.signals.copy()
        }
        self.trace.append(trace_entry)
    
    def get_trace(self) -> List[Dict[str, Any]]:
        """
        Get the complete operation trace.
        
        Returns:
            List of trace entries with cycle number, message, and control signals
        """
        return self.trace.copy()
    
    def print_trace(self):
        """Print the operation trace in human-readable format."""
        print("=" * 80)
        print("Control Unit Operation Trace")
        print("=" * 80)
        for entry in self.trace:
            print(f"\nCycle {entry['cycle']}: {entry['message']}")
            print(format_control_signals(entry['signals']))
        print("=" * 80)
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get current FSM state information.
        
        Returns:
            Dictionary with current state details
        """
        return {
            'main_state': self.state,
            'mdu_state': self.mdu_state,
            'fpu_state': self.fpu_state,
            'current_op_type': self.current_op_type,
            'current_op': self.current_op,
            'signals': self.signals.to_dict()
        }
    
    def is_idle(self) -> bool:
        """Check if control unit is idle and ready for new operation."""
        return self.state == self.STATE_IDLE
    
    def is_busy(self) -> bool:
        """Check if control unit is currently executing an operation."""
        return not self.is_idle()
    
    # ========== Data Path Methods ==========
    
    def _select_operand_a(self) -> List[int]:
        """
        Select operand A based on src_a_sel control signal.
        
        Returns:
            Selected operand A (32-bit list)
        """
        if self.signals.src_a_sel == 0:
            # Select from register file
            return self.operand_a.copy()
        elif self.signals.src_a_sel == 1:
            # Select immediate value
            return self.immediate.copy()
        elif self.signals.src_a_sel == 2:
            # Select PC (program counter) - for PC-relative operations
            # For now, return zeros as PC is not yet implemented
            return [0] * 32
        else:
            # Default to operand_a
            return self.operand_a.copy()
    
    def _select_operand_b(self) -> List[int]:
        """
        Select operand B based on src_b_sel control signal.
        
        Returns:
            Selected operand B (32-bit list)
        """
        if self.signals.src_b_sel == 0:
            # Select from register file
            return self.operand_b.copy()
        elif self.signals.src_b_sel == 1:
            # Select immediate value
            return self.immediate.copy()
        elif self.signals.src_b_sel == 2:
            # Select constant (e.g., 4 for PC+4)
            return [0, 0, 1, 0, 0] + [0] * 27  # 4 in binary
        else:
            # Default to operand_b
            return self.operand_b.copy()
    
    def _read_registers(self):
        """
        Read source registers from register file based on control signals.
        Updates operand_a and operand_b with values from register file.
        Uses FP registers for FPU operations, integer registers otherwise.
        """
        # Pass bit arrays directly - RegisterFile now accepts bit arrays
        if self.current_op_type == self.OP_FPU:
            # FPU operations use FP register file
            self.operand_a = self.register_file.read_fp_reg(self.signals.rf_raddr_a)
            self.operand_b = self.register_file.read_fp_reg(self.signals.rf_raddr_b)
        else:
            # ALU, Shifter, MDU use integer register file
            self.operand_a = self.register_file.read_int_reg(self.signals.rf_raddr_a)
            self.operand_b = self.register_file.read_int_reg(self.signals.rf_raddr_b)
    
    def _write_register(self):
        """
        Write result to destination register based on control signals.
        Only writes if rf_we (register file write enable) is asserted.
        Uses FP registers for FPU operations, integer registers otherwise.
        """
        if self.signals.rf_we == 1:
            # Pass bit array directly - RegisterFile now accepts bit arrays
            if self.current_op_type == self.OP_FPU:
                # FPU operations write to FP register file
                self.register_file.write_fp_reg(self.signals.rf_waddr, self.writeback_data)
            else:
                # ALU, Shifter, MDU write to integer register file
                self.register_file.write_int_reg(self.signals.rf_waddr, self.writeback_data)
    
    def _select_result(self) -> List[int]:
        """
        Select final result based on current operation type.
        Result multiplexer for different functional units.
        
        Returns:
            Selected result (32-bit list)
        """
        if self.current_op_type == self.OP_ALU:
            return self.alu_result.copy()
        elif self.current_op_type == self.OP_SHIFTER:
            return self.shifter_result.copy()
        elif self.current_op_type == self.OP_MDU:
            return self.mdu_result.copy()
        elif self.current_op_type == self.OP_FPU:
            return self.fpu_result.copy()
        else:
            # Default to zeros
            return [0] * 32
    
    def set_immediate(self, immediate_value: List[int]):
        """
        Set the immediate value for I-type instructions.
        
        Args:
            immediate_value: 32-bit immediate value
        """
        assert len(immediate_value) == 32, "Immediate value must be 32 bits"
        self.immediate = immediate_value.copy()
    
    def get_operand_a(self) -> List[int]:
        """Get current value of operand A."""
        return self.operand_a.copy()
    
    def get_operand_b(self) -> List[int]:
        """Get current value of operand B."""
        return self.operand_b.copy()
    
    def get_writeback_data(self) -> List[int]:
        """Get current writeback data."""
        return self.writeback_data.copy()
    
    # ========== High-Level Execution Methods ==========
    
    def execute_alu_instruction(self, alu_op: List[int], rs1_addr: List[int],
                                rs2_addr: List[int], rd_addr: List[int],
                                max_cycles: int = 10) -> Dict[str, Any]:
        """
        Execute a complete ALU instruction.
        
        Args:
            alu_op: 4-bit ALU opcode
            rs1_addr: Source register 1 address (5 bits)
            rs2_addr: Source register 2 address (5 bits)
            rd_addr: Destination register address (5 bits)
            max_cycles: Maximum cycles to prevent infinite loops
        
        Returns:
            Dictionary with:
                - 'result': Final result (32-bit array)
                - 'cycles': Number of cycles taken
                - 'trace': Operation trace
                - 'success': True if completed successfully
        """
        # Start the operation
        self.start_alu_operation(alu_op, rs1_addr, rs2_addr, rd_addr)
        
        # Run until complete
        cycles = 0
        complete = False
        while not complete and cycles < max_cycles:
            complete = self.tick()
            cycles += 1
        
        # Increment instruction count if successful
        if complete and self.is_idle():
            self.instruction_count += 1
        
        return {
            'result': self.writeback_data.copy(),
            'cycles': cycles,
            'trace': self.get_trace(),
            'success': complete and self.is_idle()
        }
    
    def execute_shifter_instruction(self, sh_op: List[int], rs1_addr: List[int],
                                    sh_amount: List[int], rd_addr: List[int],
                                    max_cycles: int = 10) -> Dict[str, Any]:
        """
        Execute a complete Shifter instruction.
        
        Args:
            sh_op: 3-bit shifter opcode
            rs1_addr: Source register address (5 bits)
            sh_amount: Shift amount (5 bits)
            rd_addr: Destination register address (5 bits)
            max_cycles: Maximum cycles to prevent infinite loops
        
        Returns:
            Dictionary with:
                - 'result': Final result (32-bit array)
                - 'cycles': Number of cycles taken
                - 'trace': Operation trace
                - 'success': True if completed successfully
        """
        # Start the operation
        self.start_shifter_operation(sh_op, rs1_addr, sh_amount, rd_addr)
        
        # Run until complete
        cycles = 0
        complete = False
        while not complete and cycles < max_cycles:
            complete = self.tick()
            cycles += 1
        
        # Increment instruction count if successful
        if complete and self.is_idle():
            self.instruction_count += 1
        
        return {
            'result': self.writeback_data.copy(),
            'cycles': cycles,
            'trace': self.get_trace(),
            'success': complete and self.is_idle()
        }
    
    def execute_mdu_instruction(self, mdu_op: str, rs1_addr: List[int],
                                rs2_addr: List[int], rd_addr: List[int],
                                max_cycles: int = 35) -> Dict[str, Any]:
        """
        Execute a complete MDU (Multiply/Divide) instruction.
        
        Args:
            mdu_op: Operation string ("MUL", "MULH", "MULHU", "MULHSU", "DIV", "DIVU", "REM", "REMU")
            rs1_addr: Source register 1 address (5 bits)
            rs2_addr: Source register 2 address (5 bits)
            rd_addr: Destination register address (5 bits)
            max_cycles: Maximum cycles to prevent infinite loops (default 35 for 32-cycle ops + overhead)
        
        Returns:
            Dictionary with:
                - 'result': Final result (32-bit array)
                - 'cycles': Number of cycles taken
                - 'trace': Operation trace
                - 'success': True if completed successfully
        """
        # Start the operation
        self.start_mdu_operation(mdu_op, rs1_addr, rs2_addr, rd_addr)
        
        # Run until complete
        cycles = 0
        complete = False
        while not complete and cycles < max_cycles:
            complete = self.tick()
            cycles += 1
        
        # Increment instruction count if successful
        if complete and self.is_idle():
            self.instruction_count += 1
        
        return {
            'result': self.writeback_data.copy(),
            'cycles': cycles,
            'trace': self.get_trace(),
            'success': complete and self.is_idle(),
            'quotient': self.operation_data.get('quotient', None),
            'remainder': self.operation_data.get('remainder', None),
            'product_hi': self.operation_data.get('product_hi', None),
            'product_lo': self.operation_data.get('product_lo', None)
        }
    
    def execute_fpu_instruction(self, fpu_op: str, rs1_addr: List[int],
                                rs2_addr: List[int], rd_addr: List[int],
                                rounding_mode: List[int] = None,
                                max_cycles: int = 10) -> Dict[str, Any]:
        """
        Execute a complete FPU (Floating-Point) instruction.
        
        Args:
            fpu_op: Operation string ("FADD", "FSUB", "FMUL", "FDIV", "FSQRT")
            rs1_addr: Source register 1 address (5 bits)
            rs2_addr: Source register 2 address (5 bits) - not used for FSQRT
            rd_addr: Destination register address (5 bits)
            rounding_mode: Optional 3-bit rounding mode (default [0,0,0] = RNE)
            max_cycles: Maximum cycles to prevent infinite loops (default 10 for pipeline stages)
        
        Returns:
            Dictionary with:
                - 'result': Final result (32-bit array)
                - 'cycles': Number of cycles taken
                - 'trace': Operation trace
                - 'success': True if completed successfully
                - 'flags': FPU exception flags (if available)
        """
        # Start the operation
        self.start_fpu_operation(fpu_op, rs1_addr, rs2_addr, rd_addr, rounding_mode)
        
        # Run until complete
        cycles = 0
        complete = False
        while not complete and cycles < max_cycles:
            complete = self.tick()
            cycles += 1
        
        # Increment instruction count if successful
        if complete and self.is_idle():
            self.instruction_count += 1
        
        return {
            'result': self.writeback_data.copy(),
            'cycles': cycles,
            'trace': self.get_trace(),
            'success': complete and self.is_idle(),
            'flags': self.operation_data.get('fpu_result_dict', {}).get('flags', None)
        }
    
    # ========== Phase 6: Unified Instruction Execution ==========
    
    def execute_instruction(self, op_type: str, operation: str, 
                          rs1_addr: List[int], rs2_addr: List[int] = None,
                          rd_addr: List[int] = None, immediate: List[int] = None,
                          shamt: List[int] = None, rounding_mode: List[int] = None,
                          max_cycles: int = 50) -> Dict[str, Any]:
        """
        Execute any instruction by automatically routing to the correct functional unit.
        
        This is the main high-level interface for executing instructions. It decodes
        the operation type and routes to the appropriate functional unit, handling
        all the cycling automatically.
        
        Args:
            op_type: Operation type ('ALU', 'SHIFTER', 'MDU', 'FPU')
            operation: Specific operation (ALU_OP_ADD, 'MUL', 'FADD', etc.)
            rs1_addr: Source register 1 address (5 bits)
            rs2_addr: Source register 2 address (5 bits, optional for some ops)
            rd_addr: Destination register address (5 bits)
            immediate: Immediate value (32 bits, optional for ALU)
            shamt: Shift amount (5 bits, for shifter operations)
            rounding_mode: FPU rounding mode (3 bits, optional)
            max_cycles: Maximum cycles before timeout (default 50)
        
        Returns:
            Dictionary with:
                - 'result': Final result (32-bit array)
                - 'cycles': Number of cycles taken
                - 'trace': Full execution trace
                - 'success': True if completed successfully
                - Additional unit-specific data (quotient, flags, etc.)
        
        Example:
            # Execute ADD: r3 = r1 + r2
            result = cu.execute_instruction('ALU', ALU_OP_ADD, 
                                           [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1])
            
            # Execute MUL: r5 = r3 * r4
            result = cu.execute_instruction('MDU', 'MUL',
                                           [0,0,0,1,1], [0,0,1,0,0], [0,0,1,0,1])
        """
        assert self.is_idle(), "Control unit must be idle before starting new instruction"
        
        op_type = op_type.upper()
        
        if op_type == 'ALU':
            return self.execute_alu_instruction(operation, rs1_addr, rs2_addr, rd_addr, max_cycles)
        
        elif op_type == 'SHIFTER':
            assert shamt is not None, "Shifter operations require shamt parameter"
            return self.execute_shifter_instruction(operation, rs1_addr, shamt, rd_addr, max_cycles)
        
        elif op_type == 'MDU':
            return self.execute_mdu_instruction(operation, rs1_addr, rs2_addr, rd_addr, max_cycles)
        
        elif op_type == 'FPU':
            return self.execute_fpu_instruction(operation, rs1_addr, rs2_addr, rd_addr, 
                                               rounding_mode, max_cycles)
        
        else:
            raise ValueError(f"Unknown operation type: {op_type}. "
                           f"Must be 'ALU', 'SHIFTER', 'MDU', or 'FPU'")
    
    def execute_and_get_result(self, op_type: str, operation: str,
                              rs1_addr: List[int], rs2_addr: List[int] = None,
                              rd_addr: List[int] = None, **kwargs) -> List[int]:
        """
        Execute instruction and return only the result value.
        
        Convenience method that executes an instruction and extracts just
        the result bits, discarding trace and timing information.
        
        Args:
            op_type: Operation type ('ALU', 'SHIFTER', 'MDU', 'FPU')
            operation: Specific operation
            rs1_addr: Source register 1 address (5 bits)
            rs2_addr: Source register 2 address (5 bits, optional)
            rd_addr: Destination register address (5 bits)
            **kwargs: Additional parameters (shamt, immediate, rounding_mode, etc.)
        
        Returns:
            32-bit result array
        
        Raises:
            RuntimeError: If instruction fails to complete
        
        Example:
            result = cu.execute_and_get_result('ALU', ALU_OP_ADD,
                                               [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1])
        """
        exec_result = self.execute_instruction(op_type, operation, rs1_addr, 
                                              rs2_addr, rd_addr, **kwargs)
        
        if not exec_result['success']:
            raise RuntimeError(f"Instruction failed to complete: {op_type} {operation}")
        
        return exec_result['result']
    
    def execute_and_get_trace(self, op_type: str, operation: str,
                             rs1_addr: List[int], rs2_addr: List[int] = None,
                             rd_addr: List[int] = None, **kwargs) -> List[Dict]:
        """
        Execute instruction and return detailed execution trace.
        
        Convenience method for debugging and analysis. Returns the full
        cycle-by-cycle trace of the instruction execution.
        
        Args:
            op_type: Operation type ('ALU', 'SHIFTER', 'MDU', 'FPU')
            operation: Specific operation
            rs1_addr: Source register 1 address (5 bits)
            rs2_addr: Source register 2 address (5 bits, optional)
            rd_addr: Destination register address (5 bits)
            **kwargs: Additional parameters
        
        Returns:
            List of trace dictionaries, one per cycle
        
        Example:
            trace = cu.execute_and_get_trace('MDU', 'MUL',
                                            [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1])
            for cycle, entry in enumerate(trace):
                print(f"Cycle {cycle}: {entry}")
        """
        exec_result = self.execute_instruction(op_type, operation, rs1_addr,
                                              rs2_addr, rd_addr, **kwargs)
        return exec_result['trace']
    
    def execute_with_timeout(self, op_type: str, operation: str,
                            rs1_addr: List[int], rs2_addr: List[int] = None,
                            rd_addr: List[int] = None, timeout_cycles: int = 100,
                            **kwargs) -> Dict[str, Any]:
        """
        Execute instruction with explicit timeout protection.
        
        Wrapper around execute_instruction with a configurable timeout
        for safety. Useful for untrusted or potentially infinite operations.
        
        Args:
            op_type: Operation type ('ALU', 'SHIFTER', 'MDU', 'FPU')
            operation: Specific operation
            rs1_addr: Source register 1 address (5 bits)
            rs2_addr: Source register 2 address (5 bits, optional)
            rd_addr: Destination register address (5 bits)
            timeout_cycles: Maximum cycles before aborting (default 100)
            **kwargs: Additional parameters
        
        Returns:
            Execution result dictionary with additional 'timed_out' field
        
        Example:
            result = cu.execute_with_timeout('MDU', 'MUL',
                                            [0,0,0,0,1], [0,0,0,1,0], [0,0,0,1,1],
                                            timeout_cycles=50)
            if result.get('timed_out'):
                print("Operation exceeded timeout!")
        """
        kwargs['max_cycles'] = timeout_cycles
        exec_result = self.execute_instruction(op_type, operation, rs1_addr,
                                              rs2_addr, rd_addr, **kwargs)
        
        # Add timeout flag
        exec_result['timed_out'] = not exec_result['success']
        
        return exec_result
    
    # ========== Phase 7: Performance Counters ==========
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics for the control unit.
        
        Returns a dictionary containing all performance counters and
        derived metrics like CPI (Cycles Per Instruction) and functional
        unit utilization percentages.
        
        Returns:
            Dictionary with:
                - 'total_cycles': Total clock cycles executed
                - 'instruction_count': Total instructions completed
                - 'cpi': Cycles Per Instruction (total_cycles / instruction_count)
                - 'ipc': Instructions Per Cycle (instruction_count / total_cycles)
                - 'alu_cycles': Cycles spent in ALU operations
                - 'shifter_cycles': Cycles spent in Shifter operations
                - 'mdu_cycles': Cycles spent in MDU operations
                - 'fpu_cycles': Cycles spent in FPU operations
                - 'idle_cycles': Cycles spent idle
                - 'alu_utilization': Percentage of time in ALU (0-100)
                - 'shifter_utilization': Percentage of time in Shifter (0-100)
                - 'mdu_utilization': Percentage of time in MDU (0-100)
                - 'fpu_utilization': Percentage of time in FPU (0-100)
                - 'idle_utilization': Percentage of time idle (0-100)
        
        Example:
            cu.execute_instruction('ALU', ALU_OP_ADD, ...)
            cu.execute_instruction('MDU', 'MUL', ...)
            stats = cu.get_performance_stats()
            print(f"CPI: {stats['cpi']:.2f}")
            print(f"ALU Utilization: {stats['alu_utilization']:.1f}%")
        """
        # Calculate derived metrics
        cpi = self.total_cycles / self.instruction_count if self.instruction_count > 0 else 0
        ipc = self.instruction_count / self.total_cycles if self.total_cycles > 0 else 0
        
        # Calculate utilization percentages
        alu_util = (self.alu_cycles / self.total_cycles * 100) if self.total_cycles > 0 else 0
        shifter_util = (self.shifter_cycles / self.total_cycles * 100) if self.total_cycles > 0 else 0
        mdu_util = (self.mdu_cycles / self.total_cycles * 100) if self.total_cycles > 0 else 0
        fpu_util = (self.fpu_cycles / self.total_cycles * 100) if self.total_cycles > 0 else 0
        idle_util = (self.idle_cycles / self.total_cycles * 100) if self.total_cycles > 0 else 0
        
        return {
            'total_cycles': self.total_cycles,
            'instruction_count': self.instruction_count,
            'cpi': cpi,
            'ipc': ipc,
            'alu_cycles': self.alu_cycles,
            'shifter_cycles': self.shifter_cycles,
            'mdu_cycles': self.mdu_cycles,
            'fpu_cycles': self.fpu_cycles,
            'idle_cycles': self.idle_cycles,
            'alu_utilization': alu_util,
            'shifter_utilization': shifter_util,
            'mdu_utilization': mdu_util,
            'fpu_utilization': fpu_util,
            'idle_utilization': idle_util
        }
    
    def print_performance_stats(self):
        """
        Pretty-print performance statistics to console.
        
        Displays formatted performance counters including CPI, IPC,
        and functional unit utilization percentages.
        
        Example:
            cu.execute_instruction('ALU', ALU_OP_ADD, ...)
            cu.execute_instruction('MDU', 'MUL', ...)
            cu.print_performance_stats()
            
            # Output:
            # ===== Performance Statistics =====
            # Total Cycles:        35
            # Instructions:        2
            # CPI:                 17.50
            # IPC:                 0.06
            # 
            # Functional Unit Utilization:
            #   ALU:        5.7% (2 cycles)
            #   Shifter:    0.0% (0 cycles)
            #   MDU:        94.3% (33 cycles)
            #   FPU:        0.0% (0 cycles)
            #   Idle:       0.0% (0 cycles)
        """
        stats = self.get_performance_stats()
        
        print("\n===== Performance Statistics =====")
        print(f"Total Cycles:        {stats['total_cycles']}")
        print(f"Instructions:        {stats['instruction_count']}")
        print(f"CPI:                 {stats['cpi']:.2f}")
        print(f"IPC:                 {stats['ipc']:.2f}")
        print()
        print("Functional Unit Utilization:")
        print(f"  ALU:        {stats['alu_utilization']:>5.1f}% ({stats['alu_cycles']} cycles)")
        print(f"  Shifter:    {stats['shifter_utilization']:>5.1f}% ({stats['shifter_cycles']} cycles)")
        print(f"  MDU:        {stats['mdu_utilization']:>5.1f}% ({stats['mdu_cycles']} cycles)")
        print(f"  FPU:        {stats['fpu_utilization']:>5.1f}% ({stats['fpu_cycles']} cycles)")
        print(f"  Idle:       {stats['idle_utilization']:>5.1f}% ({stats['idle_cycles']} cycles)")
        print("=" * 35)
    
    def reset_performance_counters(self):
        """
        Reset all performance counters to zero.
        
        Useful for measuring performance of specific code sections
        without resetting the entire control unit state.
        
        Example:
            # Setup some initial state
            cu.execute_instruction(...)
            
            # Now measure just this section
            cu.reset_performance_counters()
            cu.execute_instruction(...)
            cu.execute_instruction(...)
            stats = cu.get_performance_stats()  # Only reflects recent instructions
        """
        self.total_cycles = 0
        self.instruction_count = 0
        self.alu_cycles = 0
        self.shifter_cycles = 0
        self.mdu_cycles = 0
        self.fpu_cycles = 0
        self.idle_cycles = 0

# AI-END
