import re
import numpy as np

from rheoproc.util import is_between

# glycerol and water information from Cheng2008

GLYCEROL_RE = re.compile(r'^G0999$')
GW_RE = re.compile(r'^G(\d*):W(\d*)$')
CSGW_RE = re.compile(r'^CS(\d*):\(G(\d*):W(\d*)\)$')
S600_RE = re.compile(r'^S600$')
NONE_RE = re.compile(r'^NONE$')



def get_density_glycerol(T):
    return np.subtract(1277.0, np.multiply(0.654, T))



def get_density_water(T):
    return np.multiply(1000.0, np.subtract(1.0, np.abs(np.power(np.divide(np.subtract(T, 4.0), 622.0), 1.7))))

def get_density_glycerol_water_mix(T, Cm):
    rhog = get_density_glycerol(T)
    rhow = get_density_water(T)
    return np.add(np.multiply(Cm, rhog), np.multiply(np.subtract(1, Cm), rhow))

def get_density_material(material, T):

    match = GLYCEROL_RE.match(material)
    if match:
        return get_viscosity_glycerol(T)

    match = GW_RE.match(material)
    if match:
        RG, RW = match.groups()
        Cm = float(RG) / (float(RG) + float(RW))
        return get_viscosity_glycerol_water_mix(T, Cm)
    raise Exception(f'unknown material: {material}')


def get_viscosity_glycerol(T):
    A = 12.1
    B = -1233.0
    C = 9900.0
    D = 70.0
    num = np.multiply(np.subtract(B, T), T)
    den = np.add(C, np.multiply(D, T))
    return np.multiply(A, np.exp(np.divide(num, den)))




def get_viscosity_water(T):
    A = 0.00179
    B = -1230.0
    C = 36100.0
    D = 360.0
    num = np.multiply(np.subtract(B, T), T)
    den = np.add(C, np.multiply(D, T))
    return np.multiply(A, np.exp(np.divide(num, den)))




def get_viscosity_glycerol_water_mix(T, Cm):
    
    assert is_between(Cm, 0.0, 1.0)

    a = np.subtract(0.705, np.multiply(0.0017, T))
    b = np.multiply(np.add(4.9, np.multiply(0.036, T)), np.power(a, 2.5))
    num = np.multiply(np.multiply(a, b), np.multiply(Cm, np.subtract(1, Cm)))
    den = np.add(np.multiply(a, Cm), np.multiply(b, np.subtract(1, Cm)))
    alpha = np.add(np.subtract(1, Cm), np.divide(num, den))
    muw = get_viscosity_water(T)
    mug = get_viscosity_glycerol(T)
    mum = np.multiply(np.power(muw, alpha), np.power(mug, np.subtract(1, alpha)))
    return mum




def get_viscosity_s600(T):
    temperatures = [20,25,37.78,40,50,60,80,98.89,100]
    viscosities = [1.945,1.309,0.5277,0.4572,0.2511,0.1478,0.06091,0.03122,0.03017]
    return np.interp(T, temperatures, viscosities)




def get_material_viscosity(material, T):

    match = GLYCEROL_RE.match(material)
    if match:
        return get_viscosity_glycerol(T)

    match = GW_RE.match(material)
    if match:
        RG, RW = match.groups()
        Cm = float(RG) / (float(RG) + float(RW))
        return get_viscosity_glycerol_water_mix(T, Cm)

    match = S600_RE.match(material)
    if match:
        return get_viscosity_s600(T)

    match = NONE_RE.match(material)
    if match:
        return np.full(np.shape(T), 0.0)

    return np.full(np.shape(T), -1.0)



def get_material_heatcapacity(material):
    '''
    Get heat hapacity for glycerol mixtures in j/g•K
    '''
    
    CP_GLYCEROL = 2.43
    CP_WATER = 4.2
    
    match = GLYCEROL_RE.match(material)
    if match:
        return 2.43

    match = GW_RE.match(material)
    if match:
        RG, RW = match.groups()
        Cm = float(RG) / (float(RG) + float(RW))
        return (Cm*CP_GLYCEROL) + ( (1.0 - Cm)*CP_WATER) 

    raise Exception(f'No heat capacity data for material: {material}')
