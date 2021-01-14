# rheoproc.fit
# Provides simple utility methods for fitting functions and plotting/labelling polynomial fits.

import numpy as np

def apply_fit(fitx, coeffs):
    '''
    Given a list of coefficients and an x series, get the y series given by the polynomial
    with the coefficients given in the args.
    '''
    fity = 0.0
    for p, c in zip(range(len(coeffs)-1, -1, -1), coeffs):
        fity = np.add(fity, np.multiply(np.power(fitx, p), c))
    return fity


def fmt_polynomial(coeffs, xname='x', yname='y'):
    label = f'${yname} = '
    first = True
    for p, c in zip(range(len(coeffs)-1, -1, -1), coeffs):
        if first:
            first = False
        else:
            if c < 0.0:
                c = c * -1.0
                label += ' - '
            else:
                label += ' + '
        if p > 1:
            label += f'{c:.3f}\\,{xname}^{p}'
        elif p == 1:
            label += f'{c:.3f}\\,{xname}'
        else:
            label += f'{c:.3f}'
    label += '$'
    return label


def fit(x, y, d, return_coeffs=False, return_label=False, xname='x', yname='y', return_func=False, fitx=None):
    '''
    Light wrapper around numpy's polyfit. Returns not the coeffs, but the y-series. May also
    output the label which might be displayed on a plot, and a lambda function which applies
    the fit when called.
    '''
    coeffs = np.polyfit(x, y, d)

    if fitx is None:
        fitx = np.sort(x)
    fity = apply_fit(fitx, coeffs)

    if return_coeffs:
        rv = [coeffs]
    else:
        rv = [fitx, fity]

    if return_label:
        rv.append(fmt_polynomial(coeffs, xname=xname, yname=yname))

    if return_func:
        f = lambda x: apply_fit(x, coeffs)
        rv.append(f)

    return tuple(rv)
