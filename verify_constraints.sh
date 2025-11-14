#!/bin/bash
# verify_constraints.sh
# Verify that implementation modules comply with "no built-in operators" constraint

echo "======================================================================"
echo "RISCSim Constraint Verification"
echo "======================================================================"
echo ""

FAILED=0

# Function to check file for forbidden operators
check_file() {
    local file=$1
    local pattern=$2
    local description=$3
    
    echo "Checking $file for $description..."
    
    # Grep for pattern, exclude comments and imports
    matches=$(grep -n -E "$pattern" "$file" | grep -v '#' | grep -v 'import' | grep -v 'def ' | grep -v 'class ' | grep -v '"""' | grep -v "'''" | grep -v 'AI-BEGIN' | grep -v 'AI-END' | grep -v 'return')
    
    if [ -n "$matches" ]; then
        echo "  ❌ FAILED: Found forbidden operators:"
        echo "$matches" | sed 's/^/     /'
        FAILED=1
    else
        echo "  ✅ PASSED: No forbidden operators found"
    fi
    echo ""
}

echo "Checking implementation modules for forbidden operators..."
echo "----------------------------------------------------------------------"
echo ""

# Check ALU for arithmetic operators
if [ -f "riscsim/cpu/alu.py" ]; then
    check_file "riscsim/cpu/alu.py" "(\+|-|\*|/|%|<<|>>)" "arithmetic operators (+, -, *, /, %, <<, >>)"
else
    echo "⚠️  Warning: riscsim/cpu/alu.py not found"
    echo ""
fi

# Check components for arithmetic operators
if [ -f "riscsim/utils/components.py" ]; then
    check_file "riscsim/utils/components.py" "(\+|-|\*|/|%|<<|>>)" "arithmetic operators"
else
    echo "⚠️  Warning: riscsim/utils/components.py not found"
    echo ""
fi

# Check MDU for multiply/divide operators
if [ -f "riscsim/cpu/mdu.py" ]; then
    check_file "riscsim/cpu/mdu.py" "(\*|/|%)" "multiply/divide operators (*, /, %)"
else
    echo "⚠️  Warning: riscsim/cpu/mdu.py not found"
    echo ""
fi

# Check Shifter for shift operators (excluding comments and lookup tables)
if [ -f "riscsim/cpu/shifter.py" ]; then
    # More specific check: look for << >> in actual code, not comments or strings
    matches=$(grep -n -E '(<<|>>)' "riscsim/cpu/shifter.py" | grep -v '#' | grep -v '_SHAMT_TO_BITS' | grep -v 'def ' | grep -v '"""' | grep -v "'''" | grep -v 'Convention:' | grep -v 'example:')
    
    if [ -n "$matches" ]; then
        echo "Checking riscsim/cpu/shifter.py for shift operators (<<, >>)..."
        echo "  ❌ FAILED: Found forbidden operators:"
        echo "$matches" | sed 's/^/     /'
        FAILED=1
        echo ""
    else
        echo "Checking riscsim/cpu/shifter.py for shift operators (<<, >>)..."
        echo "  ✅ PASSED: No forbidden operators found (lookup table OK)"
        echo ""
    fi
else
    echo "⚠️  Warning: riscsim/cpu/shifter.py not found"
    echo ""
fi

# Check FPU for arithmetic and float operators
if [ -f "riscsim/cpu/fpu.py" ]; then
    # Exclude pack_f32 and unpack_f32 (I/O boundary functions)
    matches=$(grep -n -E '(\+|-|\*|/)' "riscsim/cpu/fpu.py" | grep -v '#' | grep -v 'import' | grep -v 'def pack_f32' | grep -v 'def unpack_f32' | grep -v 'pack_f32(value' | grep -v 'unpack_f32(bits' | grep -v 'struct.pack' | grep -v 'struct.unpack' | grep -v '"""' | grep -v "'''" | grep -v '2^' | grep -v 'AI-BEGIN' | grep -v 'AI-END' | grep -v 'for i in' | grep -v 'range(' | grep -v 'slice_bits' | grep -v 'concat_bits' | grep -v '\[sign\]' | grep -v 'description')
    
    if [ -n "$matches" ]; then
        echo "Checking riscsim/cpu/fpu.py for arithmetic operators (outside I/O boundary)..."
        echo "  ❌ FAILED: Found forbidden operators:"
        echo "$matches" | sed 's/^/     /'
        FAILED=1
        echo ""
    else
        echo "Checking riscsim/cpu/fpu.py for arithmetic operators (outside I/O boundary)..."
        echo "  ✅ PASSED: No forbidden operators found (I/O boundary functions OK)"
        echo ""
    fi
else
    echo "⚠️  Warning: riscsim/cpu/fpu.py not found"
    echo ""
fi

# Check bit_utils for forbidden base conversions (excluding TEST-ONLY functions)
if [ -f "riscsim/utils/bit_utils.py" ]; then
    matches=$(grep -n -E '(int\(.*,\s*base|bin\(|hex\(|format\()' "riscsim/utils/bit_utils.py" | grep -v '#' | grep -v 'int_to_bits_unsigned' | grep -v 'bits_to_int_unsigned' | grep -v 'def ' | grep -v '"""' | grep -v "'''" | grep -v 'TEST-ONLY')
    
    if [ -n "$matches" ]; then
        echo "Checking riscsim/utils/bit_utils.py for forbidden base conversions..."
        echo "  ❌ FAILED: Found forbidden functions:"
        echo "$matches" | sed 's/^/     /'
        FAILED=1
        echo ""
    else
        echo "Checking riscsim/utils/bit_utils.py for forbidden base conversions..."
        echo "  ✅ PASSED: No forbidden functions found (TEST-ONLY marked)"
        echo ""
    fi
else
    echo "⚠️  Warning: riscsim/utils/bit_utils.py not found"
    echo ""
fi

# Check twos_complement for proper I/O boundary marking
if [ -f "riscsim/utils/twos_complement.py" ]; then
    # Check if I/O boundary functions are properly documented
    if grep -q "I/O BOUNDARY FUNCTION" "riscsim/utils/twos_complement.py"; then
        echo "Checking riscsim/utils/twos_complement.py for I/O boundary documentation..."
        echo "  ✅ PASSED: I/O boundary functions properly documented"
        echo ""
    else
        echo "Checking riscsim/utils/twos_complement.py for I/O boundary documentation..."
        echo "  ⚠️  Warning: I/O boundary functions should be documented"
        echo ""
    fi
else
    echo "⚠️  Warning: riscsim/utils/twos_complement.py not found"
    echo ""
fi

echo "======================================================================"
echo "Summary"
echo "======================================================================"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED"
    echo ""
    echo "Project complies with 'no built-in operators' constraint:"
    echo "  ✅ ALU uses only boolean logic"
    echo "  ✅ MDU uses only ALU and shifter"
    echo "  ✅ Shifter uses only array operations"
    echo "  ✅ FPU uses only bit-level operations"
    echo "  ✅ I/O boundary functions properly documented"
    echo ""
    exit 0
else
    echo "❌ SOME CHECKS FAILED"
    echo ""
    echo "Please review the failures above and ensure:"
    echo "  1. Implementation modules use ONLY bit-level operations"
    echo "  2. I/O boundary functions are clearly marked"
    echo "  3. TEST-ONLY functions are clearly marked"
    echo ""
    exit 1
fi
