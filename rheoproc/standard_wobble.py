import numpy as np
from lmfit import Parameters, minimize

from rheoproc.exception import GenericRheoprocException
from rheoproc.util import norm, unnorm, sqd
from rheoproc.cache import load_from_cache


def stretch(x, xu, yu):
    if np.any(np.isnan(x)) or np.any(np.isnan(xu)) or np.any(np.isnan(yu)):
        raise GenericRheoprocException('NaN in stretch input')
    end = np.max(x)
    xr = list(np.subtract(xu, 1.0))
    yr = list(yu)
    while True:
        xr.extend(np.add(xu, xr[-1]))
        yr.extend(yu)

        if xr[-1] > end+1:
            break

    return xr, yr



def residual_phase(params, x, y, xu, yu):
    phase = float(params['phase'])
    xm = np.add(x, phase)
    yu = np.interp(xm, xu, yu)
    e = sqd(y, yu)
    return e



def match_phase(x, y, xu, yu):
    params = Parameters()
    params.add('phase', np.random.uniform(), min=0.0, max=1.0)
    res = minimize(residual_phase, params, args=(x, y, xu, yu))
    return float(res.params['phase'])


def subtract_standard_wobble(pos, lc, motor):
    data = load_from_cache(f'standard_wobble_{motor}')
    if not data:
        print(f'could not load wobble for motor = {motor}')
        return lc
    standard_pos, standard_lc = data
    standard_pos, standard_lc = stretch(pos, standard_pos, standard_lc)
    nlc = norm(lc)
    phase = match_phase(pos, nlc, standard_pos, standard_lc)
    standard_lc = np.interp(pos, np.subtract(standard_pos, phase), standard_lc)
    nfiltered = np.subtract(nlc, standard_lc)
    return unnorm(nfiltered, np.mean(lc), np.max(lc) - np.min(lc))
