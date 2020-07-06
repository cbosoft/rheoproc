import numpy as np
#import nfft # bonus points for accounting for off-grid

from rheoproc.filter import strip

def fft(t, *ys, regularise=True, chunks=1):
    ''' returns the x- and y-data for the fast fourier transform of given timeseries (t,y).'''

    t = np.array(t, dtype=np.float64)
    dt = np.average(np.diff(t))

    t_and_ys = strip(t, *ys, f=lambda r: not np.isnan(r[1]))
    if not len(t_and_ys):
        raise Exception("all res are nans")

    t = t_and_ys[0]
    ys = t_and_ys[1:]

    fft_ys = list()
    for y in ys:
        y = np.array(y, dtype=np.float64)
        (m, c) = np.polyfit(t, y, 1)

        bfline = np.add(np.multiply(t, m), c)
        y = np.subtract(y, bfline)

        chunklen = len(y)//chunks
        ys = list()
        for i in range(chunks):
            ys.append(y[chunklen*i:chunklen*(i+1)])
        ys = np.array(ys, dtype=np.float64)
        y = np.average(ys, axis=0)
        fft_y = np.fft.fft(y)
        if regularise:
            fft_y = np.abs(fft_y)[1:]
        fft_ys.append(fft_y)


    fft_x = np.fft.fftfreq(len(y), d=dt)
    if regularise:
        fft_x = np.abs(fft_x)[1:]

    if len(fft_ys) > 1:
        return fft_x, fft_ys
    return fft_x, fft_y

def psd(t, y):
    '''calculates the power-spectrum-density of a signal y in t using the FFT.'''
    # https://dsp.stackexchange.com/questions/24780/power-spectral-density-vs-fft-bin-magnitude
    fftx, ffty = fft(t, y)
    psd = np.divide(np.power(ffty, 2.0), y.size)
    return fftx, psd
