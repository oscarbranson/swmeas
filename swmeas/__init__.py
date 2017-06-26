import sys
from CO2_sensor import *
from O2_sensor import *
from live_plot import liveplot

if sys.version_info == (3,):
    sys.exit('Does not work in Python 3.')