# rheoproc.log
# Provides functions for creating the correct type of log for the database row given.

from rheoproc.rheometerlog import RheometerLog
from rheoproc.syringepumplog import SyringepumpLog
from rheoproc.dhrlog import DHRLog
from rheoproc.historiclog import HistoricRheometerLog
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

    if row['EXPERIMENT'] == 'HISTORIC_RHEO':
        return HistoricRheometerLog

    raise Exception("No suitable log type found.")



def GuessLog(row, *args, table='LOGS', **kwargs):
    logType = GuessLogType(row, table)
    return logType(row, *args, **kwargs)

