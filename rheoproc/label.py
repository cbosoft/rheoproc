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

def temperature_label(units='K'):
    return fmt_lbl('Temperature', 'T', units)

def time_label(units='s'):
    return fmt_lbl('Time', 't', units)

def freq_label(units='Hz', symbol='\\omega'):
    return fmt_lbl('Frequency', symbol, units)

def ffty_label(units=None, symbol=None):
    # TODO
    return None