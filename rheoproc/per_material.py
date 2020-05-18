from matplotlib.cm import get_cmap
import numpy as np

from rheoproc.sql import execute_sql

def get_material_list(database='../data/.database.db'):
    results = execute_sql('SELECT DISTINCT MATERIAL FROM LOGS;', database)
    materials = [row['MATERIAL'] for row in results]
    return materials

materials = get_material_list()
cs_fracs = [int(mat[2:4]) for mat in materials if 'CS' in mat]
min_cs_frac = min(cs_fracs)
max_cs_frac = max(cs_fracs)


def get_repr_frac(mat):
    f = 14
    if 'CS' in mat:
        csgw = mat.split('-')[0]
        cs, gw = mat.split(':', 1)
        f = int(cs[2:])
        f = (f - min_cs_frac)
        if f < 20:
            f /= 5
        else:
            f -= 20
            if f < 10:
                f /= 2
            else:
                f -= 5
            f += 4
    elif ':' in mat:
        mat = mat.split(':', 1)[0]
        f = int(mat[1:])
        f = (f - 85)
    return int(f)


tab10 = [get_cmap('tab10')(f) for f in np.linspace(0.0, 1.0, 10)]
tab20 = [get_cmap('tab20')(f) for f in np.linspace(0.0, 1.0, 10)]
set2 = [get_cmap('Set2')(f) for f in np.linspace(0.0, 1.0, 8)]
set1 = [get_cmap('Set1')(f) for f in np.linspace(0.0, 1.0, 9)]
accent = [get_cmap('Accent')(f) for f in np.linspace(0.0, 1.0, 8)]
dark2 = [get_cmap('Dark2')(f) for f in np.linspace(0.0, 1.0, 8)][:-1]
set1.pop(5)
set1.pop(2)
dark2.pop(0)

cs_colours = list()
cs_colours.extend(set1)
cs_colours.extend(tab10)
cs_colours.extend(dark2)


summer = get_cmap('summer')
gw_colours = [
    summer(f) for f in np.linspace(1.0, 0.0, 15)
]

def get_colour_for_material(material):
    if material == 'S600':
        return 'blue'

    f = get_repr_frac(material)
    if 'CS' in material:
        return cs_colours[f]
    else:
        return gw_colours[f]
