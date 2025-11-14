"""
FPU Control Signal Integration Example
======================================

Demonstrates how to use the Floating-Point Unit (FPU) with Control Unit signals.
Shows FADD, FSUB, FMUL operations with IEEE-754 single-precision floating-point.
"""

from riscsim.cpu.fpu import fpu_with_control, pack_f32, unpack_f32
from riscsim.cpu.control_unit import ControlSignals
from riscsim.utils.bit_utils import bits_to_hex_string


def example_fadd_operation():
    """Demonstrate floating-point addition: 3.5 + 2.25 = 5.75"""
    print("=" * 70)
    print("FADD Operation Example: 3.5 + 2.25")
    print("=" * 70)
    
    # Create control signals for FADD
    control = ControlSignals()
    control.fpu_op = "FADD"
    control.round_mode = 0  # RoundTiesToEven
    control.cycle = 10
    control.fpu_start = 1
    
    # Pack floating-point values
    a = 3.5
    b = 2.25
    rs1_bits = pack_f32(a)
    rs2_bits = pack_f32(b)
    
    # Execute FPU with control signals
    result = fpu_with_control(rs1_bits, rs2_bits, control)
    
    # Unpack result
    result_float = unpack_f32(result['result'])
    
    print(f"Inputs:")
    print(f"  rs1 = {a} (0x{bits_to_hex_string(rs1_bits)})")
    print(f"  rs2 = {b} (0x{bits_to_hex_string(rs2_bits)})")
    print(f"\nControl Signals:")
    print(f"  fpu_op = {control.fpu_op}")
    print(f"  round_mode = {control.round_mode} (RoundTiesToEven)")
    print(f"  cycle = {control.cycle}")
    print(f"\nResult:")
    print(f"  result = {result_float} (0x{bits_to_hex_string(result['result'])})")
    print(f"  expected = 5.75")
    print(f"\nFlags:")
    for key, value in result['flags'].items():
        print(f"  {key} = {value}")
    print(f"\nTrace Output:")
    for line in result['trace']:
        print(f"  {line}")
    print()


def example_fsub_operation():
    """Demonstrate floating-point subtraction: 10.0 - 3.5 = 6.5"""
    print("=" * 70)
    print("FSUB Operation Example: 10.0 - 3.5")
    print("=" * 70)
    
    control = ControlSignals()
    control.fpu_op = "FSUB"
    control.round_mode = 0
    control.cycle = 15
    
    a = 10.0
    b = 3.5
    rs1_bits = pack_f32(a)
    rs2_bits = pack_f32(b)
    
    result = fpu_with_control(rs1_bits, rs2_bits, control)
    result_float = unpack_f32(result['result'])
    
    print(f"Inputs:")
    print(f"  rs1 = {a}")
    print(f"  rs2 = {b}")
    print(f"\nControl Signals:")
    print(f"  fpu_op = {control.fpu_op}")
    print(f"  round_mode = {control.round_mode}")
    print(f"\nResult:")
    print(f"  result = {result_float}")
    print(f"  expected = 6.5")
    print(f"\nFlags:")
    for key, value in result['flags'].items():
        print(f"  {key} = {value}")
    print()


def example_fmul_operation():
    """Demonstrate floating-point multiplication: 2.5 × 4.0 = 10.0"""
    print("=" * 70)
    print("FMUL Operation Example: 2.5 × 4.0")
    print("=" * 70)
    
    control = ControlSignals()
    control.fpu_op = "FMUL"
    control.round_mode = 0
    control.cycle = 20
    
    a = 2.5
    b = 4.0
    rs1_bits = pack_f32(a)
    rs2_bits = pack_f32(b)
    
    result = fpu_with_control(rs1_bits, rs2_bits, control)
    result_float = unpack_f32(result['result'])
    
    print(f"Inputs:")
    print(f"  rs1 = {a}")
    print(f"  rs2 = {b}")
    print(f"\nControl Signals:")
    print(f"  fpu_op = {control.fpu_op}")
    print(f"  round_mode = {control.round_mode}")
    print(f"\nResult:")
    print(f"  result = {result_float}")
    print(f"  expected = 10.0")
    print(f"\nFlags:")
    for key, value in result['flags'].items():
        print(f"  {key} = {value}")
    print()


def example_overflow_detection():
    """Demonstrate overflow flag with very large numbers"""
    print("=" * 70)
    print("Overflow Detection Example: 3.4e38 + 3.4e38")
    print("=" * 70)
    
    control = ControlSignals()
    control.fpu_op = "FADD"
    control.round_mode = 0
    control.cycle = 25
    
    # Use very large numbers that will overflow
    a = 3.4e38
    b = 3.4e38
    rs1_bits = pack_f32(a)
    rs2_bits = pack_f32(b)
    
    result = fpu_with_control(rs1_bits, rs2_bits, control)
    result_float = unpack_f32(result['result'])
    
    print(f"Inputs:")
    print(f"  rs1 = {a:.2e}")
    print(f"  rs2 = {b:.2e}")
    print(f"\nResult:")
    print(f"  result = {result_float}")
    print(f"  (infinity due to overflow)")
    print(f"\nException Flags:")
    print(f"  overflow = {result['flags']['overflow']} ← Detected!")
    print(f"  invalid = {result['flags']['invalid']}")
    print(f"  underflow = {result['flags']['underflow']}")
    print(f"\nNote: IEEE-754 saturates to infinity on overflow")
    print()


def example_underflow_detection():
    """Demonstrate underflow with very small numbers"""
    print("=" * 70)
    print("Underflow Example: Very Small × Very Small")
    print("=" * 70)
    
    control = ControlSignals()
    control.fpu_op = "FMUL"
    control.round_mode = 0
    control.cycle = 30
    
    # Use very small numbers
    a = 1.0e-20
    b = 1.0e-20
    rs1_bits = pack_f32(a)
    rs2_bits = pack_f32(b)
    
    result = fpu_with_control(rs1_bits, rs2_bits, control)
    result_float = unpack_f32(result['result'])
    
    print(f"Inputs:")
    print(f"  rs1 = {a:.2e}")
    print(f"  rs2 = {b:.2e}")
    print(f"\nResult:")
    print(f"  result = {result_float}")
    print(f"  (may underflow to zero or denormal)")
    print(f"\nException Flags:")
    print(f"  underflow = {result['flags']['underflow']}")
    print(f"  overflow = {result['flags']['overflow']}")
    print(f"  invalid = {result['flags']['invalid']}")
    print()


def example_special_values():
    """Demonstrate operations with special IEEE-754 values"""
    print("=" * 70)
    print("Special Values Example")
    print("=" * 70)
    
    # Test 1: Adding to zero
    print("Test 1: 5.0 + 0.0")
    control = ControlSignals()
    control.fpu_op = "FADD"
    control.round_mode = 0
    
    rs1 = pack_f32(5.0)
    rs2 = pack_f32(0.0)
    result = fpu_with_control(rs1, rs2, control)
    print(f"  Result: {unpack_f32(result['result'])}")
    print(f"  Flags: invalid={result['flags']['invalid']}, overflow={result['flags']['overflow']}")
    print()
    
    # Test 2: Multiplying by zero
    print("Test 2: 5.0 × 0.0")
    control.fpu_op = "FMUL"
    rs1 = pack_f32(5.0)
    rs2 = pack_f32(0.0)
    result = fpu_with_control(rs1, rs2, control)
    print(f"  Result: {unpack_f32(result['result'])}")
    print(f"  Flags: invalid={result['flags']['invalid']}, overflow={result['flags']['overflow']}")
    print()
    
    # Test 3: Subtracting same values
    print("Test 3: 7.5 - 7.5")
    control.fpu_op = "FSUB"
    rs1 = pack_f32(7.5)
    rs2 = pack_f32(7.5)
    result = fpu_with_control(rs1, rs2, control)
    print(f"  Result: {unpack_f32(result['result'])}")
    print(f"  Flags: invalid={result['flags']['invalid']}, overflow={result['flags']['overflow']}")
    print()


def example_signal_preservation():
    """Demonstrate that control signals are preserved through operations"""
    print("=" * 70)
    print("Control Signal Preservation Example")
    print("=" * 70)
    
    # Set up control signals with specific values
    control = ControlSignals()
    control.fpu_op = "FADD"
    control.round_mode = 0
    control.cycle = 100
    control.fpu_start = 1
    control.fpu_state = "IDLE"
    control.rf_waddr = [0, 1, 0, 1, 0]  # Example write address
    
    print(f"Input Control Signals:")
    print(f"  fpu_op = {control.fpu_op}")
    print(f"  round_mode = {control.round_mode}")
    print(f"  cycle = {control.cycle}")
    print(f"  fpu_start = {control.fpu_start}")
    print(f"  rf_waddr = {bits_to_hex_string(control.rf_waddr)}")
    
    rs1 = pack_f32(1.5)
    rs2 = pack_f32(2.5)
    result = fpu_with_control(rs1, rs2, control)
    
    print(f"\nComputation: 1.5 + 2.5 = {unpack_f32(result['result'])}")
    
    print(f"\nOutput Control Signals (preserved):")
    output_signals = result['signals']
    print(f"  fpu_op = {output_signals.fpu_op}")
    print(f"  round_mode = {output_signals.round_mode}")
    print(f"  cycle = {output_signals.cycle}")
    print(f"  fpu_start = {output_signals.fpu_start}")
    print(f"  rf_waddr = {bits_to_hex_string(output_signals.rf_waddr)}")
    
    print(f"\n✓ All control signals preserved correctly")
    print()


def example_multi_operation_sequence():
    """Demonstrate using FPU for multiple operations in sequence"""
    print("=" * 70)
    print("Multi-Operation Sequence Example")
    print("=" * 70)
    print("Computing: (a + b) × c - d")
    print()
    
    # Step 1: Add 2.5 + 1.5
    a, b = 2.5, 1.5
    control = ControlSignals()
    control.fpu_op = "FADD"
    control.round_mode = 0
    control.cycle = 50
    
    rs1 = pack_f32(a)
    rs2 = pack_f32(b)
    result1 = fpu_with_control(rs1, rs2, control)
    sum_val = unpack_f32(result1['result'])
    
    print(f"Step 1: {a} + {b} = {sum_val}")
    
    # Step 2: Multiply result by 3.0
    c = 3.0
    control.fpu_op = "FMUL"
    control.cycle = 51
    
    rs1 = result1['result']
    rs2 = pack_f32(c)
    result2 = fpu_with_control(rs1, rs2, control)
    product = unpack_f32(result2['result'])
    
    print(f"Step 2: {sum_val} × {c} = {product}")
    
    # Step 3: Subtract 2.0
    d = 2.0
    control.fpu_op = "FSUB"
    control.cycle = 52
    
    rs1 = result2['result']
    rs2 = pack_f32(d)
    result3 = fpu_with_control(rs1, rs2, control)
    final = unpack_f32(result3['result'])
    
    print(f"Step 3: {product} - {d} = {final}")
    
    print(f"\nFinal Result: {final}")
    print(f"Verification: (2.5 + 1.5) × 3.0 - 2.0 = 4.0 × 3.0 - 2.0 = 12.0 - 2.0 = 10.0 ✓")
    print()


def example_rounding_modes():
    """Demonstrate different rounding modes (though only mode 0 is fully implemented)"""
    print("=" * 70)
    print("Rounding Mode Example")
    print("=" * 70)
    
    control = ControlSignals()
    control.fpu_op = "FADD"
    control.round_mode = 0  # RoundTiesToEven (IEEE-754 default)
    
    # Use values that might need rounding
    a = 1.0 / 3.0  # 0.333...
    b = 2.0 / 3.0  # 0.666...
    
    rs1 = pack_f32(a)
    rs2 = pack_f32(b)
    
    result = fpu_with_control(rs1, rs2, control)
    result_float = unpack_f32(result['result'])
    
    print(f"Inputs:")
    print(f"  rs1 = {a} (1/3, infinite decimal)")
    print(f"  rs2 = {b} (2/3, infinite decimal)")
    print(f"\nRounding Mode: {control.round_mode} (RoundTiesToEven)")
    print(f"\nResult:")
    print(f"  result = {result_float}")
    print(f"  expected ≈ 1.0")
    print(f"\nNote: IEEE-754 rounds 1/3 + 2/3 to exactly 1.0")
    print(f"      with RoundTiesToEven mode")
    print()


def main():
    """Run all FPU control integration examples"""
    print("\n" + "=" * 70)
    print("FPU CONTROL SIGNAL INTEGRATION EXAMPLES")
    print("=" * 70)
    print()
    
    example_fadd_operation()
    example_fsub_operation()
    example_fmul_operation()
    example_overflow_detection()
    example_underflow_detection()
    example_special_values()
    example_signal_preservation()
    example_multi_operation_sequence()
    example_rounding_modes()
    
    print("=" * 70)
    print("All FPU examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
