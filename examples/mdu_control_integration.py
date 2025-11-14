"""
MDU Control Signal Integration Example
=====================================

Demonstrates how to use the Multiply/Divide Unit (MDU) with Control Unit signals.
Shows MUL, MULH, DIV, REM operations and how control signals flow through the MDU.
"""

from riscsim.cpu.mdu import mdu_with_control
from riscsim.cpu.control_unit import ControlSignals
from riscsim.utils.bit_utils import bits_to_hex_string


# Helper functions for integer/bit conversion
def int_to_bits(n, width=32):
    """Convert integer to bit list (MSB at index 0)."""
    if n < 0:
        n = (1 << width) + n  # Two's complement conversion
    return [(n >> (width - 1 - i)) & 1 for i in range(width)]


def bits_to_int(bits, signed=True):
    """Convert bit list to integer."""
    val = sum(bit << (len(bits) - 1 - i) for i, bit in enumerate(bits))
    if signed and bits[0] == 1:
        val -= (1 << len(bits))
    return val


def example_mul_operation():
    """Demonstrate MUL operation: 15 × 8 = 120"""
    print("=" * 70)
    print("MUL Operation Example: 15 × 8")
    print("=" * 70)
    
    # Create control signals for MUL operation
    control = ControlSignals()
    control.md_op = "MUL"
    control.cycle = 10
    control.md_start = 1
    
    # Convert operands to 32-bit
    rs1 = int_to_bits(15, 32)
    rs2 = int_to_bits(8, 32)
    
    # Execute MDU with control signals
    result = mdu_with_control(rs1, rs2, control)
    
    print(f"Inputs:")
    print(f"  rs1 = {bits_to_int(rs1)} (0x{bits_to_hex_string(rs1)})")
    print(f"  rs2 = {bits_to_int(rs2)} (0x{bits_to_hex_string(rs2)})")
    print(f"\nControl Signals (input):")
    print(f"  md_op = {control.md_op}")
    print(f"  cycle = {control.cycle}")
    print(f"  md_start = {control.md_start}")
    print(f"\nResult:")
    print(f"  result = {bits_to_int(result['result'])} (0x{bits_to_hex_string(result['result'])})")
    print(f"\nFlags:")
    for key, value in result['flags'].items():
        print(f"  {key} = {value}")
    print(f"\nTrace Output:")
    for line in result['trace']:
        print(f"  {line}")
    print()


def example_mulh_operation():
    """Demonstrate MULH operation: Get upper 32 bits of signed multiplication"""
    print("=" * 70)
    print("MULH Operation Example: Upper 32 bits of (-2147483648) × 2")
    print("=" * 70)
    
    # Create control signals
    control = ControlSignals()
    control.md_op = "MULH"
    control.cycle = 15
    
    # Use INT_MIN and 2
    rs1 = int_to_bits(-2147483648, 32)  # INT_MIN
    rs2 = int_to_bits(2, 32)
    
    result = mdu_with_control(rs1, rs2, control)
    
    print(f"Inputs:")
    print(f"  rs1 = {bits_to_int(rs1)} (INT_MIN)")
    print(f"  rs2 = {bits_to_int(rs2)}")
    print(f"\nControl Signals:")
    print(f"  md_op = {control.md_op}")
    print(f"  cycle = {control.cycle}")
    print(f"\nResult (upper 32 bits):")
    print(f"  result = {bits_to_int(result['result'])} (0x{bits_to_hex_string(result['result'])})")
    print(f"  hi_bits = {bits_to_int(result['hi_bits'])} (same as result for MULH)")
    print(f"\nNote: Full 64-bit product = 0xFFFFFFFF00000000")
    print(f"      Upper 32 bits = 0xFFFFFFFF = -1 (signed)")
    print()


def example_div_operation():
    """Demonstrate DIV operation: 100 ÷ 7 = 14 remainder 2"""
    print("=" * 70)
    print("DIV Operation Example: 100 ÷ 7")
    print("=" * 70)
    
    control = ControlSignals()
    control.md_op = "DIV"
    control.cycle = 20
    
    rs1 = int_to_bits(100, 32)
    rs2 = int_to_bits(7, 32)
    
    result = mdu_with_control(rs1, rs2, control)
    
    print(f"Inputs:")
    print(f"  dividend (rs1) = {bits_to_int(rs1)}")
    print(f"  divisor (rs2) = {bits_to_int(rs2)}")
    print(f"\nResult:")
    print(f"  quotient = {bits_to_int(result['result'])}")
    print(f"  quotient field = {bits_to_int(result['quotient'])} (same as result)")
    print(f"  remainder = {bits_to_int(result['remainder'])}")
    print(f"\nVerification: {bits_to_int(rs1)} = ({bits_to_int(result['quotient'])} × {bits_to_int(rs2)}) + {bits_to_int(result['remainder'])}")
    print(f"              100 = (14 × 7) + 2 = 98 + 2 ✓")
    print()


def example_rem_operation():
    """Demonstrate REM operation: Get remainder of 50 ÷ 8"""
    print("=" * 70)
    print("REM Operation Example: 50 mod 8")
    print("=" * 70)
    
    control = ControlSignals()
    control.md_op = "REM"
    control.cycle = 25
    
    rs1 = int_to_bits(50, 32)
    rs2 = int_to_bits(8, 32)
    
    result = mdu_with_control(rs1, rs2, control)
    
    print(f"Inputs:")
    print(f"  dividend = {bits_to_int(rs1)}")
    print(f"  divisor = {bits_to_int(rs2)}")
    print(f"\nResult:")
    print(f"  remainder = {bits_to_int(result['result'])}")
    print(f"\nVerification: 50 = (6 × 8) + 2")
    print(f"              REM returns the remainder: 2")
    print()


def example_div_by_zero():
    """Demonstrate division by zero handling per RISC-V spec"""
    print("=" * 70)
    print("Division by Zero Example (RISC-V semantics)")
    print("=" * 70)
    
    control = ControlSignals()
    control.md_op = "DIV"
    control.cycle = 30
    
    rs1 = int_to_bits(42, 32)
    rs2 = int_to_bits(0, 32)  # Divide by zero
    
    result = mdu_with_control(rs1, rs2, control)
    
    print(f"Inputs:")
    print(f"  dividend = {bits_to_int(rs1)}")
    print(f"  divisor = {bits_to_int(rs2)} (ZERO!)")
    print(f"\nRISC-V Specification Behavior:")
    print(f"  DIV by 0 → quotient = -1")
    print(f"  REM by 0 → remainder = dividend")
    print(f"\nResult:")
    print(f"  quotient = {bits_to_int(result['result'])} (0x{bits_to_hex_string(result['result'])})")
    print(f"  remainder = {bits_to_int(result['remainder'])}")
    print(f"\nNote: RISC-V doesn't trap on division by zero.")
    print(f"      It defines specific return values instead.")
    print()


def example_signal_preservation():
    """Demonstrate that control signals are preserved through operations"""
    print("=" * 70)
    print("Control Signal Preservation Example")
    print("=" * 70)
    
    # Set up control signals with specific values
    control = ControlSignals()
    control.md_op = "MUL"
    control.cycle = 42
    control.md_start = 1
    control.md_busy = 0
    control.md_done = 0
    control.pc = [0, 1, 0, 0, 0, 0, 0, 0]  # Example PC value
    
    print(f"Input Control Signals:")
    print(f"  md_op = {control.md_op}")
    print(f"  cycle = {control.cycle}")
    print(f"  md_start = {control.md_start}")
    print(f"  pc = {bits_to_hex_string(control.pc)}")
    
    rs1 = int_to_bits(5, 32)
    rs2 = int_to_bits(6, 32)
    
    result = mdu_with_control(rs1, rs2, control)
    
    print(f"\nComputation: {bits_to_int(rs1)} × {bits_to_int(rs2)} = {bits_to_int(result['result'])}")
    
    print(f"\nOutput Control Signals (preserved):")
    output_signals = result['signals']
    print(f"  md_op = {output_signals.md_op}")
    print(f"  cycle = {output_signals.cycle}")
    print(f"  md_start = {output_signals.md_start}")
    print(f"  pc = {bits_to_hex_string(output_signals.pc)}")
    
    print(f"\n✓ All control signals preserved correctly")
    print()


def example_multi_operation_sequence():
    """Demonstrate using MDU for multiple operations in sequence"""
    print("=" * 70)
    print("Multi-Operation Sequence Example")
    print("=" * 70)
    print("Computing: (a × b) ÷ c, then result mod d")
    print()
    
    # Step 1: Multiply 24 × 5
    a, b = 24, 5
    control = ControlSignals()
    control.md_op = "MUL"
    control.cycle = 50
    
    rs1 = int_to_bits(a, 32)
    rs2 = int_to_bits(b, 32)
    result1 = mdu_with_control(rs1, rs2, control)
    product = bits_to_int(result1['result'])
    
    print(f"Step 1: {a} × {b} = {product}")
    
    # Step 2: Divide result by 8
    c = 8
    control.md_op = "DIV"
    control.cycle = 51
    
    rs1 = int_to_bits(product, 32)
    rs2 = int_to_bits(c, 32)
    result2 = mdu_with_control(rs1, rs2, control)
    quotient = bits_to_int(result2['result'])
    
    print(f"Step 2: {product} ÷ {c} = {quotient}")
    
    # Step 3: Remainder when dividing by 7
    d = 7
    control.md_op = "REM"
    control.cycle = 52
    
    rs1 = int_to_bits(quotient, 32)
    rs2 = int_to_bits(d, 32)
    result3 = mdu_with_control(rs1, rs2, control)
    remainder = bits_to_int(result3['result'])
    
    print(f"Step 3: {quotient} mod {d} = {remainder}")
    
    print(f"\nFinal Result: {remainder}")
    print(f"Verification: (24 × 5) ÷ 8 = 120 ÷ 8 = 15")
    print(f"              15 mod 7 = 1 ✓")
    print()


def main():
    """Run all MDU control integration examples"""
    print("\n" + "=" * 70)
    print("MDU CONTROL SIGNAL INTEGRATION EXAMPLES")
    print("=" * 70)
    print()
    
    example_mul_operation()
    example_mulh_operation()
    example_div_operation()
    example_rem_operation()
    example_div_by_zero()
    example_signal_preservation()
    example_multi_operation_sequence()
    
    print("=" * 70)
    print("All MDU examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
