# rheoproc.combined
# Contains class and functions related to creating a combined log from multiple sources - can be useful when desiring a
# mean view of a dataset.

from collections import defaultdict

import numpy as np

from rheoproc.genericlog import GenericLog
from rheoproc.varproplog import VariablePropertiesLog



def empty_numpy_array():
    return np.array([])




def defaultdict_list_factory():
    return defaultdict(empty_numpy_array)




def by_viscosity(log):
    return np.average(log.viscosity)




def by_starttime(log):
    return log.get_start_time()




class CombinedLogs(VariablePropertiesLog):

    def __init__(self, sortf=by_starttime, **kwargs):
        super().__init__(**kwargs)
        self.logs = list()
        self.materials = list()
        self.by_material = defaultdict(defaultdict_list_factory)
        self.sortf = sortf

    def __iter__(self):
        return iter(self.logs)


    def __len__(self):
        return len(self.logs)


    def __getitem__(self, key):
        
        if isinstance(key, str):
            if key in self.by_material:
                return self.by_material[key]
            raise KeyError(f"Key ({key}) not in materials dict")
        
        if isinstance(key, (int, slice)):
            return self.logs[key]
        
        raise Exception(f"CombinedLogs can act as a dictionary of data with materials (string) as keys, or as a list of logs with indexes (int) as keys. Type(Key)={type(key)} not understoond.")


    def append(self, log):

        assert issubclass(type(log), GenericLog)

        self.logs.append(log)
        self.logs = sorted(self.logs, key=self.sortf)


        for key, value in log.data.items():

            # don't deal with adc stuff
            if key in ['adc']:
                continue

            # if not array, or float, ignore
            # if float, make array of one value
            if isinstance(value, (np.ndarray, list) ):
                pass
            elif isinstance(value, (np.float, np.float64, np.float32, np.float16, float) ):
                value = [value]
            else:
                continue

            # if attr exists in self: append, otherwise create empty array
            try:
                combined_value = self.data[key]
            except KeyError:
                combined_value = empty_numpy_array()

            self.data[key] = np.concatenate((combined_value, value))
            self.by_material[log.material][key] = np.concatenate((self.by_material[log.material][key], value))


    def get_materials(self):
        materials = list(self.by_material.keys())
        materials = sorted(materials, key=lambda x: np.average(self.by_material[x]['viscosity']))
        return materials

