from distutils.core import setup, Extension

def main():
    setup(
        name='rheoproc', 
        version='0.2', 
        py_modules=['rheoproc']
        # ext_modules=[
        #     Extension('rheoproc.csv', ['src/rheoproc_csv.c'])
        # ]
    )

if __name__ == "__main__":
    main()
