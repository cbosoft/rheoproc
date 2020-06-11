import numpy as np

from rheoproc.exception import NaNError



def xcorr(sl, sr, dt=None, norm=True):
    '''

    Cross correlation of two signals is given by the fourier transform of one,
    multiplied by the conjugate of the fourier transform of the other, moved
    back into the time domain.

    i.e.

    xcorr = ifft (  fft(left) * conjugate( fft(right) ) )

    For more information, see stack exchange answer on this topic:
    https://dsp.stackexchange.com/questions/22877/intuitive-explanation-of-cross-correlation-in-frequency-domain

    If a dt keyword is supplied, then the lag axis is found and the data is
    sorted by increasing lag.
    '''

    if np.any(np.isnan(sl)) or np.any(np.isnan(sr)):
        raise NaNError('xcorr can\'t handle NaN in input: use strip before xcorr.')

    slq = np.fft.fft(sl)
    srqc = np.conjugate(np.fft.fft(sr))
    crosscorr = np.fft.ifft(np.multiply(slq, srqc))[1:]

    if norm:
        crosscorr = np.divide(np.subtract(crosscorr, np.min(crosscorr)), np.max(crosscorr) - np.min(crosscorr))

    if dt is not None:
        l = len(crosscorr)
        hl = l/2 if l%2 == 0 else (l+1)/2
        hl = int(hl)
        left = np.linspace(0, hl*dt*4, hl)
        right = np.linspace(-1*hl*dt*4, 0, hl)[1:]
        lag = [*left, *right]
        lag, crosscorr = zip(*list(sorted(zip(lag, crosscorr))))
        return lag, crosscorr

    return crosscorr



def deviation(s):
    '''returns signal as deviation from its mean'''
    return np.subtract(s, np.average(s))



def normalise(s, about_zero=False, offset_append=None):
    '''
    normalise a signal so that the smallest value is zero and the largest is 
    one: a range spanning 0 to 1. If about_zero is True, then the range spans 
    from -1 to 1 instead.
    '''
    s = list(s)
    if not offset_append is None:
        s.append(float(offset_append))

    mn = np.min(s)
    n = np.divide(np.subtract(s, mn), np.subtract(np.max(s), mn))

    if not offset_append is None:
        n = list(n)
        n.pop()

    if about_zero:
        return np.subtract(np.multiply(n, 2.0), 1.0)

    return n


