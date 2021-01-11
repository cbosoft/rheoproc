# rheoproc.peakdet
# Wrapper around the accelproc fast peak detection function

from rheoproc.accelproc import peak_detect

def get_peaks(t, v, threshold:float=0.0015, mode:str='positive', negative_peaks:[None,bool]=None, indices_output:bool=False):
    '''
    Given a signal, obtain a list of where the peaks occur.

    mode is one of ['positive', 'negative', 'both'] and describes the direction in which to detect peaks.
    For compatibility, if negative_peaks is set, this overrides the mode.

    If index output is desired rather than timepoints, set indices_output to True.
    '''

    peakdet_mode = 0
    if mode:
        if not mode in ['positive', 'negative', 'both']:
            raise Exception(f'Peakdet mode must be one of [\'positive\', \'negative\', \'both\']. Got {mode}.')
        if mode == 'negative':
            peakdet_mode = 1
        elif mode == 'both':
            peakdet_mode = 2

    if negative_peaks is not None:
        peakdet_mode = int(negative_peaks)
    return peak_detect(list(t), list(v), threshold, peakdet_mode, indices_output)
