"""
Twos Complement: is the binary representation of a negative number. Used to subtract from one number from another by converting the 2nd number into its negative sign equivalent. If the input number is positive, only its binary representation is necessary to convert. If the input number is negative, it must be represented as its twos-complment. Note: the MSB must be 1 to signify the number is a negative. 

Questions: 
1. What if the input INT is outside of the 32 bit range? Do we reject?
    * truncate or clamp bit array, and return overflow flag 1
2. Notes say to support multiple bit-widths. Can we just stick to 32 bit width regardless of size?
    * will stick to fixed width. Some requirements contradict each other, will not support multiple bit widths
3. are we replicating the int parsing process from Compiler view or from CPU view? 

two_complement() Strategy:
1. Check if value is in range. 
    * if out of range: set over flow flag, truncate to 32 bits and return or clamp to max or min rep.
    else: continue
2. Check sign of int
    * if negative: convert to two's_complement()
    * if Positive, convert_to_binary()
3. converting to twos_complement()
    * take absval = absolute_value(int), and bin_array = convert_to_binary(absval)
    * ones_complement_flip_bits(bin_array)
    * add_one(bin_array)
    * check overflow
        * if overflow: flag
        else return set
4. convert_to_bin():
    * reference character to 8bit binary table, return 8-bit binary list
        * process: binary_rep = [8-bit] * 10^n + [8-bit] * 10^n-1 * ... * [8-bit] * 10 ^ 1
            * 
    * mini_MPU()
        * calls mini_ALU()
5. convert_to_hex(binary_rep):
6. prettyprint():

"""
MAX_INT = 2147483647
MIN_INT = -2147483648
digit_to_bin_rep = {
    0: [0,0,0,0,0,0,0,0], 1: [0,0,0,0,0,0,0,1], 2: [0,0,0,0,0,0,1,0], 3: [0,0,0,0,0,0,1,1], 4: [0,0,0,0,0,1,0,0],
    5: [0,0,0,0,0,1,0,1], 6: [0,0,0,0,0,1,1,0], 7: [0,0,0,0,0,1,1,1], 8: [0,0,0,0,1,0,0,0], 9: [0,0,0,0,1,0,0,1]
}

def twos_complement(num: int):
    overflow_flag = False
    binary_vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    hex_string = ""

    if num > MAX_INT or num < MIN_INT: overflow_flag = True

    return (binary_vector, hex_string, overflow_flag)

def add32(a, b):
    """
    32-bit ripple-carry adder.
    Inputs: lists of 0/1 (any length ≤ 32). MSB at index 0.
    Pads to 32 bits with leading zeros. Returns 32-bit list.
    No arithmetic operators used.
    """
    # copy inputs (avoid concatenation)
    aa = list(a)
    bb = list(b)

    # pad to 32 with leading zeros (no +, no subtraction)
    while len(aa) < 32:
        aa.insert(0, 0)
    while len(bb) < 32:
        bb.insert(0, 0)
    # if longer than 32, keep only the least-significant 32 bits
    if len(aa) > 32:
        aa = aa[-32:]
    if len(bb) > 32:
        bb = bb[-32:]

    out = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    carry = False

    # from LSB to MSB
    for i in reversed(range(32)):
        ai = bool(aa[i])
        bi = bool(bb[i])

        # full-adder with booleans
        xor_ab = (ai != bi)
        sum_bit = (xor_ab != carry)
        carry = (ai and bi) or (carry and xor_ab)

        out[i] = 1 if sum_bit else 0

    # overflow (final carry) dropped to keep 32 bits
    return out

if __name__ == "__main__":
    result = twos_complement(2147483648)
    print(result)
    binrep1 = digit_to_bin_rep[8]
    binrep2 = digit_to_bin_rep[8]
    print(binrep1)
    sum = add32(binrep1, binrep2)
    print(sum)
    newSum = add32(sum, sum)
    print(newSum)
    

