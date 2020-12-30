# rheoproc.error
# this file contains functions related to output/printing (despite the misnomer).

from datetime import datetime

from rheoproc.colours import *
from rheoproc.interprocess import is_worker, push

# TODO: replace with a logger class?
# to be more thread/process aware and so on

def __print(*args, colour, **kwargs):
    if is_worker():
        push(( args, {'colour':colour, **kwargs}))
    else:
        print(f'\r  {colour}{datetime.now().strftime("(%x %X.%f)")}{RESET}', *args, **kwargs)


def timestamp(*args, **kwargs):
    __print(*args, colour=DIM, **kwargs)


def warning(*args, **kwargs):
    __print(*args, colour=FG_YELLOW, **kwargs)
