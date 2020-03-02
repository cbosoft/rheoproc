import os

from rheoproc.error import timestamp
from rheoproc.util import this_proc_mem_gb

class ProgressBar:

    def __init__(self, length):
        self.length = length
        self.pos = -1

    def update(self, i=None):
        rows, columns = os.popen('stty size', 'r').read().split()

        if i is None:
            i = self.pos + 1

        mem_gb = this_proc_mem_gb()
        frac = f'▌{mem_gb:.1f} GB▐▌{i+1}/{self.length}▐'
        timestamp_ex = "  (10/30/19 15:57:02.659921) "
        columns = int(columns) - len(frac) - len(timestamp_ex)
        col_per_i = columns / self.length
        prog = int(col_per_i * (i+1))
        prog = frac.rjust(prog-1, '█') + '█'
        end = '' if i < self.length-1 else '\n'
        timestamp(f'█{prog}\r', end=end)

        self.pos = i

    def clear(self):
        print('\u001b[2K')
