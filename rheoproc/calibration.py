from numpy import power
from datetime import datetime as dt

from rheoproc.sql import execute_sql
import rheoproc.nansafemath as ns

CALIBRATIONS = [
    {
        'type': 'model',
        'valid_from': dt.strptime("2019-08-01", "%Y-%M-%d"),
        'LC_z' : 2147403964.8201435,
        'k_Mlc' : 5943337.5848672595,
        'k_fM' : 0.00024034388608895618
    },
    {
        'type': 'model',
        'valid_from': dt.strptime("2019-09-01", "%Y-%M-%d"),
        'LC_z': 2147404172.2268088,
        'k_Mlc': 5830725.190810496,
        'k_fM': 0.00024102884334720187,
        'n': 0.723770242690987
    },
    {
        'type': 'model_feb20',
        'valid_from': dt.strptime("2020-01-01", "%Y-%M-%d"),
        'k_Mlc': 5.358774072092084e-08,
        'LC_z': 868008998.7095627,
        'k_oM': -0.0010503586253458334,
        'M_fz': 68.56278788864951
    }
]

CAL_STR = 'lambda loadcell, speed: np.subtract(np.divide(np.subtract(loadcell, 2147404172.2268088), 5830725.190810496), np.multiply(0.00024102884334720187, np.power(speed, 0.723770242690987)))'

#CALIBRATION = {'type': 'model', 'LC_z': 2147404172.2002132, 'k_Mlc': 5830725.80830834, 'k_fM': 0.0002410294547234848}

def get_calibration(log_row, database):
    if row := log_row['LOADCELL CALIBRATION OVERRIDE']:
        cal_str = row
    else:
        #experiment = log_row['EXPERIMENT']
        #date = log_row['DATE']
        calibration_row = execute_sql('SELECT * FROM CALIBRATIONS WHERE DATE<{date} AND EXPERIMENT="{experiment}" ORDER BY DATE DESC;', database)
        cal_str = calibration_row['FUNCTION']
    return eval(cal_str)


def apply_calibration(loadcell, speed, override_cal, date):

    cal = None
    if override_cal:
        cal = override_cal
    else:
        for CAL in CALIBRATIONS:
            if date > CAL['valid_from']:
                cal = CAL

    if cal is None:
        raise Exception("No suitable calibration for log date {date} found!")


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


