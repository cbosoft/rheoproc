import numpy as np
from scipy import signal

from rheoproc.accelproc import moving_mean as accel_moving_mean


def filt(t, v, freq=10, order=10, bt='low'):
    '''
    apply a frequency filter (butterworth) to a timeseries signal
    '''
    dt = np.average(np.diff(t))
    sample_freq = 1.0 / dt
    if isinstance(freq, list):
        w = [f/(sample_freq*0.5) for f in freq]
    else:
        w = freq / (sample_freq * 0.5)
    b, a = signal.butter(order, w, btype=bt)
    output = signal.filtfilt(b, a, v)
    return output


def strip(*args, f):
    '''
    remove a row of data from *args, where each arg is a column, if filter
    function f of the row is false. (rows where f evaluates truthy are kept.)

    The args should all be the same length.
    '''

    assert args

    ncols = len(args)
    nrows = len(args[0])
    for i in range(1, ncols):
        assert len(args[i]) == nrows
    
    byrow = list(zip(*args))
    byrow = list(filter(f, byrow))
    return list(zip(*byrow))


def moving_average(v, w, *, avf=None):

    if avf is None:
        return accel_moving_mean(list(v), w)


    l = len(v)
    rv = [0]*l
    for i in range(len(v)):
        start = i - w
        start = start if start > 0 else 0
        end = i + w
        end = end if end < (l-1) else (l-1)
        rv[i] = avf(v[start:end])
    return rv


def moving_weighted_average(v, window):

    assert isinstance(window, list)
    assert len(window) % 2 == 1

    half_window = int((len(window) - 1) // 2)

    l = len(v)
    rv = np.zeros(l)
    for i in range(len(v)):
        start = i - half_window
        wi = window

        if start < 0:
            wi = wi[-start:]
            start = 0

        end = i + half_window + 1
        if end > l-1:
            e = l-1-end
            wi = wi[:e]
            end = l-1

        rv[i] = np.sum(np.multiply(v[start:end], wi))
    return rv
