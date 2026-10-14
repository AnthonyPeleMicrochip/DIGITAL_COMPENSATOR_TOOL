#ifndef DPSK3_BUCK_Q15_VCOMP_H
#define DPSK3_BUCK_Q15_VCOMP_H

/***************************************************************************************
* DSP Coefficient header file generation in Q15 format
****************************************************************************************
* POLES AND ZEROS LOCATIONS:
*   fP0 Pole at Origin Frequency: 90.0 Hz
*   fZ1 Zero Frequency: 2551.0 Hz
*   fZ2 Zero Frequency: 3827.0 Hz
*   fP1 Pole Frequency: 80000.0 Hz
*   fP2 Pole Frequency: 170000.0 Hz
****************************************************************************************/
// DSP IIR Filter Coefficients for Compensator: dpsk3_buck_Q15_vcomp in Q15 format 
#define DPSK3_BUCK_Q15_VCOMP_A1                          (int16_t) 0x5312  // original: 1.2980294767277858, quantization error: -0.004302%
#define DPSK3_BUCK_Q15_VCOMP_A2                          (int16_t) 0xEDA0  // original: -0.28712436465984, quantization error: -0.005221%
#define DPSK3_BUCK_Q15_VCOMP_A3                          (int16_t) 0xFF4E  // original: -0.010905112067945978, quantization error: -0.374634%
#define DPSK3_BUCK_Q15_VCOMP_B0                          (int16_t) 0x4384  // original: 0.26374127108003254, quantization error: -0.003170%
#define DPSK3_BUCK_Q15_VCOMP_B1                          (int16_t) 0xC1C9  // original: -0.24303405896432573, quantization error: -0.003014%
#define DPSK3_BUCK_Q15_VCOMP_B2                          (int16_t) 0xBC96  // original: -0.26335048279661444, quantization error: -0.005430%
#define DPSK3_BUCK_Q15_VCOMP_B3                          (int16_t) 0x3E51  // original: 0.2434248472477438, quantization error: -0.000569%
#define DPSK3_BUCK_Q15_VCOMP_A_TERMS_BIT_SHIFT_SCALING   (int16_t) -1  // Common Bit Shift Scaling for A Terms
#define DPSK3_BUCK_Q15_VCOMP_B_TERMS_BIT_SHIFT_SCALING   (int16_t) 1  // Common Bit Shift Scaling for B Terms


#endif   //DPSK3_BUCK_Q15_VCOMP_H
