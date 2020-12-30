# rheoproc.dhrlog
# This file contains a class related to the processing of data from the DHR - a rheometer separate to the one I designed.

import tarfile
import os

import numpy as np

from rheoproc.genericlog import GenericLog
from rheoproc.filter import strip

def maybe_float(c):
    try:
        return float(c)
    except:
        return c

class DHRLog(GenericLog):

    def __init__(self, row, data_dir):
        
        self.path = os.path.join(data_dir, row['PATH'])
        self.members = list()
        member_data = dict()
        with tarfile.open(self.path) as tarf:
            members = tarf.getmembers()

            for member in members:
                memf = tarf.extractfile(member)
                lines = [line.decode().strip().replace('"', '') for line in memf.readlines()]
                memf.close()
                
                headers = [hdr.lower().replace(' ', '_').replace('shear', 'strain') for hdr in lines[0].split(',')]
                values = list(zip(*[[maybe_float(c) for c in line.split(',')] for line in lines[2:]]))
                member_data[member.name] = dict()
                for header, value in zip(headers, values):
                    member_data[member.name][header] = value
                self.members.append(member.name)

        self.member_data = member_data
        self.db_data = dict(row)
        self.ID = self.db_data['ID']
        self.material = self.db_data['MATERIAL']

    def get_start_time(self):
        return 0.0

    def get_stress_strainrate(self, filterf=None):
        stress = list()
        strainrate = list()
        viscosity = list()

        for member in self.members:
            stress.extend(self.member_data[member]['stress'])
            #strainrate.extend(self.member_data[member]['strain_rate'])
            viscosity.extend(self.member_data[member]['viscosity'])
        viscosity = np.divide(viscosity, 1000.0)
        strainrate = np.divide(stress, viscosity)

        if filterf:
            stripped = strip(stress, strainrate, viscosity, f=filterf)
            if not stripped:
                pass #raise Exception("no results returned from strip")
            else:
                stress, strainrate, viscosity = stripped

        return stress, strainrate, viscosity

    def get_stress_strainrate_viscosity(self):
        stress = list()
        strainrate = list()
        viscosity = list()

        for member in self.members:
            stress.extend(self.member_data[member]['stress'])
            strainrate.extend(self.member_data[member]['strain_rate'])
            viscosity.extend(self.member_data[member]['viscosity'])
        viscosity = np.divide(viscosity, 1000.0)

        return stress, strainrate, viscosity

    def get_prop(self, name):
        
        assert name in self.member_data[self.members[0]].keys()

        rv = list()
        for member in self.members:
            rv.extend(self.member_data[member][name])
        return rv
