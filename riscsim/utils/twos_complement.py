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
from riscsim.utils.bit_utils import *

MAX_INT = 2147483647
MIN_INT = -2147483648
digit_to_32bin = {
    0: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
    1: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1], 
    2: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0], 
    3: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1], 
    4: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
    5: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1], 
    6: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0], 
    7: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1], 
    8: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0], 
    9: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1]
}

def twos_complement(num: int):
    overflow_flag = False
    binary_vector = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    hex_string = ""

    if num > MAX_INT or num < MIN_INT: overflow_flag = True

    return (binary_vector, hex_string, overflow_flag)

def add32(a, b):
    # copy inputs (avoid concatenation)
    aa = list(a)
    bb = list(b)
    out = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
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

def mul32(multiplicand: list, multiplier: list):
    """
    Multiply two 32-bit numbers using shift-add algorithm.

    Args:
        multiplicand: 32-bit array (MSB at index 0)
        multiplier: 32-bit array (MSB at index 0)

    Returns:
        64-bit product as list (MSB at index 0)
        [high 32 bits][low 32 bits]
    """
    # Initialize 64-bit product to zero
    product_lo = [0] * 32
    product_hi = [0] * 32

    # Shift-add multiplication
    for i in range(32):
        # Check multiplier bit from LSB (index 31) to MSB (index 0)
        bit_index = 31 - i
        if multiplier[bit_index] == 1:
            # Add multiplicand shifted left by i positions

            if i == 0:
                # No shift needed, add to low part
                product_lo = add32(product_lo, multiplicand)
            elif i < 32:
                # Shift multiplicand left by i positions
                # Lower part: bits from position i onwards, padded with i zeros on right
                shifted_lo = multiplicand[i:] + [0] * i

                # Upper part: top i bits that were shifted out
                # These appear at the bottom (LSB side) of the high word
                shifted_hi = [0] * (32 - i) + multiplicand[0:i]

                # Add shifted values to product
                # First add to low part
                old_product_lo = list(product_lo)
                product_lo = add32(product_lo, shifted_lo)

                # Check for carry from low to high
                # Carry occurs if result wrapped around (became smaller)
                carry = False
                for j in range(32):
                    if old_product_lo[j] == 1 and shifted_lo[j] == 1:
                        carry = True
                        break
                    elif old_product_lo[j] == 1 or shifted_lo[j] == 1:
                        if product_lo[j] == 0:
                            carry = True
                            break

                # Add to high part
                product_hi = add32(product_hi, shifted_hi)
                if carry:
                    # Add 1 to high part for carry
                    carry_bit = [0] * 31 + [1]
                    product_hi = add32(product_hi, carry_bit)
            else:
                # Shift >= 32, add to high part only
                shift_amount = i - 32
                if shift_amount == 0:
                    product_hi = add32(product_hi, multiplicand)
                else:
                    shifted = multiplicand[shift_amount:] + [0] * shift_amount
                    product_hi = add32(product_hi, shifted)

    # Return 64-bit product
    return product_hi + product_lo

if __name__ == "__main__":
    result = twos_complement(2147483648)
    print(result)
    binrep1 = digit_to_32bin[8]
    binrep2 = digit_to_32bin[8]
    print(binrep1)
    sum = add32(binrep1, binrep2)
    print(sum)
    newSum = add32(sum, sum)
    print(newSum)
    

