import sys
from enum import Enum
from fxpmath import Fxp

"""        
**************************************************************************************************************************************
* DEFINES
**************************************************************************************************************************************
"""

"""        
***************************************************************************************************************************************
* CLASSES
**************************************************************************************************************************************
"""
# ----------------------------------------------------------------------------------------------------------------------------------------
# Class which defines type of flag as Enum
class flag(Enum):
    OK = 1
    KO = 0
    ERROR = -1

# ----------------------------------------------------------------------------------------------------------------------------------------
# Class which defines data structure for fractional Qn number representation of a floating point number
# Qn_Fractional:
#   - value: Floating point number to be represented in Qn fractional format
#   - n_word: Total number of bits for the Qn representation (including sign bit)
#   - n_frac: Number of fractional bits for the Qn representation (excluding sign bit)
#   - n_int: Number of integer bits for the Qn representation (always 0 for fractional Qn)
#   - bit_shift_scaler: Power of 2 scaling factor to bring the value into the representable range (2^n gain to keep Qn in [-1, 1[ range)
#   - scaler: Equivalent scaling factor (2^bit_shift_scaler) in float format
#   - scaled_value: Value after applying the scaling factor in fractional Qn format
#   - scaled_value_hex: Hexadecimal representation of the scaled value
#   - scaled_value_bin: Binary representation of the scaled value
# Methods:
#   - __init__: Initializes the Qn_Fractional object and computes the scaled value and its representations
#   - set_new_bit_shift_scaler: Updates the bit shift scaler and recomputes the scaled value and its representations
class Qn_Fractional:
    def __init__(self, value: float, n_word: int, n_frac: int, debug=False):
        self.value = value
        self.bit_shift_scaler = 0
        self.scaler = 2**self.bit_shift_scaler
        self.scaled_value = self.value * self.scaler

        while self.scaled_value > -0.5 and self.scaled_value <= 0.5:
            self.bit_shift_scaler += 1
            self.scaler = 2**self.bit_shift_scaler
            self.scaled_value = self.value * self.scaler
        
        while self.scaled_value >= 1.0 or self.scaled_value < -1.0:
            self.bit_shift_scaler -= 1
            self.scaler = 2**self.bit_shift_scaler
            self.scaled_value = self.value * self.scaler
        
        self.n_word = n_word
        self.n_frac = n_frac
        self.n_int = 0  # Since it's fractional Qn, integer bits are 0
        self.fxp = Fxp(self.scaled_value, signed=True, n_word=n_word, n_frac=n_frac, n_int=self.n_int)
        self.scaled_value_hex = self.fxp.hex()
        self.scaled_value_bin = self.fxp.bin()
        if debug:
            print("Value: ", self.value)
            print("Bit Shift Scaling (power of 2): ", self.bit_shift_scaler)
            print("Equivalent Scaler: ", self.scaler)
            print("Scaled Value: ", self.scaled_value)
            print("Scaled Value Hex: ", self.scaled_value_hex)
            print("Scaled Value Bin: ", self.scaled_value_bin)

    def set_new_bit_shift_scaler(self, new_bit_shift_scaler: int, debug=False):
        self.bit_shift_scaler = new_bit_shift_scaler
        self.scaler = 2**self.bit_shift_scaler
        self.scaled_value = self.value * self.scaler
        self.fxp = Fxp(self.scaled_value, signed=True, n_word=self.n_word, n_frac=self.n_frac, n_int=self.n_int)
        self.scaled_value_hex = self.fxp.hex()
        self.scaled_value_bin = self.fxp.bin()
        if debug:
            print("Updated Qn Fractional Representation:")
            print("Value: ", self.value)
            print("Bit Shift Scaling (power of 2): ", self.bit_shift_scaler)
            print("Equivalent Scaler: ", self.scaler)
            print("Scaled Value: ", self.scaled_value)
            print("Scaled Value Hex: ", self.scaled_value_hex)
            print("Scaled Value Bin: ", self.scaled_value_bin)
            
"""        
**************************************************************************************************************************************
* GLOBALS
**************************************************************************************************************************************
"""

"""        
**************************************************************************************************************************************
* FUNCTIONS
**************************************************************************************************************************************
"""
def main():
    # Test Qn_Fractional class
    DEBUG_FLAG = True
    try:
        qn = Qn_Fractional(-3.38, 32, 31, debug=DEBUG_FLAG)
        print()
        qn = Qn_Fractional(+3.38, 32, 31, debug=DEBUG_FLAG)
        print()
        qn = Qn_Fractional(-0.5, 32, 31, debug=DEBUG_FLAG)
        print()
        qn = Qn_Fractional(+0.5, 32, 31, debug=DEBUG_FLAG)
        print()
        qn = Qn_Fractional(-1, 32, 31, debug=DEBUG_FLAG)
        print()
        qn = Qn_Fractional(+1, 32, 31, debug=DEBUG_FLAG)
        print()
        qn = Qn_Fractional(-1.5, 32, 31, debug=DEBUG_FLAG)
        print()
        qn = Qn_Fractional(+1.5, 32, 31, debug=DEBUG_FLAG)
        print()
        qn.set_new_bit_shift_scaler(-2)
        return (flag.OK)
    except ValueError as ve:
        return (flag.KO)

"""        
**************************************************************************************************************************************
* MAIN
**************************************************************************************************************************************
"""
if __name__ == "__main__":
    sys.exit(main())