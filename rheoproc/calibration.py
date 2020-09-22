from numpy import power
from datetime import datetime as dt

from rheoproc.sql import execute_sql
import rheoproc.nansafemath as ns

def get_calibration(date):
    date = date.strftime('%Y%m%d')
    calibration_row = execute_sql(f'SELECT * FROM [STRESS CALIBRATIONS] WHERE [VALID FROM] <= {date} ORDER BY [VALID FROM] DESC LIMIT 1;', database='../data/.database.db')

    if calibration_row:
        cal_str = calibration_row[0]['DATA']
        return eval(cal_str)
    else:
        raise Exception(f'No suitable calibration for log date {date} found!')


def apply_calibration(loadcell, speed, override_cal, date):

    if override_cal:
        cal = override_cal
    else:
        cal = get_calibration(date)

    if cal['type'] == 'model':
        if 'n' not in cal:
            cal['n'] = 1.0
        total_torque = ns.divide(ns.subtract(loadcell, cal['LC_z']), cal['k_Mlc'])
        friction_torque = ns.multiply(cal['k_fM'], power(speed, cal['n']))
        load_torque = ns.subtract(total_torque, friction_torque)
    elif cal['type'] == 'model_feb20':
        total_torque = ns.multiply(ns.subtract(loadcell, cal['LC_z']), cal['k_Mlc'])
        friction_torque = ns.add(ns.multiply(cal['k_oM'], speed), cal['M_fz'])
        load_torque = ns.subtract(total_torque, friction_torque)
    elif cal['type'] == 'linear':
        load_torque = ns.add(ns.multiply(loadcell, cal['m']), cal['c'])
    else:
        raise Exception('Unrecognised cal type')

    return load_torque


