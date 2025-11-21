#ifndef DPSK4_BUCK_Q15_VCOMP_H
#define DPSK4_BUCK_Q15_VCOMP_H

/***************************************************************************************
* DSP Coefficient header file generartion in Q15, Q31, Float formats 
****************************************************************************************
* POLES AND ZEROS LOCATIONS:
*   fP0 Pole at Origin Frequency: 90 Hz
*   fZ1 Zero Frequency: 2551 Hz
*   fZ2 Zero Frequency: 3827 Hz
*   fP1 Pole Frequency: 80000 Hz
*   fP2 Pole Frequency: 170000 Hz
****************************************************************************************/
// DSP IIR Filter Coefficients for Compensator: dpsk4_buck_Q15_vcomp in Q15 format 
#define DPSK4_BUCK_Q15_VCOMP_A1                          (int16_t) 0x5312
#define DPSK4_BUCK_Q15_VCOMP_A2                          (int16_t) 0xEDA0
#define DPSK4_BUCK_Q15_VCOMP_A3                          (int16_t) 0xFF4E
#define DPSK4_BUCK_Q15_VCOMP_B1                          (int16_t) 0x4384
#define DPSK4_BUCK_Q15_VCOMP_B2                          (int16_t) 0xC1C9
#define DPSK4_BUCK_Q15_VCOMP_B3                          (int16_t) 0xBC96
#define DPSK4_BUCK_Q15_VCOMP_B4                          (int16_t) 0x3E51
#define DPSK4_BUCK_Q15_VCOMP_A_TERMS_BIT_SHIFT_SCALING   (int16_t) -1  // Common Bit Shift Scaling for A Terms
#define DPSK4_BUCK_Q15_VCOMP_B_TERMS_BIT_SHIFT_SCALING   (int16_t) 1  // Common Bit Shift Scaling for B Terms


#endif   //DPSK4_BUCK_Q15_VCOMP_H
