import sys
import os
import json
import datetime as dt
from dateutil import parser
from serial.tools import list_ports


# Helper functions
def fmt(x, dec=1, sep=None):
    """
    Formatting list of dat for output.

    Parameters
    ----------
    dec : int
        Decimal places applied to all numbers
    sep : str
        If specified, all items in list are joined using this str.
    """
    fmt_str = '{:.' + str(dec) + 'f}'
    if isinstance(x, (float, int)):
        return fmt_str.format(x)
    elif hasattr(x, '__iter__'):
        out = []
        for i in x:
            if isinstance(i, (float, int)):
                out.append(fmt_str.format(i))
            else:
                out.append(i)
        if sep is None:
            return out
        else:
            return sep.join(out)


def timed_dir(directory, new_folder_every='day'):
    if new_folder_every is None or 'day' in new_folder_every:
        time_gap = dt.timedelta(days=1)
        fmt = '%Y-%m-%d'
    elif 'hour' in new_folder_every:
        time_gap = dt.timedelta(hours=1)
        fmt = '%Y-%m-%d-%H'
    else:
        raise ValueError("now_folder_every must be either 'day' or 'hour'")

    now = dt.datetime.now()

    dtimes = []
    current_dirs = os.listdir(directory)
    for d in current_dirs:
        try:
            dtimes.append(parser.parse(d))
        except ValueError:
            pass

    most_recent = max(dtimes)

    if ((now - most_recent) >= time_gap) | (len(dtimes) == 0):
        ndir = directory + '/' + now.strftime(fmt)
        os.mkdir(ndir)
        return ndir
    else:
        return directory + '/' + most_recent.strftime(fmt)


def portscan(ID=None):
    """
    Scans available comports.

    If ID is specified, returns path of the commport that
    contains ID anywhere in its properties.
    If ID is not specified, prints and returns a list of
    comports.

    """
    ports = list_ports.comports()

    if ID is not None:
        for p in ports:
            if any([ID in i for i in p]):
                return p[0]
        print("\n\nNo port with ID '{}' found. These are the available ports:".format(ID))
    else:
        print("\n\nAvailable ports:")

    # line lengths
    L1 = max(len(p[0]) for p in ports) + 5
    L2 = max(len(p[1]) for p in ports) + 5
    fmt_str = "{:" + str(L1) + "s} {:" + str(L2) + "s} {}"
    for p in ports:
        print(fmt_str.format(p[0], p[1], p[2]))
    # print('\nUse an ID that identifies one of these ports.\n\n')

    return ports


def load_sensor_IDs(SNs_json=None):
    """
    Load sensor information from json file.

    Paramers
    --------
    SNs_json : str
        Path to json file. If None, uses built in default.

    Returns
    -------
    dict
    """
    if SNs_json is None:
        SNs_json = os.path.dirname(sys.modules['swmeas'].__file__) + '/resources/sensor_SNs.json'

    with open(SNs_json, 'r') as f:
        sensor_dict = json.load(f)

    return sensor_dict


def find_sensor(stype=None, SNs_json=None):
    """
    Scans ports to find any of the sensors listed in SNs_json

    Parameters
    ----------
    stype : str
        The type of sensor to look for. Must match or be within a key in SNs_json.
    SNs_json : str
        Path to json file containing sensor information.
    Returns
    -------
    (SN, Name, port) : tuple
    """
    sensor_dict = load_sensor_IDs(SNs_json)

    try:
        skey = [k for k in sensor_dict.keys() if stype in k][0]
    except IndexError:
        raise ValueError(("Sensor type '{}' not in SNs_json keys.\n".format(stype) +
                          "Correct stype, or update SNs_json file."))

    slist = sensor_dict[skey]
    # if stype == 'CO2':
    #     slist = sensor_dict['CO2_sensor_SNs']
    # elif stype == 'TempO2':
    #     slist = sensor_dict['TempO2_sensor_SNs']
    # else:
    #     raise ValueError("Sensor type '{}' not supported.\nShould be either 'CO2' or 'TempO2'.".format(stype))

    ports = portscan()

    available = []
    port = []
    for s in slist:
        for p in ports:
            if any(s[0] in i for i in p):
                available.append(s)
                port.append(p[0])

    if len(available) == 0:
        raise ValueError("No {} sensor found. Is it plugged in?!".format(stype))
        return
    elif len(available) > 1:
        print('More than one {} sensor found. Please specify one of them manually:\n')
        print('  \n'.join(['{}'.format(s[0] for s in available)]))
        return
    else:
        a = available[0]
        print("\n{} sensor {} ({}) found.\n".format(stype, a[1], a[0]))
        return a + port


def edit_par(par_file='params.json', data_dir=None, interval=None, stop=None,
             O2_n=None, O2_wait=None, CO2_n=None, CO2_wait=None,
             O2_ID=None, CO2_ID=None):

    if os.path.exists(par_file):
        par_out = read_par(par_file)
    else:
        par_out = {}

    par_update = {}
    for k, v in locals().iteritems():
        if k not in ('par_file', 'par_out'):
            if v is not None:
                par_out[k] = v

    par_out.update(par_update)

    write_par(par_out, par_file)


def write_par(param_dict, path):
    if path[-5:] != '.json':
        path += '.json'

    if 'kwargs' in param_dict:
        param_dict.pop('kwargs')
    with open(path, 'w+') as f:
        json.dump(param_dict, f, indent=2)
    return


def read_par(path):
    with open(path, 'r') as f:
        param_dict = json.load(f)
    return param_dict


def most_recent_json(path):
    """
    Returns most recently modified .json file in path.
    """
    max_mtime = 0
    walk = os.walk('.')
    for dirname, subdirs, files in walk:
        for fname in files:
            if 'json' in fname.lower():
                full_path = os.path.join(dirname, fname)
                mtime = os.stat(full_path).st_mtime
                if mtime > max_mtime:
                    max_mtime = mtime
                    max_dir = dirname
                    max_file = fname

    return max_dir + '/' + max_file


if __name__ == "__main__":
    # timed_dir('./test/')

    import dateutil
    print(dateutil.__version__)
