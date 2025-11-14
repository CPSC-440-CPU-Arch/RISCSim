"""
Unit tests for Hex Loader module

Tests hex file parsing and loading.

Author: RISCSim Team
Date: November 2025
"""

# AI-BEGIN: Claude Code (Anthropic) - November 14, 2025
# Prompt: "Create comprehensive tests for hex_loader module following Phase 1 requirements"

import pytest
import tempfile
import os
from riscsim.utils.hex_loader import parse_hex_line, validate_hex_file, load_hex_file


class TestParseHexLine:
    """Test parsing individual hex lines."""
    
    def test_parse_valid_hex_line(self):
        """Test parsing valid 8-digit hex line."""
        result = parse_hex_line("00500093")
        assert result == 0x00500093
    
    def test_parse_uppercase_hex(self):
        """Test parsing uppercase hex digits."""
        result = parse_hex_line("ABCDEF01")
        assert result == 0xABCDEF01
    
    def test_parse_lowercase_hex(self):
        """Test parsing lowercase hex digits."""
        result = parse_hex_line("abcdef01")
        assert result == 0xABCDEF01
    
    def test_parse_mixed_case_hex(self):
        """Test parsing mixed case hex digits."""
        result = parse_hex_line("AbCdEf01")
        assert result == 0xABCDEF01
    
    def test_parse_line_with_whitespace(self):
        """Test parsing line with leading/trailing whitespace."""
        result = parse_hex_line("  00500093  ")
        assert result == 0x00500093
    
    def test_parse_all_zeros(self):
        """Test parsing all zeros."""
        result = parse_hex_line("00000000")
        assert result == 0x00000000
    
    def test_parse_all_ones(self):
        """Test parsing all ones (0xFFFFFFFF)."""
        result = parse_hex_line("FFFFFFFF")
        assert result == 0xFFFFFFFF
    
    def test_parse_blank_line(self):
        """Test parsing blank line returns None."""
        result = parse_hex_line("   ")
        assert result is None
        
        result = parse_hex_line("")
        assert result is None
    
    def test_parse_invalid_length(self):
        """Test parsing line with wrong length."""
        with pytest.raises(ValueError, match="must be 8 digits"):
            parse_hex_line("1234567")  # Too short
        
        with pytest.raises(ValueError, match="must be 8 digits"):
            parse_hex_line("123456789")  # Too long
    
    def test_parse_invalid_characters(self):
        """Test parsing line with invalid hex characters."""
        with pytest.raises(ValueError, match="Invalid hex character"):
            parse_hex_line("1234567G")  # G is not valid hex
        
        with pytest.raises(ValueError, match="Invalid hex character"):
            parse_hex_line("1234567!")  # ! is not valid hex


class TestValidateHexFile:
    """Test hex file validation."""
    
    def test_validate_valid_file(self):
        """Test validating a valid hex file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            f.write("00500093\n")
            f.write("00A00113\n")
            f.write("002081B3\n")
            hex_file = f.name
        
        try:
            assert validate_hex_file(hex_file) is True
        finally:
            os.unlink(hex_file)
    
    def test_validate_file_with_blank_lines(self):
        """Test validating file with blank lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            f.write("00500093\n")
            f.write("\n")
            f.write("00A00113\n")
            hex_file = f.name
        
        try:
            assert validate_hex_file(hex_file) is True
        finally:
            os.unlink(hex_file)
    
    def test_validate_file_invalid_line(self):
        """Test validating file with invalid line."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            f.write("00500093\n")
            f.write("INVALID!\n")  # Invalid line
            hex_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Line 2"):
                validate_hex_file(hex_file)
        finally:
            os.unlink(hex_file)
    
    def test_validate_nonexistent_file(self):
        """Test validating nonexistent file."""
        with pytest.raises(FileNotFoundError):
            validate_hex_file("/nonexistent/file.hex")


class TestLoadHexFile:
    """Test loading hex files."""
    
    def test_load_simple_file(self):
        """Test loading simple hex file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            f.write("00500093\n")
            f.write("00A00113\n")
            f.write("002081B3\n")
            hex_file = f.name
        
        try:
            words = load_hex_file(hex_file)
            assert len(words) == 3
            assert words[0] == 0x00500093
            assert words[1] == 0x00A00113
            assert words[2] == 0x002081B3
        finally:
            os.unlink(hex_file)
    
    def test_load_file_with_blank_lines(self):
        """Test loading file with blank lines (ignored)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            f.write("00500093\n")
            f.write("\n")
            f.write("00A00113\n")
            f.write("\n\n")
            f.write("002081B3\n")
            hex_file = f.name
        
        try:
            words = load_hex_file(hex_file)
            assert len(words) == 3  # Blank lines ignored
            assert words[0] == 0x00500093
            assert words[1] == 0x00A00113
            assert words[2] == 0x002081B3
        finally:
            os.unlink(hex_file)
    
    def test_load_single_instruction(self):
        """Test loading file with single instruction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            f.write("DEADBEEF\n")
            hex_file = f.name
        
        try:
            words = load_hex_file(hex_file)
            assert len(words) == 1
            assert words[0] == 0xDEADBEEF
        finally:
            os.unlink(hex_file)
    
    def test_load_uppercase_lowercase(self):
        """Test loading file with mixed case hex."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            f.write("ABCDEF01\n")
            f.write("abcdef01\n")
            f.write("AbCdEf01\n")
            hex_file = f.name
        
        try:
            words = load_hex_file(hex_file)
            assert len(words) == 3
            assert words[0] == 0xABCDEF01
            assert words[1] == 0xABCDEF01
            assert words[2] == 0xABCDEF01
        finally:
            os.unlink(hex_file)
    
    def test_load_empty_file(self):
        """Test loading empty file raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            # Write nothing
            hex_file = f.name
        
        try:
            with pytest.raises(ValueError, match="empty"):
                load_hex_file(hex_file)
        finally:
            os.unlink(hex_file)
    
    def test_load_file_only_blanks(self):
        """Test loading file with only blank lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            f.write("\n\n\n")
            hex_file = f.name
        
        try:
            with pytest.raises(ValueError, match="empty"):
                load_hex_file(hex_file)
        finally:
            os.unlink(hex_file)
    
    def test_load_invalid_line_length(self):
        """Test loading file with invalid line length."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            f.write("00500093\n")
            f.write("123\n")  # Too short
            hex_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Line 2"):
                load_hex_file(hex_file)
        finally:
            os.unlink(hex_file)
    
    def test_load_nonexistent_file(self):
        """Test loading nonexistent file."""
        with pytest.raises(FileNotFoundError):
            load_hex_file("/nonexistent/file.hex")


class TestTestBaseHex:
    """Test loading the provided test_base.hex program."""
    
    def test_load_test_base_program(self):
        """Test loading test_base.hex if it exists."""
        # Create test_base.hex with expected instructions
        expected_instructions = [
            0x00500093,  # addi x1, x0, 5
            0x00A00113,  # addi x2, x0, 10
            0x002081B3,  # add x3, x1, x2
            0x40110233,  # sub x4, x2, x1
            0x000102B7,  # lui x5, 0x00010
            0x0032A023,  # sw x3, 0(x5)
            0x0002A203,  # lw x4, 0(x5)
            0x00418463,  # beq x3, x4, label1
            0x00100313,  # addi x6, x0, 1 (skipped)
            0x00200313,  # addi x6, x0, 2
            0x0000006F,  # jal x0, 0 (infinite loop)
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hex', delete=False) as f:
            for instr in expected_instructions:
                f.write(f"{instr:08X}\n")
            hex_file = f.name
        
        try:
            words = load_hex_file(hex_file)
            assert len(words) == len(expected_instructions)
            for i, expected in enumerate(expected_instructions):
                assert words[i] == expected
        finally:
            os.unlink(hex_file)


# AI-END
