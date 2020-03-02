from rheoproc.rheometerlog import RheometerLog
from rheoproc.syringepumplog import SyringepumpLog
from rheoproc.dhrlog import DHRLog
from rheoproc.video import Video

'''
Log helper functions.
'''


def GuessLogType(row, table='LOGS'):
    if table == 'VIDEOS':
        return Video

    if row['EXPERIMENT'] == 'RHEO':
        return RheometerLog

    if row['EXPERIMENT'] == 'SYRPU':
        return SyringepumpLog

    if row['EXPERIMENT'] == 'DHR':
        return DHRLog



def GuessLog(row, table='LOGS', *args, **kwargs):
    logType = GuessLogType(row, table)
    return logType(row, *args, **kwargs)

