from glob import glob
import os
from distutils.core import setup, Extension
from importlib.util import spec_from_file_location, module_from_spec

with open("rheoproc/version.py") as f:
    ver = f.readline().split('=')[-1].strip().replace('\'', '').replace('"', '')

os.environ["CC"] = "gcc-10"

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
