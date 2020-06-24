def fmt_lbl(label, symbol, unit):
    lbl = label
    if symbol or unit:
        lbl += ', $'
    if symbol:
        lbl += f'{symbol}'
    if unit:
        lbl += f'\\rm/{unit}'
    if symbol or unit:
        lbl += '$'
    return lbl


def strainrate_label(units=r's^{-1}'):
    return fmt_lbl('Strain rate', '\\dot\\gamma', units)

def stress_label(units='Pa'):
    return fmt_lbl('Stress', '\\sigma', units)

def viscosity_label(units=r'Pa\,s'):
    return fmt_lbl('Viscosity', '\\mu', units)

def time_label(units=r's'):
    return fmt_lbl('Time', 't', units)
