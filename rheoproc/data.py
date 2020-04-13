import os
import inspect
import importlib

def get_data_loader():
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

    return load_data

