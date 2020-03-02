import os
import time
import json
import tarfile
import sys
import re

import numpy as np

from rheoproc.exception import FileTypeError
from rheoproc.genericlog import GenericLog




class HistoricRheometerLog:

    acceptable_extensions = ['.csv']

    def __init__(self, row, data_dir):

        path = os.path.join(data_dir, row['PATH'])
        assert os.path.isfile(path)
        self.path = path
        basename = os.path.basename(path)
        name, ext = os.path.splitext(basename)
        self.ID = row['ID']

        __, __, gap_s, vf_and_c = name.split('_')
        self.gap = float(gap_s[:-2]) * 0.001 # from mm to m
        vf_pmma = int(vf_and_c[:-1])
        vf_solvent = 100 - vf_pmma
        self.material = f'PMMA{vf_pmma}:DT{vf_solvent}'
        self.vf = vf_pmma
        self.c = int(vf_and_c[-1])

        self.db_data = dict(row)

        if ext not in self.acceptable_extensions:
            raise FileTypeError(f"Log must be a comma-separeted-value file (.csv). Got: '{ext}'.")

        with open(path) as csvf:
            lines = csvf.readlines()

        data = [[float(c) for c in r.split(',')] for r in lines]
        self.data = list(zip(*data))
        self.time = self.data[0]
        self.voltage = self.data[1]
