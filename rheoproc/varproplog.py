from enum import Enum, auto

import numpy as np

from rheoproc.exception import CategoryError
import rheoproc.nonesafemath as ns

class Categories(Enum):
    RHEOLOGY_ONLY = auto()
    INTERMEDIATES_ONLY = auto()
    SENSORS_ONLY = auto()
    RHEOLOGY_AND_SENSORS = auto()
    ALL = auto()

class VariablePropertiesLog:
    '''Class which holds information that may or may not be available. If the data
    is not available, a helpful error message is raised. Otherwise, the data is
    returned.

    Rheological and sensor data may or may not be available from a log file
    depending on how it was processed. This virtual class provides a consistent
    interface to the data as properties of the object, while providing better
    feedback in the case where the requested member is not available (i.e. it
    doesn't just say "KeyError" or "ArgumentError" it informs that the correct
    settings were not given to the log constructor and so the data were not kept.
    '''

    def __init__(self, **kwargs):
        self.data = dict()
        self.cat = None
    
    @property
    def speed(self):
        return self.get('speed')
    
    @property
    def speed_av(self):
        return self.get('speed_av')
    
    @property
    def speed_std(self):
        return self.get('speed_std')

    
    @property
    def loadcell(self):
        return self.get('loadcell')
    
    @property
    def loadcell_av(self):
        return self.get('loadcell_av')
    
    @property
    def loadcell_std(self):
        return self.get('loadcell_std')

    
    @property
    def viscosity(self):
        return self.get('viscosity')

    @viscosity.setter
    def viscosity(self, value):
        self.set('viscosity', value)
    
    @property
    def viscosity_av(self):
        return self.get('viscosity_av')
    
    @property
    def viscosity_std(self):
        return self.get('viscosity_std')

    
    @property
    def stress(self):
        return self.get('stress')
    
    @property
    def stress_av(self):
        return self.get('stress_av')
    
    @property
    def stress_std(self):
        return self.get('stress_std')

    
    @property
    def strainrate(self):
        return self.get('strainrate')
    
    @property
    def strainrate_av(self):
        return self.get('strainrate_av')
    
    @property
    def strainrate_std(self):
        return self.get('strainrate_std')

    
    @property
    def time(self):
        return self.get('time')
    
    @property
    def raw_time(self):
        return self.get('raw_time')

    @property
    def adc(self):
        return self.get('adc')

    @property
    def pnd(self):
        return self.get('pnd')

    
    @property
    def expected_viscosity(self):
        return self.get('expected_viscosity')

    @property
    def expected_viscosity_av(self):
        return self.get('expected_viscosity_av')

    @property
    def expected_viscosity_std(self):
        return self.get('expected_viscosity_std')


    @property
    def temperature(self):
        return self.get('temperature')

    @property
    def temperature_av(self):
        return self.get('temperature_av')

    @property
    def temperature_std(self):
        return self.get('temperature_std')

    @property
    def encoders(self):
        return self.get('encoders')

    @property
    def photos(self):
        return self.get('photos')

    def get(self, prop):
        try:
            return np.array(self.data[prop])
        except KeyError as e:
            # TODO: generate error details once
            details  = f'Requested property "{prop}" cannot be found, '
            details += 'were the correct categories set?\n'
            details += f'Got category: {self.cat}.'
            details += 'Categories:\n'
            for cat in list(Categories):
                details += f'  {cat}'
            raise CategoryError(details) from e

    def set(self, prop, value):
        self.data[prop] = value

        if (key := f'{prop}_av') in self.data:
            self.data[key] = ns.average(value)

        if (key := f'{prop}_std') in self.data:
            self.data[key] = ns.std(value)


