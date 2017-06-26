import numpy as np
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import dates
from datetime import timedelta


def liveplot(paths, xlim_min=60, interval=5000):
    """
    create a live plot of the files listed in paths

    Parameters
    ----------
    ncol=
    """
    if isinstance(paths, str):
        paths = [paths]

    figsize = (5, 2 * len(paths))
    fig, axs = plt.subplots(len(paths), 1, figsize=figsize, sharex=True)

    if isinstance(axs, mpl.axes.Axes):
        axs = np.array([axs])

    def liveplot(i, axs, paths):

        for ax, path in zip(axs.flat, paths):
            # load data
            d = np.loadtxt(path, delimiter=',', converters={0: dates.datestr2num})

            # isolate time col, calculate stats
            t = np.array(dates.num2date(d[:, 0]))
            co2_mean = np.mean(d[:, 1:], 1)
            co2_std = np.std(d[:, 1:], 1)

            # update plot
            ax.clear()
            ax.plot(t, co2_mean, c='k')
            ax.fill_between(t, co2_mean - co2_std, co2_mean + co2_std,
                            color=(0, 0, 0, 0.2), zorder=-1)
            ax.set_ylabel(os.path.basename(path))

            # if t.ptp() > timedelta(minutes=60)
            ax.set_xlim(max(t) - timedelta(minutes=xlim_min), max(t))
            ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))

    ani = FuncAnimation(fig, liveplot, interval=interval, fargs=(axs, paths))

    fig.tight_layout(rect=(0.05, .0, 1, 1))

    plt.show()


if __name__ == '__main__':
    liveplot(['explot.csv'], 30)