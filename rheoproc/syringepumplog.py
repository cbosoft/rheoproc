# rheoproc.syringepumplog
# a class for managing the loading of data logged using another rheometer I built (https://github.com/syringepump).

import os
import time
import json
import tarfile
import sys
import re

import numpy as np

from rheoproc.accelproc import parse_csv, filter_loadcell
from rheoproc.error import timestamp, warning
from rheoproc.geometry import get_geometry
from rheoproc.viscosity import get_material_viscosity
from rheoproc.optenc import OpticalEncoderLog
from rheoproc.clean import clean_data
from rheoproc.exception import FileTypeError
from rheoproc.util import is_number
from rheoproc.genericlog import GenericLog




class SyringepumpLog(GenericLog):

    acceptable_extensions = ['.csv']

    def __init__(self, row, data_dir):

        path = os.path.join(data_dir, row['PATH'])
        assert os.path.isfile(path)
        self.path = path
        basename = os.path.basename(path)
        name, ext = os.path.splitext(basename)

        self.db_data = dict(row)

        if ext not in self.acceptable_extensions:
            raise FileTypeError(f"Log must be a (compressed) tar archive. Extension should be one of {self.acceptable_extensions}; was '{ext}'.")

        with open(path) as csvf:
            lines = csvf.readlines()

        firstline = 0
        for i, line in enumerate(lines):
            if line.startswith('Time'):
                firstline = i

        headings = [hdg[:hdg.index('(')].lower().strip().replace(' ', '_') for hdg in lines[firstline].split(',')]

        meta_data = lines[:firstline]
        if meta_data:
            meta_data = [line.split(',') for line in lines if line]
        else:
            meta_data = [pair.split('=') for pair in row['PATH'].split('_')[2].split('-') if '=' in pair]

        self.meta_data = dict()
        for key, value in meta_data:
            self.meta_data[key] = value

        lines = lines[firstline+1:]
        data = list(zip(*[[float(c) for c in line.split(',')] for line in lines]))

        for heading, dat in zip(headings, data):
            setattr(self, heading, dat)
