from . import register_format, HeaderGenContext


def _quantization_error_pct(coeff):
    reconstructed = float(coeff.fxp) / coeff.scaler
    if coeff.value == 0:
        return 0.0
    return ((reconstructed - coeff.value) / coeff.value) * 100


@register_format("Q31")
def generate_q31_coefficients(ctx: HeaderGenContext) -> str:
    ctx.compensator.Harmonize_DSP_Coefficients_Scaling_Q31()
    tf_z = ctx.compensator.transfer_function_z
    name = ctx.comp_name_string
    h = ""
    h += "// DSP IIR Filter Coefficients for Compensator: " + ctx.comp_display_name + " in Q31 format \n"
    index = 0
    for each_coeff in tf_z.A_Terms_DSP_Q31:
        err = _quantization_error_pct(each_coeff)
        h += "#define " + name + "_A" + str(index + 1) + "                          (int32_t) " + str(each_coeff.scaled_value_hex) + "  // original: " + str(each_coeff.value) + ", quantization error: " + f"{err:.6f}" + "%\n"
        index += 1
    index = 0
    for each_coeff in tf_z.B_Terms_DSP_Q31:
        err = _quantization_error_pct(each_coeff)
        h += "#define " + name + "_B" + str(index) + "                          (int32_t) " + str(each_coeff.scaled_value_hex) + "  // original: " + str(each_coeff.value) + ", quantization error: " + f"{err:.6f}" + "%\n"
        index += 1
    h += "#define " + name + "_A_TERMS_BIT_SHIFT_SCALING   (int32_t) " + str(tf_z.A_Terms_DSP_Q31[0].bit_shift_scaler) + "  // Common Bit Shift Scaling for A Terms\n"
    h += "#define " + name + "_B_TERMS_BIT_SHIFT_SCALING   (int32_t) " + str(tf_z.B_Terms_DSP_Q31[0].bit_shift_scaler) + "  // Common Bit Shift Scaling for B Terms\n\n"
    h += "\n"
    return h
