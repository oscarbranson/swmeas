import os
import time
import warnings

from .O2_sensor import O2_sensor
from .CO2_sensor import CO2_sensor
from .helpers import read_par, write_par, most_recent_json, timed_dir


def logAll(data_dir='./log_data/', interval=60, stop=0,
           O2_n=5, O2_wait=0.5, CO2_n=5, CO2_wait=1.,
           O2_ID='FT1HQ4GE', CO2_ID='FTHBSQZ9', new_folder_every=None, **kwargs):
    """
    Log CO2, O2 and Temp sequentially, and save to files in data_dir.

    Parameters
    ----------
    data_dir : str
        folder in which to store the data files.
    interval : float
        Time between measurements (seconds). Note that if this less than
        the measurement time, measurements will be run continuously
    stop : float
        How long you want the loop to run for (seconds). If zero,
        the loop will run until interrupted.
    O2_n : int
        The number of O2 measurements to make per loop.
    O2_n : float
        Time between individual O2 measurements.
    CO2_n : int
        The number of CO2 measurements to make per loop.
    CO2_wait : float
        Time between individual CO2 measurements.
    O2_ID : str
        The serial number of the O2 sensor
    CO2_ID : str
        The serial number of the CO2 sensor
    """
    # record parameters
    write_par(locals(), data_dir + '/logAll.json')

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    # create timed subdirectory, if required
    if new_folder_every is not None:
        data_dir = timed_dir(data_dir, new_folder_every)

    # initialize sensors
    o2 = O2_sensor(O2_ID)
    co2 = CO2_sensor(CO2_ID)

    print('Logging...')

    # set up timing
    start_time = os.times()[-1]
    time_now = start_time
    end_time = time_now + stop

    while (time_now < end_time) | (time_now == end_time):
        time_startloop = os.times()[-1]
        print('Elapsed Time: {}'.format(time_startloop - start_time))
        print('  CO2 Measurement')
        co2.read_multi(CO2_n, CO2_wait)
        co2.write_batch(data_dir + '/co2.csv')
        print(co2.write_str)
        print('')

        print('  O2-Temp Measurement')
        o2.read_multi(O2_n, O2_wait)
        o2.write_TempO2_batch(data_dir + '/temp.csv', data_dir + '/o2.csv')
        o2.write(data_dir + '/TempO2_raw.csv')
        print(o2.write_str)
        print('')

        if stop > 0:
            # if stop given, increment time_now so the loop eventually ends
            time_now = round(os.times()[-1])

        loop_time = os.times()[-1] - time_startloop
        print('loop time: {}'.format(loop_time))
        if loop_time < interval:
            sleeptime = interval - loop_time
            print('sleep time: {}'.format(sleeptime))
            time.sleep(sleeptime)

    return


def logCO2(data_dir='./log_data/', interval=60, stop=0,
           CO2_n=5, CO2_wait=1., CO2_ID='FTHBSQZ9', new_folder_every=None, **kwargs):
    """
    Log CO2 and save to files in data_dir.

    Can be used alongside logger_O2 to simultaneously collect both parameters

    Parameters
    ----------
    data_dir : str
        folder in which to store the data files.
    interval : float
        Time between measurements (seconds). Note that if this less than
        the measurement time, measurements will be run continuously
    stop : float
        How long you want the loop to run for (seconds). If zero,
        the loop will run until interrupted.
    CO2_n : int
        The number of CO2 measurements to make per loop.
    CO2_wait : float
        Time between individual CO2 measurements.
    CO2_ID : str
        The serial number of the CO2 sensor
    """
    # record parameters
    write_par(locals(), data_dir + '/logAll.json')

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    # create timed subdirectory, if required
    if new_folder_every is not None:
        data_dir = timed_dir(data_dir, new_folder_every)

    # initialize sensors
    co2 = CO2_sensor(CO2_ID)

    print('Logging...')

    # set up timing
    start_time = os.times()[-1]
    time_now = start_time
    end_time = time_now + stop

    while (time_now < end_time) | (time_now == end_time):
        time_startloop = os.times()[-1]
        print('Elapsed Time: {}'.format(time_startloop - start_time))
        print('  CO2 Measurement')
        co2.read_multi(CO2_n, CO2_wait)
        co2.write_batch(data_dir + '/co2.csv')
        print(co2.write_str)
        print('')
        
        if stop > 0:
            # if stop given, increment time_now so the loop eventually ends
            time_now = round(os.times()[-1])

        # timing mechanics
        loop_time = os.times()[-1] - time_startloop
        print('loop time: {}'.format(loop_time))
        if loop_time < interval:
            sleeptime = interval - loop_time
            print('sleep time: {}'.format(sleeptime))
            time.sleep(sleeptime)

    return


def logTempO2(data_dir='./log_data/', interval=60, stop=0,
              O2_n=5, O2_wait=.5, O2_ID='FT1HQ4GE',
              mode='water', new_folder_every=None, **kwargs):
    """
    Log O2 and Temp and save to files in data_dir.

    Can be used alongside logger_CO2 to simultaneously collect all parameters

    Parameters
    ----------
    data_dir : str
        folder in which to store the data files.
    interval : float
        Time between measurements (seconds). Note that if this less than
        the measurement time, measurements will be run continuously
    stop : float
        How long you want the loop to run for (seconds). If zero,
        the loop will run until interrupted.
    O2_n : int
        The number of O2 measurements to make per loop.
    O2_n : float
        Time between individual O2 measurements.
    O2_ID : str
        The serial number of the CO2 sensor
    """
    # record parameters
    write_par(locals(), data_dir + '/logAll.json')

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    # create timed subdirectory, if required
    if new_folder_every is not None:
        data_dir = timed_dir(data_dir, new_folder_every)

    # initialize sensors
    o2 = O2_sensor(O2_ID)

    print('Logging...')

    # set up timing
    start_time = os.times()[-1]
    time_now = start_time
    end_time = time_now + stop

    while (time_now < end_time) | (time_now == end_time):
        time_startloop = os.times()[-1]
        print('Elapsed Time: {}'.format(time_startloop - start_time))

        print('  O2-Temp Measurement')
        o2.read_multi(O2_n, O2_wait)
        o2.write_TempO2_batch(data_dir + '/temp.csv', data_dir + '/o2.csv')
        print(o2.write_str)
        o2.write(data_dir + '/TempO2_raw.csv')
        print('')

        if stop > 0:
            # if stop given, increment time_now so the loop eventually ends
            time_now = round(os.times()[-1])

        loop_time = os.times()[-1] - time_startloop
        print('loop time: {}'.format(loop_time))
        if loop_time < interval:
            sleeptime = interval - loop_time
            print('sleep time: {}'.format(sleeptime))
            time.sleep(sleeptime)

    return


def auto_log(mode='All', path=None, param_file=None):
    """
    Starts logging using parameters saved in .json file.

    Either path OR param_file should be specified.

    Parameters
    ----------
    mode : str
        - 'All' calls logAll
        - 'CO2' calls logCO2
        - 'TempO2' calls logTempO2
    path : str (optional)
        If specified, parameters are imported from the most
        recently modified .json file found in path.
    param_file : str (optional)
        The specific parameter file to use.

    """
    fndict = {'CO2': logCO2,
              'TempO2': logTempO2,
              'All': logAll}

    if mode in fndict:
        fn = fndict[mode]
    else:
        raise ValueError("{} is not a valid option.\n  > Please use 'All', 'CO2' or 'TempO2'.".format(mode))
    if param_file is None and path is None:
        raise ValueError('Please specify either param_file or path.')
    elif param_file is not None:
        if not os.path.exists(param_file):
            warnings.warn("param_file '{}' not found. Looking for other .json files...")
    else:
        if path is not None:
            param_file = most_recent_json(path)
        else:
            param_file = most_recent_json(os.getcwd())

    print('Using parameters in {}'.format(param_file))

    par = read_par(param_file)
    fn(**par)


if __name__ == '__main__':
    # logAll('./test_log/', 35, 0)

    pass