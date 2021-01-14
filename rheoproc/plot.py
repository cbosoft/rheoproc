# rheoproc.plot
# Provides a thin wrapper around pyplot to preempt some erroes (looking at you MacOS11 bug) as well as a class to manage
# the creation of a multi-page 'booklet' plotter.

import os
import inspect
import sys
from collections import defaultdict

from rheoproc.util import is_mac

if is_mac():
    import matplotlib as mpl
    mpl.use('macosx') # avoid tkinter issue on macOS 11.1 beta
from matplotlib import pyplot

from rheoproc.error import warning
from rheoproc.usage import show_usage_and_exit
from rheoproc.util import runsh, get_hostname
from rheoproc.error import timestamp


def get_plot_name(subplot_name=None, ext='.pdf'):
    n = inspect.stack()[1].filename
    d = os.path.dirname(n)
    loc = '.' if not d else os.path.relpath(d, '.')
    n = os.path.basename(n).replace('.py', '')

    if subplot_name:
        name = f'../img/{loc}/{n}-{subplot_name}{ext}'
    else:
        name = f'../img/{loc}/{n}{ext}'

    loc = os.path.dirname(name)
    if not os.path.isdir(loc):
        timestamp(f'Creating previously absent directory "{loc}"')
        os.mkdir(loc)
    timestamp(f'Plotting "{name}"')

    return name


class Styler:

    def __init__(self):
        self.styles = dict()

    def _call_or_get(self, item):
        if item not in self.styles:
            self.styles[item] = self.get_style(item)
        return self.styles[item]

    def __call__(self, item):
        return self._call_or_get(item)

    def __getitem__(self, item):
        return self._call_or_get(item)

    def get_style(self, item):
        raise NotImplementedError('Not Implemented')


class Colourist(Styler):
    ''' Class which dishes out colours based on a key.
    Uses the matplotlib default colours by default,
    override method "get_colour(i)" to change
    colouring behaviour.'''

    def get_style(self, item):
        '''Called once per item, on first creation of the style (i.e. item is not in styles dict yet).'''
        return self.get_colour(len(self.styles))

    @staticmethod
    def get_colour(i: int) -> str:
        return f'C{i}'

class Shaperist:
    '''as colurist, but for marker shapes.'''

    def get_style(self, item):
        '''Called once per item, on first creation of the style (i.e. item is not in styles dict yet).'''
        return self.get_shape(len(self.styles))

    @staticmethod
    def get_shape(i: int) -> str:
        strs = 'ovs*PD^1pX'
        i = i % len(strs)
        return strs[i]


__orig_plot = pyplot.plot
def __plot_wrapped(*args, colour_by=None, shape_by=None, colourist=None, shaperist=None, auto_raster=True, **kwargs):
    if args and auto_raster:
        if len(args[0]) > 10000:
            kwargs['rasterized'] = True
    if colour_by is None:
        if shape_by is None:
            __orig_plot(*args, **kwargs)
        else:
            x, y = args[:2]
            args = args[2:]
            xc, yc = defaultdict(list), defaultdict(list)

            for xi, yi, ci in zip(x, y, shape_by):
                xc[ci].append(xi)
                yc[ci].append(yi)

            for c in xc.keys():
                x, y = xc[c], yc[c]
                _kwargs = {'fmt': shaperist[c], **kwargs}
                __plot_wrapped(x, y, *args, **_kwargs)
    else:
        x, y = args[:2]
        args = args[2:]
        xc, yc = defaultdict(list), defaultdict(list)

        for xi, yi, ci in zip(x, y, colour_by):
            xc[ci].append(xi)
            yc[ci].append(yi)

        for c in xc.keys():
            x, y = xc[c], yc[c]
            _kwargs = {'color': colourist[c], 'label': c, **kwargs}
            __plot_wrapped(x, y, *args, **_kwargs)
pyplot.plot = __plot_wrapped

__orig_legend = pyplot.legend
def __legend_wrapped(*args, position=None, position_offset=0.02, **kwargs):
    if position == 'right':
        t = 1.0 + position_offset
        __orig_legend(loc='center left', bbox_to_anchor=(t, 0.5))
    elif position == 'above':
        t = 1.0 + position_offset
        __orig_legend(loc='lower center', bbox_to_anchor=(0.5, t))
    else:
        __orig_legend(*args, **kwargs)
pyplot.legend = __legend_wrapped

def plot_init(*args, **kwargs):
    '''Legacy wrapper around matplotlib.'''
    return pyplot



class MultiPagePlot:
    '''
    Context manager which manages the creation of a multi-page pdf plot from 
    pyplot. Pyplot has their own multipage pdf facility, but for huge booklets 
    it is really slow. This solution saves many single plots to a temporary 
    directory, then stitches them together.

    Example usage:

        with MultiPagePlot('path_to_save_booklet.pdf', tmp='/tmp') as pdf:
            # plot a bunch of figures
            plt.figure()
            plt.plot(x1, y1)

            pdf.savefig() #  use pdf.savefig to save plot to booklet

            plt.close()

            plt.figure()
            plt.plot(x2, y2)
            pdf.savefig()
            plt.close()

            ...

    '''

    def __init__(self, path, tmp='/tmp'):
        self.path = path
        self.tmp = tmp
        self.pages = list()


    def __enter__(self):
        return self


    def __len__(self):
        return len(self.pages)


    def __exit__(self, *args):
        if self.pages:
            pdfs_in = ' '.join(self.pages)
            pdf_out = self.path
            command = f'pdfunite {pdfs_in} {pdf_out}'
            runsh(command)


    def savefig(self):
        page_count = len(self.pages)
        page_path = f'{self.tmp}/tdlib_multi_page_plot-{page_count}.pdf'
        pyplot.savefig(page_path)
        self.pages.append(page_path)
