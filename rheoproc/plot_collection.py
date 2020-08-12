import string

import numpy as np

from rheoproc.plot import pyplot as plt
from rheoproc.fft import get_fftx, get_ffty
from rheoproc.temperature import get_predicted_temperature
from rheoproc.viscosity import get_material_viscosity
from rheoproc.filter import moving_average
from rheoproc.label import *

# LogPlotter a class which manages the plotting of a specific subset of data
# from a single log. This could, for e.g., be for plotting the stress
# timeseries from a log.
# 
# The base class is a very generic version, which is made specific in the
# derived:
#  - TSLogPlotter takes y info and plots against time (timeseries)
#  - FFTLogPlotter takes y info and plots the fft of y against frequency (FFT)
#
# There are further derived classes which simplify the construction by being
# specifically for stress or strainrate or another specific log property.

class LogPlotter:

    def __init__(self, x_func, y_func, xlabel=None, ylabel=None):
        self.x_func = x_func
        self.y_func = y_func
        self.xlabel = xlabel
        self.ylabel = ylabel
    
    def get_x(self, log):
        return self.x_func(log)
    
    def get_y(self, log):
        return self.y_func(log)
    
    def get_xlabel(self):
        return self.xlabel
    
    def get_ylabel(self):
        return self.ylabel
    
    def plot(self, log):
        x = self.get_x(log)
        y = self.get_y(log)
        plt.plot(x, y)
        plt.xlabel(self.get_xlabel())
        plt.ylabel(self.get_ylabel())
        return x, y

###############################################################################
## TS Plotters

class TSLogPlotter(LogPlotter):
    def __init__(self, **kwargs):
        x_func = lambda log: log.time
        xlabel = time_label()
        super().__init__(x_func=x_func, xlabel=xlabel, **kwargs)


class StressTSLogPlotter(TSLogPlotter):

    def __init__(self):
        y_func = lambda log: log.stress
        ylabel = stress_label()
        super().__init__(y_func=y_func, ylabel=ylabel)


class StrainrateTSLogPlotter(TSLogPlotter):

    def __init__(self):
        y_func = lambda log: log.strainrate
        ylabel = strainrate_label()
        super().__init__(y_func=y_func, ylabel=ylabel)


class ViscosityTSLogPlotter(TSLogPlotter):

    def __init__(self):
        y_func = lambda log: log.viscosity
        ylabel = viscosity_label()
        super().__init__(y_func=y_func, ylabel=ylabel)
    
    def plot(self, log):
        x, y = super().plot(log)
        T = get_predicted_temperature(log)
        pmu = get_material_viscosity(log.material, T)
        plt.plot(x, pmu)
        return x, y


class TempTSLogPlotter(TSLogPlotter):

    def __init__(self):
        y_func = lambda log: log.temperature
        ylabel = temperature_label()
        super().__init__(y_func=y_func, ylabel=ylabel)
    
    def plot(self, log):
        x, y = super().plot(log)
        ma = moving_average(y, 1000)
        plt.plot(x, ma, '--')

        trise = get_predicted_temperature(log)
        plt.plot(x, trise)
        return x, y


###############################################################################
## FFT Plotters

class FFTLogPlotter(LogPlotter):

    def __init__(self, **kwargs):
        x_func = lambda log: get_fftx(log.time)
        xlabel = freq_label()
        super().__init__(x_func=x_func, xlabel=xlabel, **kwargs)
    
    def plot(self, log):
        x, y = super().plot(log)
        plt.xscale('log')

        rot_hz = np.mean(log.speed)
        plt.axvline(rot_hz, ls='--', color='orange')
        return x, y



class StressFFTLogPlotter(FFTLogPlotter):

    def __init__(self):
        y_func = lambda log: get_ffty(log.time, log.stress)
        ylabel = None
        super().__init__(y_func=y_func, ylabel=ylabel)


class StrainrateFFTLogPlotter(FFTLogPlotter):

    def __init__(self):
        y_func = lambda log: get_ffty(log.time, log.strainrate)
        ylabel = None
        super().__init__(y_func=y_func, ylabel=ylabel)


class ViscosityFFTLogPlotter(FFTLogPlotter):

    def __init__(self):
        y_func = lambda log: get_ffty(log.time, log.viscosity)
        ylabel = None
        super().__init__(y_func=y_func, ylabel=ylabel)


###############################################################################
## Plot Collection
# 
# A PlotCollection object manages the creation of axes for, and the plotting of
# a set of log properties (specified through the passed in list of log plotters).


class PlotCollection:


    def __init__(self, *, logplotters, title=None, fig=None, **kwargs):
        self.fig = fig if fig is not None else plt.figure()

        self.index = 0
        self.title = title
        self.letters = self._get_letters(**kwargs)
        self.logplotters = logplotters


    def _get_letters(self, parens=False, case='upper', **kwargs):
        letter_base = string.ascii_lowercase if case == 'lower' else string.ascii_uppercase
        parens = ('(', ')') if parens else ('', '')
        return [f'{parens[0]}{a}{parens[1]}' for a in letter_base]

    def plot_log(self, log, hspc=0.12, vspc=0.1, ax_width=0.4, ax_height=0.3):
        l = len(self.logplotters)
        axes = [None]*l

        total_width = hspc + ax_width + hspc
        total_height = vspc + ax_height + vspc
        border_width = total_width - hspc*0.5
        border_height = total_height*l + vspc
        dx = total_width * self.index
        for ax_index, logplotter in enumerate(self.logplotters):
            voff = total_height*(l - ax_index)
            ax_x = dx + hspc
            ax_y = voff - (vspc + ax_height)
            axes[ax_index] = plt.axes([ax_x, ax_y, ax_width, ax_height])
            logplotter.plot(log)
        
        self.fig.patches.extend([
            plt.Rectangle(
                (dx, -0.5*hspc),
                border_width,
                border_height,
                fc='none',
                ec='0.5',
                clip_on=False,
                lw=1,
                transform=self.fig.transFigure,
                ls='--'
            )
        ])
        letter = self.letters[self.index]
        title = self.get_title(log)
        plt.text(dx+0.05, total_height*l, f'\\huge \\textbf{{{letter}}}: {title}',
            clip_on=False,
            transform=self.fig.transFigure,
            size='x-large',
            ha='left',
            va='top')

        self.index += 1

        return axes
    
    def plot_logs(self, logs, plot_name=None, **kwargs):
        for log in logs:
            self.plot_log(log, **kwargs)
        
        if plot_name:
            plt.savefig(plot_name)


    def get_title(self, log):
        if isinstance(self.title, str):
            return self.title

        if log is not None and self.title is not None:
            return self.title(log)
        
        return ""