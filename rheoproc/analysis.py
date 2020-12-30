# rheoproc.analysis
# Contains functions for performing analysis on data (histogramming, cross- and auto-correlation).

import warnings

import numpy as np

from rheoproc.exception import NaNError


def get_lag(t):
    '''
    Get the lag of a time series - this is the x axis for a correlation plot.
    'Lag' is centred about zero, with -half_period on the left and +half_period on
    the right.

    This function returns the lag series which corresponds to a given time series.
    '''
    lags = np.cumsum(np.diff(t))

    l = len(t)
    if l%2 == 1:
        hl = int(len(lags)//2)
        mid2 = lags[hl:hl+2]
        dl = (mid2[1] - mid2[0])*0.5
        for i in range(hl):
            lags[i] = lags[i] + dl
        for i in range(hl,len(lags)):
            lags[i] = lags[i] - dl
    lags = np.subtract(lags, np.median(lags))
    return lags


def xcorr(sl, sr, norm=True, real=True):
    '''

    Cross correlation of two signals is given by the fourier transform of one,
    multiplied by the conjugate of the fourier transform of the other, moved
    back into the time domain.

    i.e.

    xcorr = ifft (  fft(left) * conjugate( fft(right) ) )

    For more information, see stack exchange answer on this topic:
    https://dsp.stackexchange.com/questions/22877/intuitive-explanation-of-cross-correlation-in-frequency-domain
    '''

    if np.any(np.isnan(sl)) or np.any(np.isnan(sr)):
        raise NaNError('xcorr can\'t handle NaN in input: use strip before xcorr.')

    slq = np.fft.fft(sl)
    srqc = np.conjugate(np.fft.fft(sr))
    crosscorr = np.fft.ifft(np.multiply(slq, srqc))[1:]

    if real:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=np.ComplexWarning)
            crosscorr = np.real(crosscorr)

    if norm:
        crosscorr = np.divide(np.subtract(crosscorr, np.min(crosscorr)), np.max(crosscorr) - np.min(crosscorr))

    # the crosscorr is a little mixed up. We want zero lag to be in the middle
    l = len(crosscorr)
    hl = int(l//2)
    if l % 2 == 1:
        crosscorr = [*crosscorr[hl:],*crosscorr[1:hl+1]]
    else:
        crosscorr = [*crosscorr[hl:],*crosscorr[:hl]]

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


