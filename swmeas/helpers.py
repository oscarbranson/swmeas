import sys
import os
import json
import datetime as dt
from dateutil import parser
from serial.tools import list_ports


# Helper functions
# def fmt(x, dec=1, sep=None):
#     """
#     Formatting list of dat for output.

#     Parameters
#     ----------
#     dec : int
#         Decimal places applied to all numbers
#     sep : str
#         If specified, all items in list are joined using this str.
#     """
#     if dec is not None:
#         fmt_str = '{:.' + str(dec) + 'f}'
#     else:
#         fmt_str = '{:}'
#     if isinstance(x, (float, int)):
#         return fmt_str.format(x)
#     elif hasattr(x, '__iter__'):
#         out = []
#         for i in x:
#             if isinstance(i, (float, int)):
#                 out.append(fmt_str.format(i))
#             else:
#                 out.append(i)
#         if sep is None:
#             return out
#         else:
#             return sep.join(out)

# def write(dat, file, dec=None, sep=','):
#     """
#     Append data to file.
#     """
#     wstr = ''
#     if isinstance(dat[0], list):
#         lines = []
#         for d in dat:
#             lines.append(fmt(d, dec, sep))
#         wstr = '\n'.join(lines)
#     else:
#         wstr += fmt(dat, dec, sep)
    
#     with open(file, 'a+') as f:
#         f.write(wstr)

# def timed_dir(directory, new_folder_every='day'):
#     if new_folder_every is None or 'day' in new_folder_every:
#         time_gap = dt.timedelta(days=1)
#         fmt = '%Y-%m-%d'
#     elif 'hour' in new_folder_every:
#         time_gap = dt.timedelta(hours=1)
#         fmt = '%Y-%m-%d-%H'
#     else:
#         raise ValueError("now_folder_every must be either 'day' or 'hour'")

#     now = dt.datetime.now()

#     dtimes = []
#     current_dirs = os.listdir(directory)
#     for d in current_dirs:
#         try:
#             dtimes.append(parser.parse(d))
#         except ValueError:
#             pass

#     if len(dtimes) > 0:
#         most_recent = max(dtimes)

#         if ((now - most_recent) >= time_gap):
#             ndir = directory + '/' + now.strftime(fmt)
#             os.mkdir(ndir)
#             return ndir
#         else:
#             return directory + '/' + most_recent.strftime(fmt)
#     else:
#         ndir = directory + '/' + now.strftime(fmt)
#         os.mkdir(ndir)
#         return ndir

## Output functions
def fmt(a, fmt_str="{:.3f}"):
    """
    Recursively format all elements of `a` according to `fmt_str`.

    Strings are returned as-is, with no modification.

    Parameters
    ----------
    a : str, numeric or iterable
    fmt_str : str
        Valid formatting string, default is `"{:.3f}"`
    
    Returns
    -------
    list of formatted values
    """
    if isinstance(a, str):
        return a
    elif isinstance(a, (int, float)):
        return fmt_str.format(a)
    else:
        return [fmt(i, fmt_str) for i in a]

def fmt_lines(a, fmt_str="{:.2f}", sep=','):
    """
    Format output as lines of text.
    
    Parameters
    ----------
    a : iterable
        Data to format.
    fmt_str : str
        Format specification for numbers.
    sep : str
        Character used to separate data
    
    Returns
    -------
    str
        formatted data.
    """
    f = fmt(a, fmt_str)
    if isinstance(f[0], str):
        return sep.join(f)
    else:
        return '\n'.join([sep.join(r) for r in f])

## Misc Helpers
def time_now():
    """
    Return the current time as a formatted str (to nearest 0.1 second).
    """
    tnow = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())
    return tnow + '{:.1f}'.format(time.time() % 1)[-2:]


if __name__ == "__main__":
    print('Nothing to see here...')
