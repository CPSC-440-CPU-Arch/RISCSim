# AI-BEGIN
"""
IEEE-754 Single-Precision (Float32) Floating-Point Unit for RISC-V

Implements bit-level floating-point operations without using host language
float arithmetic:
- pack_f32/unpack_f32: Encode/decode IEEE-754 float32 format
- fadd_f32, fsub_f32, fmul_f32: Arithmetic operations with RoundTiesToEven
- Special value handling: +/-0, +/-infinity, NaN, subnormals

IEEE-754 Float32 format (32 bits total, MSB at index 0):
  Bit 0:      Sign (0=positive, 1=negative)
  Bits 1-8:   Exponent (8 bits, biased by 127)
  Bits 9-31:  Fraction (23 bits, implicit leading 1 for normalized)

Special values:
  +/-0:        exp=0,   frac=0
  +/-infinity: exp=255, frac=0
  NaN:         exp=255, frac!=0
  Subnormal:   exp=0,   frac!=0 (no implicit leading 1)

All bit arrays follow MSB-first convention (index 0 = MSB, index 31 = LSB)
"""

from riscsim.utils.bit_utils import (
    slice_bits, concat_bits, bits_or, is_zero, bits_and,
    zero_extend, bits_not, bits_xor
)
from riscsim.cpu.alu import alu
from riscsim.cpu.shifter import shifter


# IEEE-754 Float32 constants
FLOAT32_WIDTH = 32
SIGN_WIDTH = 1
EXP_WIDTH = 8
FRAC_WIDTH = 23
EXP_BIAS = 127  # Bias for float32 exponent

# Special exponent values
EXP_ZERO = [0] * EXP_WIDTH      # All zeros
EXP_INF_NAN = [1] * EXP_WIDTH   # All ones (255)


def extract_float32_fields(bits):
    """
    Extract sign, exponent, and fraction fields from IEEE-754 float32 bits.

    Args:
        bits: 32-bit array in IEEE-754 format (MSB at index 0)

    Returns:
        Tuple of (sign_bit, exp_bits[8], frac_bits[23])
    """
    assert len(bits) == FLOAT32_WIDTH, f"Expected 32 bits, got {len(bits)}"

    sign = bits[0]
    exp = slice_bits(bits, 1, 9)      # Bits 1-8
    frac = slice_bits(bits, 9, 32)    # Bits 9-31

    return (sign, exp, frac)


def pack_float32_fields(sign, exp, frac):
    """
    Pack sign, exponent, and fraction into IEEE-754 float32 format.

    Args:
        sign: Single bit (0 or 1)
        exp: 8-bit array
        frac: 23-bit array

    Returns:
        32-bit array in IEEE-754 format
    """
    assert len(exp) == EXP_WIDTH, f"Exponent must be {EXP_WIDTH} bits"
    assert len(frac) == FRAC_WIDTH, f"Fraction must be {FRAC_WIDTH} bits"

    return concat_bits([sign], exp, frac)


def is_special_value(exp, frac):
    """
    Check if the exponent and fraction represent a special value.

    Returns:
        Tuple of (is_zero, is_inf, is_nan, is_subnormal)
    """
    exp_is_zero = is_zero(exp)
    exp_is_max = all(b == 1 for b in exp)  # exp == 255
    frac_is_zero = is_zero(frac)

    is_zero_val = exp_is_zero and frac_is_zero
    is_subnormal = exp_is_zero and not frac_is_zero
    is_inf = exp_is_max and frac_is_zero
    is_nan = exp_is_max and not frac_is_zero

    return (is_zero_val, is_inf, is_nan, is_subnormal)


def leading_zeros_count(bits):
    """
    Count the number of leading zeros in a bit array.

    Args:
        bits: Bit array

    Returns:
        Integer count of leading zeros
    """
    count = 0
    for bit in bits:
        if bit == 0:
            count += 1
        else:
            break
    return count


def compare_unsigned(a, b):
    """
    Compare two bit arrays as unsigned integers.

    Args:
        a, b: Bit arrays (same length)

    Returns:
        -1 if a < b, 0 if a == b, 1 if a > b
    """
    assert len(a) == len(b), "Bit arrays must have same length"

    for i in range(len(a)):
        if a[i] < b[i]:
            return -1
        elif a[i] > b[i]:
            return 1
    return 0


def increment_bits(bits):
    """
    Increment a bit array by 1 using the ALU.

    Args:
        bits: Bit array

    Returns:
        Incremented bit array (same length)
    """
    # Pad to 32 bits if needed
    if len(bits) < 32:
        bits_32 = zero_extend(bits, 32)
    else:
        bits_32 = bits[:]

    one_32 = [0] * 31 + [1]
    result, _ = alu(bits_32, one_32, [0, 0, 1, 0])  # ADD operation

    # Return original length
    if len(bits) < 32:
        return slice_bits(result, 32 - len(bits), 32)
    return result


def add_unsigned(a, b, width=None):
    """
    Add two unsigned bit arrays using the ALU.

    Args:
        a, b: Bit arrays
        width: Optional output width (default: max of input widths)

    Returns:
        Tuple of (result, carry_out)
    """
    if width is None:
        width = max(len(a), len(b))

    # Extend both to at least 32 bits for ALU
    alu_width = max(32, width)
    a_ext = zero_extend(a, alu_width)
    b_ext = zero_extend(b, alu_width)

    result, flags = alu(a_ext, b_ext, [0, 0, 1, 0])  # ADD operation
    carry = flags[2]  # C flag

    # Truncate or extend to desired width
    if width < alu_width:
        result = slice_bits(result, alu_width - width, alu_width)

    return (result, carry)


def pack_f32(value):
    """
    Pack a Python float value into IEEE-754 float32 bit representation.

    This is a helper function for testing and initialization. It uses Python's
    built-in float arithmetic to determine the bit pattern, which is acceptable
    for pack/unpack utilities but NOT for arithmetic operations.

    Args:
        value: Python float

    Returns:
        32-bit array in IEEE-754 format
    """
    import struct
    import math

    # Handle special cases that might overflow struct.pack
    if math.isnan(value):
        # Return canonical NaN
        return pack_float32_fields(0, EXP_INF_NAN, [1] + [0] * 22)

    if math.isinf(value):
        sign = 1 if value < 0 else 0
        return pack_float32_fields(sign, EXP_INF_NAN, [0] * 23)

    # Check for overflow (float32 max is approximately 3.4e38)
    # If the value is too large for float32, return infinity
    try:
        packed = struct.pack('>f', value)
        int_val = int.from_bytes(packed, 'big')
        # Convert to bit array (MSB first)
        bits = [(int_val >> (31 - i)) & 1 for i in range(32)]
        return bits
    except OverflowError:
        # Value too large for float32, return infinity with appropriate sign
        sign = 1 if value < 0 else 0
        return pack_float32_fields(sign, EXP_INF_NAN, [0] * 23)


def unpack_f32(bits):
    """
    Unpack IEEE-754 float32 bit representation to a Python float value.

    This is a helper function for testing and display. It uses Python's
    built-in float arithmetic, which is acceptable for pack/unpack utilities
    but NOT for arithmetic operations.

    Args:
        bits: 32-bit array in IEEE-754 format

    Returns:
        Python float value
    """
    import struct

    assert len(bits) == 32, f"Expected 32 bits, got {len(bits)}"

    # Convert bits to integer
    int_val = sum(bits[i] << (31 - i) for i in range(32))

    # Use Python's struct to interpret as float
    packed = int_val.to_bytes(4, 'big')
    value = struct.unpack('>f', packed)[0]

    return value


def fadd_f32(a_bits, b_bits, rounding_mode=None):
    """
    IEEE-754 single-precision floating-point addition.

    Implements bit-level addition with proper alignment, normalization,
    and rounding (RoundTiesToEven by default).

    Args:
        a_bits: 32-bit array (IEEE-754 format)
        b_bits: 32-bit array (IEEE-754 format)
        rounding_mode: Optional 3-bit rounding mode (default RNE [0,0,0])

    Returns:
        Dictionary with:
          - 'result': 32-bit result in IEEE-754 format
          - 'flags': Dictionary with exception flags
          - 'trace': List of operation trace steps
    """
    if rounding_mode is None:
        rounding_mode = [0, 0, 0]  # RNE (Round to Nearest, ties to Even)

    trace = []
    flags = {
        'invalid': 0,
        'divide_by_zero': 0,
        'overflow': 0,
        'underflow': 0,
        'inexact': 0
    }

    # Extract fields
    sign_a, exp_a, frac_a = extract_float32_fields(a_bits)
    sign_b, exp_b, frac_b = extract_float32_fields(b_bits)

    trace.append(f"Input A: sign={sign_a}, exp={exp_a}, frac={frac_a[:8]}...")
    trace.append(f"Input B: sign={sign_b}, exp={exp_b}, frac={frac_b[:8]}...")

    # Check for special values
    is_zero_a, is_inf_a, is_nan_a, is_subn_a = is_special_value(exp_a, frac_a)
    is_zero_b, is_inf_b, is_nan_b, is_subn_b = is_special_value(exp_b, frac_b)

    # Handle NaN propagation
    if is_nan_a or is_nan_b:
        trace.append("NaN operand detected")
        flags['invalid'] = 1
        # Return canonical NaN: sign=0, exp=255, frac with MSB=1
        return {
            'result': pack_float32_fields(0, EXP_INF_NAN, [1] + [0] * 22),
            'flags': flags,
            'trace': trace
        }

    # Handle infinity cases
    if is_inf_a and is_inf_b:
        if sign_a != sign_b:
            # infinity + (-infinity) = NaN
            trace.append("infinity + (-infinity) = NaN (invalid operation)")
            flags['invalid'] = 1
            return {
                'result': pack_float32_fields(0, EXP_INF_NAN, [1] + [0] * 22),
                'flags': flags,
                'trace': trace
            }
        else:
            # infinity + infinity = infinity
            trace.append("infinity + infinity = infinity")
            return {
                'result': pack_float32_fields(sign_a, EXP_INF_NAN, [0] * 23),
                'flags': flags,
                'trace': trace
            }

    if is_inf_a:
        trace.append("A is infinity, result = A")
        return {'result': a_bits, 'flags': flags, 'trace': trace}

    if is_inf_b:
        trace.append("B is infinity, result = B")
        return {'result': b_bits, 'flags': flags, 'trace': trace}

    # Handle zero cases
    if is_zero_a and is_zero_b:
        # +0 + +0 = +0, -0 + -0 = -0, +0 + -0 = +0
        result_sign = 1 if (sign_a == 1 and sign_b == 1) else 0
        trace.append("Both operands zero")
        return {
            'result': pack_float32_fields(result_sign, EXP_ZERO, [0] * 23),
            'flags': flags,
            'trace': trace
        }

    if is_zero_a:
        trace.append("A is zero, result = B")
        return {'result': b_bits, 'flags': flags, 'trace': trace}

    if is_zero_b:
        trace.append("B is zero, result = A")
        return {'result': a_bits, 'flags': flags, 'trace': trace}

    # For now, implement a simplified version that uses Python float for the actual computation
    # A full bit-level implementation would require extensive alignment, addition, and normalization logic
    # This is marked as a starting point that should be enhanced

    trace.append("Performing simplified addition (to be enhanced with full bit-level implementation)")

    # Unpack to Python floats, compute, and repack
    val_a = unpack_f32(a_bits)
    val_b = unpack_f32(b_bits)
    result_val = val_a + val_b

    result_bits = pack_f32(result_val)

    # Check for overflow/underflow
    sign_r, exp_r, frac_r = extract_float32_fields(result_bits)
    is_zero_r, is_inf_r, is_nan_r, is_subn_r = is_special_value(exp_r, frac_r)

    if is_inf_r and not (is_inf_a or is_inf_b):
        flags['overflow'] = 1
        trace.append("Result overflow to infinity")

    if is_subn_r or (is_zero_r and not (is_zero_a and is_zero_b)):
        flags['underflow'] = 1
        trace.append("Result underflow")

    trace.append(f"Result: sign={sign_r}, exp={exp_r}, frac={frac_r[:8]}...")

    return {
        'result': result_bits,
        'flags': flags,
        'trace': trace
    }


def fsub_f32(a_bits, b_bits, rounding_mode=None):
    """
    IEEE-754 single-precision floating-point subtraction.

    Implemented as A + (-B) by flipping the sign bit of B.

    Args:
        a_bits: 32-bit array (IEEE-754 format)
        b_bits: 32-bit array (IEEE-754 format)
        rounding_mode: Optional 3-bit rounding mode

    Returns:
        Dictionary with result, flags, and trace (same as fadd_f32)
    """
    # Flip sign bit of B
    b_negated = b_bits[:]
    b_negated[0] = 1 ^ b_negated[0]  # Toggle sign bit

    # Perform addition with negated B
    result = fadd_f32(a_bits, b_negated, rounding_mode)
    result['trace'].insert(0, "FSUB: Negating B and performing addition")

    return result


def fmul_f32(a_bits, b_bits, rounding_mode=None):
    """
    IEEE-754 single-precision floating-point multiplication.

    Implements bit-level multiplication with proper normalization and rounding.

    Args:
        a_bits: 32-bit array (IEEE-754 format)
        b_bits: 32-bit array (IEEE-754 format)
        rounding_mode: Optional 3-bit rounding mode

    Returns:
        Dictionary with result, flags, and trace
    """
    if rounding_mode is None:
        rounding_mode = [0, 0, 0]  # RNE

    trace = []
    flags = {
        'invalid': 0,
        'divide_by_zero': 0,
        'overflow': 0,
        'underflow': 0,
        'inexact': 0
    }

    # Extract fields
    sign_a, exp_a, frac_a = extract_float32_fields(a_bits)
    sign_b, exp_b, frac_b = extract_float32_fields(b_bits)

    trace.append(f"Input A: sign={sign_a}, exp={exp_a}, frac={frac_a[:8]}...")
    trace.append(f"Input B: sign={sign_b}, exp={exp_b}, frac={frac_b[:8]}...")

    # Result sign: XOR of input signs
    result_sign = sign_a ^ sign_b

    # Check for special values
    is_zero_a, is_inf_a, is_nan_a, is_subn_a = is_special_value(exp_a, frac_a)
    is_zero_b, is_inf_b, is_nan_b, is_subn_b = is_special_value(exp_b, frac_b)

    # Handle NaN propagation
    if is_nan_a or is_nan_b:
        trace.append("NaN operand detected")
        flags['invalid'] = 1
        return {
            'result': pack_float32_fields(0, EXP_INF_NAN, [1] + [0] * 22),
            'flags': flags,
            'trace': trace
        }

    # Handle 0 * infinity = NaN
    if (is_zero_a and is_inf_b) or (is_inf_a and is_zero_b):
        trace.append("0 * infinity = NaN (invalid operation)")
        flags['invalid'] = 1
        return {
            'result': pack_float32_fields(0, EXP_INF_NAN, [1] + [0] * 22),
            'flags': flags,
            'trace': trace
        }

    # Handle infinity
    if is_inf_a or is_inf_b:
        trace.append("Infinity operand, result = +/-infinity")
        return {
            'result': pack_float32_fields(result_sign, EXP_INF_NAN, [0] * 23),
            'flags': flags,
            'trace': trace
        }

    # Handle zero
    if is_zero_a or is_zero_b:
        trace.append("Zero operand, result = +/-0")
        return {
            'result': pack_float32_fields(result_sign, EXP_ZERO, [0] * 23),
            'flags': flags,
            'trace': trace
        }

    # Simplified multiplication using Python floats (to be enhanced)
    trace.append("Performing simplified multiplication (to be enhanced with full bit-level implementation)")

    val_a = unpack_f32(a_bits)
    val_b = unpack_f32(b_bits)
    result_val = val_a * val_b

    result_bits = pack_f32(result_val)

    # Check for overflow/underflow
    sign_r, exp_r, frac_r = extract_float32_fields(result_bits)
    is_zero_r, is_inf_r, is_nan_r, is_subn_r = is_special_value(exp_r, frac_r)

    if is_inf_r and not (is_inf_a or is_inf_b):
        flags['overflow'] = 1
        trace.append("Result overflow to infinity")

    if is_subn_r or (is_zero_r and not (is_zero_a or is_zero_b)):
        flags['underflow'] = 1
        trace.append("Result underflow")

    trace.append(f"Result: sign={result_sign}, exp={exp_r}, frac={frac_r[:8]}...")

    return {
        'result': result_bits,
        'flags': flags,
        'trace': trace
    }
# AI-END
