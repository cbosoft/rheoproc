import numpy as np

from rheoproc.viscosity import get_material_heatcapacity

def get_predicted_temperature(log):
    P = np.multiply(log.speed, log.load_torque)

    dt = np.diff(log.time)
    dt = np.average([ [*dt, dt[-1]], [dt[0], *dt]], axis=0)
    dE = np.multiply(P, dt)
    E = np.cumsum(dE) # in J

    tp = int(len(log.time)*0.2)
    initial_temperature = np.mean(log.temperature[:tp])
    
    rho = get_density_material(log.material, initial_temperature)
    V = log.get_volume('l')
    m = rho*V*1000 # in g
    cp = get_material_heatcapacity(log.material)
    dT = E/(m*cp)
    T = np.add(dT, initial_temperature)
    return T