import numpy as np
#import nfft # bonus points for accounting for off-grid

from rheoproc.filter import strip

def get_fftx(t, regularise=True, chunks=1, **kwargs):
    l = len(t) // chunks
    dt = np.mean(np.diff(t))
    fft_x = np.fft.fftfreq(l, d=dt)
    if regularise:
        fft_x = np.abs(fft_x)
        fft_x[0] = np.nan
    return fft_x


def get_ffty(t, y, regularise=True, chunks=1, trim_baseline=True):

    if trim_baseline:
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
        fft_y = np.power(np.real(fft_y), 2.0)
    return fft_y



def fft(t, *ys, **kwargs):
    ''' returns the x- and y-data for the fast fourier transform of given timeseries (t,y).'''

    t_and_ys = strip(t, *ys, f=lambda r: not np.isnan(r[1]))
    if not len(t_and_ys):
        raise Exception("all res are nans")

    t = t_and_ys[0]
    ys = t_and_ys[1:]

    fft_ys = [get_ffty(t, y, **kwargs) for y in ys]
    fft_x = get_fftx(t, **kwargs)

    if len(fft_ys) > 1:
        return fft_x, fft_ys
    return fft_x, fft_y

def psd(t, y):
    '''calculates the power-spectrum-density of a signal y in t using the FFT.'''
    # https://dsp.stackexchange.com/questions/24780/power-spectral-density-vs-fft-bin-magnitude
    fftx, ffty = fft(t, y)
    psd = np.divide(np.power(ffty, 2.0), y.size)
    return fftx, psd
