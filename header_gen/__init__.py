from dataclasses import dataclass
from typing import List


@dataclass
class HeaderGenContext:
    comp_name_string: str
    comp_display_name: str
    comp_format: str
    fp0_freq: float
    zeros_freqs: List[float]
    poles_freqs: List[float]
    compensator: object


_FORMAT_GENERATORS = {}


def register_format(name: str):
    def decorator(func):
        _FORMAT_GENERATORS[name] = func
        return func
    return decorator


def _build_preamble(ctx: HeaderGenContext) -> str:
    h = ""
    h += "#ifndef " + ctx.comp_name_string + "_H\n"
    h += "#define " + ctx.comp_name_string + "_H\n\n"
    h += "/***************************************************************************************\n"
    h += "* DSP Coefficient header file generation in " + ctx.comp_format + " format\n"
    h += "****************************************************************************************\n"
    h += "* POLES AND ZEROS LOCATIONS:\n"
    h += "*   fP0 Pole at Origin Frequency: " + str(ctx.fp0_freq) + " Hz\n"
    for i, freq in enumerate(ctx.zeros_freqs):
        h += "*   fZ" + str(i + 1) + " Zero Frequency: " + str(freq) + " Hz\n"
    for i, freq in enumerate(ctx.poles_freqs):
        h += "*   fP" + str(i + 1) + " Pole Frequency: " + str(freq) + " Hz\n"
    h += "****************************************************************************************/\n"
    return h


def _build_footer(ctx: HeaderGenContext) -> str:
    return "\n#endif   //" + ctx.comp_display_name.upper() + "_H\n"


def generate_header_file(ctx: HeaderGenContext) -> str:
    if ctx.comp_format not in _FORMAT_GENERATORS:
        raise ValueError(
            f"Unknown coefficient format '{ctx.comp_format}'. "
            f"Supported formats: {list(_FORMAT_GENERATORS.keys())}"
        )
    h_file = _build_preamble(ctx)
    h_file += _FORMAT_GENERATORS[ctx.comp_format](ctx)
    h_file += _build_footer(ctx)
    return h_file


from . import header_gen_float
from . import header_gen_Q31
from . import header_gen_Q15
