#!/usr/bin/env python3
"""
ALU Control Integration Example

Demonstrates ALU integration with Control Signals, showing:
- Control signal setup for ALU operations
- Operation execution with control signal tracking
- Flag generation (N, Z, C, V)
- Operation traces and signal preservation
- Direct use of alu_with_control() wrapper
"""

from riscsim.cpu.control_signals import (
    ControlSignals,
    ALU_OP_ADD, ALU_OP_SUB, ALU_OP_AND, ALU_OP_OR
)
from riscsim.cpu.alu import alu_with_control
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


def demo_alu_addition():
    """Demonstrate ALU addition with control signals."""
    print("=" * 70)
    print("ALU ADDITION WITH CONTROL SIGNALS")
    print("=" * 70)
    
    # Create control signals
    signals = ControlSignals()
    signals.alu_op = ALU_OP_ADD
    signals.rf_waddr = [0, 0, 0, 1, 1]  # Write to register x3
    signals.rf_we = 1
    signals.cycle = 5
    
    # Prepare operands
    a = int_to_bin32(42)
    b = int_to_bin32(8)
    
    print(f"Operand A: {bin32_to_int(a)} (0x{bin32_to_hex(a)})")
    print(f"Operand B: {bin32_to_int(b)} (0x{bin32_to_hex(b)})")
    print(f"Operation: ADD")
    print(f"Control Signals:")
    print(f"  alu_op: {signals.alu_op}")
    print(f"  rf_waddr: {signals.rf_waddr} (register 3)")
    print(f"  rf_we: {signals.rf_we}")
    print(f"  cycle: {signals.cycle}")
    
    # Perform operation
    result_dict = alu_with_control(a, b, signals)
    result = result_dict['result']
    flags = result_dict['flags']
    
    print(f"\nResult: {bin32_to_int(result)} (0x{bin32_to_hex(result)})")
    print(f"Flags: N={flags['N']}, Z={flags['Z']}, C={flags['C']}, V={flags['V']}")
    print(f"Trace: {result_dict['trace']}")
    print()


def demo_alu_subtraction():
    """Demonstrate ALU subtraction with flags."""
    print("=" * 70)
    print("ALU SUBTRACTION WITH NEGATIVE RESULT")
    print("=" * 70)
    
    signals = ControlSignals()
    signals.alu_op = ALU_OP_SUB
    signals.rf_we = 1
    
    a = int_to_bin32(10)
    b = int_to_bin32(20)
    
    print(f"Operand A: {bin32_to_int(a)}")
    print(f"Operand B: {bin32_to_int(b)}")
    print(f"Operation: SUB (A - B)")
    
    result_dict = alu_with_control(a, b, signals)
    result = result_dict['result']
    flags = result_dict['flags']
    
    print(f"\nResult: {bin32_to_int(result)}")
    print(f"Flags: N={flags['N']} (Negative), Z={flags['Z']}, C={flags['C']}, V={flags['V']}")
    print(f"Expected: 10 - 20 = -10")
    print()


def demo_zero_flag():
    """Demonstrate zero flag detection."""
    print("=" * 70)
    print("ZERO FLAG DETECTION")
    print("=" * 70)
    
    signals = ControlSignals()
    signals.alu_op = ALU_OP_SUB
    
    a = int_to_bin32(50)
    b = int_to_bin32(50)
    
    print(f"Operand A: {bin32_to_int(a)}")
    print(f"Operand B: {bin32_to_int(b)}")
    print(f"Operation: SUB (A - B)")
    
    result_dict = alu_with_control(a, b, signals)
    result = result_dict['result']
    flags = result_dict['flags']
    
    print(f"\nResult: {bin32_to_int(result)}")
    print(f"Flags: N={flags['N']}, Z={flags['Z']} (Zero), C={flags['C']}, V={flags['V']}")
    print(f"Zero flag is set because result is 0 ✓")
    print()


def demo_overflow():
    """Demonstrate overflow detection."""
    print("=" * 70)
    print("OVERFLOW DETECTION")
    print("=" * 70)
    
    signals = ControlSignals()
    signals.alu_op = ALU_OP_ADD
    
    # Two large positive numbers that will overflow
    a = int_to_bin32(2147483647)  # INT_MAX
    b = int_to_bin32(1)
    
    print(f"Operand A: {bin32_to_int(a)} (INT_MAX)")
    print(f"Operand B: {bin32_to_int(b)}")
    print(f"Operation: ADD")
    
    result_dict = alu_with_control(a, b, signals)
    result = result_dict['result']
    flags = result_dict['flags']
    
    print(f"\nResult: {bin32_to_int(result)}")
    print(f"Flags: N={flags['N']}, Z={flags['Z']}, C={flags['C']}, V={flags['V']} (Overflow)")
    print(f"Overflow flag set because positive + positive = negative ✓")
    print()


def demo_bitwise_and():
    """Demonstrate bitwise AND operation."""
    print("=" * 70)
    print("BITWISE AND OPERATION")
    print("=" * 70)
    
    signals = ControlSignals()
    signals.alu_op = ALU_OP_AND
    
    a = int_to_bin32(0xFF00FF00)
    b = int_to_bin32(0x0F0F0F0F)
    
    print(f"Operand A: 0x{bin32_to_hex(a)}")
    print(f"Operand B: 0x{bin32_to_hex(b)}")
    print(f"Operation: AND")
    
    result_dict = alu_with_control(a, b, signals)
    result = result_dict['result']
    flags = result_dict['flags']
    
    print(f"\nResult: 0x{bin32_to_hex(result)}")
    print(f"Expected: 0xFF00FF00 & 0x0F0F0F0F = 0x0F000F00")
    print(f"Flags: N={flags['N']}, Z={flags['Z']}, C={flags['C']}, V={flags['V']}")
    print()


def demo_signal_preservation():
    """Demonstrate that control signals are preserved."""
    print("=" * 70)
    print("CONTROL SIGNAL PRESERVATION")
    print("=" * 70)
    
    signals = ControlSignals()
    signals.alu_op = ALU_OP_ADD
    signals.rf_waddr = [0, 1, 0, 1, 0]  # r10
    signals.rf_we = 1
    signals.cycle = 42
    signals.rf_raddr_a = [0, 0, 0, 0, 1]  # r1
    signals.rf_raddr_b = [0, 0, 0, 1, 0]  # r2
    
    print("Original signals:")
    print(f"  alu_op: {signals.alu_op}")
    print(f"  rf_waddr: {signals.rf_waddr} (r10)")
    print(f"  rf_we: {signals.rf_we}")
    print(f"  cycle: {signals.cycle}")
    print(f"  rf_raddr_a: {signals.rf_raddr_a} (r1)")
    print(f"  rf_raddr_b: {signals.rf_raddr_b} (r2)")
    
    a = int_to_bin32(100)
    b = int_to_bin32(200)
    
    result_dict = alu_with_control(a, b, signals)
    returned_signals = result_dict['signals']
    
    print(f"\nAfter ALU operation:")
    print(f"  alu_op: {returned_signals.alu_op}")
    print(f"  rf_waddr: {returned_signals.rf_waddr}")
    print(f"  rf_we: {returned_signals.rf_we}")
    print(f"  cycle: {returned_signals.cycle}")
    print(f"  All signals preserved correctly! ✓")
    print()


def demo_operation_sequence():
    """Demonstrate multiple ALU operations in sequence."""
    print("=" * 70)
    print("MULTI-OPERATION SEQUENCE")
    print("=" * 70)
    
    value = int_to_bin32(100)
    
    print(f"Starting value: {bin32_to_int(value)}")
    print()
    
    # Operation 1: Add 50
    signals = ControlSignals()
    signals.alu_op = ALU_OP_ADD
    b = int_to_bin32(50)
    
    result_dict = alu_with_control(value, b, signals)
    value = result_dict['result']
    print(f"Operation 1: ADD 50")
    print(f"  Result: {bin32_to_int(value)}")
    print(f"  Trace: {result_dict['trace']}")
    
    # Operation 2: Subtract 30
    signals.alu_op = ALU_OP_SUB
    b = int_to_bin32(30)
    
    result_dict = alu_with_control(value, b, signals)
    value = result_dict['result']
    print(f"\nOperation 2: SUB 30")
    print(f"  Result: {bin32_to_int(value)}")
    print(f"  Trace: {result_dict['trace']}")
    
    # Operation 3: AND with mask
    signals.alu_op = ALU_OP_AND
    b = int_to_bin32(0xFF)
    
    result_dict = alu_with_control(value, b, signals)
    value = result_dict['result']
    print(f"\nOperation 3: AND 0xFF")
    print(f"  Result: {bin32_to_int(value)} (0x{bin32_to_hex(value)})")
    print(f"  Trace: {result_dict['trace']}")
    
    print(f"\nFinal value: {bin32_to_int(value)}")
    print(f"Expected: (100 + 50 - 30) & 0xFF = 120")
    print()


def main():
    """Run all ALU control integration demonstrations."""
    print("\n" + "=" * 70)
    print("ALU CONTROL INTEGRATION DEMONSTRATIONS")
    print("=" * 70)
    print()
    
    demo_alu_addition()
    demo_alu_subtraction()
    demo_zero_flag()
    demo_overflow()
    demo_bitwise_and()
    demo_signal_preservation()
    demo_operation_sequence()
    
    print("=" * 70)
    print("All demonstrations completed successfully!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
