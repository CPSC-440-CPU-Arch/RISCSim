# AI-BEGIN
"""
Bit manipulation utilities for RISCSim.

All functions operate on bit arrays represented as lists of 0/1 integers.
Convention: MSB at index 0, LSB at the end.
Example: [1,0,1,0] = binary 1010 (decimal 10 unsigned)

This module provides the foundation for all numeric operations without
using Python's built-in numeric operators (+, -, *, /, <<, >>).
"""


def bits_and(a, b):
    """Bitwise AND of two bit arrays.

    Args:
        a: List of bits (0 or 1)
        b: List of bits (same length as a)

    Returns:
        List of bits representing a AND b

    Raises:
        ValueError: If bit arrays have different lengths
    """
    if len(a) != len(b):
        raise ValueError(f"Bit arrays must have same length: {len(a)} != {len(b)}")
    return [a[i] & b[i] for i in range(len(a))]


def bits_or(a, b):
    """Bitwise OR of two bit arrays.

    Args:
        a: List of bits
        b: List of bits (same length as a)

    Returns:
        List of bits representing a OR b

    Raises:
        ValueError: If bit arrays have different lengths
    """
    if len(a) != len(b):
        raise ValueError(f"Bit arrays must have same length: {len(a)} != {len(b)}")
    return [a[i] | b[i] for i in range(len(a))]


def bits_xor(a, b):
    """Bitwise XOR of two bit arrays.

    Args:
        a: List of bits
        b: List of bits (same length as a)

    Returns:
        List of bits representing a XOR b

    Raises:
        ValueError: If bit arrays have different lengths
    """
    if len(a) != len(b):
        raise ValueError(f"Bit arrays must have same length: {len(a)} != {len(b)}")
    return [a[i] ^ b[i] for i in range(len(a))]


def bits_not(a):
    """Bitwise NOT of a bit array.

    Args:
        a: List of bits

    Returns:
        List of bits representing NOT a (all bits inverted)
    """
    return [1 ^ a[i] for i in range(len(a))]


def bits_equal(a, b):
    """Check if two bit arrays are equal.

    Args:
        a: List of bits
        b: List of bits

    Returns:
        Boolean: True if arrays are identical
    """
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
            return False
    return True


def is_zero(bits):
    """Check if all bits are zero.

    Args:
        bits: List of bits

    Returns:
        Boolean: True if all bits are 0
    """
    for bit in bits:
        if bit != 0:
            return False
    return True


def is_negative(bits):
    """Check if MSB (sign bit) is 1.

    Args:
        bits: List of bits

    Returns:
        Boolean: True if MSB is 1 (negative in two's complement)
    """
    return bits[0] == 1


def zero_extend(bits, target_width):
    """Zero-extend a bit array to target width by padding MSB side with zeros.

    Args:
        bits: List of bits
        target_width: Desired bit width

    Returns:
        List of bits (zero-extended or original if already >= target_width)
    """
    if len(bits) >= target_width:
        return bits[:]
    padding = [0] * (target_width - len(bits))
    return padding + bits


def sign_extend(bits, target_width):
    """Sign-extend a bit array to target width by replicating MSB.

    Args:
        bits: List of bits
        target_width: Desired bit width

    Returns:
        List of bits (sign-extended or original if already >= target_width)
    """
    if len(bits) >= target_width:
        return bits[:]
    sign_bit = bits[0]
    padding = [sign_bit] * (target_width - len(bits))
    return padding + bits


def truncate(bits, target_width):
    """Truncate a bit array to target width, keeping LSBs.

    Args:
        bits: List of bits
        target_width: Desired bit width

    Returns:
        List of bits (truncated from MSB side, keeping rightmost bits)
    """
    if len(bits) <= target_width:
        return bits[:]
    # Keep the rightmost (LSB) bits
    return bits[len(bits) - target_width:]


def get_bit(bits, index):
    """Get bit at specified index (0 = MSB, len-1 = LSB).

    Args:
        bits: List of bits
        index: Index from MSB (0-based)

    Returns:
        0 or 1

    Raises:
        IndexError: If index out of range
    """
    return bits[index]


def set_bit(bits, index, value):
    """Set bit at specified index to value (returns new list, non-destructive).

    Args:
        bits: List of bits
        index: Index from MSB (0-based)
        value: 0 or 1

    Returns:
        New list of bits with specified bit set

    Raises:
        IndexError: If index out of range
    """
    result = bits[:]
    result[index] = value
    return result


def concat_bits(*bit_arrays):
    """Concatenate multiple bit arrays (MSB to LSB order).

    Args:
        *bit_arrays: Variable number of bit arrays

    Returns:
        Concatenated bit array (first array becomes MSB portion)

    Example:
        concat_bits([1,0], [1,1]) -> [1,0,1,1]
    """
    result = []
    for arr in bit_arrays:
        result.extend(arr)
    return result


def slice_bits(bits, start, end):
    """Extract a slice of bits [start:end] (Python slice semantics).

    Args:
        bits: List of bits
        start: Start index (from MSB, 0-based, inclusive)
        end: End index (exclusive)

    Returns:
        Sliced bit array

    Example:
        slice_bits([1,0,1,0], 1, 3) -> [0,1]
    """
    return bits[start:end]


def bits_to_binary_string(bits, group_size=4):
    """Convert bit array to binary string with optional grouping.

    Args:
        bits: List of bits
        group_size: Group bits by this size with underscore separators (default 4)

    Returns:
        String like "1010_1100_0011_1111"
    """
    result = ""
    for i, bit in enumerate(bits):
        if i > 0 and i % group_size == 0:
            result += "_"
        result += str(bit)
    return result


def bits_to_hex_string(bits):
    """Convert bit array to hexadecimal string using manual lookup tables.

    No use of hex(), format(), or int() with base conversion.

    Args:
        bits: List of bits (will be padded to multiple of 4 if needed)

    Returns:
        String like "0xAC3F"
    """
    # Pad to multiple of 4 if needed
    padded_bits = bits[:]
    while len(padded_bits) % 4 != 0:
        padded_bits = [0] + padded_bits

    # Manual lookup table for nibble to hex digit
    hex_map = {
        (0,0,0,0): '0', (0,0,0,1): '1', (0,0,1,0): '2', (0,0,1,1): '3',
        (0,1,0,0): '4', (0,1,0,1): '5', (0,1,1,0): '6', (0,1,1,1): '7',
        (1,0,0,0): '8', (1,0,0,1): '9', (1,0,1,0): 'A', (1,0,1,1): 'B',
        (1,1,0,0): 'C', (1,1,0,1): 'D', (1,1,1,0): 'E', (1,1,1,1): 'F',
    }

    result = "0x"
    for i in range(0, len(padded_bits), 4):
        nibble = tuple(padded_bits[i:i+4])
        result += hex_map[nibble]

    return result


def hex_string_to_bits(hex_str, width=32):
    """Convert hex string to bit array using manual lookup tables.

    No use of int() with base conversion.

    Args:
        hex_str: String like "0xAC3F" or "AC3F"
        width: Target bit width (default 32, will zero-extend if needed)

    Returns:
        List of bits

    Raises:
        ValueError: If hex string contains invalid characters
    """
    # Remove 0x prefix if present
    if hex_str.startswith("0x") or hex_str.startswith("0X"):
        hex_str = hex_str[2:]

    # Manual lookup table for hex digit to nibble
    nibble_map = {
        '0': [0,0,0,0], '1': [0,0,0,1], '2': [0,0,1,0], '3': [0,0,1,1],
        '4': [0,1,0,0], '5': [0,1,0,1], '6': [0,1,1,0], '7': [0,1,1,1],
        '8': [1,0,0,0], '9': [1,0,0,1], 'A': [1,0,1,0], 'B': [1,0,1,1],
        'C': [1,1,0,0], 'D': [1,1,0,1], 'E': [1,1,1,0], 'F': [1,1,1,1],
        'a': [1,0,1,0], 'b': [1,0,1,1], 'c': [1,1,0,0], 'd': [1,1,0,1],
        'e': [1,1,1,0], 'f': [1,1,1,1],
    }

    bits = []
    for char in hex_str:
        if char in nibble_map:
            bits.extend(nibble_map[char])
        else:
            raise ValueError(f"Invalid hex character: {char}")

    # Pad or truncate to target width
    while len(bits) < width:
        bits = [0] + bits
    if len(bits) > width:
        bits = bits[len(bits) - width:]

    return bits


def binary_string_to_bits(bin_str):
    """Convert binary string to bit array.

    Args:
        bin_str: String like "1010" or "1010_1100" or "0b1010"

    Returns:
        List of bits

    Raises:
        ValueError: If string contains invalid characters
    """
    # Remove 0b prefix and underscores
    bin_str = bin_str.replace("0b", "").replace("0B", "").replace("_", "")

    bits = []
    for char in bin_str:
        if char == '0':
            bits.append(0)
        elif char == '1':
            bits.append(1)
        else:
            raise ValueError(f"Invalid binary character: {char}")

    return bits


def int_to_bits_unsigned(value, width):
    """Convert unsigned integer to bit array.

    Uses manual repeated division algorithm (no bin() or format()).

    Args:
        value: Non-negative integer
        width: Bit width

    Returns:
        List of bits

    Raises:
        ValueError: If value is negative

    Note: This is a utility function for testing. Implementation modules
    should build arithmetic from bit operations, not use this.
    """
    if value < 0:
        raise ValueError("Value must be non-negative for unsigned conversion")

    bits = []
    temp = value

    # Extract bits by repeated division by 2
    for _ in range(width):
        bits.append(temp % 2)
        temp = temp // 2

    # Reverse to get MSB first
    bits.reverse()

    return bits


def bits_to_int_unsigned(bits):
    """Convert bit array to unsigned integer.

    Uses manual power-of-2 accumulation (no int() with base conversion).

    Args:
        bits: List of bits

    Returns:
        Non-negative integer

    Note: This is a utility function for testing. Implementation modules
    should build arithmetic from bit operations, not use this.
    """
    result = 0
    power = 1

    # Process from LSB to MSB
    for i in range(len(bits) - 1, -1, -1):
        if bits[i] == 1:
            result += power
        # Double the power without using * operator
        power += power

    return result
# AI-END
