# rheoproc.label
# Functions for uniformly formatting units in plot labels.

def fmt_lbl(label, symbol, unit, no_label=False):
    assert (not no_label) or symbol
    lbl = '' if no_label else label
    if symbol or unit:
        if not no_label:
            lbl += ', '
        lbl += '$'
    if symbol:
        lbl += f'{symbol}'
    if unit:
        lbl += f'\\rm/{unit}'
    if symbol or unit:
        lbl += '$'
    return lbl


def strainrate_label(units=r's^{-1}', **kwargs):
    return fmt_lbl('Strain rate', '\\dot\\gamma', units, **kwargs)


def strain_label(units=r'(unitless)', **kwargs):
    return fmt_lbl('Strain', '\\gamma', units, **kwargs)


def stress_label(units='Pa', **kwargs):
    return fmt_lbl('Stress', '\\sigma', units, **kwargs)


def viscosity_label(units=r'Pa\,s', **kwargs):
    return fmt_lbl('Viscosity', '\\mu', units, **kwargs)


def temperature_label(units='K', **kwargs):
    return fmt_lbl('Temperature', 'T', units, **kwargs)


def time_label(units='s', **kwargs):
    return fmt_lbl('Time', 't', units, **kwargs)


def freq_label(units='Hz', symbol='\\omega', **kwargs):
    return fmt_lbl('Frequency', symbol, units, **kwargs)


def angular_position_label(units='rot', symbol='\\theta', **kwargs):
    return fmt_lbl('Angular Position', symbol, units, **kwargs)


def angular_velocity_label(units=r'rot\,s^{-1}', symbol='\\omega_r', **kwargs):
    return fmt_lbl('Angular Velocity', symbol, units, **kwargs)

def speed_label(units=r'rot\,s^{-1}', symbol='\\omega_r', **kwargs):
    return fmt_lbl('Angular Velocity', symbol, units, **kwargs)


def loadcell_label(units=None, symbol=r'\Lambda', **kwargs):
    return fmt_lbl('Loadcell Value', symbol, units, **kwargs)


def loadcell_norm_label(units=None, symbol=r'\hat\Lambda', **kwargs):
    return fmt_lbl('Normalised Loadcell Value', symbol, units, **kwargs)

def prsd_label(prop, symbol, **kwargs):
    return fmt_lbl(f'PRSD ({prop})', f'\\Sigma_{{{symbol}}}^{{\\%}}', '\\%', **kwargs)

def prsd_stress_label(**kwargs):
    return prsd_label('stress', '\\sigma', **kwargs)

def prsd_strainrate_label(**kwargs):
    return prsd_label('strainrate', '\\dot\\gamma', **kwargs)

def prsd_speed_label(**kwargs):
    return prsd_label('angular velocity', '\\omega_r', **kwargs)

def prsd_viscosity_label(**kwargs):
    return prsd_label('viscosity', '\\mu', **kwargs)

def pnd_label(units='V', symbol=r'V_{PND}', **kwargs):
    return fmt_lbl('PND Voltage', symbol, units, **kwargs)

def pnd_mono_label(units='V', symbol=r'\left|V_{PND}\right|', **kwargs):
    return fmt_lbl('PND Voltage (single channel)', symbol, units, **kwargs)


def ffty_label(units=None, symbol=None):
    # TODO
    return None