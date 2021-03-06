# rheoproc.standard_wobble
# Functions defined here manage the removal of the 'standard wobble' an inherent noise originating in the rheometer.

from datetime import datetime
import pickle
from sqlite3 import Error as SQLiteError

import numpy as np
from scipy import signal
from lmfit import Parameters, minimize

from rheoproc.exception import GenericRheoprocException, WobbleError
from rheoproc.util import norm, unnorm, sqd
from rheoproc.error import timestamp, warning
from rheoproc.sql import execute_sql, insert_with_blob


def stretch(x, xu, yu):
    if np.any(np.isnan(x)) or np.any(np.isnan(xu)) or np.any(np.isnan(yu)):
        raise GenericRheoprocException('NaN in stretch input')
    end = np.max(x)
    xr = list(np.subtract(xu, 1.0))
    yr = list(yu)
    while True:
        xr.extend(np.add(xu, xr[-1]))
        yr.extend(yu)

        if xr[-1] > end+1:
            break

    return xr, yr



def residual_phase(params, x, y, xu, yu):
    phase = float(params['phase'])
    xm = np.add(x, phase)
    yu = np.interp(xm, xu, yu)
    e = sqd(y, yu)
    return e



def match_phase(x, y, xu, yu):
    params = Parameters()
    params.add('phase', np.random.uniform(), min=0.0, max=1.0)
    res = minimize(residual_phase, params, args=(x, y, xu, yu), method='ampgo')
    return float(res.params['phase'])


def save_wobble_frequencies(frequencies, motor='ANY', date=None, database='../data/.database.db'):
    if date is None:
        today = datetime.today()
        date = float(today.strftime('%Y%m%d.%H%M%S'))

    frequencies = [f for f in frequencies if f == f]
    frequencies = list(sorted(set(frequencies)))
    timestamp(f'Saving wobble frequencies ({frequencies}) to database, date={date}')
    frequencies_blob = pickle.dumps(tuple(frequencies))
    insert_with_blob(
        'WOBBLE',
        (date, motor, 'frequencies', frequencies_blob),
        ('DATE', 'MOTOR', 'TYPE', 'DATA'),
        database)


def save_wobble_waveform(waveform, motor='ANY', date=None, database='../data/.database.db'):
    if date is None:
        today = datetime.today()
        date = float(today.strftime('%Y%m%d.%H%M%S'))

    waveform = [[float(b) for b in a] for a in waveform]
    assert len(waveform) == 2 and len(waveform[0]) == len(waveform[1])
    timestamp(f'Saving wobble waveform ({len(waveform[0])} points) to database, date={date}')
    waveform_blob = pickle.dumps(waveform)
    insert_with_blob(
        'WOBBLE',
        (date, motor, 'waveform', waveform_blob),
        ('DATE', 'MOTOR', 'TYPE', 'DATA'),
        database)


def load_wobble_waveform(motor:str, date:int=-1, database:str='../data/.database.db'):
    query = f'SELECT * FROM WOBBLE WHERE DATE>{date} AND (MOTOR LIKE "{motor}" OR MOTOR="ANY") AND TYPE="waveform" ORDER BY DATE DESC LIMIT 1;'
    res = execute_sql(query, database)
    if not res:
        raise WobbleError(f'No data for date {date} and motor {motor} in database.')
    data_blob = res[0]['DATA']
    data = pickle.loads(data_blob)
    return data


def load_wobble_frequencies(motor:str, date:int=-1, database:str='../data/.database.db'):
    query = f'SELECT * FROM WOBBLE WHERE DATE>{date} AND (MOTOR LIKE "{motor}" OR MOTOR="ANY") AND TYPE="frequencies" ORDER BY DATE DESC LIMIT 1;'
    res = execute_sql(query, database)
    if not res:
        raise WobbleError(f'No data for date {date} and motor {motor} in database.')
    data_blob = res[0]['DATA']
    data = pickle.loads(data_blob)
    return data


def remove_standard_wobble(pos, lc, motor, method, **kwargs):
    if method == 'any':
        for method in ['filter', 'subtract']:
            try:
                return remove_standard_wobble(pos, lc, motor, method, exceptions=True)
            except (SQLiteError, WobbleError):
                pass
        warning(f'No filtering method available: ignoring.')
        return lc
    elif method == 'subtract':
        return subtract_standard_wobble(pos, lc, motor, **kwargs)
    elif method == 'filter':
        return filter_standard_wobble(pos, lc, motor, **kwargs)
    elif method == 'dont':
        return lc
    else:
        warning(f'Unrecognised wobble removal method \'{method}\'; ignoring.')
        return lc


def filter_standard_wobble(pos, lc, motor, exceptions=False):
    try:
        frequencies = load_wobble_frequencies(motor)
    except Exception as e:
        warning(f'Could not load frequencies: {e}')
        if exceptions:
            raise
        else:
            return lc

    maxfreq = 1/np.nanmean(np.diff(pos))
    filtered = lc
    w = 0.2
    for freq in frequencies:
        band = [freq-w, freq+w]
        try:
            sos = signal.butter(3, band, btype='bandstop', output='sos', fs=maxfreq)
            filtered = signal.sosfiltfilt(sos, filtered)
        except Exception as e:
            raise WobbleError('Error when filtering frequencies') from e
    timestamp(f'standard wobble filtered.')
    return filtered


def subtract_standard_wobble(pos, lc, motor, exceptions=False):
    try:
        waveform = load_wobble_waveform(motor)
    except Exception as e:
        warning(f'Could not load waveform: {e}')
        if exceptions:
            raise
        else:
            return lc

    standard_pos, standard_lc = waveform
    standard_pos, standard_lc = stretch(pos, standard_pos, standard_lc)
    nlc = norm(lc)
    phase = match_phase(pos, nlc, standard_pos, standard_lc)
    standard_lc = np.interp(pos, np.subtract(standard_pos, phase), standard_lc)
    subtracted_normalised = np.subtract(nlc, standard_lc)
    subtracted =  unnorm(subtracted_normalised, np.mean(lc), np.max(lc) - np.min(lc))
    timestamp(f'standard wobble subtracted.')
    return subtracted
