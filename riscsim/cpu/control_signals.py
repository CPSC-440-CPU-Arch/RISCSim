# AI-BEGIN
"""
Control Signal Definitions for RISC-V CPU

This module defines the control signals used throughout the CPU to coordinate
operations across different functional units (ALU, Shifter, MDU, FPU, Register File).

Control signals are organized into categories:
- ALU control signals
- Register file control signals
- Source selection signals
- Shifter control signals
- MDU (Multiply/Divide Unit) control signals
- FPU (Floating-Point Unit) control signals
- Pipeline control signals
"""

from typing import Dict, List, Any


class ControlSignals:
    """
    Container for all CPU control signals.
    
    Provides a centralized structure for managing control signals across
    all CPU components with type checking and validation.
    """
    
    def __init__(self):
        """Initialize all control signals to default values."""
        
        # ALU Control Signals
        self.alu_op = [0, 0, 0, 0]  # 4-bit ALU opcode
        
        # Register File Control Signals
        self.rf_we = 0              # Register file write enable
        self.rf_waddr = [0] * 5     # Write address (5 bits for 32 registers)
        self.rf_raddr_a = [0] * 5   # Read address A
        self.rf_raddr_b = [0] * 5   # Read address B
        
        # Source Selection Signals
        self.src_a_sel = 0          # Source A mux: 0=register, 1=immediate
        self.src_b_sel = 0          # Source B mux: 0=register, 1=immediate
        
        # Shifter Control Signals
        self.sh_op = [0, 0, 0]      # Shifter operation (3 bits)
        self.sh_amount = [0] * 5    # Shift amount (5 bits for 0-31)
        
        # MDU Control Signals
        self.md_start = 0           # Start MDU operation
        self.md_busy = 0            # MDU busy flag
        self.md_done = 0            # MDU operation complete
        self.md_op = 'IDLE'         # MDU operation type: MUL, MULH, DIV, etc.
        
        # FPU Control Signals
        self.fpu_start = 0          # Start FPU operation
        self.fpu_state = 'IDLE'     # Current FPU FSM state
        self.fpu_op = 'IDLE'        # FPU operation: FADD, FSUB, FMUL
        self.round_mode = 'RNE'     # Rounding mode: RNE, RTZ, RDN, RUP, RMM
        
        # Pipeline Control Signals
        self.cycle = 0              # Current cycle number
        self.pc = [0] * 32          # Program counter
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert control signals to dictionary for tracing/logging.
        
        Returns:
            Dictionary containing all control signal values
        """
        return {
            'alu_op': self.alu_op.copy(),
            'rf_we': self.rf_we,
            'rf_waddr': self.rf_waddr.copy(),
            'rf_raddr_a': self.rf_raddr_a.copy(),
            'rf_raddr_b': self.rf_raddr_b.copy(),
            'src_a_sel': self.src_a_sel,
            'src_b_sel': self.src_b_sel,
            'sh_op': self.sh_op.copy(),
            'sh_amount': self.sh_amount.copy(),
            'md_start': self.md_start,
            'md_busy': self.md_busy,
            'md_done': self.md_done,
            'md_op': self.md_op,
            'fpu_start': self.fpu_start,
            'fpu_state': self.fpu_state,
            'fpu_op': self.fpu_op,
            'round_mode': self.round_mode,
            'cycle': self.cycle,
            'pc': self.pc.copy(),
        }
    
    def from_dict(self, signal_dict: Dict[str, Any]):
        """
        Load control signals from dictionary.
        
        Args:
            signal_dict: Dictionary containing control signal values
        """
        if 'alu_op' in signal_dict:
            self.alu_op = signal_dict['alu_op'].copy()
        if 'rf_we' in signal_dict:
            self.rf_we = signal_dict['rf_we']
        if 'rf_waddr' in signal_dict:
            self.rf_waddr = signal_dict['rf_waddr'].copy()
        if 'rf_raddr_a' in signal_dict:
            self.rf_raddr_a = signal_dict['rf_raddr_a'].copy()
        if 'rf_raddr_b' in signal_dict:
            self.rf_raddr_b = signal_dict['rf_raddr_b'].copy()
        if 'src_a_sel' in signal_dict:
            self.src_a_sel = signal_dict['src_a_sel']
        if 'src_b_sel' in signal_dict:
            self.src_b_sel = signal_dict['src_b_sel']
        if 'sh_op' in signal_dict:
            self.sh_op = signal_dict['sh_op'].copy()
        if 'sh_amount' in signal_dict:
            self.sh_amount = signal_dict['sh_amount'].copy()
        if 'md_start' in signal_dict:
            self.md_start = signal_dict['md_start']
        if 'md_busy' in signal_dict:
            self.md_busy = signal_dict['md_busy']
        if 'md_done' in signal_dict:
            self.md_done = signal_dict['md_done']
        if 'md_op' in signal_dict:
            self.md_op = signal_dict['md_op']
        if 'fpu_start' in signal_dict:
            self.fpu_start = signal_dict['fpu_start']
        if 'fpu_state' in signal_dict:
            self.fpu_state = signal_dict['fpu_state']
        if 'fpu_op' in signal_dict:
            self.fpu_op = signal_dict['fpu_op']
        if 'round_mode' in signal_dict:
            self.round_mode = signal_dict['round_mode']
        if 'cycle' in signal_dict:
            self.cycle = signal_dict['cycle']
        if 'pc' in signal_dict:
            self.pc = signal_dict['pc'].copy()
    
    def copy(self) -> 'ControlSignals':
        """
        Create a deep copy of control signals.
        
        Returns:
            New ControlSignals instance with copied values
        """
        new_signals = ControlSignals()
        new_signals.from_dict(self.to_dict())
        return new_signals
    
    def reset(self):
        """Reset all control signals to default values."""
        self.__init__()
    
    def __str__(self) -> str:
        """String representation of control signals for debugging."""
        return (
            f"ControlSignals(\n"
            f"  ALU: op={self.alu_op}\n"
            f"  RF: we={self.rf_we}, waddr={self.rf_waddr}, "
            f"raddr_a={self.rf_raddr_a}, raddr_b={self.rf_raddr_b}\n"
            f"  Src: a_sel={self.src_a_sel}, b_sel={self.src_b_sel}\n"
            f"  Shifter: op={self.sh_op}, amount={self.sh_amount}\n"
            f"  MDU: start={self.md_start}, busy={self.md_busy}, "
            f"done={self.md_done}, op={self.md_op}\n"
            f"  FPU: start={self.fpu_start}, state={self.fpu_state}, "
            f"op={self.fpu_op}, round={self.round_mode}\n"
            f"  Pipeline: cycle={self.cycle}, pc={self.pc}\n"
            f")"
        )


# ALU Operation Codes
ALU_OP_AND = [0, 0, 0, 0]
ALU_OP_OR = [0, 0, 0, 1]
ALU_OP_ADD = [0, 0, 1, 0]
ALU_OP_SUB = [0, 1, 1, 0]
ALU_OP_SLT = [0, 1, 1, 1]
ALU_OP_NOR = [1, 1, 0, 0]
ALU_OP_XOR = [0, 0, 1, 1]
ALU_OP_NAND = [1, 1, 0, 1]

# Shifter Operation Codes (3-bit)
# 3-bit encoding maps to 2-bit shifter encoding via last 2 bits
# Shifter expects: [0,0]=SLL, [0,1]=SRL, [1,1]=SRA
SH_OP_SLL = [0, 0, 0]   # Shift left logical   -> [0,0]
SH_OP_SRL = [0, 0, 1]   # Shift right logical  -> [0,1]
SH_OP_SRA = [0, 1, 1]   # Shift right arithmetic -> [1,1]

# FPU States
FPU_STATE_IDLE = 'IDLE'
FPU_STATE_ALIGN = 'ALIGN'
FPU_STATE_OP = 'OP'
FPU_STATE_NORMALIZE = 'NORMALIZE'
FPU_STATE_ROUND = 'ROUND'
FPU_STATE_WRITEBACK = 'WRITEBACK'

# MDU States (for reference - actual states managed by control unit)
MDU_STATE_IDLE = 'IDLE'
MDU_STATE_MUL_SHIFT = 'MUL_SHIFT'
MDU_STATE_MUL_ADD = 'MUL_ADD'
MDU_STATE_DIV_TESTBIT = 'DIV_TESTBIT'
MDU_STATE_DIV_SUB = 'DIV_SUB'
MDU_STATE_DIV_RESTORE = 'DIV_RESTORE'
MDU_STATE_DIV_SHIFT = 'DIV_SHIFT'
MDU_STATE_WRITEBACK = 'WRITEBACK'

# Rounding Modes (IEEE-754)
ROUND_MODE_RNE = 'RNE'  # Round to Nearest, ties to Even (default)
ROUND_MODE_RTZ = 'RTZ'  # Round Toward Zero
ROUND_MODE_RDN = 'RDN'  # Round Down (toward -infinity)
ROUND_MODE_RUP = 'RUP'  # Round Up (toward +infinity)
ROUND_MODE_RMM = 'RMM'  # Round to Nearest, ties to Max Magnitude


def format_control_signals(signals: ControlSignals) -> str:
    """
    Format control signals for human-readable trace output.
    
    Args:
        signals: ControlSignals instance to format
        
    Returns:
        Formatted string representation
    """
    lines = []
    lines.append(f"Cycle {signals.cycle}:")
    lines.append(f"  ALU_OP: {''.join(map(str, signals.alu_op))}")
    lines.append(f"  RF: WE={signals.rf_we}, "
                 f"WADDR={''.join(map(str, signals.rf_waddr))}, "
                 f"RADDR_A={''.join(map(str, signals.rf_raddr_a))}, "
                 f"RADDR_B={''.join(map(str, signals.rf_raddr_b))}")
    lines.append(f"  SRC: A_SEL={signals.src_a_sel}, B_SEL={signals.src_b_sel}")
    lines.append(f"  SHIFTER: OP={''.join(map(str, signals.sh_op))}, "
                 f"AMT={''.join(map(str, signals.sh_amount))}")
    lines.append(f"  MDU: START={signals.md_start}, BUSY={signals.md_busy}, "
                 f"DONE={signals.md_done}, OP={signals.md_op}")
    lines.append(f"  FPU: START={signals.fpu_start}, STATE={signals.fpu_state}, "
                 f"OP={signals.fpu_op}, ROUND={signals.round_mode}")
    
    return '\n'.join(lines)


def decode_alu_op(alu_op: List[int]) -> str:
    """
    Decode ALU opcode to operation name.
    
    Args:
        alu_op: 4-bit ALU opcode
        
    Returns:
        Operation name string
    """
    op_map = {
        tuple(ALU_OP_AND): 'AND',
        tuple(ALU_OP_OR): 'OR',
        tuple(ALU_OP_ADD): 'ADD',
        tuple(ALU_OP_SUB): 'SUB',
        tuple(ALU_OP_SLT): 'SLT',
        tuple(ALU_OP_NOR): 'NOR',
        tuple(ALU_OP_XOR): 'XOR',
        tuple(ALU_OP_NAND): 'NAND',
    }
    return op_map.get(tuple(alu_op), 'UNKNOWN')


def decode_shifter_op(sh_op: List[int]) -> str:
    """
    Decode shifter opcode to operation name.
    
    Args:
        sh_op: 3-bit shifter opcode
        
    Returns:
        Operation name string
    """
    op_map = {
        tuple(SH_OP_SLL): 'SLL',
        tuple(SH_OP_SRL): 'SRL',
        tuple(SH_OP_SRA): 'SRA',
    }
    return op_map.get(tuple(sh_op), 'UNKNOWN')
# AI-END
