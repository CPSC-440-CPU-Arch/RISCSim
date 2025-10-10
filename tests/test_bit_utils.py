# AI-BEGIN
"""
Unit tests for bit_utils module.

Tests all bit manipulation functions to ensure correct behavior.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.bit_utils import *


def test_bits_and():
    """Test bitwise AND operation."""
    a = [1, 0, 1, 0]
    b = [1, 1, 0, 0]
    result = bits_and(a, b)
    assert result == [1, 0, 0, 0], f"Expected [1,0,0,0], got {result}"
    print("✓ bits_and test passed")


def test_bits_or():
    """Test bitwise OR operation."""
    a = [1, 0, 1, 0]
    b = [1, 1, 0, 0]
    result = bits_or(a, b)
    assert result == [1, 1, 1, 0], f"Expected [1,1,1,0], got {result}"
    print("✓ bits_or test passed")


def test_bits_xor():
    """Test bitwise XOR operation."""
    a = [1, 0, 1, 0]
    b = [1, 1, 0, 0]
    result = bits_xor(a, b)
    assert result == [0, 1, 1, 0], f"Expected [0,1,1,0], got {result}"
    print("✓ bits_xor test passed")


def test_bits_not():
    """Test bitwise NOT operation."""
    a = [1, 0, 1, 0]
    result = bits_not(a)
    assert result == [0, 1, 0, 1], f"Expected [0,1,0,1], got {result}"
    print("✓ bits_not test passed")


def test_zero_extend():
    """Test zero extension."""
    bits = [1, 0, 1, 0]
    result = zero_extend(bits, 8)
    assert result == [0, 0, 0, 0, 1, 0, 1, 0], f"Expected [0,0,0,0,1,0,1,0], got {result}"
    print("✓ zero_extend test passed")


def test_sign_extend():
    """Test sign extension (negative number)."""
    bits = [1, 0, 1, 0]  # Negative (MSB=1)
    result = sign_extend(bits, 8)
    assert result == [1, 1, 1, 1, 1, 0, 1, 0], f"Expected [1,1,1,1,1,0,1,0], got {result}"

    # Positive number
    bits = [0, 1, 0, 1]  # Positive (MSB=0)
    result = sign_extend(bits, 8)
    assert result == [0, 0, 0, 0, 0, 1, 0, 1], f"Expected [0,0,0,0,0,1,0,1], got {result}"
    print("✓ sign_extend test passed")


def test_truncate():
    """Test truncation."""
    bits = [1, 0, 1, 0, 1, 1, 0, 0]
    result = truncate(bits, 4)
    assert result == [1, 1, 0, 0], f"Expected [1,1,0,0], got {result}"
    print("✓ truncate test passed")


def test_is_zero():
    """Test zero detection."""
    assert is_zero([0, 0, 0, 0]) == True
    assert is_zero([0, 0, 0, 1]) == False
    assert is_zero([1, 0, 0, 0]) == False
    print("✓ is_zero test passed")


def test_is_negative():
    """Test negative detection (MSB check)."""
    assert is_negative([1, 0, 0, 0]) == True
    assert is_negative([0, 1, 1, 1]) == False
    print("✓ is_negative test passed")


def test_concat_bits():
    """Test bit concatenation."""
    a = [1, 0]
    b = [1, 1]
    c = [0, 1]
    result = concat_bits(a, b, c)
    assert result == [1, 0, 1, 1, 0, 1], f"Expected [1,0,1,1,0,1], got {result}"
    print("✓ concat_bits test passed")


def test_slice_bits():
    """Test bit slicing."""
    bits = [1, 0, 1, 0, 1, 1, 0, 0]
    result = slice_bits(bits, 2, 6)
    assert result == [1, 0, 1, 1], f"Expected [1,0,1,1], got {result}"
    print("✓ slice_bits test passed")


def test_bits_to_binary_string():
    """Test binary string formatting."""
    bits = [1, 0, 1, 0, 1, 1, 0, 0]
    result = bits_to_binary_string(bits, group_size=4)
    assert result == "1010_1100", f"Expected '1010_1100', got '{result}'"
    print("✓ bits_to_binary_string test passed")


def test_bits_to_hex_string():
    """Test hex string conversion."""
    # Test 0xAC (10101100)
    bits = [1, 0, 1, 0, 1, 1, 0, 0]
    result = bits_to_hex_string(bits)
    assert result == "0xAC", f"Expected '0xAC', got '{result}'"

    # Test 0x0D (00001101)
    bits = [0, 0, 0, 0, 1, 1, 0, 1]
    result = bits_to_hex_string(bits)
    assert result == "0x0D", f"Expected '0x0D', got '{result}'"

    # Test 0xFFFFFFFF (32 bits all 1s)
    bits = [1] * 32
    result = bits_to_hex_string(bits)
    assert result == "0xFFFFFFFF", f"Expected '0xFFFFFFFF', got '{result}'"

    print("✓ bits_to_hex_string test passed")


def test_hex_string_to_bits():
    """Test hex string parsing."""
    # Test 0xAC
    result = hex_string_to_bits("0xAC", width=8)
    expected = [1, 0, 1, 0, 1, 1, 0, 0]
    assert result == expected, f"Expected {expected}, got {result}"

    # Test with lowercase
    result = hex_string_to_bits("0xac", width=8)
    assert result == expected, f"Expected {expected}, got {result}"

    # Test 32-bit value
    result = hex_string_to_bits("0x0000000D", width=32)
    expected = [0] * 28 + [1, 1, 0, 1]
    assert result == expected, f"Expected {expected}, got {result}"

    print("✓ hex_string_to_bits test passed")


def test_binary_string_to_bits():
    """Test binary string parsing."""
    result = binary_string_to_bits("1010")
    assert result == [1, 0, 1, 0], f"Expected [1,0,1,0], got {result}"

    result = binary_string_to_bits("1010_1100")
    assert result == [1, 0, 1, 0, 1, 1, 0, 0], f"Expected [1,0,1,0,1,1,0,0], got {result}"

    result = binary_string_to_bits("0b1010")
    assert result == [1, 0, 1, 0], f"Expected [1,0,1,0], got {result}"

    print("✓ binary_string_to_bits test passed")


def test_int_to_bits_unsigned():
    """Test unsigned integer to bits conversion."""
    # Test 13 (0b1101)
    result = int_to_bits_unsigned(13, 8)
    expected = [0, 0, 0, 0, 1, 1, 0, 1]
    assert result == expected, f"Expected {expected}, got {result}"

    # Test 255 (0b11111111)
    result = int_to_bits_unsigned(255, 8)
    expected = [1, 1, 1, 1, 1, 1, 1, 1]
    assert result == expected, f"Expected {expected}, got {result}"

    # Test 0
    result = int_to_bits_unsigned(0, 8)
    expected = [0, 0, 0, 0, 0, 0, 0, 0]
    assert result == expected, f"Expected {expected}, got {result}"

    print("✓ int_to_bits_unsigned test passed")


def test_bits_to_int_unsigned():
    """Test bits to unsigned integer conversion."""
    # Test 13
    bits = [0, 0, 0, 0, 1, 1, 0, 1]
    result = bits_to_int_unsigned(bits)
    assert result == 13, f"Expected 13, got {result}"

    # Test 255
    bits = [1, 1, 1, 1, 1, 1, 1, 1]
    result = bits_to_int_unsigned(bits)
    assert result == 255, f"Expected 255, got {result}"

    # Test 0
    bits = [0, 0, 0, 0, 0, 0, 0, 0]
    result = bits_to_int_unsigned(bits)
    assert result == 0, f"Expected 0, got {result}"

    print("✓ bits_to_int_unsigned test passed")


def test_roundtrip_conversions():
    """Test that conversions are reversible."""
    # Hex roundtrip
    original = [1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1]
    hex_str = bits_to_hex_string(original)
    recovered = hex_string_to_bits(hex_str, width=len(original))
    assert original == recovered, f"Hex roundtrip failed: {original} -> {hex_str} -> {recovered}"

    # Binary roundtrip
    bin_str = bits_to_binary_string(original, group_size=4)
    recovered = binary_string_to_bits(bin_str)
    assert original == recovered, f"Binary roundtrip failed"

    # Int roundtrip (unsigned)
    for value in [0, 1, 13, 127, 255]:
        bits = int_to_bits_unsigned(value, 8)
        recovered = bits_to_int_unsigned(bits)
        assert value == recovered, f"Int roundtrip failed for {value}"

    print("✓ roundtrip conversions test passed")


if __name__ == "__main__":
    print("Running bit_utils tests...\n")

    test_bits_and()
    test_bits_or()
    test_bits_xor()
    test_bits_not()
    test_zero_extend()
    test_sign_extend()
    test_truncate()
    test_is_zero()
    test_is_negative()
    test_concat_bits()
    test_slice_bits()
    test_bits_to_binary_string()
    test_bits_to_hex_string()
    test_hex_string_to_bits()
    test_binary_string_to_bits()
    test_int_to_bits_unsigned()
    test_bits_to_int_unsigned()
    test_roundtrip_conversions()

    print("\n✅ All bit_utils tests passed!")
# AI-END
