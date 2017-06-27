import os
import time

from .O2_sensor import O2_sensor
from .CO2_sensor import CO2_sensor


def logAll(data_dir='./log_data/', interval=60, stop=0,
           O2_n=5, O2_wait=0.5, CO2_n=5, CO2_wait=1.,
           O2_ID='FT1HQ4GE', CO2_ID='FTHBSQZ9'):
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

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

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

        print('  O2-Temp Measurement')
        o2.read_multi(O2_n, O2_wait)
        o2.write_TempO2_batch(data_dir + '/temp.csv', data_dir + '/o2.csv')
        o2.write(data_dir + '/TempO2_raw.csv')

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
           CO2_n=5, CO2_wait=1., CO2_ID='FTHBSQZ9'):
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

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

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
              O2_n=5, O2_wait=.5, O2_ID='FT1HQ4GE'):
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

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

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
        o2.write(data_dir + '/TempO2_raw.csv')

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




if __name__ == '__main__':
    logger('./test_log/', 35, 0)
