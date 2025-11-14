# AI-BEGIN
"""
Example usage of Control Unit (FSM)

Demonstrates how the control unit orchestrates multi-cycle operations
across different functional units.
"""

from riscsim.cpu.control_unit import ControlUnit
from riscsim.cpu.control_signals import ALU_OP_ADD, SH_OP_SLL


def example_alu_operation():
    """Example: Simple ALU ADD operation."""
    print("=" * 80)
    print("Example 1: ALU ADD Operation")
    print("=" * 80)
    
    cu = ControlUnit()
    
    # Start ADD operation: r3 = r1 + r2
    cu.start_alu_operation(
        alu_op=ALU_OP_ADD,
        rs1_addr=[0, 0, 0, 0, 1],  # r1
        rs2_addr=[0, 0, 0, 1, 0],  # r2
        rd_addr=[0, 0, 0, 1, 1]    # r3
    )
    
    # Run to completion
    while not cu.tick():
        pass
    
    # Print trace
    cu.print_trace()
    print()


def example_mdu_multiply():
    """Example: MDU multiply operation showing multi-cycle execution."""
    print("=" * 80)
    print("Example 2: MDU Multiply Operation (32 cycles)")
    print("=" * 80)
    
    cu = ControlUnit()
    
    # Start MUL operation: r3 = r1 * r2
    cu.start_mdu_operation(
        mdu_op='MUL',
        rs1_addr=[0, 0, 0, 0, 1],  # r1
        rs2_addr=[0, 0, 0, 1, 0],  # r2
        rd_addr=[0, 0, 0, 1, 1]    # r3
    )
    
    # Run to completion and count cycles
    cycle_count = 0
    while not cu.tick():
        cycle_count += 1
    cycle_count += 1  # Final tick
    
    print(f"\nOperation completed in {cycle_count} ticks")
    print(f"Total trace entries: {len(cu.get_trace())}")
    
    # Print first and last few trace entries
    trace = cu.get_trace()
    print("\nFirst 3 trace entries:")
    for entry in trace[:3]:
        print(f"  Cycle {entry['cycle']}: {entry['message']}")
    
    print("\nLast 3 trace entries:")
    for entry in trace[-3:]:
        print(f"  Cycle {entry['cycle']}: {entry['message']}")
    print()


def example_fpu_add():
    """Example: FPU floating-point addition showing state progression."""
    print("=" * 80)
    print("Example 3: FPU FADD Operation (5-stage pipeline)")
    print("=" * 80)
    
    cu = ControlUnit()
    
    # Start FADD operation: f3 = f1 + f2
    cu.start_fpu_operation(
        fpu_op='FADD',
        rs1_addr=[0, 0, 0, 0, 1],  # f1
        rs2_addr=[0, 0, 0, 1, 0],  # f2
        rd_addr=[0, 0, 0, 1, 1],   # f3
        round_mode='RNE'
    )
    
    # Track state progression
    states = [cu.fpu_state]
    while not cu.tick():
        states.append(cu.fpu_state)
    
    print(f"\nFPU State Progression:")
    for i, state in enumerate(states):
        print(f"  Tick {i}: {state}")
    
    # Print full trace
    print("\nFull Operation Trace:")
    for entry in cu.get_trace():
        print(f"  Cycle {entry['cycle']}: {entry['message']}")
    print()


def example_mixed_operations():
    """Example: Sequence of different operations."""
    print("=" * 80)
    print("Example 4: Mixed Operation Sequence")
    print("=" * 80)
    
    cu = ControlUnit()
    
    operations = [
        ('ALU ADD', lambda: cu.start_alu_operation(
            ALU_OP_ADD,
            [0, 0, 0, 0, 1],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 1, 1]
        )),
        ('Shifter SLL', lambda: cu.start_shifter_operation(
            SH_OP_SLL,
            [0, 0, 0, 1, 1],
            [0, 0, 1, 0, 1],  # Shift by 5
            [0, 0, 1, 0, 0]
        )),
        ('FPU FADD', lambda: cu.start_fpu_operation(
            'FADD',
            [0, 0, 0, 0, 1],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 1, 1]
        )),
    ]
    
    total_cycles = 0
    for op_name, start_func in operations:
        print(f"\nStarting {op_name}...")
        start_func()
        
        cycles = 0
        while not cu.tick():
            cycles += 1
        cycles += 1
        
        total_cycles += cycles
        print(f"  Completed in {cycles} cycles")
        print(f"  Control unit now idle: {cu.is_idle()}")
    
    print(f"\nTotal cycles for all operations: {total_cycles}")
    print()


def example_control_signals():
    """Example: Inspecting control signals during operation."""
    print("=" * 80)
    print("Example 5: Control Signal Inspection")
    print("=" * 80)
    
    cu = ControlUnit()
    
    # Start an MDU divide operation
    cu.start_mdu_operation(
        mdu_op='DIV',
        rs1_addr=[0, 0, 0, 0, 1],
        rs2_addr=[0, 0, 0, 1, 0],
        rd_addr=[0, 0, 0, 1, 1]
    )
    
    print("\nControl signals at key points:")
    print("\n1. After starting DIV operation:")
    state = cu.get_current_state()
    signals = state['signals']
    print(f"   Main state: {state['main_state']}")
    print(f"   MDU state: {state['mdu_state']}")
    print(f"   md_busy: {signals['md_busy']}")
    print(f"   md_done: {signals['md_done']}")
    print(f"   md_op: {signals['md_op']}")
    
    # Tick a few times
    for i in range(3):
        cu.tick()
    
    print(f"\n2. After {cu.signals.cycle} cycles:")
    state = cu.get_current_state()
    signals = state['signals']
    print(f"   Main state: {state['main_state']}")
    print(f"   MDU state: {state['mdu_state']}")
    print(f"   md_busy: {signals['md_busy']}")
    
    # Complete the operation
    while not cu.is_idle():
        cu.tick()
    
    print(f"\n3. After completion (cycle {cu.signals.cycle}):")
    state = cu.get_current_state()
    signals = state['signals']
    print(f"   Main state: {state['main_state']}")
    print(f"   MDU state: {state['mdu_state']}")
    print(f"   md_busy: {signals['md_busy']}")
    print(f"   md_done: {signals['md_done']}")
    print()


if __name__ == '__main__':
    example_alu_operation()
    example_mdu_multiply()
    example_fpu_add()
    example_mixed_operations()
    example_control_signals()
    
    print("=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)
# AI-END
