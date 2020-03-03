import numpy as np
from matplotlib import patches

import sympy as sy

class WCData(dict):

    def __init__(self, *, phi_o, phi_m, mu_f, sigma_star, beta):
        self['phi_o'] = phi_o
        self['phi_m'] = phi_m
        self['mu_f'] = mu_f
        self['sigma_star'] = sigma_star
        self['beta'] = beta
        self.phi_o = phi_o
        self.phi_m = phi_m
        self.mu_f = mu_f
        self.sigma_star = sigma_star
        self.beta = beta

class CSData(dict):

    def __init__(self, *, rho_cs=1.63, rho_water=1.0, rho_solvent=1.225, moisture_content=0.13, porosity=0.31):
        self['rho_cs'] = rho_cs
        self['rho_water'] = rho_water
        self['rho_solvent'] = rho_solvent
        self['moisture_content'] = moisture_content
        self['porosity'] = porosity
        self.rho_cs = rho_cs
        self.rho_water = rho_water
        self.rho_solvent = rho_solvent
        self.moisture_content = moisture_content
        self.porosity = porosity


def plot_phase_diagram(plt, *, phi_m, phi_o, mu_f, sigma_star, beta,
                       mass_fractions=False, compositions=None, names=None,
                       legend=True, lowphi=0.01, highphi=1.0, xlim_off=0.01, 
                       npoints=1000, sigma_max=1e4, sigma_min=0.1, yield_line=1e5,
                       **kwargs):
    assert 0.0 <= lowphi < highphi
    assert lowphi < highphi <= 1.0
    phi = np.linspace(phi_m*0.9, phi_o, npoints)
    sigma_jam = get_sigma_jam(phi, phi_m, phi_o, beta, sigma_star)
    #sigma_jam = sigma_jam_transition*20.0
    phi_dst, sigma_dst, __ = get_sigma_dst(phi_m=phi_m, phi_o=phi_o,
            mu_f=mu_f, sigma_star=sigma_star, beta=beta, phi_vec=phi)

    #phij_dst = np.interp(sigma_dst, sigma_jam_transition, phi)
    sigj_dst = np.interp(phi_dst, phi, sigma_jam)
    plt.fill_between(phi_dst, sigma_dst, sigj_dst, color='green', alpha=0.2)
    plt.fill_betweenx(sigma_dst, phi_dst, [phi_m]*len(phi_dst), where=[phi_dst_i < phi_m for phi_dst_i in phi_dst], color='green', alpha=0.2)
    #plt.fill_between(phi, sigma_jam_transition, sigma_jam, color='blue', alpha=0.2)
    plt.fill_between(phi, sigma_jam, yield_line, color='orange', alpha=0.4)
    plt.fill_betweenx([sigma_min, sigma_max], phi_o, 1.0, color='red', alpha=0.4)
    plt.plot(phi_dst, sigma_dst, color='green')
    #plt.plot(phi, sigma_jam_transition, color='blue')
    plt.plot(phi, sigma_jam, color='orange')
    plt.plot([phi_m, 1.0], [yield_line]*2, color='red', ls='--')

    plt.yscale('log')
    #plt.xscale('log')

    if compositions:
        assert isinstance(compositions, list)
        colors = [f'C{i}' for i in range(1,10)]

        if names:
            assert len(names) == len(compositions)

        for i, (composition, color) in enumerate(zip(compositions, colors)):

            if mass_fractions:
                assert 'rho_cs' in kwargs
                composition = get_phi_from_mf(composition, **kwargs)
                print('vf', composition)

            if names:
                lbl = names[i]
            else:
                lbl = f'$\\phi = {composition}$'
            plt.vlines([composition], ymin=sigma_min/10, ymax=sigma_max*10, linewidth=5, color=color, alpha=0.5, label=lbl)

    plt.axvline(phi_m, linestyle='--', color='0.3')
    plt.axvline(phi_o, linestyle='--', color='0.3')
    plt.text(phi_m*1.01, 2*sigma_min, '$\\phi_m$', ha='left')
    plt.text(phi_o*1.01, 2*sigma_min, '$\\phi_o$', ha='left')
    plt.xlabel(r'Volume Fraction, $\phi$')

    plt.ylabel(r"$\sigma\rm/Pa$")

    # plt.text(
    #         phi_o + (0.7*(highphi - phi_o)),
    #         100.0*sigma_star,
    #         f'$\\sigma^\\star = {sigma_star}$\n'+
    #         f'${conc}_m = {phi_m}$\n'+
    #         f'${conc}_o = {phi_o}$',
    #         ha='center',va='center', bbox=dict(edgecolor='gray',facecolor='white'))
    plt.text(
            lowphi + (0.3*(phi_m - lowphi)),
            np.power(sigma_max - sigma_min, 0.3),
            '\\centering Continuous Shear\\\\Thickening\\\\',
            ha='center',
            va='center')
    plt.text(
            phi_o + np.max([(0.5*(highphi - phi_o)), xlim_off/2]),
            np.power(sigma_max - sigma_min,0.3),
            'Jammed',
            ha='center',
            color='red')
    plt.text(
            phi_m + (0.5*(phi_o - phi_m)),
            np.nanmean(sigma_jam),
            'Shear Jammed',
            color='C1',
            ha='center',
            va='center')
    # plt.text(
    #         phi_m + (0.5*(phi_o - phi_m)),
    #         np.nanmean(sigma_jam_transition),
    #         'Transition',
    #         color='blue',
    #         ha='center',
    #         va='center')
    # plt.text(
    #         phi_o + (0.1*(highphi - phi_o)),
    #         3*yield_line,
    #         'Yielded (est)', 
    #         color='red',
    #         ha='left',
    #         va='center')
    plt.text(
            phi_m + 0.15*(phi_o-phi_m),
            sigma_star*2,
            '\\textbf{dst}',
            color='green',
            ha='center',
            va='center')

    plt.xlim(left=lowphi-xlim_off, right=highphi+xlim_off)
    plt.ylim(bottom=sigma_min, top=sigma_max)
    if legend and compositions:
        plt.legend(loc='center', bbox_to_anchor=(0.5, -.3, 0.0, 0.0), ncol=(len(compositions)//2)+1)


    if 'rho_cs' in kwargs.keys():
        ax = plt.gca()
        twax = ax.twiny()
        #twax.set_xscale('log')
        ticks = ax.get_xticks()
        mfs = ticks
        vfs = [get_phi_from_mf(mfi, **kwargs) for mfi in mfs]
        twax.set_xticks(vfs)
        twax.set_xticklabels([f'{mf:.2f}' for mf in mfs])
        twax.set_xlim(ax.get_xlim())
        twax.set_xlabel(r'Mass Fraction, $w$')
        plt.sca(ax)

def get_phij(f, phi_m, phi_o):
    return np.add(np.multiply(f, phi_m), np.multiply(np.subtract(1, f), phi_o))

def get_eta(phi, phij, etaf):
    rv = np.power(np.subtract(1, np.divide(phi, phij)), -2)
    #if phi > phij:
    #    rv = np.nan
    return np.multiply(rv, etaf)

def get_f(sigma, sigma_star, beta):
    rv = np.exp(np.multiply(-1, np.power(np.divide(sigma_star, sigma), beta)))
    return rv

def get_gamma_dot(sigma, eta):
    rv = np.divide(sigma, eta)
    #if np.isnan(rv):
    #    rv = 0.0
    return rv

def get_sigma_jam(phi, phi_m, phi_o, beta, sigma_star):
    A = np.multiply(np.log(np.divide(np.subtract(phi, phi_o), np.subtract(phi_m, phi_o))), -1)
    return np.divide(sigma_star, np.power(A, 1.0/beta))
    #f_sigj = sy.lambdify([sigma_star, phi, phi_o, phi_m, beta], e_sigj, 'numpy')
    #print(phi, phi_m, phi_o, beta, sigma_star)
    #return f_sigj(sigma_star, phi, phi_o, phi_m, beta)


srho_cs, srho_water, srho_solvent, sporosity, smoisture_content, smf, sphi = sy.symbols('rho_cs rho_water rho_solvent porosity moisture_content mf phi', real=True)
e_A = (1.0 - smoisture_content) * (smf / srho_cs)
e_B = 1. / (1. - sporosity)
e_phi_and_mf = e_B * e_A/(e_A+((1-smf)/srho_solvent) + (smoisture_content * (smf / srho_water))) - sphi

def get_mf_from_phi(phi, rho_cs, rho_water, rho_solvent, porosity, moisture_content):
    se = e_phi_and_mf.subs({
        srho_cs : rho_cs,
        srho_water : rho_water,
        srho_solvent : rho_solvent,
        sporosity: porosity,
        smoisture_content: moisture_content,
    })
    e = sy.solve(se, smf)[0]
    f = sy.lambdify([sphi], e, 'numpy')
    return f(np.array(phi, dtype=np.float64))
    
def get_phi_from_mf(mf, rho_cs, rho_water, rho_solvent, porosity, moisture_content):
    A = np.multiply(np.subtract(1, moisture_content), np.divide(mf, rho_cs))
    B = np.divide(1, np.subtract(1, porosity))
    return np.multiply(B, np.divide(A, np.add(A, np.add(np.divide(np.subtract(1, mf), rho_solvent), np.multiply(moisture_content, np.divide(mf, rho_water))))))


sigma, sigma_star, phi, phi_m, phi_o, mu_f, beta = sy.symbols('sigma sigma_star phi phi_m phi_o mu_f beta', real=True)
e_f = sy.exp(-1.* (sy.Pow((sigma_star/sigma), beta)))
e_phij = e_f*(phi_m - phi_o) + phi_o
e_mu = mu_f*sy.Pow(1-(phi/e_phij),-2.0)
e_gd = sigma/e_mu
e_dgds = sy.diff(e_gd, sigma)
e_sigj = sigma_star / sy.Pow(-sy.log( (phi - phi_o) / (phi_m - phi_o) ), 1./beta)

f_f    = sy.lambdify([sigma, sigma_star, beta], e_f, 'numpy')
f_phij = sy.lambdify([sigma, sigma_star, beta, phi_m, phi_o], e_phij, 'numpy')
f_mu   = sy.lambdify([sigma, sigma_star, beta, phi_m, phi_o, phi, mu_f], e_mu, 'numpy')
f_gd   = sy.lambdify([sigma, sigma_star, beta, phi_m, phi_o, phi, mu_f], e_gd, 'numpy')
f_dgds = sy.lambdify([sigma, sigma_star, beta, phi_m, phi_o, phi, mu_f], e_dgds, 'numpy')
f_sigj = sy.lambdify([sigma_star, phi, phi_o, phi_m, beta], e_sigj, 'numpy')

def get_sigma_dst(*, sigma_star, beta, phi_m, phi_o, mu_f, 
        sigma_threshold=0.1, grad_threshold=1e-5, sigma_min=0.01, sigma_max=1e4, n=1000, phi_vec=None, **kwargs):
    sigma_vec = np.power(10, np.linspace(int(np.log10(sigma_min)), int(np.log10(sigma_max)), n))
    phi_vec = phi_vec if phi_vec is not None else np.linspace(0.9*phi_m, phi_o, n)
    sigma_DST = list()
    phi_DST = list()
    gd_DST = list()
    for sigma in sigma_vec:
        grad_vec = f_dgds(sigma, sigma_star, beta, phi_m, phi_o, phi_vec, mu_f)
        for phi, grad in zip(phi_vec, grad_vec):
            if  -grad_threshold < grad < grad_threshold:
                sig_j = get_sigma_jam(phi, phi_m, phi_o, beta, sigma_star)
                if np.power((sig_j - sigma)/sig_j, 2.0) < sigma_threshold:
                    continue
                sigma_DST.append(sigma)
                phi_DST.append(phi)
                gd_DST.append(f_gd(sigma, sigma_star, beta, phi_m, phi_o, phi, mu_f))
                break
    phi_off = phi_o - phi_DST[0]
    phi_DST = np.add(phi_DST, phi_off)
    return phi_DST, sigma_DST, gd_DST
