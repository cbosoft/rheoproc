import os
import sqlite3
import sys
import multiprocessing as mp

from rheoproc.combined import CombinedLogs
from rheoproc.log import GuessLog, GuessLogType
from rheoproc.exception import TooManyResultsError, QueryError
from rheoproc.progress import ProgressBar
from rheoproc.cache import load_from_cache, save_to_cache
from rheoproc.sql import execute_sql
from rheoproc.util import runsh, get_hostname
from rheoproc.error import timestamp


ACCEPTED_TABLES = ['LOGS', 'VIDEOS']


def get_log(ID, database, Log=GuessLog, **kwargs):

    assert isinstance(ID, (int, list))

    if isinstance(ID, list):
        return [get_log(ID_item, database, Log=Log) for ID_item in ID]

    query = f'SELECT * FROM LOGS WHERE ID={ID};'

    caching = '--no-cache' not in sys.argv

    if caching:
        obj = load_from_cache(query)
        if obj is not None:
            return obj

    results = execute_sql(query, database)

    assert results

    data_dir = '/'.join(database.split('/')[:-1])

    rv = Log(results[0], data_dir, **kwargs)

    if caching:
        save_to_cache(query, rv, [rv.path])

    return rv




def format_condition(column, operand, operation='=', combination='any'):
    if not isinstance(operand, (str, list)):
        raise TypeError(f'Argument operand must be str, or list^n of str. Got {type(operand)}.')

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





def get_group(GROUP, database, *other_sql, Log=GuessLog, order_by=None, descending=False, **kwargs):

    assert isinstance(GROUP, (str, list))

    if isinstance(GROUP, list):
        return [get_group(GROUP_item, Log, **kwargs) for GROUP_item in GROUP]

    if order_by is not None:
        orderbysql = f"ORDER BY '{order_by}'"
        if descending:
            orderbysql += " DESC"
    else:
        orderbysql = ""

    other_sql_f = ' '.join(other_sql)

    return query_db(f'SELECT * FROM LOGS WHERE (TAGS LIKE "%;{GROUP};%" OR TAGS LIKE "{GROUP};%" OR TAGS = "{GROUP}") {other_sql_f} {orderbysql};', database, plain_collection=True, **kwargs)


def async_get(args_and_kwargs):
    args, kwargs = args_and_kwargs
    rv = GuessLog(*args, **kwargs)
    return rv


def query_db(query, database, plain_collection=False, max_results=500, process_results=True, max_processes=20, **kwargs):

    caching = '--no-cache' not in sys.argv

    if not query.startswith("SELECT * FROM"):
        raise QueryError(f'SQL query to database must be in the form "SELECT * FROM <TABLE> [WHERE ...];"\n Troublesome query: {query}')

    global table
    table = query.replace(';', '').split(' ')[3]

    if not table in ACCEPTED_TABLES:
        raise QueryError(f'SQL queries can only be used to access data-containing tables in the database: \n Troublesome table: {table}')

    if caching:
        obj = load_from_cache(f'QUERY: {query}, KWARGS: {kwargs}')
        if obj is not None:
            return obj

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

    processes = int(runsh('nproc')[0])
    running_threads = int(runsh('top -b -n 1 | grep "^Tasks"')[0].split()[3])
    processes = int((processes - running_threads)*0.7)
    if max_processes:
        processes = min([processes, max_processes])
    timestamp(f'processing {len(results)} logs over {processes} processes.')

    data_dir = '/'.join(database.split('/')[:-1])
    with mp.Pool(processes=processes) as pool:
        for r in pool.imap_unordered(async_get, [tuple([ tuple([dict(res), data_dir]), kwargs]) for res in results], 10):
            pb.update()
            processed_results[r.ID] = r

    timestamp('Sorting')
    for ID in order:
        rv.append(processed_results[ID])

    if len(types) == 1 and not plain_collection:
        processed_results = CombinedLogs(**kwargs)
        for log in rv:
            processed_results.append(log)
    else:
        processed_results = rv

    if caching:
        timestamp('Caching')
        depends_on = [log.path for log in processed_results]
        depends_on.append(database)
        save_to_cache(f'QUERY: {query}, KWARGS: {kwargs}', processed_results, depends_on)

    return processed_results

