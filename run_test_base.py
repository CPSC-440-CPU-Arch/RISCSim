#!/usr/bin/env python3
"""
Simple script to run the test_base.hex program using the RISC-V CPU simulator.

This demonstrates how to:
1. Create a CPU instance
2. Load a program from a .hex file
3. Execute the program
4. Inspect results
"""

from riscsim.cpu.cpu import CPU

def main():
    print("=" * 60)
    print("RISC-V CPU Simulator - Running test_base.hex")
    print("=" * 60)

    # Create CPU instance with sufficient memory
    # 128KB to accommodate data region at 0x00010000
    cpu = CPU(memory_size=131072)

    # Load the test_base program
    print("\n📂 Loading program: tests/programs/test_base.hex")
    cpu.load_program('tests/programs/test_base.hex')

    print("\n▶️  Executing program...")
    print("-" * 60)

    # Run the program (max 100 cycles to prevent infinite loops)
    result = cpu.run(max_cycles=100)

    print("\n✅ Execution Complete!")
    print("=" * 60)

    # Display execution statistics
    print(f"\n📊 Execution Statistics:")
    print(f"   Instructions executed: {result.instructions}")
    print(f"   Cycles: {result.cycles}")
    print(f"   CPI (Cycles Per Instruction): {result.cycles / result.instructions:.2f}")
    print(f"   Halt reason: {result.halt_reason}")

    # Display register state
    print(f"\n📝 Final Register State:")
    print(cpu.dump_registers())

    # Verify expected results
    print(f"\n🔍 Verification:")
    print(f"   x1 = {cpu.get_register(1):10d} (expected: 5)")
    print(f"   x2 = {cpu.get_register(2):10d} (expected: 10)")
    print(f"   x3 = {cpu.get_register(3):10d} (expected: 15)")
    print(f"   x4 = {cpu.get_register(4):10d} (expected: 15)")
    print(f"   x5 = 0x{cpu.get_register(5):08X} (expected: 0x00010000)")
    print(f"   x6 = {cpu.get_register(6):10d} (expected: 2)")

    # Check memory
    mem_value = cpu.get_memory_word(0x00010000)
    print(f"\n💾 Memory at 0x00010000: {mem_value} (expected: 15)")

    # Validation
    print("\n" + "=" * 60)
    if (cpu.get_register(1) == 5 and
        cpu.get_register(2) == 10 and
        cpu.get_register(3) == 15 and
        cpu.get_register(4) == 15 and
        cpu.get_register(5) == 0x00010000 and
        cpu.get_register(6) == 2 and
        mem_value == 15):
        print("✅ ALL CHECKS PASSED! Program executed correctly.")
    else:
        print("❌ VERIFICATION FAILED! Check register values above.")
    print("=" * 60)

if __name__ == '__main__':
    main()
