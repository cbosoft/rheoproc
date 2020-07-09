from datetime import datetime

from rheoproc.colours import *

import __main__ as main
interactivep = hasattr(main, '__file__')

def timestamp(*args, **kwargs):
    print(f'\r  {DIM}{datetime.now().strftime("(%x %X.%f)")}{RESET}', *args, **kwargs)


def warning(*args, **kwargs):
    print(f'\r  {FG_YELLOW}{datetime.now().strftime("(%x %X.%f)")}{RESET}', *args, **kwargs)

def do_nothing(*args, **kwargs):
    return

if not interactivep:
    timestamp = do_nothing
    warning = do_nothing
