def invert(a):
    if a == 1:
        return 0
    if a == 0:
        return 1

def carryOut(a, b, carryIn):
    return (a and carryIn) or (b and carryIn) or (a and b)

def OneBitALU(a, b, ainvert, binvert, carryIn, operation):
    if ainvert: a = invert(a)
    if binvert: b = invert(b)
        


if __name__ == "__main__":
    output = carryOut(1, 1, 1)
    print(output)