# Helper functions

def fmt(x, dec=1, sep=None):
    """
    Helper function for formatting outputs.
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