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


# def overFLowDetection(binvert, b, carryOut, )

def OneBitALU(a, b, ainvert, binvert, carry_in, operation):
    if ainvert: a = invert(a)
    if binvert: b = invert(b)

    AND_OUT = a and b
    OR_OUT = a or b
    SUM_BIT, COUT = oneBitAdder(a, b, carry_in)

    if operation == [0,0]:
        result = AND_OUT
    elif operation == [0,1]:
        result = OR_OUT
    elif operation == [1,0]:
        result = SUM_BIT
    else:
        raise ValueError("Invalid operation control bits")
    return result, COUT
        

if __name__ == "__main__":
    result = OneBitALU(1, 1, 0, 0, 0, [1, 0])
    print(result)