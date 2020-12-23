import numpy as np

from rheoproc.accelproc import filter_loadcell
from rheoproc.filter import strip


def clean_data(data, *, chop_first_seconds=0, strip_errors=False, acctdlib_lcfilt_same_thresh=100, **kwargs):
    '''
    remove errored loadcell data from data table (column-major). error prone
    data is replaced with Nones, or relevant rows are stripped (depending on arg
    STRIP_ERRORS).
    '''
    
    loadcell = list(data[11])
    filter_loadcell(loadcell, acctdlib_lcfilt_same_thresh)
    data[11] = np.array(loadcell)

    if strip_errors:
        # todel = list(reversed([i for i, l in enumerate(loadcell) if l is None]))
        # for i, dummy in enumerate(data):
        #     for deli in todel:
        #         data[i].pop(deli)
        data = strip(*data, f=lambda row: all([not np.isnan(rowi) for rowi in row]))
        if np.any(np.isnan(data)):
            print('NAN AFTER STRIP :(')


    if chop_first_seconds:
        init_time = data[0][0]
        data = strip(*data, f=lambda row: row[0] - init_time > chop_first_seconds)

    data = np.array(data, dtype=np.float64)

    return data
