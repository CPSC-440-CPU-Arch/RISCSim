"""
Hex File Loader for RISC-V CPU Simulator

Loads .hex files containing 32-bit words in hexadecimal format.
Format: 8 hex digits per line (32-bit word)

Example .hex file:
    00500093
    00A00113
    002081B3

Author: RISCSim Team
Date: November 2025
"""

# AI-BEGIN: Claude Code (Anthropic) - November 14, 2025
# Prompt: "Implement hex file loader for RISC-V CPU Phase 1, following constraints"

from typing import List


def parse_hex_line(line: str) -> int:
    """
    Parse a single hex line to integer.
    
    Args:
        line: String containing 8 hex digits (32-bit word)
    
    Returns:
        Integer value of hex string
    
    Raises:
        ValueError: If line format is invalid
    
    Convention:
    - I/O BOUNDARY FUNCTION (converts hex string to int)
    - Must be exactly 8 hex digits
    - Case insensitive (A-F or a-f)
    """
    # Remove whitespace
    line = line.strip()
    
    # Check if empty (skip blank lines)
    if not line:
        return None
    
    # Check length
    if len(line) != 8:
        raise ValueError(f"Hex line must be 8 digits, got {len(line)}: '{line}'")
    
    # Validate hex characters
    valid_hex = set('0123456789ABCDEFabcdef')
    for char in line:
        if char not in valid_hex:
            raise ValueError(f"Invalid hex character '{char}' in line: '{line}'")
    
    # Convert to int (I/O BOUNDARY: using int() for format conversion)
    try:
        value = int(line, 16)
    except ValueError as e:
        raise ValueError(f"Failed to parse hex line '{line}': {e}")
    
    return value


def validate_hex_file(filepath: str) -> bool:
    """
    Validate hex file format.
    
    Args:
        filepath: Path to .hex file
    
    Returns:
        True if valid, False otherwise
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If format is invalid
    """
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip blank lines
                if not line:
                    continue
                
                # Validate line
                try:
                    parse_hex_line(line)
                except ValueError as e:
                    raise ValueError(f"Line {line_num}: {e}")
        
        return True
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Hex file not found: {filepath}")


def load_hex_file(filepath: str) -> List[int]:
    """
    Load .hex file into list of 32-bit words.
    
    Args:
        filepath: Path to .hex file
    
    Returns:
        List of 32-bit words as integers
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    
    Convention:
    - Each line is 8 hex digits (32 bits)
    - Blank lines are ignored
    - Returns list of integers (for boundary conversion to bit arrays)
    
    Example:
        Input file:
            00500093
            00A00113
            002081B3
        
        Returns:
            [0x00500093, 0x00A00113, 0x002081B3]
    """
    words = []
    
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                # Parse line
                try:
                    word = parse_hex_line(line)
                    
                    # Skip blank lines
                    if word is None:
                        continue
                    
                    # Add to list
                    words.append(word)
                
                except ValueError as e:
                    raise ValueError(f"Line {line_num}: {e}")
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Hex file not found: {filepath}")
    
    # Validate we got at least one word
    if not words:
        raise ValueError(f"Hex file is empty: {filepath}")
    
    return words

# AI-END
