"""
Barrel Shifter for RISC-V RV32 Architecture

Implements three shift operations:
- SLL (Shift Left Logical): Shift left, fill right with zeros
- SRL (Shift Right Logical): Shift right, fill left with zeros
- SRA (Shift Right Arithmetic): Shift right, fill left with sign bit

Uses a 5-stage barrel shifter design (shifts by 16, 8, 4, 2, 1 bits)
to avoid using Python's built-in shift operators.

All bit arrays follow MSB-first convention (index 0 = MSB, index 31 = LSB)
"""

from riscsim.utils.bit_utils import slice_bits, concat_bits


# Lookup table for shift amounts 0-63 as 5-bit arrays (with mod 32 wrapping)
# RISC-V uses only lower 5 bits, so 32->0, 33->1, etc.
_SHAMT_TO_BITS = {
    0: [0,0,0,0,0], 1: [0,0,0,0,1], 2: [0,0,0,1,0], 3: [0,0,0,1,1],
    4: [0,0,1,0,0], 5: [0,0,1,0,1], 6: [0,0,1,1,0], 7: [0,0,1,1,1],
    8: [0,1,0,0,0], 9: [0,1,0,0,1], 10: [0,1,0,1,0], 11: [0,1,0,1,1],
    12: [0,1,1,0,0], 13: [0,1,1,0,1], 14: [0,1,1,1,0], 15: [0,1,1,1,1],
    16: [1,0,0,0,0], 17: [1,0,0,0,1], 18: [1,0,0,1,0], 19: [1,0,0,1,1],
    20: [1,0,1,0,0], 21: [1,0,1,0,1], 22: [1,0,1,1,0], 23: [1,0,1,1,1],
    24: [1,1,0,0,0], 25: [1,1,0,0,1], 26: [1,1,0,1,0], 27: [1,1,0,1,1],
    28: [1,1,1,0,0], 29: [1,1,1,0,1], 30: [1,1,1,1,0], 31: [1,1,1,1,1],
    # Wrap-around values (32-63 map to 0-31)
    32: [0,0,0,0,0], 33: [0,0,0,0,1], 34: [0,0,0,1,0], 35: [0,0,0,1,1],
    36: [0,0,1,0,0], 37: [0,0,1,0,1], 38: [0,0,1,1,0], 39: [0,0,1,1,1],
    40: [0,1,0,0,0], 41: [0,1,0,0,1], 42: [0,1,0,1,0], 43: [0,1,0,1,1],
    44: [0,1,1,0,0], 45: [0,1,1,0,1], 46: [0,1,1,1,0], 47: [0,1,1,1,1],
    48: [1,0,0,0,0], 49: [1,0,0,0,1], 50: [1,0,0,1,0], 51: [1,0,0,1,1],
    52: [1,0,1,0,0], 53: [1,0,1,0,1], 54: [1,0,1,1,0], 55: [1,0,1,1,1],
    56: [1,1,0,0,0], 57: [1,1,0,0,1], 58: [1,1,0,1,0], 59: [1,1,0,1,1],
    60: [1,1,1,0,0], 61: [1,1,1,0,1], 62: [1,1,1,1,0], 63: [1,1,1,1,1]
}


# AI-BEGIN
def shifter(bits, shamt, op):
    """
    Barrel shifter for RISC-V shift operations.

    Args:
        bits: 32-bit array (MSB at index 0, LSB at index 31)
        shamt: Shift amount - either integer (0-31) or 5-bit array
        op: Operation code - string ("SLL", "SRL", "SRA") or 2-bit array
            - "SLL" or [0,0]: Shift Left Logical
            - "SRL" or [0,1]: Shift Right Logical
            - "SRA" or [1,1]: Shift Right Arithmetic

    Returns:
        32-bit array with shifted result (MSB at index 0)
    """
    # Input validation
    assert len(bits) == 32, f"Input bits must be 32-bit array, got {len(bits)}"

    # Parse shamt - convert to 5-bit array if integer
    if isinstance(shamt, int):
        # Use lookup table (supports 0-63 with mod 32 wrapping)
        # For test convenience; production code should use bit arrays
        if shamt < 0:
            shamt_bits = _SHAMT_TO_BITS[0]
        elif shamt <= 63:
            shamt_bits = _SHAMT_TO_BITS[shamt]
        else:
            # For values > 63, default to 0 (undefined behavior)
            shamt_bits = _SHAMT_TO_BITS[0]
    else:
        assert len(shamt) == 5, f"Shift amount must be 5 bits, got {len(shamt)}"
        shamt_bits = shamt

    # Parse operation
    if isinstance(op, str):
        op_str = op.upper()
        assert op_str in ["SLL", "SRL", "SRA"], f"Invalid operation: {op}"
    else:
        assert len(op) == 2, f"Operation code must be 2 bits, got {len(op)}"
        # Map bit patterns to operation strings
        if op == [0, 0]:
            op_str = "SLL"
        elif op == [0, 1]:
            op_str = "SRL"
        elif op == [1, 1]:
            op_str = "SRA"
        else:
            raise ValueError(f"Invalid operation code: {op}")

    # Extract sign bit for SRA operation
    sign_bit = bits[0]  # MSB is at index 0

    # Barrel shifter implementation
    # 5 stages: shift by 16, 8, 4, 2, 1 (controlled by shamt bits)
    current = bits

    if op_str == "SLL":
        # Shift Left Logical - process from LSB to MSB of shamt
        # shamt[0] = bit 4 (shift by 16)
        # shamt[1] = bit 3 (shift by 8)
        # shamt[2] = bit 2 (shift by 4)
        # shamt[3] = bit 1 (shift by 2)
        # shamt[4] = bit 0 (shift by 1)

        # Stage 1: Shift by 16 if shamt_bits[0] == 1
        if shamt_bits[0] == 1:
            current = concat_bits(slice_bits(current, 16, 32), [0]*16)

        # Stage 2: Shift by 8 if shamt_bits[1] == 1
        if shamt_bits[1] == 1:
            current = concat_bits(slice_bits(current, 8, 32), [0]*8)

        # Stage 3: Shift by 4 if shamt_bits[2] == 1
        if shamt_bits[2] == 1:
            current = concat_bits(slice_bits(current, 4, 32), [0]*4)

        # Stage 4: Shift by 2 if shamt_bits[3] == 1
        if shamt_bits[3] == 1:
            current = concat_bits(slice_bits(current, 2, 32), [0]*2)

        # Stage 5: Shift by 1 if shamt_bits[4] == 1
        if shamt_bits[4] == 1:
            current = concat_bits(slice_bits(current, 1, 32), [0]*1)

    elif op_str == "SRL":
        # Shift Right Logical - fill with zeros

        # Stage 1: Shift by 16 if shamt_bits[0] == 1
        if shamt_bits[0] == 1:
            current = concat_bits([0]*16, slice_bits(current, 0, 16))

        # Stage 2: Shift by 8 if shamt_bits[1] == 1
        if shamt_bits[1] == 1:
            current = concat_bits([0]*8, slice_bits(current, 0, 24))

        # Stage 3: Shift by 4 if shamt_bits[2] == 1
        if shamt_bits[2] == 1:
            current = concat_bits([0]*4, slice_bits(current, 0, 28))

        # Stage 4: Shift by 2 if shamt_bits[3] == 1
        if shamt_bits[3] == 1:
            current = concat_bits([0]*2, slice_bits(current, 0, 30))

        # Stage 5: Shift by 1 if shamt_bits[4] == 1
        if shamt_bits[4] == 1:
            current = concat_bits([0]*1, slice_bits(current, 0, 31))

    elif op_str == "SRA":
        # Shift Right Arithmetic - fill with sign bit

        # Stage 1: Shift by 16 if shamt_bits[0] == 1
        if shamt_bits[0] == 1:
            current = concat_bits([sign_bit]*16, slice_bits(current, 0, 16))

        # Stage 2: Shift by 8 if shamt_bits[1] == 1
        if shamt_bits[1] == 1:
            current = concat_bits([sign_bit]*8, slice_bits(current, 0, 24))

        # Stage 3: Shift by 4 if shamt_bits[2] == 1
        if shamt_bits[2] == 1:
            current = concat_bits([sign_bit]*4, slice_bits(current, 0, 28))

        # Stage 4: Shift by 2 if shamt_bits[3] == 1
        if shamt_bits[3] == 1:
            current = concat_bits([sign_bit]*2, slice_bits(current, 0, 30))

        # Stage 5: Shift by 1 if shamt_bits[4] == 1
        if shamt_bits[4] == 1:
            current = concat_bits([sign_bit]*1, slice_bits(current, 0, 31))

    return current


def shifter_with_control(operand, control_signals):
    """
    Shifter operation wrapper that integrates with control unit signals.
    
    This function provides a bridge between the control unit and the raw shifter,
    allowing for cycle-accurate simulation with control signal tracking.
    
    Args:
        operand: 32-bit array to be shifted
        control_signals: ControlSignals instance containing shift operation and amount
        
    Returns:
        Dictionary containing:
          - 'result': 32-bit shifted result array
          - 'signals': Updated ControlSignals instance
          - 'trace': Operation trace string
    """
    from riscsim.cpu.control_signals import decode_shifter_op
    
    # Extract shift operation and amount from control signals
    sh_op = control_signals.sh_op
    sh_amount = control_signals.sh_amount
    
    # Convert 3-bit op code to 2-bit code for shifter
    # sh_op format: [unused, bit1, bit0]
    # We use only the lower 2 bits
    shifter_op = [sh_op[1], sh_op[2]]
    
    # Perform shift operation
    result = shifter(operand, sh_amount, shifter_op)
    
    # Create trace message
    op_name = decode_shifter_op(sh_op)
    # Convert sh_amount bits to integer for display
    amount_val = 0
    for i, bit in enumerate(sh_amount):
        amount_val = (amount_val << 1) | bit
    
    trace = f"Shifter {op_name} by {amount_val}"
    
    # Return results with control signals
    return {
        'result': result,
        'signals': control_signals.copy(),
        'trace': trace
    }


# AI-END

