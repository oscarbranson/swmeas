import os, time

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
        out_paths.append([usb_dir + '/' + log_file])
    
    # write file header
    for p in out_paths:
        with open(p, 'a+') as f:
            f.write('#################\n# START NEW LOG #\n#################\n')

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




# import os
# import time
# import warnings

# from .O2_sensor import O2_sensor
# from .CO2_sensor import CO2_sensor
# from .helpers import read_par, write_par, most_recent_json, timed_dir, find_sensor


# def logCO2(data_dir='./log_data/', interval=30, stop=0,
#            n=5, wait=1., ID=None, sensor_json=None,
#            new_folder_every=None, verbose=False, **kwargs):
#     """
#     Log CO2 and save to files in data_dir.

#     Can be used alongside logger_O2 to simultaneously collect both parameters

#     Parameters
#     ----------
#     data_dir : str
#         folder in which to store the data files.
#     interval : float
#         Time between measurements (seconds). Note that if this less than
#         the measurement time, measurements will be run continuously
#     stop : float
#         How long you want the loop to run for (seconds). If zero,
#         the loop will run until interrupted.
#     n : int
#         The number of CO2 measurements to make per loop.
#     wait : float
#         Time between individual CO2 measurements.
#     ID : str
#         A unique identifier of the sensor (e.g. serial number). If None
#         a sensor of the correct type is found automatically.
#     """
#     # record parameters
#     if not os.path.exists(data_dir):
#         os.mkdir(data_dir)
#     write_par(locals(), data_dir + '/logCO2.json')

#     # if ID not specified, find a sensor listed in json file
#     if ID is None:
#         co2 = CO2_sensor()  # find sensor automatically
#     else:
#         co2 = CO2_sensor(ID=ID)

#     print('Logging CO2...')

#     # initialize sensor
#     start_time = os.times()[-1]
#     time_now = start_time
#     run = True

#     while run:
#         # create timed subdirectory, if required
#         if new_folder_every is not None:
#             save_dir = timed_dir(data_dir, new_folder_every)
#         else:
#             save_dir = data_dir
#         # do the logging
#         time_startloop = os.times()[-1]  # time at start of loop
#         elapsed = time_startloop - start_time  # total elapsed time at start of loop
#         # print('Elapsed Time: {:.1f}'.format(elapsed))
#         # print('  CO2 Measurement')
#         co2.read_multi(n, wait)
#         co2.write_batch(save_dir + '/co2.csv')
#         if verbose:
#             print(co2.write_str[:-1])
#         # print('')

#         # timing mechanics
#         loop_time = os.times()[-1] - time_startloop
#         # print('loop time: {:.1f}'.format(loop_time))
#         if stop > 0:
#             # if the next interval's start time > stop time
#             if elapsed + loop_time + interval > stop:
#                 print('\nFinished.')
#                 break  # stop the loop
#         if loop_time < interval:
#             sleeptime = interval - loop_time
#             # print('sleep time: {:.1f}'.format(sleeptime))
#             time.sleep(sleeptime)

#     return


# def logTempO2(data_dir='./log_data/', interval=30, stop=0,
#               n=5, wait=.5, ID=None, sensor_json=None,
#               mode='water', new_folder_every=None, verbose=False, **kwargs):
#     """
#     Log O2 and Temp and save to files in data_dir.

#     Can be used alongside logger_CO2 to simultaneously collect all parameters

#     Parameters
#     ----------
#     data_dir : str
#         folder in which to store the data files.
#     interval : float
#         Time between measurements (seconds). Note that if this less than
#         the measurement time, measurements will be run continuously
#     stop : float
#         How long you want the loop to run for (seconds). If zero,
#         the loop will run until interrupted.
#     n : int
#         The number of O2 measurements to make per loop.
#     wait : float
#         Time between individual O2 measurements.
#     ID : str
#         A unique identifier of the sensor (e.g. serial number). If None
#         a sensor of the correct type is found automatically.
#     """
#     # record parameters
#     if not os.path.exists(data_dir):
#         os.mkdir(data_dir)

#     write_par(locals(), data_dir + '/logTempO2.json')

#     # initialize sensor
#     if ID is None:
#         o2 = O2_sensor()  # find sensor automatically
#     else:
#         o2 = O2_sensor(ID=ID)

#     print('Logging TempO2...')

#     # set up timing
#     start_time = os.times()[-1]
#     time_now = start_time
#     run = True

#     while run:
#         # create timed subdirectory, if required
#         if new_folder_every is not None:
#             save_dir = timed_dir(data_dir, new_folder_every)
#         else:
#             save_dir = data_dir
#         # do the logging
#         time_startloop = os.times()[-1]  # time at start of loop
#         elapsed = time_startloop - start_time  # total elapsed time at start of loop
#         # print('Elapsed Time: {:.1f}'.format(time_startloop - start_time))
#         # print('  O2-Temp Measurement')
#         o2.read_multi(n, wait)
#         o2.write_TempO2_batch(save_dir + '/temp.csv', save_dir + '/o2.csv', mode=mode)
#         if verbose:
#             print(o2.write_str[:-1])
#         o2.write(save_dir + '/TempO2_raw.csv')
#         # print('')

#         # timing mechanics
#         loop_time = os.times()[-1] - time_startloop
#         # print('loop time: {:.1f}'.format(loop_time))
#         if stop > 0:
#             # if the next interval's start time > stop time
#             if elapsed + loop_time + interval > stop:
#                 print('\nFinished.')
#                 break  # stop the loop
#         if loop_time < interval:
#             sleeptime = interval - loop_time
#             # print('sleep time: {:.1f}'.format(sleeptime))
#             time.sleep(sleeptime)

#     return


# def auto_log(mode='All', path=None, param_file=None):
#     """
#     Starts logging using parameters saved in .json file.

#     Either path OR param_file should be specified.

#     Parameters
#     ----------
#     mode : str
#         - 'All' calls logAll
#         - 'CO2' calls logCO2
#         - 'TempO2' calls logTempO2
#     path : str (optional)
#         If specified, parameters are imported from the most
#         recently modified .json file found in path.
#     param_file : str (optional)
#         The specific parameter file to use.

#     """
#     fndict = {'CO2': logCO2,
#               'TempO2': logTempO2}

#     if mode in fndict:
#         fn = fndict[mode]
#     else:
#         raise ValueError("{} is not a valid option.\n  > Please use 'All', 'CO2' or 'TempO2'.".format(mode))
#     if param_file is None and path is None:
#         raise ValueError('Please specify either param_file or path.')
#     elif param_file is not None:
#         if not os.path.exists(param_file):
#             warnings.warn("param_file '{}' not found. Looking for other .json files...")
#     else:
#         if path is not None:
#             param_file = most_recent_json(path)
#         else:
#             param_file = most_recent_json(os.getcwd())

#     print('Using parameters in {}'.format(param_file))

#     par = read_par(param_file)
#     fn(**par)


# if __name__ == '__main__':
#     # logAll('./test_log/', 35, 0)

#     pass
