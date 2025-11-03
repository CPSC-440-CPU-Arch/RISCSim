# AI-BEGIN
"""
RISC-V Multiply/Divide Unit (MDU) for M Extension

Implements integer multiply and divide operations using bit-level algorithms:
- MUL, MULH, MULHU, MULHSU: Multiplication with shift-add algorithm
- DIV, DIVU: Division with restoring division algorithm
- REM, REMU: Remainder operations

All operations follow RISC-V M extension semantics including edge cases.
Operations produce cycle-by-cycle traces showing internal state.

All bit arrays follow MSB-first convention (index 0 = MSB, index 31 = LSB)
"""

from riscsim.utils.bit_utils import (
    slice_bits, concat_bits, is_zero, zero_extend, sign_extend,
    bits_to_hex_string, bits_not
)
from riscsim.cpu.alu import alu
from riscsim.cpu.shifter import shifter


def is_negative(bits):
    """Check if a bit array represents a negative number (MSB = 1)."""
    return bits[0] == 1


def negate_twos_complement(bits):
    """
    Negate a two's complement number: invert bits and add 1.

    Args:
        bits: 32-bit array

    Returns:
        Negated 32-bit array
    """
    # Invert all bits
    inverted = bits_not(bits)

    # Add 1 using ALU
    one = [0] * 31 + [1]
    result, _ = alu(inverted, one, [0, 0, 1, 0])  # ADD

    return result


def mdu_mul(rs1_bits, rs2_bits, op="MUL"):
    """
    RISC-V integer multiplication using shift-add algorithm.

    Implements MUL, MULH, MULHU, MULHSU operations.

    Algorithm (shift-add multiplication):
    - Maintain 64-bit accumulator (product), 32-bit multiplier, 32-bit multiplicand
    - For each bit of multiplier (LSB to MSB):
      - If multiplier bit is 1, add multiplicand to accumulator
      - Shift multiplicand left by 1
    - Return appropriate 32 bits based on operation

    Args:
        rs1_bits: 32-bit multiplicand
        rs2_bits: 32-bit multiplier
        op: Operation type - "MUL", "MULH", "MULHU", "MULHSU"
            MUL: Lower 32 bits of product
            MULH: Upper 32 bits (signed x signed)
            MULHU: Upper 32 bits (unsigned x unsigned)
            MULHSU: Upper 32 bits (signed x unsigned)

    Returns:
        Dictionary with:
          - 'result': 32-bit result
          - 'hi_bits': 32-bit upper half (for reference)
          - 'flags': Dictionary with overflow flag
          - 'trace': List of cycle-by-cycle operation trace
    """
    trace = []
    flags = {'overflow': 0}

    trace.append(f"=== {op} Operation ===")
    trace.append(f"Multiplicand (rs1): {bits_to_hex_string(rs1_bits)}")
    trace.append(f"Multiplier (rs2):   {bits_to_hex_string(rs2_bits)}")

    # Determine signedness
    if op == "MUL" or op == "MULH":
        # Signed x Signed
        signed_op = True
        rs1_signed = True
        rs2_signed = True
    elif op == "MULHU":
        # Unsigned x Unsigned
        signed_op = False
        rs1_signed = False
        rs2_signed = False
    elif op == "MULHSU":
        # Signed x Unsigned
        signed_op = True
        rs1_signed = True
        rs2_signed = False
    else:
        raise ValueError(f"Invalid operation: {op}")

    # Handle signs for signed operations
    rs1_negative = rs1_signed and is_negative(rs1_bits)
    rs2_negative = rs2_signed and is_negative(rs2_bits)

    # Work with absolute values for signed multiplication
    if rs1_negative:
        multiplicand = negate_twos_complement(rs1_bits)
        trace.append(f"rs1 is negative, using absolute value: {bits_to_hex_string(multiplicand)}")
    else:
        multiplicand = rs1_bits[:]

    if rs2_negative:
        multiplier = negate_twos_complement(rs2_bits)
        trace.append(f"rs2 is negative, using absolute value: {bits_to_hex_string(multiplier)}")
    else:
        multiplier = rs2_bits[:]

    # Initialize 64-bit accumulator (product)
    product_lo = [0] * 32
    product_hi = [0] * 32

    trace.append(f"\nShift-Add Multiplication (32 cycles):")
    trace.append(f"{'Cycle':<6} {'Multiplier Bit':<15} {'Action':<30} {'Accumulator (Hi:Lo)'}")
    trace.append("-" * 90)

    # Perform shift-add multiplication
    for i in range(32):
        cycle = i + 1
        bit_index = 31 - i  # Process from LSB to MSB
        multiplier_bit = multiplier[bit_index]

        action = ""
        if multiplier_bit == 1:
            # Add multiplicand shifted left by i positions to 64-bit accumulator
            # When shifting left by i:
            # - If i < 32: bits go to low part, but top i bits also go to high part
            # - If i >= 32: all bits go to high part

            if i < 32:
                # Shift multiplicand left by i positions
                if i == 0:
                    add_lo = multiplicand[:]
                    add_hi = [0] * 32
                else:
                    shifted = shifter(multiplicand, i, "SLL")
                    # Top i bits that got shifted out go to high part
                    # Extract them from the original multiplicand
                    add_lo = shifted[:]
                    # Get the top i bits from original that were shifted out
                    top_bits = slice_bits(multiplicand, 0, i)
                    # These become the low i bits of add_hi
                    add_hi = concat_bits([0] * (32 - i), top_bits)
            else:
                # Shift >= 32, everything goes to high part
                shift_amount = i - 32
                if shift_amount == 0:
                    add_hi = multiplicand[:]
                else:
                    add_hi = shifter(multiplicand, shift_amount, "SLL")
                add_lo = [0] * 32

            # Add to 64-bit product (lo + add_lo, hi + add_hi + carry)
            temp_lo, flags_lo = alu(product_lo, add_lo, [0, 0, 1, 0])
            carry = flags_lo[2]  # Carry flag

            # Add to high part with carry
            temp_hi, flags_hi = alu(product_hi, add_hi, [0, 0, 1, 0])

            if carry:
                # Add carry to high part
                one_32 = [0] * 31 + [1]
                temp_hi, _ = alu(temp_hi, one_32, [0, 0, 1, 0])

            product_lo = temp_lo
            product_hi = temp_hi

            action = f"Add multiplicand << {i}"
        else:
            action = "Skip (bit = 0)"

        # Only show trace for first few, middle, and last few cycles
        if cycle <= 3 or cycle >= 30 or (cycle % 8 == 0):
            trace.append(f"{cycle:<6} {multiplier_bit:<15} {action:<30} {bits_to_hex_string(product_hi)}:{bits_to_hex_string(product_lo)}")

    trace.append(f"...")
    trace.append(f"\nFinal 64-bit product: {bits_to_hex_string(product_hi)}:{bits_to_hex_string(product_lo)}")

    # Apply sign correction for signed multiplication
    result_negative = signed_op and (rs1_negative != rs2_negative)

    if result_negative:
        trace.append("Result should be negative, negating 64-bit product")
        # Negate the 64-bit product
        # Invert all bits
        product_lo_inv = bits_not(product_lo)
        product_hi_inv = bits_not(product_hi)

        # Add 1 to 64-bit value
        one_32 = [0] * 31 + [1]
        product_lo, flags_add = alu(product_lo_inv, one_32, [0, 0, 1, 0])
        if flags_add[2]:  # Carry
            product_hi, _ = alu(product_hi_inv, one_32, [0, 0, 1, 0])
        else:
            product_hi = product_hi_inv

    # Check for overflow (for MUL operation)
    if op == "MUL":
        # Overflow if high 32 bits are not sign extension of low 32 bits
        sign_bit = product_lo[0]
        expected_hi = [sign_bit] * 32
        if product_hi != expected_hi:
            flags['overflow'] = 1
            trace.append("Overflow detected: high bits not sign extension of low bits")

    # Return appropriate bits based on operation
    if op == "MUL":
        result = product_lo
        trace.append(f"\nMUL result (low 32 bits): {bits_to_hex_string(result)}")
    else:  # MULH, MULHU, MULHSU
        result = product_hi
        trace.append(f"\n{op} result (high 32 bits): {bits_to_hex_string(result)}")

    return {
        'result': result,
        'hi_bits': product_hi,
        'lo_bits': product_lo,
        'flags': flags,
        'trace': trace
    }


def mdu_div(rs1_bits, rs2_bits, op="DIV"):
    """
    RISC-V integer division using restoring division algorithm.

    Implements DIV, DIVU, REM, REMU operations with RISC-V semantics.

    RISC-V Edge Cases:
    - Division by zero:
      - DIV/REM: quotient = -1, remainder = dividend
      - DIVU/REMU: quotient = 0xFFFFFFFF, remainder = dividend
    - Overflow (INT_MIN / -1):
      - DIV: quotient = INT_MIN, remainder = 0
      - REM: quotient = INT_MIN, remainder = 0

    Algorithm (restoring division):
    - Maintain 64-bit remainder (initialized with dividend), 32-bit quotient
    - For 32 iterations:
      - Shift remainder left by 1
      - Subtract divisor from upper half of remainder
      - If result is non-negative, set quotient bit to 1
      - Else, restore remainder (add divisor back)

    Args:
        rs1_bits: 32-bit dividend
        rs2_bits: 32-bit divisor
        op: Operation type - "DIV", "DIVU", "REM", "REMU"

    Returns:
        Dictionary with:
          - 'quotient': 32-bit quotient
          - 'remainder': 32-bit remainder
          - 'flags': Dictionary with overflow flag
          - 'trace': List of cycle-by-cycle operation trace
    """
    trace = []
    flags = {'overflow': 0}

    trace.append(f"=== {op} Operation ===")
    trace.append(f"Dividend (rs1):  {bits_to_hex_string(rs1_bits)}")
    trace.append(f"Divisor (rs2):   {bits_to_hex_string(rs2_bits)}")

    # Determine signedness
    if op == "DIV" or op == "REM":
        signed_op = True
    else:  # DIVU or REMU
        signed_op = False

    # Check for division by zero
    if is_zero(rs2_bits):
        trace.append("Division by zero detected!")
        if signed_op:
            quotient = [1] * 32  # -1 in two's complement
            remainder = rs1_bits[:]
            trace.append(f"DIV/REM by zero: quotient = -1 (0xFFFFFFFF), remainder = dividend")
        else:
            quotient = [1] * 32  # Maximum unsigned value
            remainder = rs1_bits[:]
            trace.append(f"DIVU/REMU by zero: quotient = 0xFFFFFFFF, remainder = dividend")

        if op == "DIV" or op == "DIVU":
            return {'quotient': quotient, 'remainder': remainder, 'flags': flags, 'trace': trace}
        else:
            return {'quotient': quotient, 'remainder': remainder, 'flags': flags, 'trace': trace}

    # Check for overflow: INT_MIN / -1
    if signed_op:
        int_min = [1] + [0] * 31  # 0x80000000
        neg_one = [1] * 32        # 0xFFFFFFFF
        if rs1_bits == int_min and rs2_bits == neg_one:
            trace.append("Overflow case: INT_MIN / -1")
            quotient = int_min  # Returns INT_MIN
            remainder = [0] * 32
            flags['overflow'] = 1

            if op == "DIV" or op == "DIVU":
                return {'quotient': quotient, 'remainder': remainder, 'flags': flags, 'trace': trace}
            else:
                return {'quotient': quotient, 'remainder': remainder, 'flags': flags, 'trace': trace}

    # Handle signs
    dividend_negative = signed_op and is_negative(rs1_bits)
    divisor_negative = signed_op and is_negative(rs2_bits)

    if dividend_negative:
        dividend = negate_twos_complement(rs1_bits)
        trace.append(f"Dividend is negative, using absolute value: {bits_to_hex_string(dividend)}")
    else:
        dividend = rs1_bits[:]

    if divisor_negative:
        divisor = negate_twos_complement(rs2_bits)
        trace.append(f"Divisor is negative, using absolute value: {bits_to_hex_string(divisor)}")
    else:
        divisor = rs2_bits[:]

    # Initialize remainder with dividend (in lower 32 bits of 64-bit value)
    remainder_lo = dividend[:]
    remainder_hi = [0] * 32
    quotient = [0] * 32

    trace.append(f"\nRestoring Division (32 cycles):")
    trace.append(f"{'Cycle':<6} {'Action':<40} {'Remainder (Hi:Lo)':<35} {'Quotient'}")
    trace.append("-" * 110)

    # Perform restoring division
    for i in range(32):
        cycle = i + 1

        # Shift remainder left by 1
        remainder_hi = shifter(remainder_hi, 1, "SLL")
        remainder_hi[31] = remainder_lo[0]  # Transfer MSB from lo to LSB of hi
        remainder_lo = shifter(remainder_lo, 1, "SLL")

        # Subtract divisor from upper half of remainder
        temp_rem, flags_sub = alu(remainder_hi, divisor, [0, 1, 1, 0])  # SUB

        # Check if result is non-negative (no borrow means C=1 for SUB)
        if flags_sub[2] == 1 or is_zero(temp_rem):  # C flag or zero result
            # Result is non-negative, keep subtraction
            remainder_hi = temp_rem
            quotient = shifter(quotient, 1, "SLL")
            quotient[31] = 1  # Set LSB of quotient
            action = "Shift, Subtract (success), Q bit = 1"
        else:
            # Result is negative, restore remainder
            action = "Shift, Subtract (restore), Q bit = 0"
            quotient = shifter(quotient, 1, "SLL")
            quotient[31] = 0  # Set LSB of quotient

        # Show trace for first few, middle, and last few cycles
        if cycle <= 3 or cycle >= 30 or (cycle % 8 == 0):
            trace.append(f"{cycle:<6} {action:<40} {bits_to_hex_string(remainder_hi)}:{bits_to_hex_string(remainder_lo):<19} {bits_to_hex_string(quotient)}")

    trace.append("...")

    # Apply sign correction
    quotient_negative = signed_op and (dividend_negative != divisor_negative)
    remainder_negative = signed_op and dividend_negative

    if quotient_negative and not is_zero(quotient):
        trace.append("Quotient should be negative, negating")
        quotient = negate_twos_complement(quotient)

    if remainder_negative and not is_zero(remainder_hi):
        trace.append("Remainder should be negative, negating")
        remainder_hi = negate_twos_complement(remainder_hi)

    trace.append(f"\nFinal quotient:  {bits_to_hex_string(quotient)}")
    trace.append(f"Final remainder: {bits_to_hex_string(remainder_hi)}")

    return {
        'quotient': quotient,
        'remainder': remainder_hi,
        'flags': flags,
        'trace': trace
    }


# Convenience wrappers for specific operations
def mul(rs1_bits, rs2_bits):
    """MUL: Lower 32 bits of signed multiplication."""
    return mdu_mul(rs1_bits, rs2_bits, op="MUL")


def mulh(rs1_bits, rs2_bits):
    """MULH: Upper 32 bits of signed x signed multiplication."""
    return mdu_mul(rs1_bits, rs2_bits, op="MULH")


def mulhu(rs1_bits, rs2_bits):
    """MULHU: Upper 32 bits of unsigned x unsigned multiplication."""
    return mdu_mul(rs1_bits, rs2_bits, op="MULHU")


def mulhsu(rs1_bits, rs2_bits):
    """MULHSU: Upper 32 bits of signed x unsigned multiplication."""
    return mdu_mul(rs1_bits, rs2_bits, op="MULHSU")


def div(rs1_bits, rs2_bits):
    """DIV: Signed division quotient."""
    return mdu_div(rs1_bits, rs2_bits, op="DIV")


def divu(rs1_bits, rs2_bits):
    """DIVU: Unsigned division quotient."""
    return mdu_div(rs1_bits, rs2_bits, op="DIVU")


def rem(rs1_bits, rs2_bits):
    """REM: Signed division remainder."""
    return mdu_div(rs1_bits, rs2_bits, op="REM")


def remu(rs1_bits, rs2_bits):
    """REMU: Unsigned division remainder."""
    return mdu_div(rs1_bits, rs2_bits, op="REMU")
# AI-END
