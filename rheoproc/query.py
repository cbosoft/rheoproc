# rheoproc.query
# Contains functions for efficiently querying the databse for logs and managing the processing of the data.
# Spawns processes using the 'multiprocessing' library or asks a remote process server to deal with it if
# server address given.

import os
import sys
import time
from queue import Empty
import multiprocessing as mp
import threading

from rheoproc.combined import CombinedLogs
from rheoproc.log import GuessLog, GuessLogType
from rheoproc.exception import GenericRheoprocException, TooManyResultsError, QueryError
from rheoproc.progress import ProgressBar
from rheoproc.cache import load_from_cache, save_to_cache, get_cache_path
from rheoproc.sql import execute_sql
from rheoproc.util import runsh, get_hostname, is_mac
from rheoproc.error import timestamp, warning
from rheoproc.interprocess import set_q, set_worker
from rheoproc.client import get_from_server


ACCEPTED_TABLES = ['LOGS', 'VIDEOS']


def get_log(ID, database='../data/.database.db', **kwargs):
    query = f'SELECT * FROM LOGS WHERE ID={ID};'
    return query_db(query, database=database, **kwargs)[0]


def get_logs(IDs, database='../data/.database.db', **kwargs):
    conds = ' OR '.join([f'ID={ID}' for ID in IDs])
    query = f'SELECT * FROM LOGS WHERE {conds};'
    return query_db(query, database=database, **kwargs)



def format_condition(column, operand, operation='=', combination='any'):
    if not isinstance(operand, (str, list)):
        raise TypeError(f'Argument operand must be str, or list of str. Got {type(operand)}.')

    if combination not in ['any', 'all']:
        raise TypeError(f'Keyword combination must be either \'any\' or \'all\' (corresponding to OR and AND respectively). Got \'{combination}\'.')

    if isinstance(operand, str):
        return f"{column} {operation} {operand} "

    rv = '('
    for op in operand[:-1]:
        rv += format_condition(column, op, operation=operation, combination=combination)
        if combination == 'any':
            rv += 'OR '
        else:
            rv += 'AND '
    rv += format_condition(column, operand[-1], operation=operation, combination=combination)
    rv += ')'
    return rv





def get_group(GROUP, database='../data/.database.db', Log=GuessLog, order_by=None, descending=False, flat=True, **kwargs):

    assert isinstance(GROUP, (str, list))

    if isinstance(GROUP, list):
        get_sub_group = lambda gi: get_group(gi, Log=Log, order_by=order_by, descending=descending, **kwargs)
        if flat:
            rv = list()
            for GROUP_item in GROUP:
                res = get_sub_group(GROUP_item)
                for res_item in res:
                    rv.append(res_item)
            return rv
        else:
            return [get_sub_group(GROUP_item) for GROUP_item in GROUP]

    database = os.path.expanduser(database)

    if order_by is not None:
        orderbysql = f"ORDER BY '{order_by}'"
        if descending:
            orderbysql += " DESC"
    else:
        orderbysql = ""

    return query_db(f'SELECT * FROM LOGS WHERE (TAGS LIKE "%;{GROUP};%" OR TAGS LIKE "{GROUP};%" OR TAGS = "{GROUP}") {orderbysql};', database, plain_collection=True, **kwargs)



def async_get(args_and_kwargs):
    q, args, kwargs = args_and_kwargs
    set_q(q)
    set_worker()
    try:
        rv = GuessLog(*args, **kwargs)
    except GenericRheoprocException as e:
        if kwargs['ignore_exceptions']:
            print('ignored exception')
            print(e)
            return None
        else:
            raise e
    return rv


def get_n_processes():
    return mp.cpu_count()


def printer(q: mp.Queue, pb: ProgressBar):
    while True:
        try:
            pl = q.get(timeout=10)
        except Empty:
            time.sleep(0.1)
            continue
        if isinstance(pl, int):
            break
        args, kwargs = pl
        pb.print(*args, **kwargs)

# This whole section is a bit of a mess! TODO: tidy up

def get_from_local(query, *, database='../data/.database.db', process_results=True, max_results=500, max_processes=20,
                   ignore_exceptions=False, plain_collection=True, **kwargs):
    database = os.path.expanduser(database)
    results = execute_sql(query, database)

    if not results:
        raise QueryError(f"No results returned by query \"{query}\"")

    if not process_results:
        return [dict(result) for result in results]

    if (lr := len(results)) > max_results and get_hostname() != 'Poseidona':
        raise TooManyResultsError(f"Jeez, that's a lot of data! ({lr} > {max_results}, set 'max_results' to override.)")

    types = list({GuessLogType(row, table) for row in results})

    rv = list()

    pb = ProgressBar(len(results))

    processed_results = dict()
    order = [r['ID'] for r in results]

    processes = get_n_processes()
    processes = min([processes, max_processes])

    timestamp(f'processing {len(results)} logs over {processes} processes.')

    data_dir = '/'.join(database.split('/')[:-1])

    mp.set_start_method('fork', True)
    m = mp.Manager()
    q = m.Queue()
    printer_thread = threading.Thread(target=printer, args=(q,pb), daemon=True)
    printer_thread.start()
    list_of_args_kwargs = [(q, (dict(res), data_dir), kwargs) for res in results]
    if processes == 1:
        warning('Only using one core: this could take a while.')
        for a_kw in list_of_args_kwargs:
            r = async_get(a_kw)
            pb.update()
            if r:
                processed_results[r.ID] = r
    else:
        with mp.Pool(processes=processes) as pool:
            for r in pool.imap_unordered(async_get, list_of_args_kwargs):
                pb.update()
                if r:
                    processed_results[r.ID] = r
    q.put(0)
    printer_thread.join()

    timestamp('Sorting')
    for ID in order:
        try:
            rv.append(processed_results[ID])
        except Exception as e:
            if ignore_exceptions:
                pass
            else:
                warning(processed_results)
                raise e

    if plain_collection:
        processed_results = rv
    else:
        if len(types) == 1:
            processed_results = CombinedLogs(**kwargs)
            for log in rv:
                processed_results.append(log)
        else:
            raise GenericRheoprocException('multiple log types not destined for plain collection')
    return processed_results


def query_db(query, *args, database='../data/.database.db', server=None, returns='data', **kwargs):

    args = (query, *args)
    kwargs['database'] = database
    kwargs['returns'] = returns

    if not query.startswith("SELECT * FROM"):
        raise QueryError(f'SQL query to database must be in the form "SELECT * FROM <TABLE> [WHERE ...];"\n Troublesome query: {query}')

    global table
    table = query.replace(';', '').split(' ')[3]

    if not table in ACCEPTED_TABLES:
        raise QueryError(f'SQL queries can only be used to access data-containing tables in the database: \n Troublesome table: {table}')

    cache_key = f'QUERY: {query}, KWARGS: {kwargs}'
    obj = load_from_cache(cache_key)
    if obj is not None:
        if returns == 'cache_path':
            return get_cache_path(cache_key)
        else:
            return obj

    processed_results = get_from_local(*args, **kwargs) if not server else get_from_server(server, *args, **kwargs)

    timestamp('Caching')
    depends_on = [log.path for log in processed_results]
    depends_on.append(database)
    save_to_cache(cache_key, processed_results, depends_on)

    if returns == 'data':
        return processed_results
    elif returns == 'cache_path':
        return get_cache_path(cache_key)

