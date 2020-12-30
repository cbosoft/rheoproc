# rheproc.progress
# flexible progress indicator class

import os
from threading import Lock

from rheoproc.error import __print as raw_print, timestamp

class ProgressBar:

    def __init__(self, length, info_func=None):
        self.length = length
        self.pos = -1
        self.lock = Lock()
        self.columns = int(os.popen('stty size', 'r').read().split()[1])
        self.info_func = info_func

    def update(self, i=None):

        try:
            self.lock.acquire(timeout=10)
        except:
            return

        if i is None:
            i = self.pos + 1

        if self.info_func:
            info = self.info_func(self.length, i)
            info = f'▌{info}▐'
        else:
            info = f'▌{i+1}/{self.length}▐'
        columns = self.columns - len(info)
        col_per_i = columns / self.length
        prog = int(col_per_i * (i+1))
        prog = info.rjust(prog-1, '█') + '█'
        end = '' if i < self.length-1 else '\n'
        print(f'█{prog}\r', end=end)

        self.pos = i
        self.lock.release()

    def clear(self):
        print('\u001b[2K', end='')

    def print(self, *args, **kwargs):
        self.clear()
        raw_print(*args, **kwargs)
        self.update(self.pos)
