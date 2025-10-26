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
def ALU(a, b, opcode):
    ainvert = opcode[0]
    binvert = opcode[1]
    operation = [opcode[2], opcode[3]]

    lsb_carry_in = binvert
    lsb_less = 0
    # lsb_less = set_bit if operation == [1, 1]
    
    lsb_result, lsb_carry_out = OneBitALU(a[4], b[4], ainvert, binvert, lsb_carry_in, operation, lsb_less)
    result_01, carry_out_01 = OneBitALU(a[3], b[3], ainvert, binvert,lsb_carry_out, operation)
    result_02, carry_out_02 = OneBitALU(a[2], b[2], ainvert, binvert, carry_out_01, operation)
    result_03, carry_out_03 = OneBitALU(a[1], b[1], ainvert, binvert, carry_out_02, operation)
    msb_result, msb_carry_out, overflow_flag, set_bit = MSBOneBitALU(a[0], b[0], ainvert, binvert, carry_out_03, operation)

    
    if operation == [1, 1]:
        lsb_result = set_bit

    result = [msb_result, result_03, result_02, result_01, lsb_result]

    zero = 1 if not(lsb_result or result_01 or result_02 or result_03 or msb_result) else 0
  
    return (result, f"N: {msb_result}, Z: {zero}, C: {msb_carry_out}, V:{overflow_flag}")


if __name__ == "__main__":
    result = ALU([1,1,1,1,0], [0,0,0,1,0], [1,1,0,0])
    print(result)


    

    
   
    


    