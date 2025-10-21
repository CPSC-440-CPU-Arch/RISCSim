"""
Twos Complement: is the binary representation of a negative number. Used to subtract from one number from another by converting the 2nd number into its negative sign equivalent. If the input number is positive, only its binary representation is necessary to convert. If the input number is negative, it must be represented as its twos-complment. Note: the MSB must be 1 to signify the number is a negative. 

Questions: 
1. What if the input INT is outside of the 32 bit range? Do we reject?

Strategy:
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
    * 
4. convert_to_bin():
    * 


"""

def check_sign(num: int):
    if num

"""Function from converting from integer number into 32-bit binary"""
def int_to_bin(num: int):
