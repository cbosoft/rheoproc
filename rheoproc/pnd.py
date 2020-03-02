import numpy as np


def pnd_recombine(channel1, channel2):
    '''
    Recombine the two separate unsigned PND channels (+ve, -ve) into a single signed channel.
    '''
    #TODO: improve this
    return convert_bit_to_volts(np.subtract(channel1, channel2), bit_length=12, max_voltage=3.3)


def convert_bit_to_volts(b, *, bit_length, max_voltage):
    '''
    Convert a signal from n-bit number to a voltage.
    '''
    max_b = (2 << bit_length) - 1
    return np.multiply(np.divie(b, max_b), max_voltage)
