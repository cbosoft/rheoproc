# rheoproc.usage
# Shows some help on usage when a rheoproc script is run with '--help' as an argument

import sys

from rheoproc.colours import *
USAGE = [
    f'  {BOLD}rheoproc -- Rheometer log processing library{RESET}',
    '',
    '  This script uses the library to read data from logs and plot the',
    '  result. A script which uses rheoporc has some optional arguments.',
    '',
    f'  {BOLD} Usage:{RESET}',
    '     <SCRIPT-NAME.PY> [<SCRIPT-OPTIONS>] [<RHEOPROC-OPTIONS>]',
    '',
    f'  {BOLD} Options:{RESET}',
    '     --fresh     If caching is used in the script, clear the ',
    '                 relevant objects from it instead of loading them.',
    '     --help      Show this help message'
]

def show_usage_and_exit():
    print('\n'.join(USAGE))
    sys.exit(0)
