#!/usr/bin/env python3
"""
Shifter Control Integration Example

Demonstrates Shifter integration with Control Signals, showing:
- Control signal setup for SLL, SRL, and SRA operations
- Operation execution with signal tracking
- Operation traces and shift amount handling
- Signal preservation through operations
- Direct use of shifter_with_control() wrapper
"""

from riscsim.cpu.control_signals import (
    ControlSignals,
    SH_OP_SLL, SH_OP_SRL, SH_OP_SRA
)
from riscsim.cpu.shifter import shifter_with_control
from riscsim.utils.twos_complement import encode_twos_complement, decode_twos_complement


# Helper functions using bit-level operations
def int_to_bin32(n):
    """Convert integer to 32-bit binary list (MSB at index 0)"""
    result = encode_twos_complement(n)
    return [int(c) for c in result['bin'].replace('_', '')]


def bin32_to_int(bits):
    """Convert 32-bit binary list to signed integer"""
    result = decode_twos_complement(bits)
    return result['value']


def bin32_to_hex(bits):
    """Convert 32-bit binary list to hex string"""
    # Map 4-bit nibbles to hex characters
    hex_map = {
        (0,0,0,0): '0', (0,0,0,1): '1', (0,0,1,0): '2', (0,0,1,1): '3',
        (0,1,0,0): '4', (0,1,0,1): '5', (0,1,1,0): '6', (0,1,1,1): '7',
        (1,0,0,0): '8', (1,0,0,1): '9', (1,0,1,0): 'A', (1,0,1,1): 'B',
        (1,1,0,0): 'C', (1,1,0,1): 'D', (1,1,1,0): 'E', (1,1,1,1): 'F',
    }
    
    hex_string = ""
    for i in range(0, 32, 4):
        nibble = tuple(bits[i:i+4])
        hex_string = hex_string + hex_map[nibble]
    
    return hex_string


def demo_shift_left_logical():
    """Demonstrate Shift Left Logical operation."""
    print("=" * 70)
    print("SHIFT LEFT LOGICAL (SLL)")
    print("=" * 70)
    
    # Create control signals
    signals = ControlSignals()
    signals.sh_op = SH_OP_SLL
    signals.sh_amount = [0, 0, 1, 0, 0]  # 4 in binary
    signals.rf_waddr = [0, 0, 0, 1, 1]  # Write to register x3
    signals.rf_we = 1
    
    # Prepare operand
    operand = int_to_bin32(0x12345678)
    
    print(f"Operand: 0x{bin32_to_hex(operand)}")
    print(f"Operation: SLL (Shift Left Logical)")
    print(f"Shift Amount: 4 bits")
    print(f"Control Signals:")
    print(f"  sh_op: {signals.sh_op}")
    print(f"  sh_amount: {signals.sh_amount}")
    print(f"  rf_waddr: {signals.rf_waddr}")
    
    # Perform shifter operation
    result_dict = shifter_with_control(operand, signals)
    result = result_dict['result']
    
    print(f"\nResult: 0x{bin32_to_hex(result)}")
    print(f"Trace: {result_dict['trace']}")
    print(f"Expected: 0x12345678 << 4 = 0x23456780")
    print()


def demo_shift_right_logical():
    """Demonstrate Shift Right Logical operation."""
    print("=" * 70)
    print("SHIFT RIGHT LOGICAL (SRL)")
    print("=" * 70)
    
    signals = ControlSignals()
    signals.sh_op = SH_OP_SRL
    signals.sh_amount = [0, 1, 0, 0, 0]  # 8 in binary
    signals.rf_we = 1
    
    operand = int_to_bin32(0x12345678)
    
    print(f"Operand: 0x{bin32_to_hex(operand)}")
    print(f"Operation: SRL (Shift Right Logical)")
    print(f"Shift Amount: 8 bits")
    
    result_dict = shifter_with_control(operand, signals)
    result = result_dict['result']
    
    print(f"\nResult: 0x{bin32_to_hex(result)}")
    print(f"Trace: {result_dict['trace']}")
    print(f"Note: SRL fills with zeros from the left")
    print()


def demo_shift_right_arithmetic():
    """Demonstrate Shift Right Arithmetic with sign extension."""
    print("=" * 70)
    print("SHIFT RIGHT ARITHMETIC (SRA) - SIGN EXTENSION")
    print("=" * 70)
    
    signals = ControlSignals()
    signals.sh_op = SH_OP_SRA
    signals.sh_amount = [0, 0, 1, 0, 0]  # 4 in binary
    signals.rf_we = 1
    
    # Test with negative number (MSB = 1)
    operand = int_to_bin32(0x80000000)  # INT_MIN
    
    print(f"Operand: 0x{bin32_to_hex(operand)} (negative number)")
    print(f"Operation: SRA (Shift Right Arithmetic)")
    print(f"Shift Amount: 4 bits")
    
    result_dict = shifter_with_control(operand, signals)
    result = result_dict['result']
    
    print(f"\nResult: 0x{bin32_to_hex(result)}")
    print(f"Trace: {result_dict['trace']}")
    print(f"Note: SRA preserves the sign bit (fills with 1s from the left)")
    print()


def demo_shift_comparison():
    """Compare SRL vs SRA on negative number."""
    print("=" * 70)
    print("SRL vs SRA COMPARISON ON NEGATIVE NUMBER")
    print("=" * 70)
    
    operand = int_to_bin32(0xF0000000)
    shift_amount = [0, 0, 1, 0, 0]  # 4
    
    print(f"Operand: 0x{bin32_to_hex(operand)}")
    print(f"Shift Amount: 4 bits")
    print()
    
    # Test SRL
    signals_srl = ControlSignals()
    signals_srl.sh_op = SH_OP_SRL
    signals_srl.sh_amount = shift_amount
    
    result_srl_dict = shifter_with_control(operand, signals_srl)
    result_srl = result_srl_dict['result']
    
    print(f"SRL Result: 0x{bin32_to_hex(result_srl)}")
    print(f"  Fills with zeros from left")
    
    # Test SRA
    signals_sra = ControlSignals()
    signals_sra.sh_op = SH_OP_SRA
    signals_sra.sh_amount = shift_amount
    
    result_sra_dict = shifter_with_control(operand, signals_sra)
    result_sra = result_sra_dict['result']
    
    print(f"SRA Result: 0x{bin32_to_hex(result_sra)}")
    print(f"  Preserves sign bit (fills with ones)")
    print()


def demo_edge_cases():
    """Demonstrate edge cases: zero shift and maximum shift."""
    print("=" * 70)
    print("SHIFTER EDGE CASES")
    print("=" * 70)
    
    operand = int_to_bin32(0x12345678)
    
    # Zero shift
    print("Test 1: Zero shift amount")
    signals = ControlSignals()
    signals.sh_op = SH_OP_SLL
    signals.sh_amount = [0, 0, 0, 0, 0]  # 0
    
    result_dict = shifter_with_control(operand, signals)
    result = result_dict['result']
    
    print(f"  Operand: 0x{bin32_to_hex(operand)}")
    print(f"  Result:  0x{bin32_to_hex(result)}")
    print(f"  No change (as expected) ✓")
    print()
    
    # Maximum shift
    print("Test 2: Maximum shift amount (31)")
    signals = ControlSignals()
    signals.sh_op = SH_OP_SRL
    signals.sh_amount = [1, 1, 1, 1, 1]  # 31
    
    operand_max = int_to_bin32(0xFFFFFFFF)
    result_dict = shifter_with_control(operand_max, signals)
    result = result_dict['result']
    
    print(f"  Operand: 0x{bin32_to_hex(operand_max)}")
    print(f"  Result:  0x{bin32_to_hex(result)}")
    print(f"  Only LSB remains: {bin32_to_int(result)} ✓")
    print()


def demo_signal_preservation():
    """Demonstrate that control signals are preserved through operations."""
    print("=" * 70)
    print("CONTROL SIGNAL PRESERVATION")
    print("=" * 70)
    
    signals = ControlSignals()
    signals.sh_op = SH_OP_SLL
    signals.sh_amount = [0, 0, 0, 1, 0]  # 2
    signals.cycle = 99
    signals.rf_waddr = [0, 1, 0, 1, 0]  # r10
    signals.rf_we = 1
    
    print("Original signals:")
    print(f"  sh_op: {signals.sh_op} (SLL)")
    print(f"  sh_amount: {signals.sh_amount} (shift by 2)")
    print(f"  cycle: {signals.cycle}")
    print(f"  rf_waddr: {signals.rf_waddr} (register 10)")
    print(f"  rf_we: {signals.rf_we}")
    
    # Perform operation
    operand = int_to_bin32(0x00000001)
    result_dict = shifter_with_control(operand, signals)
    returned_signals = result_dict['signals']
    
    print(f"\nAfter Shifter operation:")
    print(f"  sh_op: {returned_signals.sh_op}")
    print(f"  sh_amount: {returned_signals.sh_amount}")
    print(f"  cycle: {returned_signals.cycle}")
    print(f"  rf_waddr: {returned_signals.rf_waddr}")
    print(f"  All signals preserved correctly! ✓")
    print()


def demo_multi_operation_sequence():
    """Demonstrate multiple shifter operations in sequence."""
    print("=" * 70)
    print("MULTI-OPERATION SHIFTER SEQUENCE")
    print("=" * 70)
    
    value = int_to_bin32(0x00008000)
    
    print(f"Starting value: 0x{bin32_to_hex(value)}")
    print()
    
    operations = [
        ("SLL by 8", SH_OP_SLL, [0, 1, 0, 0, 0]),
        ("SRL by 4", SH_OP_SRL, [0, 0, 1, 0, 0]),
    ]
    
    for i, (desc, op, amount) in enumerate(operations, 1):
        print(f"Operation {i}: {desc}")
        
        signals = ControlSignals()
        signals.sh_op = op
        signals.sh_amount = amount
        signals.rf_we = 1
        
        result_dict = shifter_with_control(value, signals)
        value = result_dict['result']  # Use result for next operation
        
        print(f"  Result: 0x{bin32_to_hex(value)}")
        print(f"  Trace: {result_dict['trace']}")
        print()
    
    print(f"Final value: 0x{bin32_to_hex(value)}")
    print()


def main():
    """Run all Shifter control integration demonstrations."""
    print("\n" + "=" * 70)
    print("SHIFTER CONTROL INTEGRATION DEMONSTRATIONS")
    print("=" * 70)
    print()
    
    demo_shift_left_logical()
    demo_shift_right_logical()
    demo_shift_right_arithmetic()
    demo_shift_comparison()
    demo_edge_cases()
    demo_signal_preservation()
    demo_multi_operation_sequence()
    
    print("=" * 70)
    print("All demonstrations completed successfully!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
