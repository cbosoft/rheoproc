import numpy as np


def gentwo(N, alpha, *, beta=None, randfunc=np.random.standard_normal):
    a = randfunc(N)
    b = randfunc(N)

    if beta:
        if not ((alpha**2) + beta**2) == 1:
            raise Exception('alpha^2 + beta^2 \\neq 1')
    else:
        beta = (1-(alpha**2))**0.5

    y1 = a
    y2 = np.add(np.multiply(a, alpha), np.multiply(b, beta))

    return y1, y2


def genOU(N, dt=1.0, tau=1.0, c=1.0):
    mu = np.exp(-dt/tau)
    sigma2_X = 0.5*c*tau*(1.0-mu*mu)
    sigma2_Y = c*tau**3*(dt/tau-2.0*(1.0-mu)+0.5*(1.0-mu*mu))
    kappa_XY = (0.5*c*tau*tau)*(1.0-mu)**2
    sigma_X = np.sqrt(sigma2_X)
    sigma_Y = np.sqrt(sigma2_Y)
    
    X = 0.0
    Y = 0.0
    Xs = list()
    Ys = list()
    for k in range(N):
        n1 = np.random.normal(0.0, 1.0)
        n2 = np.random.normal(0.0, 1.0)
        dX = X*(mu-1.0) + sigma_X*n1
        dY = X*tau*(1.0-mu) + (kappa_XY/sigma_X)*n1 \
          + np.sqrt(sigma_Y**2-(kappa_XY/sigma_X)**2)*n2
        X += dX
        Y += dY
        Xs.append(X)
        Ys.append(Y)
    return Xs, Ys, sigma_Y
