import numpy as np


def xcorr(sl, sr):
    '''

    Cross correlation of two signals is given by the fourier transform of one,
    multiplied by the conjugate of the fourier transform of the other, moved
    back into the time domain.

    i.e.

    xcorr = ifft (  fft(left) * conjugate( fft(right) ) )

    For more information, see stack exchange answer on this topic:
    https://dsp.stackexchange.com/questions/22877/intuitive-explanation-of-cross-correlation-in-frequency-domain
    '''
    slq = np.fft.fft(sl)
    srqc = np.conjugate(np.fft.fft(sr))
    crosscorr = np.fft.ifft(np.multiply(slq, srqc))
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


