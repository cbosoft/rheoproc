import os
import inspect
import sys

from matplotlib import pyplot

from rheoproc.error import warning
from rheoproc.usage import show_usage_and_exit
from rheoproc.util import runsh, get_hostname
from rheoproc.error import timestamp


def get_plot_name(subplot_name=None, ext='.pdf'):
    n = inspect.stack()[1].filename
    n = os.path.basename(n).replace('.py', '')

    if subplot_name:
        name = f'../img/{n}-{subplot_name}{ext}'
    else:
        name = f'../img/{n}{ext}'

    timestamp(f'Plotting "{name}"')

    return name



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
        pdfs_in = ' '.join(self.pages)
        pdf_out = self.path
        command = f'pdfunite {pdfs_in} {pdf_out}'
        runsh(command)


    def savefig(self):
        page_count = len(self.pages)
        page_path = f'{self.tmp}/tdlib_multi_page_plot-{page_count}.pdf'
        pyplot.savefig(page_path)
        self.pages.append(page_path)
