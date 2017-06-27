import json
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
    print('\nUse an ID that identifies one of these ports.\n\n')

    return ports


def write_par(param_dict, path):
    with open(path, 'w+') as f:
        json.dump(param_dict, f)
    return


def read_par(path):
    with open(path, 'r') as f:
        param_dict = json.load(f)
    return param_dict



if __name__ == "__main__":
    print(portscan())