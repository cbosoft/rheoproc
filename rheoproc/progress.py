import os
from threading import Lock

from rheoproc.error import __print as raw_print, timestamp

class ProgressBar:

    def __init__(self, length):
        self.length = length
        self.pos = -1
        self.lock = Lock()
        self.columns = int(os.popen('stty size', 'r').read().split()[1])

    def update(self, i=None):

        try:
            self.lock.acquire(timeout=10)
        except:
            return

        if i is None:
            i = self.pos + 1

        frac = f'▌{i+1}/{self.length}▐'
        timestamp_ex = "  (10/30/19 15:57:02.659921) "
        columns = self.columns - len(frac) - len(timestamp_ex)
        col_per_i = columns / self.length
        prog = int(col_per_i * (i+1))
        prog = frac.rjust(prog-1, '█') + '█'
        end = '' if i < self.length-1 else '\n'
        timestamp(f'█{prog}\r', end=end)

        self.pos = i
        self.lock.release()

    def clear(self):
        print('\u001b[2K', end='')

    def print(self, *args, **kwargs):
        self.clear()
        raw_print(*args, **kwargs)
        self.update(self.pos)
