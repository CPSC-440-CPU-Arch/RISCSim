# AI-BEGIN
"""
Twos Complement: is the binary representation of a negative number. Used to subtract from one number from another by converting the 2nd number into its negative sign equivalent. If the input number is positive, only its binary representation is necessary to convert. If the input number is negative, it must be represented as its twos-complment. Note: the MSB must be 1 to signify the number is a negative. 

Questions: 
1. What if the input INT is outside of the 32 bit range? Do we reject?
    * truncate or clamp bit array, and return overflow flag 1
2. Notes say to support multiple bit-widths. Can we just stick to 32 bit width regardless of size?
    * will stick to fixed width. Some requirements contradict each other, will not support multiple bit widths
3. are we replicating the int parsing process from Compiler view or from CPU view? 

two_complement() Strategy:
1. Check if value is in range. 
    * if out of range: set over flow flag, truncate to 32 bits and return or clamp to max or min rep.
    else: continue
2. Check sign of int
    * if negative: convert to two's_complement()
    * if Positive, convert_to_binary()
3. converting to twos_complement()
    * take absval = absolute_value(int), and bin_array = convert_to_binary(absval)
    * ones_complement_flip_bits(bin_array)
    * add_one(bin_array)
    * check overflow
        * if overflow: flag
        else return set
4. convert_to_bin():
    * reference character to 8bit binary table, return 8-bit binary list
        * process: binary_rep = [8-bit] * 10^n + [8-bit] * 10^n-1 * ... * [8-bit] * 10 ^ 1
            * 
    * mini_MPU()
        * calls mini_ALU()
5. convert_to_hex(binary_rep):
6. prettyprint():

"""
from riscsim.utils.bit_utils import *

MAX_INT = 2147483647
MIN_INT = -2147483648
digit_to_32bin = {
    0: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
    1: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1], 
    2: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0], 
    3: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1], 
    4: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
    5: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1], 
    6: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0], 
    7: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1], 
    8: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0], 
    9: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1]
}

def _int_to_bits_boundary(value, width):
    """
    I/O boundary helper: Convert Python int to bit array.

    ***** I/O BOUNDARY FUNCTION *****
    This function converts between Python's native integer type and bit arrays.
    It uses arithmetic operators (%, //) for FORMAT CONVERSION only, not for
    implementing arithmetic algorithms.

    Analogous to:
    - struct.pack() for binary format conversion
    - int_to_bits_unsigned() in bit_utils (TEST-ONLY)

    Used ONLY at module boundaries for input conversion.
    All arithmetic algorithms use ALU/MDU bit-level operations.

    Args:
        value: Non-negative integer to convert
        width: Bit width (e.g., 32)

    Returns:
        Bit array [MSB...LSB] of specified width
    """
    if value < 0:
        raise ValueError("Value must be non-negative")

    bits = []
    temp = value

    # I/O format conversion - not arithmetic
    for _ in range(width):
        bits.append(temp % 2)
        temp = temp // 2

    bits.reverse()
    return bits


def encode_twos_complement(value: int):
    """
    Encode an integer to 32-bit two's complement representation.

    Uses bit-level operations for two's complement arithmetic.
    I/O conversion (Python int to bits) uses boundary helpers.

    Args:
        value: Integer to encode

    Returns:
        Dictionary with:
          - 'bin': Binary string with underscores (e.g., "00000000_00000000_00000000_00001101")
          - 'hex': Hex string (e.g., "0x0000000D")
          - 'overflow': Boolean, True if value outside [-2^31, 2^31-1]
    """
    overflow = False

    # Check for overflow
    if value > MAX_INT or value < MIN_INT:
        overflow = True
        # Clamp to valid range for encoding
        if value > MAX_INT:
            value = MAX_INT
        else:
            value = MIN_INT

    # Convert to 32-bit two's complement using bit-level operations
    if value >= 0:
        # Positive: direct conversion
        binary_vector = _int_to_bits_boundary(value, 32)
    else:
        # Negative: compute two's complement using bit-level operations
        # Step 1: Get magnitude (use absolute value for I/O conversion)
        magnitude = _int_to_bits_boundary(-value, 32)  # I/O boundary only

        # Step 2: Two's complement = invert bits + add 1 (bit-level operations)
        inverted = bits_not(magnitude)
        one = [0] * 31 + [1]
        binary_vector = add32(inverted, one)

    # Create binary string with underscores every 8 bits
    bin_parts = []
    for i in range(0, 32, 8):
        byte_str = ''.join(str(binary_vector[i+j]) for j in range(8))
        bin_parts.append(byte_str)
    binary_string = '_'.join(bin_parts)

    # Create hex string using manual nibble conversion
    hex_map = {
        (0,0,0,0): '0', (0,0,0,1): '1', (0,0,1,0): '2', (0,0,1,1): '3',
        (0,1,0,0): '4', (0,1,0,1): '5', (0,1,1,0): '6', (0,1,1,1): '7',
        (1,0,0,0): '8', (1,0,0,1): '9', (1,0,1,0): 'A', (1,0,1,1): 'B',
        (1,1,0,0): 'C', (1,1,0,1): 'D', (1,1,1,0): 'E', (1,1,1,1): 'F',
    }

    hex_string = "0x"
    for i in range(0, 32, 4):
        nibble = tuple(binary_vector[i:i+4])
        hex_string += hex_map[nibble]

    return {
        'bin': binary_string,
        'hex': hex_string,
        'overflow': overflow
    }


def _bits_to_int_boundary(bits):
    """
    I/O boundary helper: Convert bit array to Python int.

    ***** I/O BOUNDARY FUNCTION *****
    This function converts between bit arrays and Python's native integer type.
    It uses arithmetic operators (+) for FORMAT CONVERSION only, not for
    implementing arithmetic algorithms.

    Analogous to:
    - struct.unpack() for binary format conversion
    - bits_to_int_unsigned() in bit_utils (TEST-ONLY)

    Used ONLY at module boundaries for output conversion.
    All arithmetic algorithms use ALU/MDU bit-level operations.

    Args:
        bits: Bit array [MSB...LSB]

    Returns:
        Non-negative integer
    """
    result = 0
    power = 1

    # I/O format conversion - not arithmetic
    for i in range(len(bits) - 1, -1, -1):
        if bits[i] == 1:
            result += power
        power += power  # Double

    return result


def decode_twos_complement(bits):
    """
    Decode two's complement representation to signed integer.

    Uses bit-level operations for two's complement arithmetic.
    I/O conversion (bits to Python int) uses boundary helpers.

    Args:
        bits: Either a 32-bit array, binary string, or hex string

    Returns:
        Dictionary with:
          - 'value': Signed integer value
    """
    # Handle different input formats
    if isinstance(bits, str):
        if bits.startswith('0x') or bits.startswith('0X'):
            # Hex string input
            hex_str = bits[2:]
            nibble_map = {
                '0': [0,0,0,0], '1': [0,0,0,1], '2': [0,0,1,0], '3': [0,0,1,1],
                '4': [0,1,0,0], '5': [0,1,0,1], '6': [0,1,1,0], '7': [0,1,1,1],
                '8': [1,0,0,0], '9': [1,0,0,1], 'A': [1,0,1,0], 'B': [1,0,1,1],
                'C': [1,1,0,0], 'D': [1,1,0,1], 'E': [1,1,1,0], 'F': [1,1,1,1],
                'a': [1,0,1,0], 'b': [1,0,1,1], 'c': [1,1,0,0], 'd': [1,1,0,1],
                'e': [1,1,1,0], 'f': [1,1,1,1],
            }
            binary_vector = []
            for char in hex_str:
                binary_vector.extend(nibble_map[char])
            # Pad or truncate to 32 bits
            while len(binary_vector) < 32:
                binary_vector = [0] + binary_vector
            binary_vector = binary_vector[-32:]
        else:
            # Binary string input (may have underscores or 0b prefix)
            bin_str = bits.replace('0b', '').replace('_', '')
            binary_vector = [int(c) for c in bin_str]
            # Pad to 32 bits
            while len(binary_vector) < 32:
                binary_vector = [0] + binary_vector
            binary_vector = binary_vector[-32:]
    else:
        # Already a bit array
        binary_vector = list(bits)
        assert len(binary_vector) == 32, "Bit array must be 32 bits"

    # Decode using bit-level operations
    if binary_vector[0] == 0:
        # Positive: direct conversion to int
        signed_val = _bits_to_int_boundary(binary_vector)
    else:
        # Negative: reverse two's complement using bit-level operations
        # Step 1: Subtract 1 (add -1)
        minus_one = [1] * 32  # -1 in two's complement is all 1s
        subtracted = add32(binary_vector, minus_one)

        # Step 2: Invert bits to get magnitude
        magnitude_bits = bits_not(subtracted)

        # Step 3: Convert to int and negate (negation only for final I/O)
        magnitude = _bits_to_int_boundary(magnitude_bits)
        signed_val = -magnitude

    return {'value': signed_val}


# Keep old function for backward compatibility
def twos_complement(num: int):
    """Legacy function - use encode_twos_complement instead."""
    result = encode_twos_complement(num)
    return (
        [int(c) for c in result['bin'].replace('_', '')],
        result['hex'],
        result['overflow']
    )

def add32(a, b):
    # copy inputs (avoid concatenation)
    aa = list(a)
    bb = list(b)
    out = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    carry = False
    # from LSB to MSB
    for i in reversed(range(32)):
        ai = bool(aa[i])
        bi = bool(bb[i])

        # full-adder with booleans
        xor_ab = (ai != bi)
        sum_bit = (xor_ab != carry)
        carry = (ai and bi) or (carry and xor_ab)

        out[i] = 1 if sum_bit else 0
    # overflow (final carry) dropped to keep 32 bits
    return out

def mul32(multiplicand: list, multiplier: list):
    """
    Multiply two 32-bit numbers using shift-add algorithm.

    Args:
        multiplicand: 32-bit array (MSB at index 0)
        multiplier: 32-bit array (MSB at index 0)

    Returns:
        64-bit product as list (MSB at index 0)
        [high 32 bits][low 32 bits]
    """
    # Initialize 64-bit product to zero
    product_lo = [0] * 32
    product_hi = [0] * 32

    # Shift-add multiplication
    for i in range(32):
        # Check multiplier bit from LSB (index 31) to MSB (index 0)
        bit_index = 31 - i
        if multiplier[bit_index] == 1:
            # Add multiplicand shifted left by i positions

            if i == 0:
                # No shift needed, add to low part
                product_lo = add32(product_lo, multiplicand)
            elif i < 32:
                # Shift multiplicand left by i positions
                # Lower part: bits from position i onwards, padded with i zeros on right
                shifted_lo = multiplicand[i:] + [0] * i

                # Upper part: top i bits that were shifted out
                # These appear at the bottom (LSB side) of the high word
                shifted_hi = [0] * (32 - i) + multiplicand[0:i]

                # Add shifted values to product
                # First add to low part
                old_product_lo = list(product_lo)
                product_lo = add32(product_lo, shifted_lo)

                # Check for carry from low to high
                # Carry occurs if result wrapped around (became smaller)
                carry = False
                for j in range(32):
                    if old_product_lo[j] == 1 and shifted_lo[j] == 1:
                        carry = True
                        break
                    elif old_product_lo[j] == 1 or shifted_lo[j] == 1:
                        if product_lo[j] == 0:
                            carry = True
                            break

                # Add to high part
                product_hi = add32(product_hi, shifted_hi)
                if carry:
                    # Add 1 to high part for carry
                    carry_bit = [0] * 31 + [1]
                    product_hi = add32(product_hi, carry_bit)
            else:
                # Shift >= 32, add to high part only
                shift_amount = i - 32
                if shift_amount == 0:
                    product_hi = add32(product_hi, multiplicand)
                else:
                    shifted = multiplicand[shift_amount:] + [0] * shift_amount
                    product_hi = add32(product_hi, shifted)

    # Return 64-bit product
    return product_hi + product_lo

if __name__ == "__main__":
    result = twos_complement(2147483648)
    print(result)
    binrep1 = digit_to_32bin[8]
    binrep2 = digit_to_32bin[8]
    print(binrep1)
    sum = add32(binrep1, binrep2)
    print(sum)
    newSum = add32(sum, sum)
    print(newSum)
    

# AI-END

