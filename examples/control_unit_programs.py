"""
Example Programs for Control Unit FSM Demonstration

This module demonstrates complete programs running on the Control Unit FSM,
showing cycle-accurate execution of multi-instruction sequences.

Examples include:
- Fibonacci sequence calculation
- Factorial computation
- Floating-point calculations
- Mixed integer and floating-point operations
"""

from riscsim.cpu.control_unit import ControlUnit
from riscsim.cpu.control_signals import ALU_OP_ADD, ALU_OP_SUB, SH_OP_SLL


def int_to_5bit(value):
    """Convert integer to 5-bit array (MSB-first)."""
    return [(value >> (4 - i)) & 1 for i in range(5)]


def int_to_32bit(value):
    """Convert integer to 32-bit array (MSB-first)."""
    if value < 0:
        value = (1 << 32) + value
    return [(value >> (31 - i)) & 1 for i in range(32)]


def bits_to_int(bits):
    """Convert bit array (MSB-first) to integer."""
    value = sum(bit << (len(bits) - 1 - i) for i, bit in enumerate(bits))
    # Handle signed 32-bit
    if len(bits) == 32 and bits[0] == 1:  # MSB is sign bit
        value -= (1 << 32)
    return value


def fibonacci_program(n=10):
    """
    Calculate the nth Fibonacci number using the Control Unit.
    
    Algorithm:
        fib(0) = 0
        fib(1) = 1
        fib(n) = fib(n-1) + fib(n-2)
    
    Implementation:
        r1 = 0         # fib(i-2)
        r2 = 1         # fib(i-1)
        r3 = n         # counter
        loop:
            r4 = r1 + r2   # fib(i)
            r1 = r2        # shift: fib(i-2) = fib(i-1)
            r2 = r4        # shift: fib(i-1) = fib(i)
            r3 = r3 - 1    # decrement counter
            if r3 > 0 goto loop
        return r2
    
    Args:
        n: Which Fibonacci number to calculate (default 10)
    
    Returns:
        Dictionary with:
            - 'result': The nth Fibonacci number
            - 'cycles': Total cycles taken
            - 'instructions': Number of instructions executed
            - 'trace': Execution trace
    """
    cu = ControlUnit()
    
    # Initialize registers
    cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(0))   # r1 = 0
    cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(1))   # r2 = 1
    cu.register_file.write_int_reg(int_to_5bit(3), int_to_32bit(n-1)) # r3 = n-1 (iterations)
    
    print(f"\n{'='*60}")
    print(f"Fibonacci Program: Calculate fib({n})")
    print(f"{'='*60}")
    print(f"Initial state:")
    print(f"  r1 (fib(i-2)) = 0")
    print(f"  r2 (fib(i-1)) = 1")
    print(f"  r3 (counter)  = {n-1}")
    print(f"\nExecuting loop {n-1} times...")
    
    # Execute the loop
    for i in range(n-1):
        # r4 = r1 + r2 (calculate next Fibonacci number)
        cu.execute_instruction('ALU', ALU_OP_ADD,
                              int_to_5bit(1), int_to_5bit(2), int_to_5bit(4))
        
        # r1 = r2 (shift fib(i-2) = fib(i-1))
        cu.execute_instruction('ALU', ALU_OP_ADD,
                              int_to_5bit(2), int_to_5bit(0), int_to_5bit(1))
        
        # r2 = r4 (shift fib(i-1) = fib(i))
        cu.execute_instruction('ALU', ALU_OP_ADD,
                              int_to_5bit(4), int_to_5bit(0), int_to_5bit(2))
        
        # r3 = r3 - 1 (decrement counter)
        cu.execute_instruction('ALU', ALU_OP_SUB,
                              int_to_5bit(3), int_to_5bit(0), int_to_5bit(3))
        
        if (i + 1) % 3 == 0 or i == n-3:
            r2_bits = cu.register_file.read_int_reg(int_to_5bit(2))
            r2_val = bits_to_int(r2_bits)
            print(f"  Iteration {i+1}: fib = {r2_val}")
    
    # Get result
    result_bits = cu.register_file.read_int_reg(int_to_5bit(2))
    result = bits_to_int(result_bits)
    
    # Get performance stats
    stats = cu.get_performance_stats()
    
    print(f"\nResult: fib({n}) = {result}")
    print(f"\nPerformance:")
    print(f"  Total Cycles:     {stats['total_cycles']}")
    print(f"  Instructions:     {stats['instruction_count']}")
    print(f"  CPI:              {stats['cpi']:.2f}")
    print(f"  ALU Utilization:  {stats['alu_utilization']:.1f}%")
    print(f"{'='*60}\n")
    
    return {
        'result': result,
        'cycles': stats['total_cycles'],
        'instructions': stats['instruction_count'],
        'cpi': stats['cpi'],
        'stats': stats
    }


def factorial_program(n=5):
    """
    Calculate n! (factorial) using the Control Unit.
    
    Algorithm:
        result = 1
        for i from 1 to n:
            result = result * i
    
    Implementation:
        r1 = 1         # result accumulator
        r2 = 1         # current multiplier
        r3 = n         # target value
        loop:
            r1 = r1 * r2   # result *= i (using MDU)
            r2 = r2 + 1    # i++
            if r2 <= r3 goto loop
        return r1
    
    Args:
        n: Calculate n! (default 5)
    
    Returns:
        Dictionary with result, cycles, and performance stats
    """
    cu = ControlUnit()
    
    # Initialize registers
    cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(1))   # r1 = 1 (result)
    cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(1))   # r2 = 1 (counter)
    cu.register_file.write_int_reg(int_to_5bit(3), int_to_32bit(n))   # r3 = n (target)
    
    print(f"\n{'='*60}")
    print(f"Factorial Program: Calculate {n}!")
    print(f"{'='*60}")
    print(f"Initial state:")
    print(f"  r1 (result)   = 1")
    print(f"  r2 (counter)  = 1")
    print(f"  r3 (target)   = {n}")
    print(f"\nExecuting multiplication loop...")
    
    # Execute the loop
    for i in range(1, n + 1):
        # r1 = r1 * r2 (multiply using MDU)
        cu.execute_instruction('MDU', 'MUL',
                              int_to_5bit(1), int_to_5bit(2), int_to_5bit(1))
        
        # r2 = r2 + 1 (increment counter)
        cu.register_file.write_int_reg(int_to_5bit(4), int_to_32bit(1))  # r4 = 1 (constant)
        cu.execute_instruction('ALU', ALU_OP_ADD,
                              int_to_5bit(2), int_to_5bit(4), int_to_5bit(2))
        
        r1_bits = cu.register_file.read_int_reg(int_to_5bit(1))
        r1_val = bits_to_int(r1_bits)
        print(f"  {i}! = {r1_val}")
    
    # Get result
    result_bits = cu.register_file.read_int_reg(int_to_5bit(1))
    result = bits_to_int(result_bits)
    
    # Get performance stats
    stats = cu.get_performance_stats()
    
    print(f"\nResult: {n}! = {result}")
    print(f"\nPerformance:")
    print(f"  Total Cycles:     {stats['total_cycles']}")
    print(f"  Instructions:     {stats['instruction_count']}")
    print(f"  CPI:              {stats['cpi']:.2f}")
    print(f"  ALU Utilization:  {stats['alu_utilization']:.1f}%")
    print(f"  MDU Utilization:  {stats['mdu_utilization']:.1f}%")
    print(f"{'='*60}\n")
    
    return {
        'result': result,
        'cycles': stats['total_cycles'],
        'instructions': stats['instruction_count'],
        'cpi': stats['cpi'],
        'stats': stats
    }


def floating_point_program():
    """
    Demonstrate floating-point calculations using the Control Unit FPU.
    
    Calculates: result = (a + b) * (c + d)
    Where: a=1.5, b=2.5, c=3.0, d=4.0
    Expected: (1.5 + 2.5) * (3.0 + 4.0) = 4.0 * 7.0 = 28.0
    
    Returns:
        Dictionary with result, cycles, and performance stats
    """
    cu = ControlUnit()
    
    # IEEE 754 single precision values
    fp_1_5 = int_to_32bit(0x3FC00000)  # 1.5
    fp_2_5 = int_to_32bit(0x40200000)  # 2.5
    fp_3_0 = int_to_32bit(0x40400000)  # 3.0
    fp_4_0 = int_to_32bit(0x40800000)  # 4.0
    
    # Initialize FP registers
    cu.register_file.write_fp_reg(int_to_5bit(1), fp_1_5)  # f1 = 1.5
    cu.register_file.write_fp_reg(int_to_5bit(2), fp_2_5)  # f2 = 2.5
    cu.register_file.write_fp_reg(int_to_5bit(3), fp_3_0)  # f3 = 3.0
    cu.register_file.write_fp_reg(int_to_5bit(4), fp_4_0)  # f4 = 4.0
    
    print(f"\n{'='*60}")
    print(f"Floating-Point Program")
    print(f"{'='*60}")
    print(f"Calculate: (1.5 + 2.5) * (3.0 + 4.0)")
    print(f"\nStep 1: f5 = f1 + f2 = 1.5 + 2.5 = 4.0")
    
    # f5 = f1 + f2
    cu.execute_instruction('FPU', 'FADD',
                          int_to_5bit(1), int_to_5bit(2), int_to_5bit(5))
    
    print(f"Step 2: f6 = f3 + f4 = 3.0 + 4.0 = 7.0")
    
    # f6 = f3 + f4
    cu.execute_instruction('FPU', 'FADD',
                          int_to_5bit(3), int_to_5bit(4), int_to_5bit(6))
    
    print(f"Step 3: f7 = f5 * f6 = 4.0 * 7.0 = 28.0")
    
    # f7 = f5 * f6
    cu.execute_instruction('FPU', 'FMUL',
                          int_to_5bit(5), int_to_5bit(6), int_to_5bit(7))
    
    # Get result (extract float value - simplified)
    result_bits = cu.register_file.read_fp_reg(int_to_5bit(7))
    result_int = sum(bit << i for i, bit in enumerate(result_bits))
    
    # Get performance stats
    stats = cu.get_performance_stats()
    
    print(f"\nResult bits: 0x{result_int:08X}")
    print(f"\nPerformance:")
    print(f"  Total Cycles:     {stats['total_cycles']}")
    print(f"  Instructions:     {stats['instruction_count']}")
    print(f"  CPI:              {stats['cpi']:.2f}")
    print(f"  FPU Utilization:  {stats['fpu_utilization']:.1f}%")
    print(f"{'='*60}\n")
    
    return {
        'result_bits': result_int,
        'cycles': stats['total_cycles'],
        'instructions': stats['instruction_count'],
        'cpi': stats['cpi'],
        'stats': stats
    }


def mixed_operations_program():
    """
    Demonstrate mixed integer and floating-point operations.
    
    Performs various operations using all functional units:
    - Integer arithmetic (ALU)
    - Bit shifting (Shifter)
    - Integer multiplication (MDU)
    - Floating-point addition (FPU)
    
    Returns:
        Dictionary with performance stats for all units
    """
    cu = ControlUnit()
    
    print(f"\n{'='*60}")
    print(f"Mixed Operations Program")
    print(f"{'='*60}")
    print(f"Demonstrating all functional units...\n")
    
    # Setup integer values
    cu.register_file.write_int_reg(int_to_5bit(1), int_to_32bit(10))
    cu.register_file.write_int_reg(int_to_5bit(2), int_to_32bit(20))
    
    # Setup FP values
    fp_1_0 = int_to_32bit(0x3F800000)  # 1.0
    fp_2_0 = int_to_32bit(0x40000000)  # 2.0
    cu.register_file.write_fp_reg(int_to_5bit(10), fp_1_0)
    cu.register_file.write_fp_reg(int_to_5bit(11), fp_2_0)
    
    print("Operation 1: ALU - Integer Addition")
    print("  r3 = r1 + r2 = 10 + 20 = 30")
    cu.execute_instruction('ALU', ALU_OP_ADD,
                          int_to_5bit(1), int_to_5bit(2), int_to_5bit(3))
    
    print("\nOperation 2: Shifter - Left Shift")
    print("  r4 = r1 << 2 = 10 << 2 = 40")
    cu.execute_instruction('SHIFTER', SH_OP_SLL,
                          int_to_5bit(1), rd_addr=int_to_5bit(4),
                          shamt=int_to_5bit(2))
    
    print("\nOperation 3: MDU - Integer Multiplication")
    print("  r5 = r1 * r2 = 10 * 20 = 200")
    cu.execute_instruction('MDU', 'MUL',
                          int_to_5bit(1), int_to_5bit(2), int_to_5bit(5))
    
    print("\nOperation 4: FPU - Floating-Point Addition")
    print("  f12 = f10 + f11 = 1.0 + 2.0 = 3.0")
    cu.execute_instruction('FPU', 'FADD',
                          int_to_5bit(10), int_to_5bit(11), int_to_5bit(12))
    
    # Get performance stats
    stats = cu.get_performance_stats()
    
    print(f"\n{'='*60}")
    print("Performance Summary:")
    print(f"{'='*60}")
    cu.print_performance_stats()
    
    return {
        'cycles': stats['total_cycles'],
        'instructions': stats['instruction_count'],
        'cpi': stats['cpi'],
        'stats': stats
    }


def main():
    """Run all example programs."""
    print("\n" + "="*70)
    print(" Control Unit FSM - Example Programs Demonstration")
    print("="*70)
    
    # Run Fibonacci
    fib_result = fibonacci_program(n=10)
    
    # Run Factorial
    fact_result = factorial_program(n=5)
    
    # Run Floating-Point
    fp_result = floating_point_program()
    
    # Run Mixed Operations
    mixed_result = mixed_operations_program()
    
    print("\n" + "="*70)
    print(" All Programs Complete!")
    print("="*70)
    print(f"\nSummary:")
    print(f"  Fibonacci(10):     {fib_result['result']} in {fib_result['cycles']} cycles")
    print(f"  Factorial(5):      {fact_result['result']} in {fact_result['cycles']} cycles")
    print(f"  FP Calculation:    {fp_result['cycles']} cycles")
    print(f"  Mixed Operations:  {mixed_result['cycles']} cycles")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
