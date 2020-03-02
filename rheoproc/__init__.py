import sys
major, minor, micro, rel, serial = sys.version_info
if major < 3 or minor < 8:
    raise Exception('rheoproc needs at least Python 3.8 (Got: Python {0}.{1})'.format(major, minor))

import importlib
def __check_module(name):
    try:
        mod = importlib.import_module(name)
        return True
    except:
        return False

__modules = ['numpy', 'matplotlib', 'sympy', 'lmfit', 'scipy']
__missing_modules = [__module for __module in __modules if not __check_module(__module)]

if __missing_modules:
    raise ImportError(f"Some required modules are missing: {' '.join(__missing_modules)}.")
