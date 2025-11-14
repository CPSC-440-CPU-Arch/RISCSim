#!/usr/bin/env python3
"""
Register File Control Signal Integration Examples

Demonstrates how the Register File integrates with the Control Unit
through control signals (rf_we, rf_waddr, rf_raddr_a, rf_raddr_b).

This shows how register operations are orchestrated by control signals
in a typical CPU pipeline.
"""

from riscsim.cpu.registers import RegisterFile, register_with_control
from riscsim.cpu.control_signals import ControlSignals


def int_to_bits(n, width):
    """Helper: Convert integer to bit array."""
    if n < 0:
        n = (1 << width) + n
    return [(n >> (width - 1 - i)) & 1 for i in range(width)]


def int_to_bin32(n):
    """Helper: Convert integer to 32-bit array."""
    return int_to_bits(n, 32)


def bits_to_int(bits):
    """Helper: Convert bit array to integer."""
    return sum(bit << (len(bits) - 1 - i) for i, bit in enumerate(bits))


def print_separator():
    """Print a section separator."""
    print("=" * 70)


# =============================================================================
# Example 1: Basic Register Write and Read
# =============================================================================

def example_basic_write_read():
    """Example: Write to a register and read it back."""
    print_separator()
    print("Example 1: Basic Register Write and Read")
    print_separator()
    
    rf = RegisterFile()
    signals = ControlSignals()
    
    # Step 1: Write value 42 to register x5
    print("\nStep 1: Write 42 to x5")
    signals.rf_we = 1  # Enable write
    signals.rf_waddr = int_to_bits(5, 5)  # Write to x5
    signals.rf_raddr_a = int_to_bits(0, 5)  # Read x0
    signals.rf_raddr_b = int_to_bits(0, 5)  # Read x0
    
    result = register_with_control(rf, signals, int_to_bin32(42))
    
    print(f"  Control Signals:")
    print(f"    rf_we = {signals.rf_we}")
    print(f"    rf_waddr = {bits_to_int(signals.rf_waddr)} (x5)")
    print(f"  Written: {result['written']}")
    print(f"  Trace: {result['trace'][0]}")
    
    # Step 2: Read back from x5
    print("\nStep 2: Read from x5")
    signals.rf_we = 0  # Disable write
    signals.rf_raddr_a = int_to_bits(5, 5)  # Read x5
    signals.rf_raddr_b = int_to_bits(0, 5)  # Read x0
    
    result = register_with_control(rf, signals)
    
    print(f"  Control Signals:")
    print(f"    rf_we = {signals.rf_we}")
    print(f"    rf_raddr_a = {bits_to_int(signals.rf_raddr_a)} (x5)")
    print(f"  Value read from x5: {bits_to_int(result['read_a'])}")
    print(f"  Trace:")
    for trace_line in result['trace']:
        print(f"    {trace_line}")


# =============================================================================
# Example 2: x0 is Hardwired to Zero
# =============================================================================

def example_x0_hardwired():
    """Example: Demonstrate that x0 is always zero."""
    print_separator()
    print("Example 2: x0 is Hardwired to Zero")
    print_separator()
    
    rf = RegisterFile()
    signals = ControlSignals()
    
    # Try to write to x0 (should be ignored)
    print("\nAttempting to write 999 to x0...")
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(0, 5)  # x0
    signals.rf_raddr_a = int_to_bits(0, 5)
    signals.rf_raddr_b = int_to_bits(0, 5)
    
    result = register_with_control(rf, signals, int_to_bin32(999))
    
    print(f"  Write attempted: {result['written']}")
    print(f"  Value in x0: {bits_to_int(result['read_a'])} (should be 0)")
    print(f"  Trace: {result['trace'][0]}")
    
    print("\nx0 is hardwired to zero - writes are silently ignored!")


# =============================================================================
# Example 3: Typical ALU Operation Sequence
# =============================================================================

def example_alu_operation():
    """Example: Typical sequence for an ALU operation (ADD x3, x1, x2)."""
    print_separator()
    print("Example 3: Typical ALU Operation - ADD x3, x1, x2")
    print_separator()
    
    rf = RegisterFile()
    signals = ControlSignals()
    
    # Initialize x1 and x2 with values
    print("\nSetup: Initialize registers")
    rf.write_int_reg(1, int_to_bin32(10))
    rf.write_int_reg(2, int_to_bin32(20))
    print("  x1 = 10")
    print("  x2 = 20")
    
    # Step 1: Instruction Decode - Read operands
    print("\nStep 1: Instruction Decode - Read operands from x1 and x2")
    signals.rf_we = 0  # No write during decode
    signals.rf_raddr_a = int_to_bits(1, 5)  # Read x1
    signals.rf_raddr_b = int_to_bits(2, 5)  # Read x2
    
    result = register_with_control(rf, signals)
    
    operand_a = bits_to_int(result['read_a'])
    operand_b = bits_to_int(result['read_b'])
    
    print(f"  Operand A (x1): {operand_a}")
    print(f"  Operand B (x2): {operand_b}")
    
    # Step 2: Execute - Perform ALU operation (simulated)
    print("\nStep 2: Execute - ALU performs ADD")
    alu_result = operand_a + operand_b
    print(f"  ALU Result: {operand_a} + {operand_b} = {alu_result}")
    
    # Step 3: Writeback - Store result to x3
    print("\nStep 3: Writeback - Store result to x3")
    signals.rf_we = 1  # Enable write
    signals.rf_waddr = int_to_bits(3, 5)  # Write to x3
    signals.rf_raddr_a = int_to_bits(3, 5)  # Read back x3 to verify
    
    result = register_with_control(rf, signals, int_to_bin32(alu_result))
    
    print(f"  Written to x3: {bits_to_int(result['read_a'])}")
    print(f"  Operation complete!")


# =============================================================================
# Example 4: Pipeline Simulation
# =============================================================================

def example_pipeline_simulation():
    """Example: Simulate multiple instructions in a pipeline."""
    print_separator()
    print("Example 4: Pipeline Simulation - Multiple Instructions")
    print_separator()
    
    rf = RegisterFile()
    signals = ControlSignals()
    
    # Program:
    # ADDI x1, x0, 5    -> x1 = 5
    # ADDI x2, x0, 10   -> x2 = 10
    # ADD  x3, x1, x2   -> x3 = x1 + x2 = 15
    # SUB  x4, x3, x1   -> x4 = x3 - x1 = 10
    
    print("\nProgram:")
    print("  ADDI x1, x0, 5")
    print("  ADDI x2, x0, 10")
    print("  ADD  x3, x1, x2")
    print("  SUB  x4, x3, x1")
    print("\nExecution:")
    
    # Instruction 1: ADDI x1, x0, 5
    print("\n1. ADDI x1, x0, 5")
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(1, 5)
    signals.rf_raddr_a = int_to_bits(1, 5)
    result = register_with_control(rf, signals, int_to_bin32(5))
    print(f"   x1 = {bits_to_int(result['read_a'])}")
    
    # Instruction 2: ADDI x2, x0, 10
    print("\n2. ADDI x2, x0, 10")
    signals.rf_waddr = int_to_bits(2, 5)
    signals.rf_raddr_a = int_to_bits(2, 5)
    result = register_with_control(rf, signals, int_to_bin32(10))
    print(f"   x2 = {bits_to_int(result['read_a'])}")
    
    # Instruction 3: ADD x3, x1, x2
    print("\n3. ADD x3, x1, x2")
    # Read operands
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(1, 5)
    signals.rf_raddr_b = int_to_bits(2, 5)
    result = register_with_control(rf, signals)
    sum_val = bits_to_int(result['read_a']) + bits_to_int(result['read_b'])
    # Write result
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(3, 5)
    signals.rf_raddr_a = int_to_bits(3, 5)
    result = register_with_control(rf, signals, int_to_bin32(sum_val))
    print(f"   x3 = {bits_to_int(result['read_a'])}")
    
    # Instruction 4: SUB x4, x3, x1
    print("\n4. SUB x4, x3, x1")
    # Read operands
    signals.rf_we = 0
    signals.rf_raddr_a = int_to_bits(3, 5)
    signals.rf_raddr_b = int_to_bits(1, 5)
    result = register_with_control(rf, signals)
    diff_val = bits_to_int(result['read_a']) - bits_to_int(result['read_b'])
    # Write result
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(4, 5)
    signals.rf_raddr_a = int_to_bits(4, 5)
    result = register_with_control(rf, signals, int_to_bin32(diff_val))
    print(f"   x4 = {bits_to_int(result['read_a'])}")
    
    print("\nFinal Register State:")
    for i in [1, 2, 3, 4]:
        signals.rf_we = 0
        signals.rf_raddr_a = int_to_bits(i, 5)
        result = register_with_control(rf, signals)
        print(f"  x{i} = {bits_to_int(result['read_a'])}")


# =============================================================================
# Example 5: Trace Output Analysis
# =============================================================================

def example_trace_analysis():
    """Example: Analyzing trace output for debugging."""
    print_separator()
    print("Example 5: Trace Output for Debugging")
    print_separator()
    
    rf = RegisterFile()
    signals = ControlSignals()
    
    # Pre-load some registers
    rf.write_int_reg(5, int_to_bin32(100))
    rf.write_int_reg(10, int_to_bin32(200))
    
    print("\nPerforming: Write 300 to x15, Read x5 and x10")
    signals.rf_we = 1
    signals.rf_waddr = int_to_bits(15, 5)
    signals.rf_raddr_a = int_to_bits(5, 5)
    signals.rf_raddr_b = int_to_bits(10, 5)
    
    result = register_with_control(rf, signals, int_to_bin32(300))
    
    print("\nDetailed Trace:")
    for i, trace_line in enumerate(result['trace'], 1):
        print(f"  {i}. {trace_line}")
    
    print("\nTrace shows:")
    print("  - WRITE operation to x15")
    print("  - READ_A operation from x5")
    print("  - READ_B operation from x10")
    print("  - Bit patterns for verification")


# =============================================================================
# Main
# =============================================================================

def main():
    """Run all register control integration examples."""
    print("\n" + "=" * 70)
    print("REGISTER FILE CONTROL SIGNAL INTEGRATION EXAMPLES")
    print("=" * 70)
    
    example_basic_write_read()
    print("\n")
    
    example_x0_hardwired()
    print("\n")
    
    example_alu_operation()
    print("\n")
    
    example_pipeline_simulation()
    print("\n")
    
    example_trace_analysis()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
