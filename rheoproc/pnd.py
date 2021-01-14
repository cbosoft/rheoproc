# rheoproc.pnd
# file containing a method for converting the dual (unsigned) channel novel piezoelectric-needle device (PND) to
# single (signed) channel.

import numpy as np


def pnd_recombine(channel1, channel2):
    '''
    Recombine the two separate unsigned PND channels (+ve, -ve) into a single signed channel.
    '''
    return np.subtract(channel1, channel2)
