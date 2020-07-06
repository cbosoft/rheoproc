from glob import glob
import os
import re
from distutils.core import setup, Extension
from importlib.util import spec_from_file_location, module_from_spec

with open("rheoproc/version.py") as f:
    ver = f.readline().split('=')[-1].strip().replace('\'', '').replace('"', '')


def reglob(directory, pattern):
    contents = os.listdir(directory)
    return [c for c in contents if re.match(pattern, c)]

def get_cc():
    brewgcc = list(sorted(reglob('/usr/local/bin', 'gcc-\\d+')))
    if not brewgcc:
        return 'gcc'
    return brewgcc[-1]


# Find latest GNU gcc installed by homebrew
os.environ["CC"] = get_cc()

def main():
    accelproc_sources = glob('src/*.c')
    setup(
        name='rheoproc', 
        description='Rheometer log processing library',
        version=ver, 
        packages=['rheoproc'],
        install_requires=[
            'numpy',
            'scipy',
            'sympy',
            'matplotlib',
            'lmfit',
            'opencv-python'
        ],
        ext_modules=[
            Extension('rheoproc.accelproc', accelproc_sources)
        ]
    )

if __name__ == "__main__":
    main()
