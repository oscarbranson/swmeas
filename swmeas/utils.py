import sys, os, json
from dateutil import parser
from subprocess import check_output
from serial.tools import list_ports
from pkg_resources import resource_string

## Control Utilities
def check_usb_mounted():
    """
    Returns True if a USB storage device in mounted to /media/usb0
    """
    mnt = check_output(['mount']).splitlines()
    for m in mnt[::-1]:
        if 'usb0' in str(m.split()[2]):
            return True
    return False

## Sensor connection and identification functions
def portscan(ID=None, silent=True):
    """
    Scans available comports.

    If ID is specified, returns path of the commport that
    contains ID anywhere in its properties.
    If ID is not specified, prints and returns a list of
    comports.

    Returns:
    IF found: (port, Serial_number)
    if not, list of ports.

    """
    ports = list_ports.comports()

    if ID is not None:
        for p in ports:
            if any([ID in i for i in p]):
                return p
        if not silent:
            print("\n\nNo port with ID '{}' found. These are the available ports:".format(ID))
    else:
        if not silent:
            print("\n\nAvailable ports:")

    if not silent and (len(ports) > 0):
        # line lengths
        L1 = max(len(p[0]) for p in ports) + 5
        L2 = max(len(p[1]) for p in ports) + 5
        fmt_str = "{:" + str(L1) + "s} {:" + str(L2) + "s} {}"
        for p in ports:
            print(fmt_str.format(p[0], p[1], p[2]))
        # print('\nUse an ID that identifies one of these ports.\n\n')
    else:
        print('   Nothing Connected.')
    return None


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
        sensor_dict = eval(resource_string('swmeas', '/resources/sensor_SNs.json'))
    else:
        with open(SNs_json, 'r') as f:
            sensor_dict = json.load(f)

    return sensor_dict


def get_sensor_name(SN, SNs_json=None):

    sdict = load_sensor_IDs(SNs_json)

    for k, v in sdict.items():
        for sn, name in v:
            if SN == sn:
                return name
    return ''


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

    ports = list_ports.comports()

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

# Sensor database management
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