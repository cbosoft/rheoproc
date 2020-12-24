import subprocess as sp
import os

import numpy as np


def convert_bit_to_volts(b, *, bit_length, max_voltage):
    '''
    Convert a signal from n-bit number to a voltage.
    e.g. a value of 512 for a 10 bit number 
    representing a voltage up to 5v would give 2.5v.
    '''
    max_b = (2 << (bit_length - 1)) - 1
    return np.multiply(np.divide(b, max_b), max_voltage)


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
    
    assert output in ['stdout', 'stderr', 'both', 'none']

    kwargs = dict()

    if output in ['stdout', 'both']:
        kwargs['stdout'] = sp.PIPE

    if output in ['stderr', 'both']:
        kwargs['stderr'] = sp.PIPE

    pr = sp.Popen(command, shell=True, **kwargs)
    pr.wait()

    if output in ['stderr', 'both']:
        stdout = pr.stdout.read().decode().split('\n')

    if output in ['stderr', 'both']:
        stderr = pr.stderr.read().decode().split('\n')

    if output == 'both':
        return stdout, stderr
    
    if output == 'stdout':
        return stdout

    if output == 'stderr':
        return stderr

    return


def this_proc_mem_gb():
    pid = os.getpid()
    #children = [int(child_pid) for child_pid in runsh(f'pgrep -P {pid}')[:-1]]
    try:
        total_memkb = int(runsh(f'cat /proc/{pid}/status | grep VmSize | awk \'{{print $2}}\'')[0])
    except:
        total_memkb = -1
    # for child_pid in children:
    #     child_memkb = runsh(f'cat /proc/{child_pid}/status | grep VmSize | awk \'{{print $2}}\'')[0]
    #     if child_memkb:
    #         total_memkb += int(child_memkb)
    # total_memkb += shared_memkb
    return float(total_memkb)*0.001*0.001

def is_between(v, mn, mx):
    try:
        len(v)
        return all([is_between(vi, mn, mx) for vi in v])
    except:
        return mn <= v <= mx

def is_mac():
    import platform
    return platform.system() == 'Darwin'


def run_other_script(path):
    runsh(f'python {path}', output='none')
