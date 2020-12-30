# rheoproc.peakdet
# Wrapper around the accelproc fast peak detection function

from rheoproc.accelproc import peak_detect

def get_peaks(t, v, threshold=0.0015, negative_peaks=False):
    '''
    Given a signal, obtain a list of where the peaks occur.
    '''
    return peak_detect(list(t), list(v), threshold, negative_peaks)
