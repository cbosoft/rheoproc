import numpy as np
from scipy.interpolate import interp1d

def rec_choose(vec, indices):
    '''recursive application of np.choose'''

    if len(np.shape(vec)) > 1:
        return [rec_choose(v, indices) for v in vec]
    try:
        return [vec[i] for i in indices]
    except Exception:
        return vec

def rat_times(k, *vectors):

    rv = [list()]
    distinct_indices = list()
    kp = float('nan')
    for i, ki in enumerate(k):
        if ki != kp:
            distinct_indices.append(i)
            kp = ki
            rv[0].append(ki)

    for i, vector in enumerate(vectors):
        try:
            rv.append(rec_choose(vector, distinct_indices))
        except Exception as e:
            print(vector, i)
            raise e

    return tuple(rv)

def recreate(t, lc, *vs, kind='cubic'):
    ltvp = rat_times(lc, t, *vs)
    lp = ltvp[0]
    tp = ltvp[1]
    vps = ltvp[2:]

    rv = list()
    for vp in vps:
        v = interp1d(tp, vp, kind=kind, fill_value='extrapolate')(t)
        rv.append(v)
    if len(rv) == 1:
        rv = rv[0]
    return rv
