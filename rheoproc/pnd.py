import numpy as np
from rheoproc.util import convert_bit_to_volts


def pnd_recombine(channel1, channel2):
    '''
    Recombine the two separate unsigned PND channels (+ve, -ve) into a single signed channel.
    '''
    #TODO: improve this
    return convert_bit_to_volts(np.subtract(channel1, channel2), bit_length=12, max_voltage=3.3)
