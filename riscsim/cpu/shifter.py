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
        # Use only lower 5 bits (RISC-V spec: shift amount is 5 bits)
        shamt = shamt & 0x1F
        shamt_bits = [(shamt >> (4 - i)) & 1 for i in range(5)]
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
# AI-END
