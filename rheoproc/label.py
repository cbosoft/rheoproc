# rheoproc.label
# Functions for uniformly formatting units in plot labels.

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


def strain_label(units=r'(unitless)'):
    return fmt_lbl('Strain', '\\gamma', units)


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


def angular_position_label(units='rot', symbol='\\theta'):
    return fmt_lbl('Angular Position', symbol, units)


def angular_velocity_label(units=r'rot\,s^{-1}', symbol='\\omega_r'):
    return fmt_lbl('Angular Velocity', symbol, units)

def speed_label(units=r'rot\,s^{-1}', symbol='\\omega_r'):
    return fmt_lbl('Angular Velocity', symbol, units)


def loadcell_label(units=None, symbol=r'\Lambda'):
    return fmt_lbl('Loadcell Value', symbol, units)


def loadcell_norm_label(units=None, symbol=r'\hat\Lambda'):
    return fmt_lbl('Normalised Loadcell Value', symbol, units)

def prsd_label(prop, symbol):
    return fmt_lbl(f'PRSD ({prop})', f'\\Sigma_{{{symbol}}}^{{\\%}}', '\\%')

def prsd_stress_label():
    return prsd_label('stress', '\\sigma')

def prsd_strainrate_label():
    return prsd_label('strainrate', '\\dot\\gamma')

def prsd_speed_label():
    return prsd_label('angular velocity', '\\omega_r')

def prsd_viscosity_label():
    return prsd_label('viscosity', '\\mu')

def pnd_label(units='V', symbol=r'V_{PND}'):
    return fmt_lbl('PND Voltage', symbol, units)

def pnd_mono_label(units='V', symbol=r'\left|V_{PND}\right|'):
    return fmt_lbl('PND Voltage (single channel)', symbol, units)


def ffty_label(units=None, symbol=None):
    # TODO
    return None