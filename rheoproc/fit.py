import numpy as np

def apply_fit(fitx, coeffs):
    fity = 0.0
    for p, c in zip(range(len(coeffs)-1, -1, -1), coeffs):
        fity = np.add(fity, np.multiply(np.power(fitx, p), c))
    return fity


def fit(x, y, d, return_label=False, xname='x', yname='y', return_func=False, fitx=None):
    coeffs = np.polyfit(x, y, d)

    if fitx is None:
        fitx = np.sort(x)
    fity = apply_fit(fitx, coeffs)

    rv = [fitx, fity]

    if return_label:
        label = f'${yname} = '
        first = True
        for p, c in zip(range(d, -1, -1), coeffs):
            if first:
                first = False
            else:
                if c < 0.0:
                    c = c*-1.0
                    label = label + ' - '
                else:
                    label = label + ' + '
            if p > 1:
                label = label + f'{c:.3f}{xname}^{p}'
            elif p == 1:
                label = label + f'{c:.3f}{xname}'
            else:
                label = label + f'{c:.3f}'
        label = label + '$'
        rv.append(label)

    if return_func:
        f = lambda x: apply_fit(x, coeffs)
        rv.append(f)

    return tuple(rv)
