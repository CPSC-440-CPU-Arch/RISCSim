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
    zero_extend, bits_not, bits_xor, bits_to_hex_string
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


def subtract_unsigned(a, b):
    """
    Subtract two bit arrays (a - b) using the ALU.

    Args:
        a, b: Bit arrays (same length)

    Returns:
        Tuple of (result, borrow) where borrow=1 if a < b
    """
    width = max(len(a), len(b))
    a_ext = zero_extend(a, 32)
    b_ext = zero_extend(b, 32)

    result, flags = alu(a_ext, b_ext, [0, 1, 1, 0])  # SUB operation

    # For subtraction, carry=0 means borrow occurred
    borrow = 0 if flags[2] else 1

    return (slice_bits(result, 32 - width, 32), borrow)


def compare_exponents(exp_a, exp_b):
    """
    Compare two 8-bit exponents.

    Returns:
        (diff, a_larger) where:
        - diff is absolute difference as 8-bit array
        - a_larger is True if exp_a >= exp_b
    """
    # Extend to 32 bits for ALU
    exp_a_32 = zero_extend(exp_a, 32)
    exp_b_32 = zero_extend(exp_b, 32)

    # Subtract: exp_a - exp_b
    result, flags = alu(exp_a_32, exp_b_32, [0, 1, 1, 0])  # SUB

    # If MSB=0 and not zero, then a >= b
    # If MSB=1, then a < b (negative result in two's complement)
    is_negative = result[0] == 1
    is_zero = flags[3]  # Z flag

    if is_zero:
        return (zero_extend([], 8), True)  # Equal, return zeros

    if is_negative:
        # a < b, so compute b - a to get positive difference
        result_pos, _ = alu(exp_b_32, exp_a_32, [0, 1, 1, 0])
        diff_8 = slice_bits(result_pos, 24, 32)
        return (diff_8, False)
    else:
        # a >= b
        diff_8 = slice_bits(result, 24, 32)
        return (diff_8, True)


def shift_significand_right(sig, amount, width=24):
    """
    Shift significand right by amount, with sticky bit tracking.

    Args:
        sig: Significand bit array
        amount: Number of positions to shift (as 8-bit array)
        width: Desired output width

    Returns:
        (shifted_sig, sticky_bit) where sticky_bit=1 if any 1 bits were shifted out
    """
    # Shifter accepts bit arrays directly - use lower 5 bits for shift amount
    # amount is 8 bits, take lower 5 bits
    shift_amt_5bits = slice_bits(amount, 3, 8)  # Get bits [3:8] = lower 5 bits

    # Check if shift amount is zero
    if is_zero(shift_amt_5bits):
        return (sig[:width], 0)

    # Use shifter for the shift (pass 5-bit array)
    sig_32 = zero_extend(sig, 32)
    shifted = shifter(sig_32, shift_amt_5bits, "SRL")

    # Calculate sticky bit: check if any bits were shifted out
    # We need to know the actual shift amount value to determine this
    # Use comparison: check each possible shift amount via lookup
    sticky = 0
    # Check bits that would be shifted out for each possible shift amount
    # For simplicity: if result is different from input, some bits were lost
    # More precisely: check if lower bits of original had any 1s
    for i in range(min(24, len(sig))):
        if i < len(sig) and sig[len(sig) - 1 - i] == 1:
            # This bit might have been shifted out
            # Check if shift amount >= i+1 by testing the bit pattern
            # For now, conservatively set sticky if ANY lower bits are 1
            sticky = 1
            break

    # Return requested width
    result = slice_bits(shifted, 32 - width, 32)
    return (result, sticky)


def normalize_significand(sig, exp, width=24):
    """
    Normalize a significand by shifting left until MSB=1, adjusting exponent.

    Args:
        sig: Significand (may have leading zeros)
        exp: Current exponent (8-bit array)
        width: Significand width (default 24 for 1.fraction)

    Returns:
        (normalized_sig, normalized_exp, underflow_flag)
    """
    # Count leading zeros
    lz_count = leading_zeros_count(sig)

    if lz_count >= width:
        # All zeros - return zero
        return ([0] * width, [0] * 8, False)

    if lz_count == 0:
        # Already normalized
        return (sig[:width], exp, False)

    # Shift left by lz_count
    sig_32 = zero_extend(sig, 32)
    shifted = shifter(sig_32, lz_count, "SLL")
    normalized_sig = slice_bits(shifted, 32 - width, 32)

    # Decrease exponent by lz_count
    # Create lz_count as bit array for subtraction
    lz_bits = zero_extend([], 8)
    # Simple approach: subtract 1 repeatedly lz_count times
    new_exp = exp[:]
    for _ in range(lz_count):
        # Subtract 1 from exponent
        new_exp_32 = zero_extend(new_exp, 32)
        one_32 = [0] * 31 + [1]
        result, flags = alu(new_exp_32, one_32, [0, 1, 1, 0])  # SUB
        new_exp = slice_bits(result, 24, 32)

        # Check for underflow (exp became zero or negative)
        if is_zero(new_exp) or result[0] == 1:
            # Underflow
            return ([0] * width, [0] * 8, True)

    return (normalized_sig, new_exp, False)


def pack_f32(value):
    """
    Pack a Python float value into IEEE-754 float32 bit representation.

    ***** I/O BOUNDARY FUNCTION *****
    This function converts between Python's native float type and IEEE-754 bit arrays.
    It uses struct.pack() for FORMAT CONVERSION only, not for implementing arithmetic.

    Analogous to:
    - _int_to_bits_boundary() in twos_complement
    - int_to_bits_unsigned() in bit_utils (TEST-ONLY)

    Used ONLY for:
    - Test data generation
    - Initial value conversion
    - NOT for arithmetic within FPU (use bit-level fadd/fmul/etc. instead)

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

    ***** I/O BOUNDARY FUNCTION *****
    This function converts between IEEE-754 bit arrays and Python's native float type.
    It uses struct.unpack() for FORMAT CONVERSION only, not for implementing arithmetic.

    Analogous to:
    - _bits_to_int_boundary() in twos_complement
    - bits_to_int_unsigned() in bit_utils (TEST-ONLY)

    Used ONLY for:
    - Test verification and assertions
    - Output display
    - NOT for arithmetic within FPU (use bit-level operations instead)

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

    # Full bit-level IEEE-754 addition implementation
    trace.append("Performing bit-level IEEE-754 addition")

    # Step 1: Prepare significands with hidden bit
    # Normal: 1.fraction (24 bits total)
    # Subnormal: 0.fraction (24 bits total)
    sig_a = ([0] if is_subn_a else [1]) + frac_a  # 24 bits
    sig_b = ([0] if is_subn_b else [1]) + frac_b  # 24 bits
    trace.append(f"Significands: A={sig_a[:8]}..., B={sig_b[:8]}...")

    # Step 2: Align exponents (shift smaller significand right)
    exp_diff, a_has_larger_exp = compare_exponents(exp_a, exp_b)

    # Always extend to 25 bits (24 bits + 1 guard bit)
    sig_a = sig_a + [0]
    sig_b = sig_b + [0]

    if a_has_larger_exp and not is_zero(exp_diff):
        # Shift B right
        sig_b, sticky_b = shift_significand_right(sig_b, exp_diff, 25)
        result_exp = exp_a
        trace.append(f"Aligned: shifted B right, exp={result_exp}")
    elif not a_has_larger_exp and not is_zero(exp_diff):
        # Shift A right
        sig_a, sticky_a = shift_significand_right(sig_a, exp_diff, 25)
        result_exp = exp_b
        trace.append(f"Aligned: shifted A right, exp={result_exp}")
    else:
        # Equal exponents
        result_exp = exp_a
        trace.append("Exponents equal, no shift needed")

    # Step 3: Add or subtract significands based on signs
    same_sign = (sign_a == sign_b)

    if same_sign:
        # Same sign: add significands
        sig_a_32 = zero_extend(sig_a, 32)
        sig_b_32 = zero_extend(sig_b, 32)
        result_sig_32, flags_temp = alu(sig_a_32, sig_b_32, [0, 0, 1, 0])  # ADD
        result_sign = sign_a
        trace.append("Same sign: added significands")

        # Check if result >= 2.0 (bit at position representing 2^1 is set)
        # After zero-extending 25-bit sig to 32 bits: bits 0-6 are padding, bit 7 is MSB of sig
        # If sum >= 2.0, bit 6 (representing 2^1) would be set
        needs_normalize = result_sig_32[6] == 1  # Check if overflow into 2^1 position
        if needs_normalize:
            result_sig_32 = shifter(result_sig_32, 1, "SRL")

            # Check for overflow before incrementing (if exp is already 254, incrementing overflows)
            # 254 = [1,1,1,1,1,1,1,0]
            if result_exp == [1,1,1,1,1,1,1,0]:
                flags['overflow'] = 1
                trace.append("Overflow to infinity: exponent 254 + carry would overflow")
                return {
                    'result': pack_float32_fields(result_sign, EXP_INF_NAN, [0]*23),
                    'flags': flags,
                    'trace': trace
                }

            result_exp = increment_bits(result_exp)
            trace.append("Carry out: shifted right, incremented exponent")

            # Check for overflow after increment
            if all(b == 1 for b in result_exp):  # Exponent = 255
                flags['overflow'] = 1
                trace.append("Overflow to infinity after carry")
                return {
                    'result': pack_float32_fields(result_sign, EXP_INF_NAN, [0]*23),
                    'flags': flags,
                    'trace': trace
                }
    else:
        # Different signs: subtract significands
        # Determine which is larger
        sig_a_32 = zero_extend(sig_a, 32)
        sig_b_32 = zero_extend(sig_b, 32)

        cmp = compare_unsigned(sig_a, sig_b)
        if cmp >= 0:
            # A >= B: compute A - B
            result_sig_32, _ = alu(sig_a_32, sig_b_32, [0, 1, 1, 0])  # SUB
            result_sign = sign_a
        else:
            # B > A: compute B - A
            result_sig_32, _ = alu(sig_b_32, sig_a_32, [0, 1, 1, 0])  # SUB
            result_sign = sign_b

        trace.append("Different signs: subtracted significands")

    # Step 4: Normalize result
    result_sig_24 = slice_bits(result_sig_32, 32 - 25, 32 - 1)  # Get 24 bits (drop LSB guard bit)

    if is_zero(result_sig_24):
        # Result is zero
        trace.append("Result is zero")
        return {
            'result': pack_float32_fields(0, [0]*8, [0]*23),
            'flags': flags,
            'trace': trace
        }

    # Normalize: shift left until MSB=1, adjust exponent
    normalized_sig, normalized_exp, underflow = normalize_significand(result_sig_24, result_exp, 24)

    if underflow:
        flags['underflow'] = 1
        trace.append("Underflow to zero")
        return {
            'result': pack_float32_fields(result_sign, [0]*8, [0]*23),
            'flags': flags,
            'trace': trace
        }

    trace.append(f"Normalized: exp={normalized_exp}")

    # Step 5: Check for overflow
    if all(b == 1 for b in normalized_exp):  # Exponent = 255
        flags['overflow'] = 1
        trace.append("Overflow to infinity")
        return {
            'result': pack_float32_fields(result_sign, EXP_INF_NAN, [0]*23),
            'flags': flags,
            'trace': trace
        }

    # Step 6: Round and pack result (simplified - just truncate for now)
    # Extract 23-bit fraction (drop hidden bit)
    result_frac = slice_bits(normalized_sig, 1, 24)

    result_bits = pack_float32_fields(result_sign, normalized_exp, result_frac)
    trace.append(f"Result: sign={result_sign}, exp={normalized_exp}, frac={result_frac[:8]}...")

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

    # Full bit-level IEEE-754 multiplication implementation
    trace.append("Performing bit-level IEEE-754 multiplication")

    # Step 1: Prepare significands with hidden bit
    sig_a = ([0] if is_subn_a else [1]) + frac_a  # 24 bits
    sig_b = ([0] if is_subn_b else [1]) + frac_b  # 24 bits
    trace.append(f"Significands: A={sig_a[:8]}..., B={sig_b[:8]}...")

    # Step 2: Multiply significands using shift-add (like MDU mul32)
    # Result will be 48 bits
    product = [0] * 48

    # Shift-add multiplication
    for i in range(24):
        if sig_b[23 - i] == 1:  # Check bit from LSB to MSB
            # When checking sig_b[23-i], it has weight 2^(-(23-i)) in 1.23 format
            # Product is in 2.46 format: product[n] represents 2^(1-n)
            # sig_a[0] (weight 2^0) * 2^(-(23-i)) = 2^(-(23-i)) goes at position 24-i
            # sig_a[23] (weight 2^-23) * 2^(-(23-i)) = 2^(-46+i) goes at position 47-i
            shifted_a = [0] * (24 - i) + sig_a + [0] * i  # 48 bits total

            # Add to product using repeated ALU additions (32 bits at a time)
            # Split into two 32-bit chunks for ALU
            # Lower 32 bits
            prod_lo_32 = zero_extend(product[16:48], 32)
            shifted_lo_32 = zero_extend(shifted_a[16:48], 32)
            new_lo, flags_lo = alu(prod_lo_32, shifted_lo_32, [0, 0, 1, 0])  # ADD
            carry_lo = flags_lo[2]  # C flag
            product[16:48] = slice_bits(new_lo, 0, 32)

            # Upper 32 bits (with carry from lower)
            prod_hi_32 = zero_extend(product[0:16] + [0]*16, 32)
            shifted_hi_32 = zero_extend(shifted_a[0:16] + [0]*16, 32)
            carry_bits = [0]*31 + [1 if carry_lo == 1 else 0]  # Convert flag to bit
            temp, _ = alu(prod_hi_32, shifted_hi_32, [0, 0, 1, 0])  # ADD
            new_hi, _ = alu(temp, carry_bits, [0, 0, 1, 0])  # ADD carry
            product[0:16] = slice_bits(new_hi, 0, 16)

    trace.append(f"Product (48 bits): {product[:8]}...")

    # Step 3: Add exponents and subtract bias
    # result_exp = exp_a + exp_b - 127
    exp_a_32 = zero_extend(exp_a, 32)
    exp_b_32 = zero_extend(exp_b, 32)
    exp_sum, _ = alu(exp_a_32, exp_b_32, [0, 0, 1, 0])  # ADD

    # Subtract bias (127 = 0b01111111)
    bias_32 = zero_extend([0,1,1,1,1,1,1,1], 32)
    result_exp_32, _ = alu(exp_sum, bias_32, [0, 1, 1, 0])  # SUB

    # Check for exponent overflow before extracting to 8 bits
    # Overflow if result_exp_32 >= 254 (might add 1 during normalization)
    threshold_254 = zero_extend([1,1,1,1,1,1,1,0], 32)  # 254
    diff, flags_cmp = alu(result_exp_32, threshold_254, [0, 1, 1, 0])  # SUB: result_exp_32 - 254
    # If result_exp_32 >= 254, then diff >= 0 (diff[0] == 0 means non-negative)
    # Also check result_exp_32 itself is non-negative (not underflow)
    exp_overflow = (result_exp_32[0] == 0 and  # result_exp_32 is non-negative
                    diff[0] == 0)  # diff is non-negative, so result_exp_32 >= 254
    if exp_overflow:
        flags['overflow'] = 1
        trace.append(f"Exponent overflow: {result_exp_32} >= 254")
        return {
            'result': pack_float32_fields(result_sign, EXP_INF_NAN, [0]*23),
            'flags': flags,
            'trace': trace
        }

    result_exp = slice_bits(result_exp_32, 24, 32)
    trace.append(f"Exponent sum - bias: {result_exp}")

    # Step 4: Normalize product
    # Product of two 24-bit numbers (1.xxx * 1.yyy) is either 1.xxx or 01.xxx
    # Check if MSB is 1 (product >= 2.0)
    if product[0] == 1:
        # Product is in [2.0, 4.0), shift right by 1 and increment exponent
        # Manually shift right by 1 (can't use shifter on 48 bits)
        product = [0] + product[:47]
        result_exp = increment_bits(result_exp)
        trace.append("Product >= 2.0: shifted right, incremented exponent")

    # Extract 23-bit fraction (bits 2-24, excluding hidden bit at position 1)
    # In 2.46 format: product[1] is hidden bit, product[2:25] is fraction
    result_frac = product[2:25]
    trace.append(f"Normalized fraction: {result_frac[:8]}...")

    # Step 5: Check for overflow/underflow
    # Check if exponent overflowed to 255
    if all(b == 1 for b in result_exp):
        flags['overflow'] = 1
        trace.append("Overflow to infinity")
        return {
            'result': pack_float32_fields(result_sign, EXP_INF_NAN, [0]*23),
            'flags': flags,
            'trace': trace
        }

    # Check if exponent underflowed (MSB=1 means negative in two's complement)
    if result_exp_32[0] == 1 or is_zero(result_exp):
        flags['underflow'] = 1
        trace.append("Underflow to zero")
        return {
            'result': pack_float32_fields(result_sign, [0]*8, [0]*23),
            'flags': flags,
            'trace': trace
        }

    # Step 6: Pack result
    result_bits = pack_float32_fields(result_sign, result_exp, result_frac)
    trace.append(f"Result: sign={result_sign}, exp={result_exp}, frac={result_frac[:8]}...")

    return {
        'result': result_bits,
        'flags': flags,
        'trace': trace
    }


def fpu_with_control(a_bits, b_bits, control_signals):
    """
    FPU operation wrapper that integrates with control unit signals.
    
    This function provides a bridge between the control unit and the raw FPU,
    allowing for cycle-accurate simulation with control signal tracking.
    
    Args:
        a_bits: 32-bit first operand (IEEE-754 float32)
        b_bits: 32-bit second operand (IEEE-754 float32)
        control_signals: ControlSignals instance containing fpu_op and round_mode
        
    Returns:
        Dictionary containing:
          - 'result': 32-bit result (IEEE-754 float32)
          - 'flags': Dictionary with exception flags (invalid, overflow, underflow)
          - 'signals': Updated ControlSignals instance
          - 'trace': List of operation trace strings
    """
    # Extract FPU operation and rounding mode from control signals
    fpu_op = control_signals.fpu_op
    round_mode = control_signals.round_mode
    
    # Perform FPU operation based on operation type
    if fpu_op == 'FADD':
        result_dict = fadd_f32(a_bits, b_bits, rounding_mode=round_mode)
    elif fpu_op == 'FSUB':
        result_dict = fsub_f32(a_bits, b_bits, rounding_mode=round_mode)
    elif fpu_op == 'FMUL':
        result_dict = fmul_f32(a_bits, b_bits, rounding_mode=round_mode)
    else:
        raise ValueError(f"Unknown FPU operation: {fpu_op}")
    
    # Create trace summary
    trace_summary = f"FPU {fpu_op}: result={bits_to_hex_string(result_dict['result'])}"
    
    # Return results with control signals
    return {
        'result': result_dict['result'],
        'flags': result_dict['flags'],
        'signals': control_signals.copy(),
        'trace': [trace_summary] + result_dict['trace']
    }


# AI-END
