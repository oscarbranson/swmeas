import os
import time
import warnings

from .O2_sensor import O2_sensor
from .CO2_sensor import CO2_sensor
from .helpers import read_par, write_par, most_recent_json, timed_dir, find_sensor


def logAll(data_dir='./log_data/', interval=60, stop=0,
           O2_n=5, O2_wait=0.5, CO2_n=5, CO2_wait=1.,
           O2_ID=None, CO2_ID=None, sensor_json=None,
           new_folder_every=None, O2_mode='water', verbose=False, **kwargs):
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

    # if ID not specified, find a sensor listed in json file
    if CO2_ID is None:
        CO2_ID, CO2_name, CO2_port = find_sensor('CO2', sensor_json)
    else:
        CO2_name = ''
        CO2_port = None
    # if ID not specified, find a sensor listed in json file
    if O2_ID is None:
        O2_ID, O2_name, O2_port = find_sensor('TempO2', sensor_json)
    else:
        O2_name = ''
        O2_port = None

    # initialize sensors
    o2 = O2_sensor(ID=O2_ID, port=O2_port, name=O2_name)
    co2 = CO2_sensor(ID=CO2_ID, port=CO2_port, name=CO2_name)

    print('Logging...')

    # set up timing
    start_time = os.times()[-1]
    time_now = start_time
    run = True

    while run:
        # create timed subdirectory, if required
        if new_folder_every is not None:
            save_dir = timed_dir(data_dir, new_folder_every)
        else:
            save_dir = data_dir
        # do the logging
        time_startloop = os.times()[-1]
        elapsed = time_startloop - start_time  # total elapsed time at start of loop
        # print('Elapsed Time: {}'.format(time_startloop - start_time))
        # print('  CO2 Measurement')
        co2.read_multi(CO2_n, CO2_wait)
        co2.write_batch(save_dir + '/co2.csv')
        if verbose:
            print(co2.write_str[:-1])
        # print('')

        # print('  O2-Temp Measurement')
        o2.read_multi(O2_n, O2_wait)
        o2.write_TempO2_batch(save_dir + '/temp.csv', save_dir + '/o2.csv', mode=O2_mode)
        o2.write(save_dir + '/TempO2_raw.csv')
        if verbose:
            print(o2.write_str[:-1])
        # print('')

        # timing mechanics
        loop_time = os.times()[-1] - time_startloop
        # print('loop time: {:.1f}'.format(loop_time))
        if stop > 0:
            # if the next interval's start time > stop time
            if elapsed + loop_time + interval > stop:
                print('\nFinished.')
                break  # stop the loop
        if loop_time < interval:
            sleeptime = interval - loop_time
            # print('sleep time: {:.1f}'.format(sleeptime))
            time.sleep(sleeptime)

    return


def logCO2(data_dir='./log_data/', interval=30, stop=0,
           CO2_n=5, CO2_wait=1., CO2_ID=None, sensor_json=None,
           new_folder_every=None, verbose=False, **kwargs):
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
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    write_par(locals(), data_dir + '/logCO2.json')

    # if ID not specified, find a sensor listed in json file
    if CO2_ID is None:
        CO2_ID, CO2_name, CO2_port = find_sensor('CO2', sensor_json)
    else:
        CO2_name = ''
        CO2_port = None

    # initialize sensors
    co2 = CO2_sensor(ID=CO2_ID, port=CO2_port, name=CO2_name)

    print('Logging CO2...')

    # set up timing
    start_time = os.times()[-1]
    time_now = start_time
    run = True

    while run:
        # create timed subdirectory, if required
        if new_folder_every is not None:
            save_dir = timed_dir(data_dir, new_folder_every)
        else:
            save_dir = data_dir
        # do the logging
        time_startloop = os.times()[-1]  # time at start of loop
        elapsed = time_startloop - start_time  # total elapsed time at start of loop
        # print('Elapsed Time: {:.1f}'.format(elapsed))
        # print('  CO2 Measurement')
        co2.read_multi(CO2_n, CO2_wait)
        co2.write_batch(save_dir + '/co2.csv')
        if verbose:
            print(co2.write_str[:-1])
        # print('')

        # timing mechanics
        loop_time = os.times()[-1] - time_startloop
        # print('loop time: {:.1f}'.format(loop_time))
        if stop > 0:
            # if the next interval's start time > stop time
            if elapsed + loop_time + interval > stop:
                print('\nFinished.')
                break  # stop the loop
        if loop_time < interval:
            sleeptime = interval - loop_time
            # print('sleep time: {:.1f}'.format(sleeptime))
            time.sleep(sleeptime)

    return


def logTempO2(data_dir='./log_data/', interval=30, stop=0,
              O2_n=5, O2_wait=.5, O2_ID=None, sensor_json=None,
              mode='water', new_folder_every=None, verbose=False, **kwargs):
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
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    write_par(locals(), data_dir + '/logTempO2.json')

    # if ID not specified, find a sensor listed in json file
    if O2_ID is None:
        O2_ID, O2_name, O2_port = find_sensor('TempO2', sensor_json)
    else:
        O2_name = ''
        O2_port = None

    # initialize sensors
    o2 = O2_sensor(ID=O2_ID, port=O2_port, name=O2_name)

    print('Logging TempO2...')

    # set up timing
    start_time = os.times()[-1]
    time_now = start_time
    run = True

    while run:
        # create timed subdirectory, if required
        if new_folder_every is not None:
            save_dir = timed_dir(data_dir, new_folder_every)
        else:
            save_dir = data_dir
        # do the logging
        time_startloop = os.times()[-1]  # time at start of loop
        elapsed = time_startloop - start_time  # total elapsed time at start of loop
        # print('Elapsed Time: {:.1f}'.format(time_startloop - start_time))
        # print('  O2-Temp Measurement')
        o2.read_multi(O2_n, O2_wait)
        o2.write_TempO2_batch(save_dir + '/temp.csv', save_dir + '/o2.csv', mode=mode)
        if verbose:
            print(o2.write_str[:-1])
        o2.write(save_dir + '/TempO2_raw.csv')
        # print('')
        
        # timing mechanics
        loop_time = os.times()[-1] - time_startloop
        # print('loop time: {:.1f}'.format(loop_time))
        if stop > 0:
            # if the next interval's start time > stop time
            if elapsed + loop_time + interval > stop:
                print('\nFinished.')
                break  # stop the loop
        if loop_time < interval:
            sleeptime = interval - loop_time
            # print('sleep time: {:.1f}'.format(sleeptime))
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