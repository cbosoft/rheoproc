import os
from datetime import datetime, timedelta
import time
import json

import cv2
import numpy as np

from rheoproc.genericlog import GenericLog
from rheoproc.util import runsh, bash_safe
from rheoproc.progress import ProgressBar


class Video(GenericLog):


    def __init__(self, row, data_dir):

        self.path = os.path.join(data_dir, row['PATH'])
        self.db_data = dict(row)

        roi = json.loads(row['RECT OF INTEREST'])
        self.rect_of_interest = roi['x'], roi['y'], roi['w'], roi['h']
        print(self.rect_of_interest)
        self.ref_z = roi['refz']
        self.scale = roi['scale']

        self.relevant_log_id = int(row['LOG ID'])

        __, ffmpeg_lines = runsh(f'ffmpeg -i {bash_safe(self.path)}', output='both')

        trim_from = -1
        trim_to = -1
        for i, line in enumerate(ffmpeg_lines):
            if trim_from == -1:
                if 'Input' in line:
                    trim_from = i
            elif trim_to == -1:
                if ':' not in line:
                    trim_to = i
                    break
        ffmpeg_lines = ffmpeg_lines[trim_from:trim_to]
        
        self.meta_data = dict()
        for line in ffmpeg_lines:
            print(line)
            key, value = line.split(':', 1)
            if not value:
                continue

            key = key.strip()
            value = value.strip()
            if key in self.meta_data:
                pv = self.meta_data[key]
                if isinstance(pv, list):
                    self.meta_data[key].append(value)
                else:
                    self.meta_data[key] = [pv, value]
            else:
                self.meta_data[key] = value

        for stream in self.meta_data['Stream #0']:
            if 'Video' in stream:
                i = stream.index('fps')
                fps = stream[i-3:i]
                self.fps = float(fps)
        
        duration_str = self.meta_data['Duration']
        duration_str = duration_str[:duration_str.index(',')]
        self.duration = datetime.strptime(f'1970-01-01T{duration_str}', '%Y-%m-%dT%H:%M:%S.%f')
        self.duration = timedelta(0, 
                (self.duration.minute*60.0) + 
                (self.duration.second) + 
                (self.duration.microsecond*1e-6))

        try:
            self.endtime = datetime.strptime(self.meta_data['creation_time'][0], '%Y-%m-%dT%H:%M:%S.%fZ')
            is_dst = time.localtime(self.endtime.timestamp()).tm_isdst
            if is_dst == 1:
                self.endtime += timedelta(0, 3600)
            self.starttime = self.endtime - self.duration
        except KeyError:
            self.starttime = -1
            self.endtime = -1

        cap = cv2.VideoCapture(self.path)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.framecount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap.release()

        self.thresh = None
        self.height_timeseries = None
        self.get_height_timeseries()


    def get_frame(self, limit=None):
        cap = cv2.VideoCapture(self.path)
        
        i = 0
        while True:
            success, frame = cap.read()
            i += 1
            if success:
                yield frame
            else:
                break

            if isinstance(limit, int) and i >= limit:
                break
        cap.release()


    def get_rectangle_of_interest(self, limit=None):

        x, y, w, h = self.rect_of_interest

        cap = cv2.VideoCapture(self.path)

        i = 0
        while True:
            success, frame = cap.read()
            i += 1
            if success:
                yield frame[y:y+h, x:x+w]
            else:
                break

            if isinstance(limit, int) and i >= limit:
                break
        cap.release()


    def measure_height(self, roi, thresh=None): 
        '''If video is of rheometer, use this function to measure height of CS
        above the rim of the Couette'''

        roi = cv2.bilateralFilter(roi, 9, 75, 75)
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(roi)
        roi = v


        avy = np.average(roi, axis=1)
        avy = list(reversed(avy))
        if not thresh:
            if not self.thresh:
                self.thresh = np.average(avy)*1.1
            thresh = self.thresh

        h = self.rect_of_interest[3]
        y = self.rect_of_interest[1]

        yv = None
        vp = avy[0]
        for i, v in enumerate(avy):
            if v < thresh:
                yv = h - i
                break
        self.yv = yv

        dist_rty = self.ref_z - y - yv
        dist_rty = dist_rty*self.scale
        return dist_rty


    def get_height_timeseries(self, limit=None, recalc=False, progress='none'):

        if self.height_timeseries and not recalc:
            return self.height_timeseries

        assert progress in ['none', 'bar']

        if progress == 'bar':
            if limit:
                progress = ProgressBar(limit)
            else:
                progress = ProgressBar(self.estimate_number_frames())
        else:
            progress = False


        height = list()
        time = list()
        tz = self.starttime.timestamp()
        for i, roi in enumerate(self.get_rectangle_of_interest()):
            if progress and i % 10 == 0:
                progress.update(i)
            height.append(self.measure_height(roi))
            time.append(tz+(i/self.fps))
            if limit and i >= limit:
                break

        self.height_timeseries = [time, height]
        return time, height


    def get_start_time(self):
        return self.starttime.timestamp()
