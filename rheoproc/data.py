# rheoproc.data
# Functions here relate to the offloading of processing onto another script. I find when plotting it can be helpful
# to split up the two tasks of organising and processing data, and plotting the result into separate scripts/files.

import os
import inspect
import importlib

def get_data():
    '''
    Facilitates the separation between plotting and processing, while keeping things automatic and fast.
    A data ('data_<name>.py') script is used separate to the plot script ('fig_<name>.py'). This function,
    called from the plot script, finds and runs the data script's 'load_data' function which returns the
    processed data ready for plotting. This has the advantages of splitting design (art) and function (science)
    and also facilitating the use of disk-caching the processed data.
    '''
    n = inspect.stack()[1].filename
    n = os.path.basename(n)
    n = n.replace('fig_', 'data_')
    n = n.replace('.py', '')

    try:
        module = importlib.import_module(n)
    except Exception as e:
        raise ImportError(f'Data script (\'{n}.py\') not found.') from e

    try:
        load_data = module.load_data
    except Exception as e:
        raise ImportError(f'No load_data function found in \'{n}.py\'.') from e

    return load_data()
