from tdlib.accelproc import peak_detect

def get_peaks(t, v, threshold=0.0015):
    '''
    Given a signal, obtain a list of where the peaks occur.
    '''
    return peak_detect(list(t), list(v), threshold)
