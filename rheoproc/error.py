from datetime import datetime

from rheoproc.colours import *


def timestamp(*args, **kwargs):
    print(f'\r  {DIM}{datetime.now().strftime("(%x %X.%f)")}{RESET}', *args, **kwargs)


def warning(*args, **kwargs):
    print(f'\r  {FG_YELLOW}{datetime.now().strftime("(%x %X.%f)")}{RESET}', *args, **kwargs)
