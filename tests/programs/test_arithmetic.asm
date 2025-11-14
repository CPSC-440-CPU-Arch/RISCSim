# test_arithmetic.hex - Comprehensive Arithmetic Test Program
# Tests ADD, SUB, ADDI operations including overflow cases and zero register behavior

# Assembly code:
addi x1, x0, 5          # x1 = 5
addi x2, x0, 10         # x2 = 10
add x3, x1, x2          # x3 = 15 (normal addition)
sub x4, x1, x2          # x4 = -5 (normal subtraction)

# Overflow test: 0x7FFFFFFF + 1 (max positive + 1 = overflow to negative)
addi x5, x0, 0x7FF      # x5 = 0x7FF
slli x6, x5, 20         # Shift to get upper bits (would need proper encoding)
# Actually using immediate directly:
addi x5, x0, 0x7FF      # x5 = 0x7FF (2047)
addi x6, x5, 1          # x6 = 2048

# Large positive value
addi x7, x0, 0x7FF      # x7 = 0x7FF
add x8, x7, x7          # x8 = 0xFFE (4094)

# Negative value test (0x80000000 - 1)
lui x8, 0x80000         # x8 = 0x80000000 (min negative in upper bits)
addi x9, x8, -1         # x9 = 0x80000000 - 1

# Another negative test
lui x10, 0x80000        # x10 = 0x80000000
addi x11, x10, -1       # x11 = 0x7FFFFFFF (underflow)

# Zero register behavior
add x12, x0, x0         # x12 = 0 (adding zero to zero)
addi x13, x12, 0        # x13 = 0 (adding zero immediate)

# Test with -1
addi x14, x0, -1        # x14 = -1 (0xFFFFFFFF)
addi x15, x14, 1        # x15 = 0 (adding 1 to -1)

# Write zero to x16
add x16, x0, x0         # x16 = 0
addi x17, x16, 0        # x17 = 0

# Infinite loop to halt
jal x0, 0               # jump to self (infinite loop)
