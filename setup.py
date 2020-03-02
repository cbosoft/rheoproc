from glob import glob
from distutils.core import setup, Extension

def main():
    accelproc_sources = glob('src/*.c')
    setup(
        name='rheoproc', 
        version='0.2', 
        packages=['rheoproc'],
        ext_modules=[
            Extension('rheoproc.accelproc', accelproc_sources)
        ]
    )

if __name__ == "__main__":
    main()
