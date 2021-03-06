

import sys
def args_check():
    if '--help' in sys.argv or '-h' in sys.argv:
        from rheoproc.usage import show_usage_and_exit
        show_usage_and_exit()

def version_check():
    major, minor, micro, rel, serial = sys.version_info
    if major < 3 or minor < 8:
        raise Exception('tdlib needs at least Python 3.8 (Got: Python {0}.{1})'.format(major, minor))

def modules_check():
    import importlib
    def check_module(name):
        try:
            mod = importlib.import_module(name)
            return True
        except:
            return False
    modules = ['numpy', 'matplotlib', 'sympy', 'lmfit', 'scipy', 'cv2']
    missing_modules = [module for module in modules if not check_module(module)]
    if missing_modules:
        raise ImportError(f'Could not import required modules: {", ".join(missing_modules)}')

args_check()
version_check()
modules_check()

import atexit
def closing_message():
    from rheoproc.error import timestamp
    timestamp(f'done!')

atexit.register(closing_message)

del atexit

del args_check
del version_check
del modules_check
del sys

import rheoproc.plot as plot
import rheoproc.query as query
import rheoproc.nansafemath as nansafemath
import rheoproc.util as util
import rheoproc.fft as fft

from rheoproc.plot import plot_init, get_plot_name, MultiPagePlot, pyplot
from rheoproc.data import get_data
from rheoproc.query import get_log, get_logs, get_group, query_db
from rheoproc.error import timestamp, warning
from rheoproc.version import version

timestamp(f'rheoproc {version} initialised')
