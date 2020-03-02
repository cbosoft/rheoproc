import subprocess as sp
import os

import numpy as np

def get_hostname():
    pr = sp.Popen('hostname', stdout=sp.PIPE)
    rv = pr.wait()
    hname = pr.stdout.read().decode()[:-1]
    return hname

def head(table, rows=5, column_first=True):
    '''
    prints the first ROWS rows of table. COLUMN_FIRST describes the row- or
    column-major mode of the table array.
    '''
    if column_first:
        table = list(zip(*table))
    for row in table[:rows]:
        print(row)

def tex_safe(unsafe_string):
    safe_string = unsafe_string.replace('_', '\\_')
    safe_string = safe_string.replace('%', '\\%')
    safe_string = safe_string.replace('&', '\\&')
    safe_string = safe_string.replace('#', '\\#')
    return safe_string

def bash_safe(unsafe_string):
    safe_string = unsafe_string.replace('(', r'\(')
    safe_string = safe_string.replace(')', r'\)')
    safe_string = safe_string.replace(']', r'\]')
    safe_string = safe_string.replace('[', r'\[')
    safe_string = safe_string.replace('?', r'\?')
    safe_string = safe_string.replace('!', r'\!')
    return safe_string

def is_number(s):
    
    assert isinstance(s, str)

    try:
        v = float(s)
    except ValueError:
        return False
    return not np.isnan(v)

def runsh(command, output='stdout'):
    
    assert output in ['stdout', 'stderr', 'both']

    kwargs = dict()

    if output == 'stdout' or 'both':
        kwargs['stdout'] = sp.PIPE

    if output == 'stderr' or 'both':
        kwargs['stderr'] = sp.PIPE

    pr = sp.Popen(command, shell=True, **kwargs)
    pr.wait()

    if output == 'stdout' or 'both':
        stdout = pr.stdout.read().decode().split('\n')

    if output == 'stderr' or 'both':
        stderr = pr.stderr.read().decode().split('\n')

    if output == 'both':
        return stdout, stderr
    
    if output == 'stdout':
        return stdout
    return stderr


def this_proc_mem_gb():
    pid = os.getpid()
    #children = [int(child_pid) for child_pid in runsh(f'pgrep -P {pid}')[:-1]]
    total_memkb = int(runsh(f'cat /proc/{pid}/status | grep VmSize | awk \'{{print $2}}\'')[0])
    # for child_pid in children:
    #     child_memkb = runsh(f'cat /proc/{child_pid}/status | grep VmSize | awk \'{{print $2}}\'')[0]
    #     if child_memkb:
    #         total_memkb += int(child_memkb)
    # total_memkb += shared_memkb
    return float(total_memkb)*0.001*0.001
