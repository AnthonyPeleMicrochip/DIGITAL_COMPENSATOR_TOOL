import os, sys

import check_packages as check
if check.check_package_installed('numpy') == check.flag.KO:
    print("Numpy package not found. Need to install Numpy through regular pip command...")
    sys.exit()
if check.check_package_installed('math') == check.flag.KO:
    print("Math package not found. Need to install Math through regular pip command...")
    sys.exit()
if check.check_package_installed('control') == check.flag.KO:
    print("Control package not found. Need to install control through regular pip command...")
    sys.exit()
if check.check_package_installed('scipy') == check.flag.KO:
    print("Scipy package not found. Need to install scipy through regular pip command...")
    sys.exit()
if check.check_package_installed('enum') == check.flag.KO:
    print("Enum package not found. Need to install enum through regular pip command...")
    sys.exit()
if check.check_package_installed('matplotlib') == check.flag.KO:
    print("Matplotlib package not found. Need to install matplotlib through regular pip command...")
    sys.exit()
if check.check_package_installed('json') == check.flag.KO:
    print("Json package not found. Need to install json through regular pip command...")
    sys.exit()

import numpy as np
import math
from numpy.polynomial import Polynomial as poly
import control
from scipy import signal
from enum import Enum
import matplotlib.pyplot as plt
import matplotlib
import json
import Qn_Fractional_lib as Qn
import get_plant_from_txt as plant
from header_gen import generate_header_file, HeaderGenContext


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
# Class which defines type of filter as Enum
class filter_type(Enum):
    INTEGRATOR = "Integrator"
    POLE = "Pole"
    ZERO = "Zero"
    COMPENSATOR = "Compensator"

# ----------------------------------------------------------------------------------------------------------------------------------------
# Class which stores polynomial as Coefficients table or numpy polynomial. BEWARE ordering is different!
class POLYNOM:
    def __init__(self, descending_coeffs, symbol = "s"):
        self.coeffs = descending_coeffs
        self.polynom = poly(np.flip(descending_coeffs), symbol="s") # polynomial in numpy takes ascending coeff table from s^0 to s^n

# ----------------------------------------------------------------------------------------------------------------------------------------
# Class which stores S Space (continuous time) Transfer Function data as:
#              - numerator/denominator polynoms from s^n to s^0
#              - Control library transfer function
#              - Signal library transfer function
class TRANSFER_FUNCTION_S:
    def __init__(self, numerator_descending_coeffs, denominator_descending_coeffs):
        self.numerator = POLYNOM(numerator_descending_coeffs)               
        self.denominator = POLYNOM(denominator_descending_coeffs)
        self.control_tf = control.TransferFunction(self.numerator.coeffs, self.denominator.coeffs)  # takes descending coeffs for polynom
        self.signal_tf = signal.lti(self.numerator.coeffs, self.denominator.coeffs)                 # takes descending coeffs for polynom
        self.control_tf.input_labels = "input"
        self.control_tf.output_labels = "output"

# ----------------------------------------------------------------------------------------------------------------------------------------
# Class which stores Z Space (Digital/discrete time) Transfer Function data as:
#              - numerator/denominator polynoms from z^n to s^0
#              - Control library transfer function
#              - A-Terms/B-Terms coefficients
#              - A-Terms/B-Terms coefficients for DSP add/accumulate instruction (Storing -An Terms)
class TRANSFER_FUNCTION_Z:
    def __init__(self, transfer_function_s:TRANSFER_FUNCTION_S, Fs):
        # Calculate A and B Terms IIR filter according to S transfer function using bilinear transform
        self.B_Terms, self.A_Terms = signal.bilinear(transfer_function_s.numerator.coeffs, transfer_function_s.denominator.coeffs, Fs)
        # H(z) = (Bn.Z^-n + ... + B1.z^-1 + B0) / (-An.z^-n - ... - A1.z^-1 + 1) -- the +1 at denominator is always 1 and refers to A0
        # Shaping coefficients to reflect H(z) for sums only for DSP coding
        self.A_Terms_DSP = self.A_Terms * (-1)  # inverting sign of A-Terms for DSP add/accumulate ONLY operations, no sub
        self.A_Terms_DSP[0] = 1                 # putting back A(0) = 1
        self.B_Terms_DSP = self.B_Terms
        
        # Create float format of DSP A and B Terms rounded to 6 decimals
        self.A_Terms_DSP_float = np.round(self.A_Terms_DSP, 6)
        self.A_Terms_DSP_float = self.A_Terms_DSP_float[1:]
        self.B_Terms_DSP_float = np.round(self.B_Terms_DSP, 6)

        # Create Q31 format of DSP A and B Terms with scaling factor for each coefficient
        self.A_Terms_DSP_Q31 = []
        self.B_Terms_DSP_Q31 = []
        for i in range (1, len(self.A_Terms_DSP)):
            self.A_Terms_DSP_Q31.append(Qn.Qn_Fractional(self.A_Terms_DSP[i], n_word=32, n_frac=31, debug=False))
        for i in range (0, len(self.B_Terms_DSP)):
            self.B_Terms_DSP_Q31.append(Qn.Qn_Fractional(self.B_Terms_DSP[i], n_word=32, n_frac=31, debug=False))
        
        # Create Q15 format of DSP A and B Terms with scaling factor for each coefficient
        self.A_Terms_DSP_Q15 = []
        self.B_Terms_DSP_Q15 = []
        for i in range (1, len(self.A_Terms_DSP)):
            self.A_Terms_DSP_Q15.append(Qn.Qn_Fractional(self.A_Terms_DSP[i], n_word=16, n_frac=15, debug=False))
        for i in range (0, len(self.B_Terms_DSP)):
            self.B_Terms_DSP_Q15.append(Qn.Qn_Fractional(self.B_Terms_DSP[i], n_word=16, n_frac=15, debug=False))
            
        self.control_tf = control.TransferFunction(self.B_Terms, self.A_Terms, dt=True, display_format='poly')
        self.control_tf.input_labels = "input(n)"
        self.control_tf.output_labels = "output(n)"

# ----------------------------------------------------------------------------------------------------------------------------------------
# Class which stores Bode plots data in S and Z domains
class BODE_DATA:
    def __init__(self, w, Fs):              
        self.w_s = w                    # store W vector for S domain
        self.f_s = w / _2pi             # store Frequency vector for S domain
        self.mag_s = np.zeros(len(w))                 # magnitude vector for S domain in dB
        self.phase_s = np.zeros(len(w))               # phase vector for S domain in degrees
        self.phase_s_with_erosion = np.zeros(len(w))  # phase vector for S domain in degrees taking into account phase erosion estimation (due to Didtal filtering implementation)
        self.dPhi_Erosion_factor = 1         # Phase erosion factor equal to -360° * ((Ts - ADC_TRIG_DELAY)/Ts) * Calculation delay. Multiplying this factor by frequency f/Fs will give phase erosion impact at f  
        self.h_s = np.zeros(len(w))                   # complex frequency response for S domain    

        self.w_z = w / Fs               # store W vector for Z domain (normalized to sampling frequency)
        self.f_z = self.w_z / _2pi      # store Frequency vector for Z domain in Hertz (Hz) (normalized to sampling frequency)    
        self.mag_z = np.zeros(len(w))                 # magnitude vector for Z domain in dB
        self.phase_z = np.zeros(len(w))               # phase vector for Z domain in degrees
        self.phase_z_with_erosion = np.zeros(len(w))  # phase vector for Z domain in degrees taking into account phase erosion estimation (due to Didtal filtering implementation)
        self.h_z = np.zeros(len(w))                   # complex frequency response for Z domain  

# ----------------------------------------------------------------------------------------------------------------------------------------
# Class which stores filter data structure which uses above data structures
# Filter Data structure common to Integrator, Pole, Zero or full Compensator filter
# comp_num and comp_den are numertor/denominator of compensator filter if created, descending coeffs tables
class filter:
    def __init__(self, name, type = filter_type.INTEGRATOR, freq=1, KGain = 1, comp_num=[1], comp_den=[1], omega_vector=[], Fs=1): 
        self.name = name
        self.freq = freq
        self.Omega = freq*(2*math.pi)
        self.DC_Gain = KGain
        self.type = type
        self.Fs = Fs
        self.bode_data = BODE_DATA(omega_vector, self.Fs)

        match self.type:
            case filter_type.INTEGRATOR:
                self.numerator = POLYNOM([self.DC_Gain * self.Omega])
                self.denominator = POLYNOM([1 , 0])
                
            case filter_type.POLE:
                self.numerator = POLYNOM([self.DC_Gain])
                self.denominator = POLYNOM([1/self.Omega , 1])
                
            case filter_type.ZERO:
                self.denominator = POLYNOM([1])
                self.numerator = POLYNOM([self.DC_Gain*(1/self.Omega) , self.DC_Gain])
                
            case filter_type.COMPENSATOR:
                self.numerator = POLYNOM(comp_num)
                self.denominator = POLYNOM(comp_den)

        self.transfer_function_s = TRANSFER_FUNCTION_S(self.numerator.coeffs, self.denominator.coeffs)
        self.transfer_function_z = TRANSFER_FUNCTION_Z(self.transfer_function_s, Fs)
        self.bode_data.h_s = self.transfer_function_s.control_tf.frequency_response(omega=self.bode_data.w_s)
        self.bode_data.mag_s = 20 * np.log10(abs(self.bode_data.h_s.magnitude))
        self.bode_data.phase_s = self.bode_data.h_s.phase * (180/np.pi)

    def Calculate_Z_Transfer_Funtion (self):
        # Calculate Z transfert function (data structure) from S transfer function with Fs Sampling frequency
        self.transfer_function_z = TRANSFER_FUNCTION_Z(self.transfer_function_s, self.Fs)
        self.bode_data.h_z = self.transfer_function_z.control_tf.frequency_response(omega=self.bode_data.w_z)
        self.bode_data.mag_z = 20 * np.log10(abs(self.bode_data.h_z.magnitude))    
        self.bode_data.phase_z = self.bode_data.h_z.phase * (180/np.pi)
    
    def Harmonize_DSP_Coefficients_Scaling_Q31 (self):
        # Harmonize all DSP A and B Terms Qn_Fractional bit_shift_scaler to target_bit_shift_scaler
        # A-Terms will have their own scaling factor, B-Terms will have their own scaling factor
        # This equates to PowerSmart Dual bit-shift sclaing for A and B Terms in DSP IIR filter implementation
        minimum_shift_A = min(each.bit_shift_scaler for each in self.transfer_function_z.A_Terms_DSP_Q31)
        minimum_shift_B = min(each.bit_shift_scaler for each in self.transfer_function_z.B_Terms_DSP_Q31)
        for each in self.transfer_function_z.A_Terms_DSP_Q31:
            each.set_new_bit_shift_scaler(minimum_shift_A, debug=False)
        for each in self.transfer_function_z.B_Terms_DSP_Q31:
            each.set_new_bit_shift_scaler(minimum_shift_B, debug=False)

    def Harmonize_DSP_Coefficients_Scaling_Q15 (self):
        # Harmonize all DSP A and B Terms Qn_Fractional bit_shift_scaler to target_bit_shift_scaler
        # A-Terms will have their own scaling factor, B-Terms will have their own scaling factor
        # This equates to PowerSmart Dual bit-shift sclaing for A and B Terms in DSP IIR filter implementation
        minimum_shift_A = min(each.bit_shift_scaler for each in self.transfer_function_z.A_Terms_DSP_Q15)
        minimum_shift_B = min(each.bit_shift_scaler for each in self.transfer_function_z.B_Terms_DSP_Q15)
        for each in self.transfer_function_z.A_Terms_DSP_Q15:
            each.set_new_bit_shift_scaler(minimum_shift_A, debug=False)
        for each in self.transfer_function_z.B_Terms_DSP_Q15:
            each.set_new_bit_shift_scaler(minimum_shift_B, debug=False)
    
    def Update_filter_from_s_polynoms_update (self):
        self.transfer_function_s = TRANSFER_FUNCTION_S(self.numerator.coeffs, self.denominator.coeffs)
        self.transfer_function_z = TRANSFER_FUNCTION_Z(self.transfer_function_s, self.Fs)
        self.bode_data.h_s = self.transfer_function_s.control_tf.frequency_response(omega=self.bode_data.w_s)
        self.bode_data.mag_s = 20 * np.log10(abs(self.bode_data.h_s.magnitude))
        self.bode_data.phase_s = self.bode_data.h_s.phase * (180/np.pi)
        self.Calculate_Z_Transfer_Funtion()
        self.Harmonize_DSP_Coefficients_Scaling_Q31()
        self.Harmonize_DSP_Coefficients_Scaling_Q15()


"""        
**************************************************************************************************************************************
* GLOBALS
**************************************************************************************************************************************
"""
_2pi = np.pi* 2

"""        
**************************************************************************************************************************************
* FUNCTIONS
**************************************************************************************************************************************
"""
# CALL MAIN FUNCTION Wwith specific JSON config file
def compensator_setup (json_config_file, verbose = False):
    main(json_config_file, verbose)


"""        
**************************************************************************************************************************************
* MAIN
**************************************************************************************************************************************
"""
def main(json_config_file = "./_config/filter_config.json" , verbose = True):
    # Taking filter configuration from "filter_config.json" file by default when script is called directly
    with open(json_config_file, "r") as f:
        data_from_json = json.load(f)
    # INIT DATA WITH JSON CONTENT READ
    print("Digital Filter:")
    print("   Name: ", data_from_json.get("name"))
    print("   Type: ", data_from_json.get("type"))
    print("   Description: ", data_from_json.get("description"))
    print(".  Output header file name: ", data_from_json.get("h_file_name"))
    
    Compensator_Name = data_from_json.get("name")
    BODE_PLOT_MIN_FREQ = int(data_from_json["filter_parameters"]["BODE_PLOT_MIN_FREQ_10powerN"])      # defines n for minimum frequency 10^n in Hertz (Hz)
    BODE_PLOT_MAX_FREQ = int(data_from_json["filter_parameters"]["BODE_PLOT_MAX_FREQ_10powerN"])      # defines n for maximum frequency 10^n in Hertz (Hz)
    BODE_PLOT_NB_POINTS = int(data_from_json["filter_parameters"]["BODE_PLOT_NB_POINTS"])             # number of points for Bode plots
    SamplingFreq = int(data_from_json["filter_parameters"]["SAMPLING_FREQUENCY_HZ"])                  # Sampling frequency in Hertz (Hz)
    # Digital Power user defines
    # Sampling frequency in Hertz (Hz)
    Fs=SamplingFreq
    Ts=1/SamplingFreq
    header_file_name = "./_output_docs/" + data_from_json["h_file_name"]
    bode_plot_output = "./_output_docs/" + data_from_json["bode_plot_output_file_name"]
    # Retrieve parameters from JSON file to estimate phase erosion impact
    ESTIMATED_DIGITAL_FILTER_TIME_DELAY_IN_S = data_from_json["filter_parameters"]["ESTIMATED_DIGITAL_FILTER_TIME_DELAY_IN_S"]
    ESTIMATED_ADC_TRIGGER_POINT_DELAY = data_from_json["filter_parameters"]["ESTIMATED_ADC_TRIGGER_POINT_DELAY"]

    freq_vector = np.logspace(BODE_PLOT_MIN_FREQ, BODE_PLOT_MAX_FREQ, BODE_PLOT_NB_POINTS) # build frequency vector for bode plots
    w_vector = _2pi * freq_vector # calculate corresponding W vector (W=2*pi*freq)
     
    # FILTER CALCULATIONS WHEN USED AS STANDALONE SCRIPTs
    filter_list = data_from_json["filter_parameters"]["frequencies_Hz"]
    filters_struct_list = []
    # Define Pole At Origin frequency from JSON file
    FP0_FREQ = filter_list["Integrator_pole"][0]["frequency"]                   
    Fp0 = filter("Pole At Origin", filter_type.INTEGRATOR, freq=FP0_FREQ, KGain=1, omega_vector=w_vector, Fs=Fs)
    # Define Zeros frequencies from JSON file
    Zeros = []
    index = 0
    for zero in filter_list["Zeros"]:
        Zeros.append(filter("Zero #" + str(index + 1), filter_type.ZERO, freq=zero["frequency"], KGain=1, omega_vector=w_vector, Fs=Fs))
        index += 1
    # Define Poles frequencies from JSON file
    Poles = []
    index = 0
    for pole in filter_list["Poles"]:
        Poles.append(filter("Pole #" + str(index + 1), filter_type.POLE, freq=pole["frequency"], KGain=1, omega_vector=w_vector, Fs=Fs))
        index += 1

    # Build compensator numerator and denominator polynoms from pole ate origin, zeros and poles
    # Starting with integrator
    compensator_num_polynom = Fp0.numerator.polynom
    # Computing Zeros
    for zero in Zeros:
        compensator_num_polynom = compensator_num_polynom * zero.numerator.polynom
    compensator_den_polynom = Fp0.denominator.polynom
    # Computing Poles
    for pole in Poles:
        compensator_den_polynom = compensator_den_polynom * pole.denominator.polynom
    compensator_num_coeffs = np.flip(compensator_num_polynom.convert().coef)    # Numpy polynom gives ascending coeffs, control/signal libraries take descending coeffs, need to flip
    compensator_den_coeffs = np.flip(compensator_den_polynom.convert().coef)    # Numpy polynom gives ascending coeffs, control/signal libraries take descending coeffs, need to flip
    # Build Compensator Data Object from numerator/denominator polynoms calculated with Integrator/Poles/zeros 
    Compensator = filter(data_from_json.get("name"), filter_type.COMPENSATOR,comp_num=compensator_num_coeffs,comp_den=compensator_den_coeffs, omega_vector=w_vector, Fs=Fs)
    Compensator.numerator.polynom = compensator_num_polynom
    Compensator.denominator.polynom = compensator_den_polynom
    Compensator.transfer_function_s.control_tf.input_labels = "error e"
    Compensator.transfer_function_s.control_tf.output_labels = "control_output u"
    
    # Calculate Digital filter from Analog filter
    Compensator.Calculate_Z_Transfer_Funtion()
    # Evaluate Phase erosion
    Compensator.bode_data.dPhi_Erosion_factor = -360 * ((Ts - ESTIMATED_ADC_TRIGGER_POINT_DELAY) / Ts) * ESTIMATED_DIGITAL_FILTER_TIME_DELAY_IN_S
    index = 0
    for f in Compensator.bode_data.f_s:
        Compensator.bode_data.phase_s_with_erosion[index] = Compensator.bode_data.phase_s[index] + (Compensator.bode_data.dPhi_Erosion_factor * (f))
        Compensator.bode_data.phase_z_with_erosion[index] = Compensator.bode_data.phase_z[index] + (Compensator.bode_data.dPhi_Erosion_factor * (f))
        index += 1
    
    # Generate header file content via format-specific generator
    comp_name_string = str(Compensator.name.replace(" ", "_").upper())
    comp_format = (data_from_json["filter_parameters"]["coefficient_format"]).upper()
    ctx = HeaderGenContext(
        comp_name_string=comp_name_string,
        comp_display_name=Compensator.name,
        comp_format=comp_format,
        fp0_freq=FP0_FREQ,
        zeros_freqs=[z.freq for z in Zeros],
        poles_freqs=[p.freq for p in Poles],
        compensator=Compensator,
    )
    h_file = generate_header_file(ctx)
        
    # Write h_file to coeffs.h
    output_file_path = os.path.join(os.path.dirname(__file__), header_file_name)
    with open(output_file_path, 'w') as f:
        f.write(h_file)
    print(f"Coefficients written to: {output_file_path}")

    
    """ BODE PLOTS """
    try:
        plant_data_file = data_from_json["plant_data_file"]
        CompPlt, axs = plt.subplots(2,2, figsize=(13, 8))
        CompGainPlt =axs[0,0]
        CompPhasePlt = axs[1,0]
        PlantGainPlt = axs[0,1]
        PlantPhasePlt = axs[1,1]
        plant_data_file_found = True
    except KeyError:
        CompPlt, axs = plt.subplots(2,1, figsize=(10, 8))
        CompGainPlt = axs[0]
        CompPhasePlt = axs[1]
        plant_data_file_found = False
        
    CompPlt.suptitle(Compensator.name.upper())
    CompGainPlt.semilogx(Compensator.bode_data.f_z*Fs, Compensator.bode_data.mag_z, label="Digital", dashes=[6, 2])   # Bode magnitude plot of Digital Filter (contructed from Analog through bilinear transform)
    CompGainPlt.semilogx(Compensator.bode_data.f_s, Compensator.bode_data.mag_s, label="Analog")       # Bode magnitude plot of Analog Filte
    plot_max = np.round(np.max(Compensator.bode_data.mag_s),-1) + 10    # Search for max gain value and round to upper 10's value + 10dB
    plot_min = np.round(np.min(Compensator.bode_data.mag_s),-1) - 10    # Search for min gain value and round to lower 10's value - 10dB
    CompGainPlt.set_ylim(plot_min,plot_max)
    CompGainPlt.set_ylabel("Gain [dB]")
    CompGainPlt.set_xlabel("Frequency [Hz]")
    CompGainPlt.grid(True, which="both")
    CompGainPlt.axvline(x=Fs/2, color='r', linestyle='dotted', linewidth=3, label=("Fs/2 limit @ " + str((Fs/2)/1000) + " kHz"))
    CompGainPlt.axvline(x=FP0_FREQ, color='k', linestyle='solid', linewidth=2, label=("fP0 @ " + str(FP0_FREQ) + " Hz"))
    for zero in Zeros:
        CompGainPlt.axvline(x=zero.freq, color='k', linestyle='dashed', linewidth=2, label=("fZ @ " + str(zero.freq) + " Hz"))
    for pole in Poles:
        CompGainPlt.axvline(x=pole.freq, color='k', linestyle='dotted', linewidth=2, label=("fP @ " + str(pole.freq) + " Hz"))
    CompGainPlt.legend(loc='best', fontsize='small')

    CompPhasePlt.semilogx(Compensator.bode_data.f_z*Fs, Compensator.bode_data.phase_z_with_erosion, label="Digital with erosion", dashes=[6, 2])   # Bode phase plot of Digital Filter (contructed from Analog through bilinear transform)
    CompPhasePlt.semilogx(Compensator.bode_data.f_s, Compensator.bode_data.phase_s_with_erosion, label="Analog with erosion")       # Bode phase plot of    Analog Filter
    CompPhasePlt.set_ylabel("Phase [°]")
    CompPhasePlt.set_xlabel("Frequency [Hz]")
    CompPhasePlt.grid(True, which="both")
    
    CompPhasePlt.semilogx(Compensator.bode_data.f_z*Fs, Compensator.bode_data.phase_z, label="Digital", dashes=[6, 2])   # Bode phase plot of Digital Filter (contructed from Analog through bilinear transform)
    CompPhasePlt.semilogx(Compensator.bode_data.f_s, Compensator.bode_data.phase_s, label="Analog")       # Bode phase plot of    Analog Filter
    CompPhasePlt.set_ylabel("Phase [°]")
    CompPhasePlt.set_xlabel("Frequency [Hz]")
    CompPhasePlt.grid(True, which="both")
    CompPhasePlt.axvline(x=Fs/2, color='r', linestyle='dotted', linewidth=3, label=("Fs/2 limit @ " + str((Fs/2)/1000) + " kHz"))
    CompPhasePlt.axvline(x=FP0_FREQ, color='k', linestyle='solid', linewidth=2, label=("fP0 @ " + str(FP0_FREQ) + " Hz"))
    for zero in Zeros:
        CompPhasePlt.axvline(x=zero.freq, color='k', linestyle='dashed', linewidth=2, label=("fZ @ " + str(zero.freq) + " Hz"))
    for pole in Poles:
        CompPhasePlt.axvline(x=pole.freq, color='k', linestyle='dotted', linewidth=2, label=("fP @ " + str(pole.freq) + " Hz"))
    CompPhasePlt.legend(loc='upper left', fontsize='small')
    CompPhasePlt.set_ylim(-180, 181)
    CompPhasePlt.set_yticks(np.arange(-180, 181, 20))
    
    #Plant data graph
    if plant_data_file_found == True:
        plant_data_file = data_from_json["plant_data_file"]
        flag_return, Plant_RAW = plant.main(plant_data_file)
        Plant_RAW = np.array(Plant_RAW)
        #print(Plant_RAW)
        print(len(Compensator.bode_data.f_s))
        Plant = plant.reshape_plant_data(Plant_RAW, Compensator.bode_data.f_s)
        plant_bode = BODE_DATA(w_vector, Fs)
        index = 0
        for data_point in Plant:
            plant_bode.f_s[index] = data_point[0]
            plant_bode.mag_s[index] = data_point[1]
            plant_bode.phase_s[index] = data_point[2]
            index += 1
        PlantGainPlt.semilogx(plant_bode.f_s, plant_bode.mag_s, label="Plant", dashes=[6, 2])       # Bode magnitude plot of Plant
        PlantGainPlt.semilogx(plant_bode.f_s, plant_bode.mag_s + Compensator.bode_data.mag_z, label="Plant + Comp")       # Bode magnitude plot of Plant
        PlantGainPlt.set_ylabel("Gain [dB]")
        PlantGainPlt.set_xlabel("Frequency [Hz]")
        PlantGainPlt.grid(True, which="both")
        PlantGainPlt.axvline(x=Fs/2, color='r', linestyle='dotted', linewidth=3, label=("Fs/2 limit @ " + str((Fs/2)/1000) + " kHz"))
        PlantGainPlt.legend(loc='best', fontsize='small')
        PlantGainPlt.set_ylim(-80, 60)
        PlantGainPlt.set_yticks(np.arange(-80, 61, 10))
        PlantGainPlt.axhline(y=0, color='k', linewidth=2)
        
        PlantPhasePlt.semilogx(plant_bode.f_s, -180 + plant_bode.phase_s, label="Plant", dashes=[6, 2])       # Bode magnitude plot of Plant
        PlantPhasePlt.semilogx(plant_bode.f_s, -180 + plant_bode.phase_s + Compensator.bode_data.phase_z, label="Plant + Comp")       # Bode magnitude plot of Plant
        PlantPhasePlt.set_ylabel("Phase [°]")
        PlantPhasePlt.set_xlabel("Frequency [Hz]")
        PlantPhasePlt.grid(True, which="both")
        PlantPhasePlt.axvline(x=Fs/2, color='r', linestyle='dotted', linewidth=3, label=("Fs/2 limit @ " + str((Fs/2)/1000) + " kHz"))
        PlantPhasePlt.legend(loc='best', fontsize='small')
        PlantPhasePlt.set_ylim(-270, 30)
        PlantPhasePlt.set_yticks(np.arange(-180, 1, 20))
        PlantPhasePlt.axhline(y=-180, color='k', linewidth=2)
        
    plt.show()
    CompPlt.savefig(bode_plot_output, format='pdf')

    # Display filter creation summary
    if verbose == True:
        print("Digital Filter:")
        print("   Name: ", data_from_json.get("name"))
        print("   Type: ", data_from_json.get("type"))
        print("   Description: ", data_from_json.get("description"))
        print("   Output header file name: ", data_from_json.get("h_file_name"))
        print("   Filter Parameters:")
        print("      BODE_PLOT_MIN_FREQ=10^", BODE_PLOT_MIN_FREQ, " (",10**BODE_PLOT_MIN_FREQ, "Hz )")
        print("      BODE_PLOT_MAX_FREQ=10^", BODE_PLOT_MAX_FREQ, " (",10**BODE_PLOT_MAX_FREQ, "Hz )")
        print("      BODE_PLOT_NB_POINTS=", BODE_PLOT_NB_POINTS, " points")
        print("      SAMPLING_FREQUENCY_HZ=", SamplingFreq, "Hz \n")
        print("      Creating Integrator ", FP0_FREQ, "Hz")
        for zeros in filter_list["Zeros"]: print("      Creating Zero at ", zeros["frequency"], "Hz")
        for poles in filter_list["Poles"]: print("      Creating Pole at ", poles["frequency"], "Hz")
        print()
        print("CALCULATIONS....")
        print(" Analog Compensator TF: ", Compensator.transfer_function_s.control_tf)
        print()
        print(" Equivalent Digital Compensator TF: ", Compensator.transfer_function_z.control_tf)
        """ DSP COEFFICIENTS PRINTING """
        print("DSP IIR Filter Coefficients for Compensator: " + Compensator.name)
        print("B Terms Coefficients (B0 to B" + str(len(Compensator.transfer_function_z.B_Terms_DSP) - 1) + "): " + str(Compensator.transfer_function_z.B_Terms_DSP))
        print("A Terms Coefficients (A0 to A" + str(len(Compensator.transfer_function_z.A_Terms_DSP) - 1) + "): " + str(Compensator.transfer_function_z.A_Terms_DSP))
        print(" ")
        print (h_file)
    return flag.OK

if __name__ == "__main__":
    # Retrieve config file name if any
    try :
        sys.argv[1]
        main(sys.argv[1])
    except IndexError:
        main()
    sys.exit()

