from riscsim.utils.components import OneBitALU, MSBOneBitALU


"""
opcodes:
[0, 0, 0, 0] = and
[0, 0, 0, 1] = or
[0, 0, 1, 0] = add
[0, 1, 1, 0] = subtract
[0, 1, 1, 1] = a < b? (SLT)
[1, 1, 0, 0] = Bitwise NOR !(A|B)
[0, 0, 1, 1] = Bitwise XOR A ^ B
[1, 1, 0, 1] = NAND !(A & B)
"""
def alu(bitsA, bitsB, opcode):

    assert len(bitsA) == 32 and len(bitsB) == 32
    ainvert = opcode[0]
    binvert  = opcode[1]
    operation = [opcode[2], opcode[3]]

    # Initial Carry-in for LSB ALU for Bnegate function
    c00 = binvert

    """ 
    Avoided For loop intentionally, handstitched style coding to best represent simple redundant logic of ALU
    """
    r00, c01 = OneBitALU(bitsA[31], bitsB[31], ainvert, binvert, c00, operation, less=0)  # LSB
    r01, c02 = OneBitALU(bitsA[30], bitsB[30], ainvert, binvert, c01, operation, less=0)
    r02, c03 = OneBitALU(bitsA[29], bitsB[29], ainvert, binvert, c02, operation, less=0)
    r03, c04 = OneBitALU(bitsA[28], bitsB[28], ainvert, binvert, c03, operation, less=0)
    r04, c05 = OneBitALU(bitsA[27], bitsB[27], ainvert, binvert, c04, operation, less=0)
    r05, c06 = OneBitALU(bitsA[26], bitsB[26], ainvert, binvert, c05, operation, less=0)
    r06, c07 = OneBitALU(bitsA[25], bitsB[25], ainvert, binvert, c06, operation, less=0)
    r07, c08 = OneBitALU(bitsA[24], bitsB[24], ainvert, binvert, c07, operation, less=0)
    r08, c09 = OneBitALU(bitsA[23], bitsB[23], ainvert, binvert, c08, operation, less=0)
    r09, c10 = OneBitALU(bitsA[22], bitsB[22], ainvert, binvert, c09, operation, less=0)
    r10, c11 = OneBitALU(bitsA[21], bitsB[21], ainvert, binvert, c10, operation, less=0)
    r11, c12 = OneBitALU(bitsA[20], bitsB[20], ainvert, binvert, c11, operation, less=0)
    r12, c13 = OneBitALU(bitsA[19], bitsB[19], ainvert, binvert, c12, operation, less=0)
    r13, c14 = OneBitALU(bitsA[18], bitsB[18], ainvert, binvert, c13, operation, less=0)
    r14, c15 = OneBitALU(bitsA[17], bitsB[17], ainvert, binvert, c14, operation, less=0)
    r15, c16 = OneBitALU(bitsA[16], bitsB[16], ainvert, binvert, c15, operation, less=0)
    r16, c17 = OneBitALU(bitsA[15], bitsB[15], ainvert, binvert, c16, operation, less=0)
    r17, c18 = OneBitALU(bitsA[14], bitsB[14], ainvert, binvert, c17, operation, less=0)
    r18, c19 = OneBitALU(bitsA[13], bitsB[13], ainvert, binvert, c18, operation, less=0)
    r19, c20 = OneBitALU(bitsA[12], bitsB[12], ainvert, binvert, c19, operation, less=0)
    r20, c21 = OneBitALU(bitsA[11], bitsB[11], ainvert, binvert, c20, operation, less=0)
    r21, c22 = OneBitALU(bitsA[10], bitsB[10], ainvert, binvert, c21, operation, less=0)
    r22, c23 = OneBitALU(bitsA[ 9], bitsB[ 9], ainvert, binvert, c22, operation, less=0)
    r23, c24 = OneBitALU(bitsA[ 8], bitsB[ 8], ainvert, binvert, c23, operation, less=0)
    r24, c25 = OneBitALU(bitsA[ 7], bitsB[ 7], ainvert, binvert, c24, operation, less=0)
    r25, c26 = OneBitALU(bitsA[ 6], bitsB[ 6], ainvert, binvert, c25, operation, less=0)
    r26, c27 = OneBitALU(bitsA[ 5], bitsB[ 5], ainvert, binvert, c26, operation, less=0)
    r27, c28 = OneBitALU(bitsA[ 4], bitsB[ 4], ainvert, binvert, c27, operation, less=0)
    r28, c29 = OneBitALU(bitsA[ 3], bitsB[ 3], ainvert, binvert, c28, operation, less=0)
    r29, c30 = OneBitALU(bitsA[ 2], bitsB[ 2], ainvert, binvert, c29, operation, less=0)
    r30, c31 = OneBitALU(bitsA[ 1], bitsB[ 1], ainvert, binvert, c30, operation, less=0)

    # MSB ALU, V is the overflow flag
    r31, c32, V, set_bit = MSBOneBitALU(bitsA[0], bitsB[0], ainvert, binvert, c31, operation, less=0)

    # Set_bit redirected to LSB result
    if operation == [1, 1] and binvert == 1:
        r00 = set_bit
    

    # Other Flags:

    # Negative sign flag taken directly from MSB result
    N = r31      
    # zero flag without loops: Z=1 if all result bits are 0
    Z = 1 if (r00|r01|r02|r03|r04|r05|r06|r07|
              r08|r09|r10|r11|r12|r13|r14|r15|
              r16|r17|r18|r19|r20|r21|r22|r23|
              r24|r25|r26|r27|r28|r29|r30|r31) == 0 else 0
    # carry out from MSB (no-borrow for SUB)
    C = c32                          

    result = [
        r31,r30,r29,r28,r27,r26,r25,r24,
        r23,r22,r21,r20,r19,r18,r17,r16,
        r15,r14,r13,r12,r11,r10,r09,r08,
        r07,r06,r05,r04,r03,r02,r01,r00
    ]

    flags = [N, Z, C, V]

    return (result, flags)



   


    

    
   
    


    