import os, time
from .helpers import time_now

def log(Sensor, log_file, period=30., n_meas=5, n_wait=0.5,
        out_dir='/users/pi/log_data', usb_dir='/media/usb/log_data', usb_save=False):
    """
    Log data from a sensor.
    
    Parameters
    ----------
    Sensor : object
        A sensor object, with `read_multi` and `write`
        methods.
    log_file : str
        Name of log file.
    period : float
        Seconds between measurements.
    n_meas : int
        Number of repeat measurements to take.
    n_wait : float
        Seconds to wait between repeat measurements.
    out_dir : str
        A local path to a save directory.
    usb_dir : str
        The path to a save directory on a USB drive.
    usb_save : bool
        Whether or not to save data to a USB drive.
    """
    # ------------------------------------------
    # Set up file system
    # ------------------------------------------
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    # make a list of save locations
    out_paths = [out_dir + '/' + log_file]

    if usb_save:
        if not os.path.isdir(usb_dir):
            os.mkdir(usb_dir)
        out_paths.append(usb_dir + '/' + log_file)

    if os.path.exists('/home/pi/header.info'):
        with open('/home/pi/header.info', 'r') as f:
            extra = '\n' + f.read().strip()
    else:
        extra = ''

    # write file header
    tnow = time_now()
    nlog = 'START NEW LOG ' + tnow
    pad = '#' * len(nlog)
    header = '\n'.join([pad, nlog, extra, pad]) + '\n'
    for p in out_paths:
        with open(p, 'a+') as f:
            f.write(header)

    # ------------------------------------------
    # Logging
    # ------------------------------------------

    # Initialize sensor
    sensor = Sensor()

    # looped measurement
    measure = True
    while measure:
        time_startloop = os.times()[-1]

        # read data
        sensor.read_multi(n_meas, n_wait)
        # write data
        for p in out_paths:
            sensor.write(p)

        loop_time = os.times()[-1] - time_startloop
        if loop_time < period:
            sleeptime = period - loop_time

            time.sleep(sleeptime)
