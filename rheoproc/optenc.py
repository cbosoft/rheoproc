import numpy as np
from matplotlib import pyplot as plt

from rheoproc.accelproc import clean_optenc_events, speed_from_optenc_events
from rheoproc.filter import moving_average
from rheoproc.exception import ZeroSpeedError


class OpticalEncoderLog:
    '''
    Object holding information about an optical encoder log. Provides methods 
    for calulating speed and interpolating that speed for an alternative time.
    '''

    def __init__(self, optenc_log_object, parent_log, optenc_devent_thresh=0.3, **kwargs):
        self.parent_log = parent_log
        self.raw_events = [float(l.decode("utf-8")) for l in optenc_log_object.readlines()]
        self.events = clean_optenc_events(self.raw_events)

        # TODO: move this to .c (combine with current cleaning function) ->
        # get rate of change of event, normalise
        de = np.diff(self.events)
        mde = np.mean(de)
        mde = np.abs(np.divide(np.subtract(de, mde), mde))

        # strip changes that are too large or small
        # i.e. more than $optenc_devent_thresh
        de = [di for di, mdi in zip(de, mde) if mdi < optenc_devent_thresh]

        # recombine derivatives, convert to list (required for speed calc).
        self.events = list(np.add(self.events[0], np.cumsum(de)))
        # <-


    def calc_speed(self):
        '''
        Calculates the speed of rotation for the list of events held by this log.
        '''
        if any([e == 0.0 for e in self.events]):
            raise ZeroSpeedError(f"Corrupt log (zero event found). {self.parent_log}")

        self.speed = speed_from_optenc_events(self.events)
        if any([s == 0.0 for s in self.speed]):
            raise ZeroSpeedError(f"Corrupt speed calc (zero speed found). {self.parent_log}")


    def speed_in_alt_time(self, alt_time):
        '''
        Interpolates the speed.
        '''

        if len(self.speed) == 0:
            return np.array([np.nan]*len(alt_time))

        arr_alt = np.array(alt_time, dtype=np.float64)
        spd_in_alt = np.interp(
            np.array(alt_time, dtype=np.float64),
            np.array(self.events, dtype=np.float64),
            np.array(self.speed, dtype=np.float64))
        return spd_in_alt
