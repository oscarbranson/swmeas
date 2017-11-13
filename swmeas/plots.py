import numpy as np
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import dates
from datetime import timedelta
from dateutil import parser


def dfmt(dstr):
    """
    function for reading dates
    """
    return dates.date2num(parser.parse(dstr))


def liveplot(files, directory='./', xlim_min=60, interval=10, latest_dir=False):
    """
    create a live plot of the files listed in paths

    Parameters
    ----------
    directory : str
        Base folder containing the files to plot
    files : list
        A list of files to plot
    xlim_min : float
        The range of x, in minutes.
    interval : float
        Plot refresh rate, in seconds.
    dir : str
        If True, searches for most recently named
        dir in path. Useful for plotting logs.
    """
    if latest_dir:
        try:
            dirs = os.listdir(directory)
            ds = []
            for d in dirs:
                try:
                    ds.append([d, parser.parse(d)])
                except ValueError:
                    pass
            filepath = sorted(ds, key=lambda x: x[-1], reverse=True)[0][0]
        except:
            raise ValueError('No dated directories found in {}'.format(directory))
    else:
        filepath = directory

    if isinstance(files, str):
        files = [files]

    figsize = (5, 2 * len(files))
    fig, axs = plt.subplots(len(files), 1, figsize=figsize, sharex=True)

    if isinstance(axs, mpl.axes.Axes):
        axs = np.array([axs])

    def liveplot(i, axs, files):

        for ax, file in zip(axs.flat, files):
            # load data
            d = np.genfromtxt(filepath + '/' + file, delimiter=',', converters={0: dfmt})

            # isolate time col, calculate stats
            t = np.array(dates.num2date(d[:, 0]))
            co2_mean = np.mean(d[:, 1:], 1)
            co2_std = np.std(d[:, 1:], 1)

            # # this could be more efficient by just updating the line data? e.g.:
            # line, = ax.plot(dates,plt_data, "o-")
            # plt.show(block=False)

            # while True:
            #   # use some method as the one proposed by jcoppens to read your new data
            #   line.set_data(new_dates, new_data)
            #   # timeout/sleep until new data arrives
            # from: https://stackoverflow.com/questions/31231781/self-updating-graphs-over-time-with-python-and-matplotlib

            # update plot
            ax.clear()
            ax.plot(t, co2_mean, c='k')
            ax.fill_between(t, co2_mean - co2_std, co2_mean + co2_std,
                            color=(0, 0, 0, 0.2), zorder=-1)
            ax.set_ylabel(os.path.basename(file))

            # if t.ptp() > timedelta(minutes=60)
            ax.set_xlim(max(t) - timedelta(minutes=xlim_min), max(t))
            ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))

    ani = FuncAnimation(fig, liveplot, interval=interval * 1000., fargs=(axs, files))

    fig.tight_layout(rect=(0.05, .0, 1, 1))

    plt.show()


if __name__ == '__main__':
    liveplot(directory='/Users/oscarbranson/Desktop/co2_log/', files=['co2.csv'], xlim_min=30)