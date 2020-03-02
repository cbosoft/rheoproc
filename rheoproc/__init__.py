import sys

from rheoproc.usage import show_usage_and_exit

if '--help' or '-h' in sys.argv:
    show_usage_and_exit()

major, minor, micro, rel, serial = sys.version_info
if major < 3 or minor < 8:
    raise Exception('tdlib needs at least Python 3.8 (Got: Python {0}.{1})'.format(major, minor))

import importlib
def __check_module(name):
    try:
        mod = importlib.import_module(name)
        return True
    except:
        return False

__modules = ['numpy', 'matplotlib', 'sympy', 'lmfit', 'scipy']

__exit = False
for __module in __modules:
    if not __check_module(__module):
        print(f'Could not import {__module}, ensure it is installed.')
        __exit = True

if __exit:
    sys.exit(1)
