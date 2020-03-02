from rheoproc.accelproc import tcorr

def get_time_corr(t, v, *, bin_width=None, width_factor=0.0005, max_lag=20.0):
    t, v = zip(*sorted(zip(t, v)))
    t = list(t)
    v = list(v)
    return tcorr(t, v, bin_width if bin_width is not None else -1.0, max_lag, width_factor)
