import os
import pickle
import hashlib
import json
import sys
import time

from rheoproc.error import timestamp, warning


CACHE_DIR = os.path.expanduser("~/.cache/phd")


def set_cache_dir(path):
    global CACHE_DIR
    CACHE_DIR = path


def check_cache():
    if not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    if not os.path.isfile(f'{CACHE_DIR}/index.json'):
        with open(f'{CACHE_DIR}/index.json', 'w') as indexf:
            json.dump(dict(), indexf)


def get_next_cache_name(query):
    check_cache()
    hsh = hashlib.sha1(query.encode()).hexdigest()
    return f'{CACHE_DIR}/{hsh}.pickle', hsh


def read_index():
    with open(f'{CACHE_DIR}/index.json') as indexf:
        fc = indexf.read()
    try:
        index = json.loads(fc)
    except:
        print(fc)
        raise
    return index


def write_index(index):
    with open(f'{CACHE_DIR}/index.json', 'w') as indexf:
        json.dump(index, indexf)


def save_to_cache(key, obj, depends_on=None, expires=None, expires_in_seconds=None, expires_in_days=None):
    name, hsh = get_next_cache_name(key)

    index = read_index()

    if key not in index:
        index[key] = dict()
        index[key]['path'] = name

        if depends_on:
            if isinstance(depends_on, str):
                depends_on = [depends_on]
            index[key]['depends_on'] = depends_on

        if expires is not None:
            index[key]['expires'] = expires
        elif expires_in_seconds is not None:
            index[key]['expires'] = time.time() + expires_in_seconds
        elif expires_in_days is not None:
            index[key]['expires'] = time.time() + (expires_in_days*60.*60.*24.)
    
    write_index(index)
    
    timestamp(f'saving object {hsh[:3]}...{hsh[-3:]} to cache.')
    with open(name, 'wb') as pf:
        pickle.dump(obj, pf, protocol=4)


def remove_from_index(key, index):
    del index[key]
    write_index(index)
    return index


def load_from_cache(key):
    check_cache()

    index = read_index()

    if key not in index:
        warning('Key not in index.')
        return None

    if '--fresh' in sys.argv:
        warning('Clearing cached version of requested object.')
        remove_from_index(key, index)
        return None

    entry = index[key]
    if not os.path.isfile(entry['path']):
        warning('Could not find cached blob; removing from index.')
        remove_from_index(key, index)
        return None

    now = time.time()
    if 'expires' in entry.keys() and now > entry['expires']:
        timestamp('Cache item expired; removing from index.')
        remove_from_index(key, index)
        return None

    if 'depends_on' in entry.keys():
        pickle_mtime = os.path.getmtime(entry['path'])
        for dep in entry['depends_on']:
            dep_mtime = os.path.getmtime(dep)

            if dep_mtime > pickle_mtime:
                warning(f'Dependency {dep} newer than cache.')
                return None

    try:
        with open(entry['path'], 'rb') as pf:
            o = pickle.load(pf)
    except Exception as e:
        warning(f'Error loading cached file; removing from index. Error: {e}')
        os.remove(entry['path'])
        remove_from_index(key, index)
        return None
    return o


def diskcache(thisfile=None, **cache_kwargs):
    def decorator(f):
        def decorated_f(*args, **kwargs):
            key = f'{thisfile} {args} {kwargs}'
            val = load_from_cache(key)
            if val is None:
                rv = f(*args, **kwargs)
                save_to_cache(key, rv, depends_on=thisfile, **cache_kwargs)
                return rv
            else:
                return val
        return decorated_f
    return decorator
