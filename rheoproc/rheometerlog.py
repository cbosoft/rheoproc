# rheoproc.rheometerlog
# main log class handling the bulk of the processing.

import os
from time import time as now
import json
import tarfile
import sys
import re
from datetime import datetime

import numpy as np
import cv2 as cv

from rheoproc.accelproc import parse_csv
from rheoproc.error import timestamp, warning
from rheoproc.geometry import get_geometry
from rheoproc.calibration import apply_calibration
from rheoproc.viscosity import get_material_viscosity
from rheoproc.optenc import OpticalEncoderLog
from rheoproc.clean import clean_data
from rheoproc.exception import GenericRheoprocException, FileTypeError, PathNotAFileError, TimeRationalError
from rheoproc.genericlog import GenericLog
from rheoproc.varproplog import Categories
from rheoproc.videodata import VideoData
import rheoproc.nansafemath as ns
from rheoproc.software_versions import SW_VER_COMPLETE_LOG
from rheoproc.hardware_versions import HW_VER_PND_MONO, HW_VER_PND_SPLIT
from rheoproc.pnd import pnd_recombine
from rheoproc.rationalise import rat_times, recreate
from rheoproc.standard_wobble import subtract_standard_wobble


OPTENC_LOG_RE = re.compile(r'^(logs/)?rpir_.*_.*_opt(\d*)-(.*)\.csv$')
MAIN_LOG_RE = re.compile(r'^(logs/)?rpir_.*_.*\.csv$')
VIDEO_RE = re.compile(r'^(logs/)?rpir_.*_.*_video\.(mp4|h264)$')
PHOTO_RE = re.compile(r'^(logs/)?rpir_.*_.*_photo\.jpg$')
RUNPARAMS_RE = re.compile(r'^(logs/)?rpir_.*_.*_runparams\.json$')


class RheometerLog(GenericLog):


    acceptable_extensions = ['.tar', '.gz', '.bz2']


    def __init__(self, row, data_dir, *, quiet=True, very_quiet=False, **kwargs):
        super().__init__()
        self.quiet = quiet
        self.very_quiet = very_quiet
        self.parse_row(row, data_dir, **kwargs)
        data = self.process_data(**kwargs)
        self.set_data(data, **kwargs)


    def __repr__(self):
        return f'RheometerLog({{PATH={self.path}, ID={self.ID}, MATERIAL={self.material}, TAGS={";".join(self.tags)}}})'


    def parse_row(self, row, data_dir, **kwargs):

        path = os.path.join(data_dir, row['PATH'])

        if not os.path.isfile(path):
            raise PathNotAFileError(f'PATH must direct towards a file ({path}).')

        self.path = path
        basename = os.path.basename(path)
        name, ext = os.path.splitext(basename)

        if ext not in self.acceptable_extensions:
            raise FileTypeError(f"Log must be a (compressed) tar archive. Extension should be one of {self.acceptable_extensions}; was '{ext}'.")

        self.meta_data = dict(row)
        self.hardware_version = int(self.meta_data['HARDWARE VERSION'])
        self.software_version = int(self.meta_data['SOFTWARE VERSION'])
        self.geometry = get_geometry(self.hardware_version)
        self.material = self.meta_data['MATERIAL']
        self.motor = self.meta_data['MOTOR']
        self.ID = self.meta_data['ID']
        self.tags = self.meta_data['TAGS'].split(';')
        self.setpoint = self.meta_data['SETPOINT']
        self.date = datetime.strptime(self.meta_data['DATE'], '%Y-%m-%d')

        if self.meta_data['RECTANGLE OF INTEREST']:
            self.roi = json.loads(self.meta_data['RECTANGLE OF INTEREST'])
        else:
            self.roi = None

        if self.meta_data['LOADCELL CALIBRATION OVERRIDE']:
            self.timestamp("Using override calibration:")
            self.timestamp(' ', self.meta_data['LOADCELL CALIBRATION OVERRIDE'])
            self.override_calibration = json.loads(self.meta_data['LOADCELL CALIBRATION OVERRIDE'])
        else:
            self.override_calibration = None

    def timestamp(self, *args, **kwargs):
        if not self.quiet:
            timestamp(f'[{self.ID}]', *args, **kwargs)

    def warning(self, *args, **kwargs):
        if not self.very_quiet:
            warning(f'[{self.ID}]', *args, **kwargs)

    def process_data(self, read_video=False, read_photo=False, clean=True, calc_speed=True,
                     standard_wobble_method='subtract', **kwargs):
        self.timestamp('Processing RheometerLog')

        encoders = list()
        photos = list()
        run_params = dict()

        try:
            with tarfile.open(self.path, 'r:*') as tarlog:
                pass
        except tarfile.ReadError:
            print(self.ID, self.path)
            raise

        with tarfile.open(self.path, 'r:*') as tarlog:
            for member in tarlog.getmembers():
                if RUNPARAMS_RE.match(member.name):
                    with tarlog.extractfile(member) as _logfp:
                        run_params = json.load(_logfp)
                else:
                    pass

            self.run_params = run_params
            if 'fill_depth_mm' in run_params:
                self.fill_depth = run_params['fill_depth_mm']
            elif 'depth_mm' in run_params:
                self.fill_depth = run_params['depth_mm']
            else:
                self.warning('legacy log: no fill depth information available (using default of 73)')
                self.fill_depth = 73.0

            if 'needle_depth_mm' in run_params:
                self.needle_depth =  run_params['needle_depth_mm']
            else:
                self.warning('legacy log: no needle depth information available')

            for member in tarlog.getmembers():
                if OPTENC_LOG_RE.match(member.name):
                    with tarlog.extractfile(member) as logfp:
                        encoders.append(OpticalEncoderLog(logfp, self, **kwargs))
                elif MAIN_LOG_RE.match(member.name):
                    with tarlog.extractfile(member) as logfp:
                        lines = [l.decode('utf-8') for l in logfp.readlines()]
                elif RUNPARAMS_RE.match(member.name):
                    pass
                elif VIDEO_RE.match(member.name):
                    if read_video:
                        tarlog.extractall(path=f'/tmp', members=[member])
                        self.video = VideoData(
                            f'/tmp/{member.name}', 
                            mtime=datetime.fromtimestamp(member.mtime), 
                            rect_of_interest=self.roi,
                            db_data=self.meta_data,
                            run_params=run_params)
                    else:
                        self.warning(f"Log has video, but not reading it (arg 'read_video' is False).")
                elif PHOTO_RE.match(member.name):
                    if read_photo:
                        tarlog.extractall(path=f'/tmp', members=[member])
                        image = cv.imread(f'/tmp/{member.name}')
                        os.system(f'rm /tmp/{member.name}')
                        photos.append(image)
                    else:
                        self.warning(f"Log has a photograph, but not reading it (arg 'read_photo' is False).")
                else:
                    self.warning(f'Not processing unknown log contents: {member.name}')

        self.timestamp(f'Read tar: found {len(encoders)} encoders and a {len(lines)}pt long main log')
        dat = parse_csv(lines)

        ######### clean data based on swver
        clean_kwargs = dict(kwargs)
        if self.software_version >= SW_VER_COMPLETE_LOG:
            clean_kwargs['chop_first_seconds'] = 20
        else:
            clean_kwargs['chop_first_seconds'] = 0
            
        if clean:
            dat = clean_data(dat, **clean_kwargs) # CLEAN HERE
        ###########
            
        dat = np.array(dat)

        raw_time = dat[0]
        time = np.subtract(raw_time, raw_time[0])
        adc = np.array([np.array(a) for a in dat[1:9]])

        if HW_VER_PND_MONO <= self.hardware_version < HW_VER_PND_SPLIT:
            pnd = adc[1]
        elif HW_VER_PND_SPLIT <= self.hardware_version:
            pnd = pnd_recombine(adc[1], adc[2])
        else:
            pnd = np.array([])

        #ca = np.array(dat[9])
        if 20200908 <= self.software_version <= 20200910:
            self.warning(f'Logged using software ver {self.software_version} (between 20200908 and 20200910): fixing error in temp calc')
            broken_temp = dat[10]
            fixed_temp = np.zeros(len(broken_temp))
            for i, vi in enumerate(broken_temp):
                # fix misunderstood attempt to increase efficiency
                v16 = int(vi*16.0)
                lower = v16 & 127
                upper = (v16 >> 8) & 255
                v16nu = lower*16.0 + upper*0.0625
                fixed_temp[i] = v16nu
            temperature = fixed_temp
        else:
            temperature = dat[10]

        try:
            loadcell = dat[11]
        except IndexError:
            raise GenericRheoprocException("Log is TSTS log?") # TODO check and work around this

        lco_v, lco_t = rat_times(loadcell, time)
        self.stress_samplerate = 1./np.average(np.diff(lco_t))
        self.samplerate = 1./np.average(np.diff(time))
        self.recreated_loadcell = True
        try:
            loadcell = recreate(time, loadcell, loadcell, kind='linear')
        except ValueError as ve:
            self.warning('loadcell can\'t be recreated: may be faulty!')
            self.recreated_loadcell = False
        except Exception as e:
            #loadcell = recreate(time, loadcell, loadcell, kind='linear')
            print(self.ID)
            raise e

        if len(dat) > 12:
            ambient_temperature = dat[12]
        else:
            ambient_temperature = [np.nan for __ in temperature]

        if not encoders:
            raise GenericRheoprocException("No optical encoder logs")

        speed = np.zeros(np.shape(raw_time))

        if calc_speed:
            for encoder in encoders:
                encoder.calc_speed() # speed in ROT/S
                speed = np.add(speed, encoder.speed_in_alt_time(raw_time))
            speed = np.divide(speed, float(len(encoders)))

        if np.any(np.isnan(speed)):
            raise Exception('NaN speed')

        if (lt := len(raw_time)) != (ls := len(speed)):
            raise TimeRationalError(f'Time array and speed array must match lengths ({lt} != {ls}); something has gone wrong.')

        RIN = self.geometry['RIN']
        ROUT = self.geometry['ROUT']
        # speed in rot/s, multiply by circumference to get m/s
        speed_ms = np.multiply(speed, 2.0*np.pi*RIN) # m/s

        gap = ROUT - RIN
        strainrate = np.divide(speed_ms, gap) # inverse seconds
        # strainrate is calculated in inverse seconds (C/G/s) where C is circumference in m and G is gap size in m

        strain = list()
        dt = np.diff(time)
        strain.append(np.average(dt) * strainrate[0])
        for dti, gdi in zip(dt, strainrate[1:]):
            strain.append(dti*gdi + strain[-1])
        # strain is in C/Gs - unitless!

        position = list()
        position.append(np.average(dt) * speed[0]) # speed in rot/s
        for dti, spi in zip(dt, speed[1:]):
            position.append(dti*spi + position[-1])
        # position in rotations

        if standard_wobble_method == 'subtract':
            loadcell = subtract_standard_wobble(position, loadcell, self.motor)

        load_torque = apply_calibration(loadcell, speed, self.override_calibration, self.date)
        stress = ns.divide(load_torque, 2.0*np.pi*RIN*RIN*(0.001*self.fill_depth))

        viscosity = ns.divide(stress, strainrate)
        expected_viscosity = get_material_viscosity(self.material, np.array(temperature, dtype=np.float64))
        self.timestamp('Processing complete')

        data = {
            'rheology': {
                'viscosity': (viscosity, 'both'),
                'expected_viscosity': (expected_viscosity, 'both'),
                'strainrate': (strainrate, 'both'),
                'stress': (stress, 'both'),
                'strain': (strain, 'both'),
                'pnd' : (pnd, 'none')
            },
            'intermediates': {
                'speed': (speed, 'both'),
                'position': (position, 'none'),
                'load_torque': (load_torque, 'both')
            },
            'sensors': {
                'loadcell': (loadcell, 'both'),
                'temperature': (temperature, 'both'),
                'ambient_temperature': (ambient_temperature, 'both'),
                'adc': (adc, 'none'),
                'photos': (photos, 'none')
            },
            'required': {
                'time': (time, 'none'),
                'raw_time': (raw_time, 'average'),
            },
            'misc' : {
                'encoders': (encoders, 'none'),
            }
        }

        for category, cat_data in list(data.items()):
            for name, (value, stats) in list(cat_data.items()):
                if stats in ['average', 'both']:
                    data[category][f'{name}_av'] = (ns.average(value), 'na')
                if stats in ['deviation', 'both']:
                    data[category][f'{name}_std'] = (ns.std(value), 'na')

        return data


    def set_data(self, data, categories=Categories.ALL, averages_only=False, **kwargs):

        self.cat = categories

        assert isinstance(categories, Categories)

        if categories == Categories.RHEOLOGY_ONLY:
            categories = ['rheology']
        elif categories == Categories.INTERMEDIATES_ONLY:
            categories = ['intermediates']
        elif categories == Categories.SENSORS_ONLY:
            categories = ['sensors']
        elif categories == Categories.RHEOLOGY_AND_SENSORS:
            categories = ['rheology', 'sensors']
        elif categories == Categories.ALL:
            categories = ['rheology', 'intermediates', 'sensors', 'misc']
        else:
            raise Exception('Unrecognized category enum: {categories}. (Did you forget to update set_data after increasing scope of Categories?)')

        assert isinstance(categories, list)
        for cat in categories:
            assert isinstance(cat, str)
        
        self.data = dict()
        for category, cat_data in data.items():
            if category in categories or category == 'required':
                for name, (value, stats) in cat_data.items():
                    if averages_only:
                        if not (name.endswith('_av') or name.endswith('_std') or category == 'required'):
                            continue
                    try:
                        len(value)
                        self.data[name] = np.array(value, np.float64)
                    except:
                        self.data[name] = value

    def __sizeof__(self):
        total = 0
        for attr in dir(self):
            total += sys.getsizeof(getattr(self, attr))
        return total


    def get_start_time(self):
        try:
            return self.raw_time[0]
        except IndexError:
            return -1


    def get_end_time(self):
        try:
            return self.raw_time[-1]
        except IndexError:
            return -1

    def get_annular_area(self):
        rin = self.geometry['RIN']
        rout = self.geometry['ROUT']
        return (rout*rout - rin*rin)*np.pi

    def get_volume(self, unit='m3'):
        V_l = self.fill_depth*self.get_annular_area()

        if unit == 'm3':
            return V_l*0.001

        if unit == 'l':
            return V_l

        raise Exception(f'Unknown volume unit {unit} (valid units are "l" or "m3")')
        


### I don't think this is useful
## class RawRheometerLog(RheometerLog):
##     
##     def process_data(self, quiet=True, **kwargs):
##         if not quiet: timestamp(f"init new RawRheometerLog (DBID={self.ID})")
##         start = now() # time.time()
## 
##         if not quiet: timestamp('Reading tarfile')
##         
##         with tarfile.open(self.path, 'r:*') as tarlog:
##             for member in tarlog.getmembers():
##                 if OPTENC_LOG_RE.match(member.name):
##                     if not quiet: timestamp('Found optical encoder: ignoring')
##                 elif MAIN_LOG_RE.match(member.name):
##                     if not quiet: timestamp('Found main log')
##                     with tarlog.extractfile(member) as logfp:
##                         lines = [l.decode('utf-8') for l in logfp.readlines()]
##                     if not quiet: timestamp('--> done')
##                 elif RUNPARAMS_RE.match(member.name):
##                     with tarlog.extractfile(member) as _logfp:
##                         run_params = json.load(_logfp)
##                 elif VIDEO_RE.match(member.name):
##                     if not quiet: timestamp(f"Found video: ignoring.")
##                 else:
##                     warning(f'Not processing unknown log contents: {member.name}')
## 
##         if not quiet: timestamp('Sorting main csv data')
##         dat = parse_csv(lines)
##         if int(self.meta_data['HARDWARE VERSION']) >= 20190912: dat = clean_data(dat)
##         dat = np.array(dat)
##         if not quiet: timestamp('--> done')
## 
##         raw_time = dat[0]
##         time = np.subtract(raw_time, raw_time[0])
##         adc = np.array([np.array(a) for a in dat[1:9]])
##         ca = np.array(dat[9])
##         temperature = np.array(dat[10])
##         loadcell = dat[11]
## 
##         data = {
##             'sensors': {
##                 'time': (time, 'none'),
##                 'raw_time': (raw_time, 'average'),
##                 'loadcell': (loadcell, 'both'),
##                 'temperature': (temperature, 'both'),
##                 'adc': (adc, 'none')
##             }
##         }
## 
##         for category, cat_data in list(data.items()):
##             for name, (value, stats) in list(cat_data.items()):
##                 if stats in ['average', 'both']:
##                     data[category][f'{name}_av'] = (np.average(value), 'na')
##                 if stats in ['deviation', 'both']:
##                     data[category][f'{name}_std'] = (np.std(value), 'na')
## 
##         return data
## 
##     def set_data(self, data, categories=['rheology'], **kwargs):
##         for category, cat_data in list(data.items()):
##             for name, (value, stats) in list(cat_data.items()):
##                 setattr(self, name, value)
