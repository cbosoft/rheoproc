from datetime import datetime

from rheoproc.colours import *


def timestamp(*args, **kwargs):
    print(f'  {CLEAR}{DIM}{datetime.now().strftime("(%x %X.%f)")}{RESET}', *args, **kwargs)


def warning(*args, **kwargs):
    print(f'  {CLEAR}{FG_YELLOW}{datetime.now().strftime("(%x %X.%f)")}{RESET}', *args, **kwargs)
