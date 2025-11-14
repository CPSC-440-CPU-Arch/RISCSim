# AI-BEGIN
"""
RISC-V Register File implementation.

Implements:
- 32 integer registers (x0-x31) with x0 hardwired to zero
- 32 floating-point registers (f0-f31) for F extension (32-bit)
- FCSR (Floating-Point Control and Status Register)

All values represented as bit arrays (lists of 0/1).
Convention: MSB at index 0, LSB at end.

Usage:
    rf = RegisterFile()

    # Integer registers
    rf.write_int_reg(5, [0]*31 + [1])  # Write 1 to x5
    value = rf.read_int_reg(5)          # Read x5

    # x0 is always zero
    rf.write_int_reg(0, [1]*32)         # Ignored
    zero = rf.read_int_reg(0)           # Returns [0]*32

    # Floating-point registers
    rf.write_fp_reg(10, [1,0,1,0]*8)
    fp_value = rf.read_fp_reg(10)

    # FCSR operations
    rf.set_rounding_mode([0,0,1])       # RTZ mode
    mode = rf.get_rounding_mode()
    rf.set_fflags([1,0,1,0,1])          # Set exception flags
    flags = rf.get_fflags()
"""

from riscsim.utils.bit_utils import slice_bits, set_bit, get_bit, bits_to_int_unsigned


# Constants
XLEN = 32  # Integer register width (RV32)
FLEN = 32  # Floating-point register width (F extension)
FCSR_WIDTH = 8  # FCSR register width
NUM_INT_REGS = 32  # Number of integer registers
NUM_FP_REGS = 32  # Number of floating-point registers

# FCSR bit field positions
# Bits 7-5: frm (rounding mode)
# Bits 4-0: fflags (exception flags)
#   Bit 4: NV (Invalid Operation)
#   Bit 3: DZ (Divide by Zero)
#   Bit 2: OF (Overflow)
#   Bit 1: UF (Underflow)
#   Bit 0: NX (Inexact)


class RegisterFile:
    """
    RISC-V Register File.

    Maintains state for integer registers, floating-point registers,
    and floating-point control/status register.
    """

    def __init__(self):
        """Initialize register file with all registers set to zero."""
        # 32 integer registers (x0-x31), all initialized to zero
        # Each register is XLEN bits (32 bits for RV32)
        self.int_regs = [[0] * XLEN for _ in range(NUM_INT_REGS)]

        # 32 floating-point registers (f0-f31), all initialized to zero
        # Each register is FLEN bits (32 bits for F extension)
        self.fp_regs = [[0] * FLEN for _ in range(NUM_FP_REGS)]

        # FCSR: Floating-Point Control and Status Register (8 bits)
        # Bits 7-5: frm (rounding mode)
        # Bits 4-0: fflags (exception flags: NV, DZ, OF, UF, NX)
        self.fcsr = [0] * FCSR_WIDTH

    # =========================================================================
    # Integer Register Operations
    # =========================================================================

    def read_int_reg(self, reg_num):
        """
        Read integer register x[reg_num].

        Args:
            reg_num: Register number as 5-bit array [0,0,0,0,0] to [1,1,1,1,1]
                     or integer 0-31 for backward compatibility

        Returns:
            32-bit array representing the register value.
            x0 always returns all zeros.

        Raises:
            ValueError: If reg_num is out of range
        """
        # Convert bit array to integer if needed
        if isinstance(reg_num, list):
            if len(reg_num) != 5:
                raise ValueError(
                    f"Register number as bit array must be 5 bits, got {len(reg_num)}"
                )
            reg_num = bits_to_int_unsigned(reg_num)
        
        if not (0 <= reg_num < NUM_INT_REGS):
            raise ValueError(
                f"Invalid integer register number: {reg_num}. "
                f"Must be 0-{NUM_INT_REGS-1}"
            )

        # x0 is hardwired to zero
        if reg_num == 0:
            return [0] * XLEN

        # Return a copy to prevent external modification
        return self.int_regs[reg_num][:]

    def write_int_reg(self, reg_num, value):
        """
        Write to integer register x[reg_num].

        Args:
            reg_num: Register number as 5-bit array [0,0,0,0,0] to [1,1,1,1,1]
                     or integer 0-31 for backward compatibility
            value: 32-bit array to write

        Raises:
            ValueError: If reg_num is out of range or value is wrong width

        Note:
            Writes to x0 are silently ignored (x0 is hardwired to zero).
        """
        # Convert bit array to integer if needed
        if isinstance(reg_num, list):
            if len(reg_num) != 5:
                raise ValueError(
                    f"Register number as bit array must be 5 bits, got {len(reg_num)}"
                )
            reg_num = bits_to_int_unsigned(reg_num)
        
        if not (0 <= reg_num < NUM_INT_REGS):
            raise ValueError(
                f"Invalid integer register number: {reg_num}. "
                f"Must be 0-{NUM_INT_REGS-1}"
            )

        if len(value) != XLEN:
            raise ValueError(
                f"Value must be {XLEN} bits, got {len(value)} bits"
            )

        # Silently ignore writes to x0 (hardwired to zero)
        if reg_num == 0:
            return

        # Store a copy to prevent external modification
        self.int_regs[reg_num] = value[:]

    # =========================================================================
    # Floating-Point Register Operations
    # =========================================================================

    def read_fp_reg(self, reg_num):
        """
        Read floating-point register f[reg_num].

        Args:
            reg_num: Register number as 5-bit array [0,0,0,0,0] to [1,1,1,1,1]
                     or integer 0-31 for backward compatibility

        Returns:
            32-bit array representing the register value.

        Raises:
            ValueError: If reg_num is out of range
        """
        # Convert bit array to integer if needed
        if isinstance(reg_num, list):
            if len(reg_num) != 5:
                raise ValueError(
                    f"Register number as bit array must be 5 bits, got {len(reg_num)}"
                )
            reg_num = bits_to_int_unsigned(reg_num)
        
        if not (0 <= reg_num < NUM_FP_REGS):
            raise ValueError(
                f"Invalid FP register number: {reg_num}. "
                f"Must be 0-{NUM_FP_REGS-1}"
            )

        # Return a copy to prevent external modification
        return self.fp_regs[reg_num][:]

    def write_fp_reg(self, reg_num, value):
        """
        Write to floating-point register f[reg_num].

        Args:
            reg_num: Register number as 5-bit array [0,0,0,0,0] to [1,1,1,1,1]
                     or integer 0-31 for backward compatibility
            value: 32-bit array to write

        Raises:
            ValueError: If reg_num is out of range or value is wrong width
        """
        # Convert bit array to integer if needed
        if isinstance(reg_num, list):
            if len(reg_num) != 5:
                raise ValueError(
                    f"Register number as bit array must be 5 bits, got {len(reg_num)}"
                )
            reg_num = bits_to_int_unsigned(reg_num)
        
        if not (0 <= reg_num < NUM_FP_REGS):
            raise ValueError(
                f"Invalid FP register number: {reg_num}. "
                f"Must be 0-{NUM_FP_REGS-1}"
            )

        if len(value) != FLEN:
            raise ValueError(
                f"Value must be {FLEN} bits, got {len(value)} bits"
            )

        # Store a copy to prevent external modification
        self.fp_regs[reg_num] = value[:]

    # =========================================================================
    # FCSR (Floating-Point Control and Status Register) Operations
    # =========================================================================

    def read_fcsr(self):
        """
        Read the entire FCSR register.

        Returns:
            8-bit array representing FCSR value.
            Bits 7-5: frm (rounding mode)
            Bits 4-0: fflags (exception flags)
        """
        # Return a copy to prevent external modification
        return self.fcsr[:]

    def write_fcsr(self, value):
        """
        Write the entire FCSR register.

        Args:
            value: 8-bit array to write to FCSR

        Raises:
            ValueError: If value is wrong width
        """
        if len(value) != FCSR_WIDTH:
            raise ValueError(
                f"FCSR value must be {FCSR_WIDTH} bits, got {len(value)} bits"
            )

        # Store a copy to prevent external modification
        self.fcsr = value[:]

    def get_rounding_mode(self):
        """
        Get the rounding mode field from FCSR.

        Returns:
            3-bit array representing frm (bits 7-5 of FCSR).

        Rounding modes:
            [0,0,0] = RNE (Round to Nearest, ties to Even)
            [0,0,1] = RTZ (Round Toward Zero)
            [0,1,0] = RDN (Round Down, toward -infinity)
            [0,1,1] = RUP (Round Up, toward +infinity)
            [1,0,0] = RMM (Round to Nearest, ties to Max Magnitude)
        """
        # Extract bits 7-5 (indices 0-2 in MSB-first convention)
        return slice_bits(self.fcsr, 0, 3)

    def set_rounding_mode(self, mode):
        """
        Set the rounding mode field in FCSR.

        Args:
            mode: 3-bit array representing the rounding mode

        Raises:
            ValueError: If mode is not 3 bits
        """
        if len(mode) != 3:
            raise ValueError(
                f"Rounding mode must be 3 bits, got {len(mode)} bits"
            )

        # Set bits 7-5 (indices 0-2)
        for i in range(3):
            self.fcsr[i] = mode[i]

    def get_fflags(self):
        """
        Get the exception flags field from FCSR.

        Returns:
            5-bit array representing fflags (bits 4-0 of FCSR).

        Flags (from MSB to LSB):
            Bit 4: NV (Invalid Operation)
            Bit 3: DZ (Divide by Zero)
            Bit 2: OF (Overflow)
            Bit 1: UF (Underflow)
            Bit 0: NX (Inexact)
        """
        # Extract bits 4-0 (indices 3-7 in MSB-first convention)
        return slice_bits(self.fcsr, 3, 8)

    def set_fflags(self, flags):
        """
        Set the exception flags field in FCSR.

        Args:
            flags: 5-bit array representing the exception flags

        Raises:
            ValueError: If flags is not 5 bits
        """
        if len(flags) != 5:
            raise ValueError(
                f"Exception flags must be 5 bits, got {len(flags)} bits"
            )

        # Set bits 4-0 (indices 3-7)
        for i in range(5):
            self.fcsr[i + 3] = flags[i]

    def set_flag_nv(self, value):
        """
        Set the NV (Invalid Operation) flag.

        Args:
            value: 0 or 1
        """
        self.fcsr[3] = value  # Bit 4 of FCSR (index 3 in MSB-first)

    def set_flag_dz(self, value):
        """
        Set the DZ (Divide by Zero) flag.

        Args:
            value: 0 or 1
        """
        self.fcsr[4] = value  # Bit 3 of FCSR (index 4 in MSB-first)

    def set_flag_of(self, value):
        """
        Set the OF (Overflow) flag.

        Args:
            value: 0 or 1
        """
        self.fcsr[5] = value  # Bit 2 of FCSR (index 5 in MSB-first)

    def set_flag_uf(self, value):
        """
        Set the UF (Underflow) flag.

        Args:
            value: 0 or 1
        """
        self.fcsr[6] = value  # Bit 1 of FCSR (index 6 in MSB-first)

    def set_flag_nx(self, value):
        """
        Set the NX (Inexact) flag.

        Args:
            value: 0 or 1
        """
        self.fcsr[7] = value  # Bit 0 of FCSR (index 7 in MSB-first)

    def get_flag_nv(self):
        """Get the NV (Invalid Operation) flag (0 or 1)."""
        return self.fcsr[3]

    def get_flag_dz(self):
        """Get the DZ (Divide by Zero) flag (0 or 1)."""
        return self.fcsr[4]

    def get_flag_of(self):
        """Get the OF (Overflow) flag (0 or 1)."""
        return self.fcsr[5]

    def get_flag_uf(self):
        """Get the UF (Underflow) flag (0 or 1)."""
        return self.fcsr[6]

    def get_flag_nx(self):
        """Get the NX (Inexact) flag (0 or 1)."""
        return self.fcsr[7]


# =============================================================================
# Control Signal Integration
# =============================================================================

def register_with_control(rf, signals, write_data=None):
    """
    Perform register file operations using control signals.

    This function integrates the RegisterFile with the Control Unit by
    using control signals to determine read/write operations.

    Args:
        rf: RegisterFile instance
        signals: ControlSignals instance with:
            - rf_we: Write enable (1 = write, 0 = no write)
            - rf_waddr: Write address (5-bit array, 0-31)
            - rf_raddr_a: Read address A (5-bit array, 0-31)
            - rf_raddr_b: Read address B (5-bit array, 0-31)
        write_data: Optional 32-bit array to write if rf_we is enabled

    Returns:
        dict with:
            - 'read_a': Value read from address A (32-bit array)
            - 'read_b': Value read from address B (32-bit array)
            - 'written': True if write occurred, False otherwise
            - 'signals': ControlSignals (passed through)
            - 'trace': List of operations performed

    Example:
        >>> rf = RegisterFile()
        >>> signals = ControlSignals()
        >>>
        >>> # Write to x5
        >>> signals.rf_we = 1
        >>> signals.rf_waddr = [0,0,1,0,1]  # 5
        >>> write_data = [0]*31 + [1]  # Value 1
        >>> result = register_with_control(rf, signals, write_data)
        >>>
        >>> # Read from x5 and x0
        >>> signals.rf_we = 0
        >>> signals.rf_raddr_a = [0,0,1,0,1]  # 5
        >>> signals.rf_raddr_b = [0,0,0,0,0]  # 0
        >>> result = register_with_control(rf, signals)
        >>> result['read_a']  # Returns [0]*31 + [1]
        >>> result['read_b']  # Returns [0]*32 (x0 hardwired to 0)
    """
    from riscsim.utils.bit_utils import bits_to_int_unsigned

    trace = []

    # Convert addresses to integers
    addr_a = bits_to_int_unsigned(signals.rf_raddr_a)
    addr_b = bits_to_int_unsigned(signals.rf_raddr_b)
    addr_w = bits_to_int_unsigned(signals.rf_waddr)

    # Perform write if write enable is set
    written = False
    if signals.rf_we == 1:
        if write_data is None:
            raise ValueError("write_data required when rf_we=1")
        if len(write_data) != 32:
            raise ValueError(f"write_data must be 32 bits, got {len(write_data)}")

        rf.write_int_reg(addr_w, write_data)
        written = True
        trace.append(f"WRITE: x{addr_w} <- {write_data[:8]}...")

    # Perform reads
    read_a = rf.read_int_reg(addr_a)
    read_b = rf.read_int_reg(addr_b)
    trace.append(f"READ_A: x{addr_a} -> {read_a[:8]}...")
    trace.append(f"READ_B: x{addr_b} -> {read_b[:8]}...")

    return {
        'read_a': read_a,
        'read_b': read_b,
        'written': written,
        'signals': signals,
        'trace': trace
    }


# AI-END
