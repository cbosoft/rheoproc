# rheoproc.videodata
# used for processing the data of a single video, unlike video log which has video contained within a tarfile log.

import os
from datetime import datetime, timedelta
import time
import json

import cv2
import numpy as np

from rheoproc.genericlog import GenericLog
from rheoproc.util import runsh, bash_safe



class VideoData:

    def __init__(self, path, data_dir, *, rect_of_interest, run_params, mtime=None, db_data=None):

        self.path = path
        self.db_data = db_data
        if rect_of_interest:
            self.rect_of_interest = (
                rect_of_interest['x'],
                rect_of_interest['y'],
                rect_of_interest['w'],
                rect_of_interest['h'] )
            self.ref_z = rect_of_interest['refz']
            self.scale = rect_of_interest['scale']

        self.start_time = run_params['video_start']
        self.end_time = run_params['video_end']
        
        cap = cv2.VideoCapture(self.path)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap.release()

        self.frame_count = 0
        for frame in self.get_frames():
            self.frame_count += 1
        self.duration = self.frame_count / self.fps

        self.thresh = None
        self.height_timeseries = None


    def get_frames(self, limit=None):
        cap = cv2.VideoCapture(self.path)

        assert isinstance(limit, int) or limit is None
        
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

    def get_rectangle_of_interest(self, limit=None):
        cap = cv2.VideoCapture(self.path)

        x, y, w, h = self.rect_of_interest

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

    def measure_height(self, roi, thresh=None): 
        '''If video is of rheometer, use this function to measure height of CS
        above the rim of the Couette'''

        roi = cv2.bilateralFilter(roi, 9, 75, 75)
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(roi)
        roi = v

        x, y, w, h = self.rect_of_interest

        avy = np.average(roi, axis=1)
        avy = list(reversed(avy))
        if not thresh:
            if not self.thresh:
                self.thresh = np.average(avy)*1.1
            thresh = self.thresh

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

    def get_height_timeseries(self):
        if self.height_timeseries:
            return self.height_timeseries

        height = list()
        time = list()
        tz = self.start_time
        for i, roi in enumerate(self.get_rectangle_of_interest()):
            height.append(self.measure_height(roi))
            time.append(tz+(i/self.fps))

        self.height_timeseries = [time, height]
        return time, height

    def get_start_time(self):
        return self.start_time
