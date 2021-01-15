# rheoproc.cache
#
# This file contains functions related to disk-caching processed results.

import os
import pickle
import hashlib
import json
import sys
import time
from functools import lru_cache

from rheoproc.error import timestamp, warning


CACHE_DIR = os.path.expanduser("~/.cache/rheoproc")


class CacheIndex:

    def __init__(self, path=None):
        if path is None:
            path = f'{CACHE_DIR}/index.json'
        self.path = path

    def __getitem__(self, item):
        data = self.read()
        return data[item]

    def __setitem__(self, key, value):
        data = self.read()
        data[key] = value
        self.write(data)

    def __contains__(self, key):
        data = self.read()
        return key in data

    def remove(self, key):
        data = self.read()
        del data[key]
        self.write(data)

    @lru_cache
    def read(self) -> dict:
        with open(self.path) as indexf:
            fc = indexf.read()
        try:
            index = json.loads(fc)
        except:
            warning(f'Error encountered while parsing index "{fc}".')
            raise
        return index

    def write(self, data: dict):
        with open(self.path, 'w') as indexf:
            json.dump(data, indexf)



class CacheSingleton:

    def __init__(self, *args, **kwargs):
        self.check_paths()
        self.index = CacheIndex(*args, **kwargs)
        timestamp(f'Cache at \'{self.path}\' initialised.')

    def check_paths(self):
        if not os.path.isdir(self.path):
            os.makedirs(self.path)

        if not os.path.isfile(f'{self.path}/index.json'):
            with open(f'{self.path}/index.json', 'w') as indexf:
                json.dump(dict(), indexf)

    def get_hashed_name(self, name: str):
        hsh = hashlib.sha1(name.encode()).hexdigest()
        return f'{CACHE_DIR}/{hsh}.pickle', hsh

    def get_path_in_cache_of(self, key):
        return self.index[key]['path']

    def save_object(self, key, obj, depends_on=None, expires=None, expires_in_seconds=None, expires_in_days=None):
        name, hsh = self.get_hashed_name(key)

        if key not in self.index:
            obj_data = dict()
            obj_data['path'] = name

            if depends_on:
                if isinstance(depends_on, str):
                    depends_on = [depends_on]
                obj_data['depends_on'] = depends_on

            if expires is not None:
                obj_data['expires'] = expires
            elif expires_in_seconds is not None:
                obj_data['expires'] = time.time() + expires_in_seconds
            elif expires_in_days is not None:
                obj_data['expires'] = time.time() + (expires_in_days * 60. * 60. * 24.)

            self.index[key] = obj_data

        timestamp(f'saving object {hsh[:3]}...{hsh[-3:]} to cache.')
        with open(name, 'wb') as pf:
            pickle.dump(obj, pf, protocol=4)

    def load_object(self, key):
        if key not in self.index:
            warning('Key not in index.')
            return None

        if '--fresh' in sys.argv:
            warning('Clearing cached version of requested object.')
            self.index.remove(key)
            return None

        obj_data = self.index[key]
        if not os.path.isfile(obj_data['path']):
            warning('Could not find cached blob; removing from index.')
            self.index.remove(key)
            return None

        now = time.time()
        if 'expires' in obj_data.keys() and now > obj_data['expires']:
            timestamp('Cache item expired; removing from index.')
            self.index.remove(key)
            return None

        if 'depends_on' in obj_data.keys():
            pickle_mtime = os.path.getmtime(obj_data['path'])
            for dep in obj_data['depends_on']:
                dep_mtime = os.path.getmtime(dep)

                if dep_mtime > pickle_mtime:
                    warning(f'Dependency {dep} newer than cache.')
                    return None

        try:
            with open(obj_data['path'], 'rb') as pf:
                o = pickle.load(pf)
        except Exception as e:
            warning(f'Error loading cached file; removing from index. Error: {e}')
            os.remove(obj_data['path'])
            self.index.remove(key)
            return None
        return o

    @property
    def path(self):
        return CACHE_DIR

__cache = None
def Cache() -> CacheSingleton:
    global __cache
    if __cache is None:
        __cache = CacheSingleton()
    return __cache


def diskcache(thisfile=None, **cache_kwargs):
    def decorator(f):
        def decorated_f(*args, **kwargs):
            key = f'{thisfile} {args} {kwargs}'
            cache = Cache()
            val = cache.load_object(key)
            if val is None:
                rv = f(*args, **kwargs)
                cache.save_object(key, rv, depends_on=thisfile, **cache_kwargs)
                return rv
            else:
                return val
        return decorated_f
    return decorator
