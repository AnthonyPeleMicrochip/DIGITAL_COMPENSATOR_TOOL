from . import register_format, HeaderGenContext


@register_format("FLOAT")
def generate_float_coefficients(ctx: HeaderGenContext) -> str:
    tf_z = ctx.compensator.transfer_function_z
    name = ctx.comp_name_string
    h = ""
    h += "// DSP IIR Filter Coefficients for Compensator: " + ctx.comp_display_name + " in FLOAT format \n"
    index = 0
    for each_coeff in tf_z.A_Terms_DSP_float:
        h += "#define " + name + "_A" + str(index + 1) + "                        (float) " + str(each_coeff) + "\n"
        index += 1
    index = 0
    for each_coeff in tf_z.B_Terms_DSP_float:
        h += "#define " + name + "_B" + str(index) + "                        (float) " + str(each_coeff) + "\n"
        index += 1
    h += "\n"
    return h
