"""
Notes from appendix A:

A single carry out of the LSB (result0) can ripple all the way through the adder. Why its called a ripple carry adder. 

Subtraction is the same as adding the negative version of an operand
    * Ones Complement (invert b)
    * Add one to LSB
    * To invert each bit, we simply add a 2:1 multiplexor that chooses between b and !b
    * the added multiplexor gives the option of b or its inverted value, depending on Binvert, but this is the only step in negating a two's complement number. 
    Notice that the LSB still has a CarryIn signal even though its unnecessary for addtion. 
we also wish to add a NOR function !(a or b) = !a and !b
    * just need to add !a, since we have !b already

operations:
add,
subtract,
and
or
less than (SLT)

slt:
    operations produces 1 if rs1 < rs2 and 0 otherwise.
    * slt will set all but the LSB to 0
    * need to expand the three-input multiplexor to add an input for the slt result. We callthat new input less and use it only for slt
    figure A.5.10

    * we must connect 0 to the Less input for the upper 31 bits of the ALU, since those bits are always set to 0. 



"""

def invert(a):
    if a == 1:
        return 0
    if a == 0:
        return 1

def carryOut(a, b, carry_in):
    return (a and carry_in) or (b and carry_in) or (a and b)

def oneBitAdder(a, b, carry_in):
    sum = (a ^ b) ^ carry_in
    carry_out = carryOut(a, b, carry_in)
    return [sum, carry_out]


def OneBitALU(a, b, ainvert, binvert, carry_in, operation, less=0):

    if ainvert: a = invert(a)
    if binvert: b = invert(b)

    and_out = a and b
    or_out = a or b
    sum_bit, carry_out = oneBitAdder(a, b, carry_in)

    if operation == [0,0]:
        result = and_out
    elif operation == [0,1]:
        result = or_out
    elif operation == [1,0]:
        result = sum_bit
    elif operation == [1, 1]:
        result = less
    else:
        raise ValueError("Invalid operation control bits")
    return [result, carry_out]

def overFLowDetection(carry_in, carry_out):
    return carry_in ^ carry_out


def MSBOneBitALU(a, b, ainvert, binvert, carry_in, operation, less=0):
    if ainvert: a = invert(a)
    if binvert: b = invert(b)

    and_out = a and b
    or_out = a or b
    sum_bit, carry_out = oneBitAdder(a, b, carry_in)

    overflow_flag = overFLowDetection(carry_in, carry_out)
    set_bit = sum_bit ^ overflow_flag

    if operation == [0,0]:
        result = and_out
    elif operation == [0,1]:
        result = or_out
    elif operation == [1,0]:
        result = sum_bit
    elif operation == [1, 1]:
        result = 0
    else:
        raise ValueError("Invalid operation control bits")

    return [result, carry_out, overflow_flag, set_bit]
    


if __name__ == "__main__":
    result = OneBitALU(1, 1, 1, 0, 0, [1, 0])
    print(result)


