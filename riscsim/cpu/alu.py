from riscsim.utils.components import OneBitALU, MSBOneBitALU


def ALU(a, b, opcode):
    ainvert = opcode[0]
    binvert = opcode[1]
    operation = [opcode[2], opcode[3]]

    lsb_carry_in = 1 if binvert else 0
    lsb_less = 0
    # lsb_less = set_bit if operation == [1, 1]
    
    lsb_result, lsb_carry_out = OneBitALU(a[4], b[4], ainvert, binvert, lsb_carry_in, operation, lsb_less)
    result_01, carry_out_01 = OneBitALU(a[3], b[3], ainvert, binvert,lsb_carry_out, operation)
    result_02, carry_out_02 = OneBitALU(a[2], b[2], ainvert, binvert, carry_out_01, operation)
    result_03, carry_out_03 = OneBitALU(a[1], b[1], ainvert, binvert, carry_out_02, operation)
    msb_result, carry_out_04, overflow_flag, set_bit = MSBOneBitALU(a[0], b[0], ainvert, binvert, carry_out_03, operation)

    result = [msb_result, result_03, result_02, result_01, lsb_result]

    return result


if __name__ == "__main__":
    result = ALU([0,0,0,0,1], [0,0,1,1,1], [0,0,1,0])
    print(result)


    

    
   
    


    