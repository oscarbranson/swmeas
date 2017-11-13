import serial
import time
import random
import os
import u6
from builtins import bytes, range  # for python 2/3 compatability
from .helpers import fmt, portscan, find_sensor, get_sensor_name
from .utils import time_now

class dummy_sensor(object):
    """
    A fake sensor that returns data for testing the logging systems.
    """
    def __init__(self):
        self.ID = 'imfake'
        self.name = 'Dummy Sensor'
        self.port = 'aport'
        self.last_read = None
        return

    def read(self):
        """
        Read a single measurement from the sensor.

        Returns
        -------
        [time, float] : str, ppm CO2
        """
        # time at start of measurement
        tnow = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())

        # make up some data
        data = [random.gauss(4, .5), random.gauss(4, .5), random.gauss(4, .5)]
        self.last_read = [tnow] + data
        return self.last_read

    def write(self, path):
        if not os.path.exists(file):
            with open(file, 'a+') as f:
                f.write('# {}# Time,CO2 (ppm)\n'.format(self.label))
        # construct writing string
        if isinstance(self.last_read[0], list):
            out_str = ''
            for r in self.last_read:
                out_str += fmt(r, 1, ',') + '\n'
        else:
            out_str = fmt(self.last_read, 1, ',') + '\n'
        # save and write
        self.write_str = out_str
        with open(path, 'a+') as f:
            f.write(out_str)

    def read_multi(self, n, wait=2.):
        """
        Read multiple CO2 measurements from sensor.

        Parameters
        ----------
        n : int
            Number of measurements
        wait : float
            Seconds between measurements

        Returns
        -------
        List of ppm CO2 measurements.
        """
        out = []
        for i in range(n):
            # time at start of measurement
            out.append(self.read())
            time.sleep(wait)
        self.last_read = out
        return out


class CO2_sensor(object):
    """
    Connect to and take measurements from a K-30 CO2 Sensor.

    Parameters
    ----------
    ID : str
        The serial number of the CO2 Sensor
    msg : byte str
        The message sent to the sensor to retrieve
        a measurement (should not need to be changed).
    """

    def __init__(self, ID=None, port=None, name=''):
        self.ID = ID
        self.name = name
        self.port = port
        self.connect()
        return

    def connect(self):
        """
        Connects to CO2 Sensor identified by Serial Number.
        """
        if self.port is not None:
            p = portscan(self.port)
            if p is not None:
                self.port = p.device
                self.ID = p.serial_number
                self.name = get_sensor_name(self.ID)
            else:
                raise serial.SerialException("Can't find port: {}".format(self.port))
        elif self.ID is not None:
            p = portscan(self.ID)
            if p is not None:
                self.port = p.device
                self.ID = p.serial_number
                self.name = get_sensor_name(self.ID)
            else:
                raise serial.SerialException("Can't find port with ID: {}".format(self.ID))
        else:
            self.ID, self.name, self.port = find_sensor('CO2')

        self.label = "CO2 sensor {} ({}) on port {}\n".format(self.name, self.ID, self.port)
        print("\n" + '*' * len(self.label) + '\n' +
              self.label +
              '*' * len(self.label) + '\n')

        self.sensor = serial.Serial(self.port, baudrate=9600, timeout=.5)
        return

    # def read(self):
    #     """
    #     Read a single CO2 measurement from the sensor.

    #     Returns
    #     -------
    #     float : ppm CO2
    #     """
    #     # time at start of measurement
    #     tnow = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())

    #     self.sensor.flushInput()
    #     self.sensor.write(self.msg)
    #     # read measurement from sensor
    #     resp = self.sensor.read(7)
    #     high = ord(resp[3])
    #     low = ord(resp[4])
    #     co2 = (high * 256.) + low
    #     self.last_read = [tnow, co2]
    #     return [tnow, co2]

    def read(self):
        """
        Read a single CO2 measurement from the sensor.

        Returns
        -------
        float : ppm CO2
        """
        # time at start of measurement
        tnow = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())

        self.sensor.flushInput()
        msg = b"\xFE\x44\x00\x08\x02\x9F\x25"
        self.sensor.write(msg)
        # read measurement from sensor
        resp = bytes(self.sensor.read(7))
        high = resp[3]
        low = resp[4]
        co2 = (high * 256.) + low
        self.last_read = [tnow, co2]
        return [tnow, co2]

    def read_multi(self, n, wait=2.):
        """
        Read multiple CO2 measurements from sensor.

        Parameters
        ----------
        n : int
            Number of measurements
        wait : float
            Seconds between measurements

        Returns
        -------
        List of ppm CO2 measurements.
        """
        out = []
        for i in range(n):
            # time at start of measurement
            out.append(self.read())
            time.sleep(wait)
        self.last_read = out
        return out

    def write_batch(self, file='CO2.csv'):
        """
        Append CO2 measurements to csv file with timestamp.

        Adds a new lien to file containing: time,[CO2] * n

        Parameters
        ----------
        file : str
            Path to save file.
        n : int
            Number of measurements to make.
        wait : float
            Seconds between measurements

        Returns
        -------
        None
        """
        if not os.path.exists(file):
            with open(file, 'a+') as f:
                f.write('# {}# Time,CO2 (ppm)\n'.format(self.label))
        # construct write_str
        if isinstance(self.last_read[0], list):
            Time = [r[0] for r in self.last_read]
            CO2 = [r[1] for r in self.last_read]
            CO2str = fmt([Time[0]] + CO2, 1, ',') + '\n'
        else:
            Time = self.last_read[0]
            CO2 = self.last_read[1]
            CO2str = Time + ',' + fmt(CO2, 1) + '\n'
        # save and write out_str
        self.write_str = CO2str
        with open(file, 'a+') as f:
            f.write(CO2str)
        return

    def write(self, path):
        if not os.path.exists(file):
            with open(file, 'a+') as f:
                f.write('# {}# Time,CO2 (ppm)\n'.format(self.label))
        # construct writing string
        if isinstance(self.last_read[0], list):
            out_str = ''
            for r in self.last_read:
                out_str += fmt(r, 1, ',') + '\n'
        else:
            out_str = fmt(self.last_read, 1, ',') + '\n'
        # save and write
        self.write_str = out_str
        with open(path, 'a+') as f:
            f.write(out_str)

    def disconnect(self):
        """
        Close connection to sensor (shouldn't be necessary).
        """
        self.sensor.close()
        return


class O2_sensor(object):
    """
    Connect to and take measurements from a Piccolo2 Pyro O2 / Temperature meter.

    Parameters
    ----------
    ID : str
        The serial number of the Sensor.
    """

    def __init__(self, ID=None, port=None, name=''):
        self.ID = ID
        self.port = port
        self.name = name
        self.connect()

    def connect(self):
        """
        Connects to O2 Sensor identified by Serial Number.
        """
        if self.port is not None:
            p = portscan(self.port)
            if p is not None:
                self.port = p.device
                self.ID = p.serial_number
                self.name = get_sensor_name(self.ID)
            else:
                raise serial.SerialException("Can't find port: {}".format(self.port))
        elif self.ID is not None:
            p = portscan(self.ID)
            if p is not None:
                self.port = p.device
                self.ID = p.serial_number
                self.name = get_sensor_name(self.ID)
            else:
                raise serial.SerialException("Can't find port with ID: {}".format(self.ID))
        else:
            self.ID, self.name, self.port = find_sensor('TempO2')

        self.label = "TempO2 sensor {} ({}) on port {}\n".format(self.name, self.ID, self.port)
        print("\n" + '*' * len(self.label) + '\n' +
              self.label)

        # open serial
        self.sensor = serial.Serial(self.port,
                                    baudrate=19200,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    bytesize=serial.EIGHTBITS,
                                    timeout=1)

        # Get device version
        self.sensor.write("#VERS\r")
        self.VERSION = self.sensor.readline().rstrip()
        print('  Version: {}'.format(self.VERSION))

        # turn on power to CO2 Sensor
        self.power_on()

        print('*' * len(self.label) + '\n')
        return

    def read(self, P=1013000, S=35000):
        """
        Measure variables from sensor

        Parameters
        ----------
        P : int
            Pressure in ubar (for gas readings).
        S : int
            Salinity in mg/L (for liquid readings).

        Returns
        -------
        List of:
            0: Time at start of measurement
            1: status
            2: dphi (m)
            3: umolar (nmol / L, liquid only)
            4: mbar (ubar, liquid & gas)
            5: airSat (e-3 % air sat, liquid only)
            6: tempSample (e-3 C)
            7: tempCase (e-3 C)
            8: signalIntensity (uV)
            9: ambientLight (uV)
            10: pressure (not returned)
            11: humidity (not returned)
            12: resistorTemp (mOhm (uV))
            13: percentO2 (e-3 %O2)
        """
        # get time at start of measurement
        tnow = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())

        # measure Temp
        self.sensor.write('TMP 1\r')
        self.sensor.readline()

        # adjust environment parameters for O2 measurement
        envpar = 'ENV 1 -300000 {:.0f} {:.0f} \r'.format(P, S)
        self.sensor.write(envpar)
        # Notes:
        #   T: -300000 uses last temperature measurement
        #   P: Ambient pressure in ubar (1000000 = 1 bar)
        #   S: Salinity in mg/L (1000 = 1 g/L)
        self.sensor.readline()

        # measure O2
        self.sensor.write('MSR 1\r')
        self.sensor.readline()

        # read all results
        self.sensor.write('RAL 1\r')
        res = self.sensor.readline()

        # format data
        res = res.replace('RAL 1 ', '').rstrip()
        res = [int(r) for r in res.split(' ')]

        self.last_read = [tnow] + res
        return [tnow] + res

    def read_multi(self, n, wait=1., P=1013000, S=35000):
        """
        Read multiple measurements of all sensor variables from sensor.

        Parameters
        ----------
        n : int
            Number of measurements
        wait : float
            Seconds between measurements
        P : int
            Pressure in ubar (for gas readings).
        S : int
            Salinity in mg/L (for liquid readings).

        Returns
        -------
        An list of n items, each containing 14 variables:
            0: Time at start of measurement
            1: status
            2: dphi (m)
            3: umolar (nmol / L, liquid only)
            4: mbar (ubar, liquid & gas)
            5: airSat (e-3 % air sat, liquid only)
            6: tempSample (e-3 C)
            7: tempCase (e-3 C)
            8: signalIntensity (uV)
            9: ambientLight (uV)
            10: pressure (not returned)
            11: humidity (not returned)
            12: resistorTemp (mOhm (uV))
            13: percentO2 (e-3 %O2)
        """
        out = []
        for i in range(n):
            out.append(self.read(P=P, S=S))
            time.sleep(wait)
        self.last_read = out
        return out

    # def write_TempO2_batch(self, Tpath='Temp.csv', O2path='O2.csv', mode='water'):
    #     """
    #     Write last read batches of Temp and O2 to separate files in useful units.

    #     Parameters
    #     ----------
    #     mode : str
    #         'air' or 'water' - switches output between percentO2 and umol/L
    #     """
    #     if mode == 'water':
    #         o2ind = 3
    #         o2unit = 'umol/L'
    #     elif mode == 'air':
    #         o2ind = 13
    #         o2unit = '% O2'
    #     else:
    #         raise ValueError("mode must be either 'water' or 'air'")
    #     # create headers, if files don't exist
    #     if not os.path.exists(Tpath):
    #         with open(Tpath, 'a+') as f:
    #             f.write('# {}# Time,Temperature (C)\n'.format(self.label))
    #     if not os.path.exists(O2path):
    #         with open(O2path, 'a+') as f:
    #             f.write('# {}# Time,O2 ({}, {})\n'.format(self.label, mode, o2unit))
    #     # construct write strings
    #     if isinstance(self.last_read[0], list):
    #         Time = [r[0] for r in self.last_read]
    #         Temp = [r[6] / 1000. for r in self.last_read]
    #         O2 = [r[o2ind] / 1000. for r in self.last_read]
    #         Tstr = fmt([Time[0]] + Temp, 2, ',') + '\n'
    #         # Time[0] + ',' + ','.join(['{:.2f}'.format(t) for t in Temp]) + '\n'
    #         O2str = fmt([Time[0]] + O2, 2, ',') + '\n'
    #         # Time[0] + ',' + ','.join(['{:.2f}'.format(o) for o in O2]) + '\n'
    #     else:
    #         Time = [self.last_read[0] / 1000.]
    #         Temp = [self.last_read[6] / 1000.]
    #         O2 = [self.last_read[13] / 1000.]
    #         Tstr = fmt(Time + Temp, 2, ',') + '\n'
    #         # Time + ',' + ','.join(['{:.2f}'.format(t) for t in Temp]) + '\n'
    #         O2str = fmt(Time + O2, 2, ',') + '\n'
    #         # Time + ',' + ','.join(['{:.2f}'.format(o) for o in O2]) + '\n'

    #     # write and save data
    #     self.write_str = 'Temp: ' + Tstr + 'O2: ' + O2str
    #     with open(Tpath, 'a+') as tf:
    #         tf.write(Tstr)
    #     with open(O2path, 'a+') as of:
    #         of.write(O2str)
    #     return

    def write(self, path):
        """
        Write last read data to file.
        """
        # if file doesn't already exist, write column names in a header
        if not os.path.exists(path):
            with open(path, 'a+') as f:
                f.write('# {}# time,status,dphi,umolar,mbar,airSat,tempSample,tempCase,signalIntensity,ambientLight,pressure,humidity,resistorTemp,percentO2\n'.format(self.label))
        # generate out_str
        if isinstance(self.last_read[0], list):
            out_str = ''
            for r in self.last_read:
                out_str += fmt(r, 1, ',') + '\n'
        else:
            out_str = fmt(self.last_read, 1, ',') + '\n'
        # write and save data
        self.write_str = out_str
        with open(path, 'a+') as f:
            f.write(out_str)
        return

    def power_off(self):
        """
        Turn off the power to the meter (saves power).
        """
        print('Powering down O2 Meter ({})...'.format(self.ID))
        self.sensor.write("#PDWN\r")
        off_status = self.sensor.readline()

        if 'PDWN' in off_status:
            print('  Power Off.')
        elif 'ERR' in off_status:
            print('Power-off error: {}'.format(off_status.rstrip()))
        else:
            print('Something went wrong during power-off.\n  -> Sensor returned {}'.format(off_status))
        return

    def power_on(self, wait=0.2):
        """
        Tun on the power to the meter.
        """
        print('Powering up O2 Meter ({})...'.format(self.ID))
        self.sensor.write("#PWUP\r")
        on_status = self.sensor.readline()
        time.sleep(wait)

        if 'PWUP' in on_status:
            print('  Ready!')
        elif 'ERR' in on_status:
            print('Power-on error: {}'.format(on_status.rstrip()))
        else:
            print('Something went wrong during power-on.\n  -> Sensor returned {}'.format(on_status))
        return


class pH_sensor(object):
    """
    Connect to and take measurements from a Durafit pH probe via a LabJack U6-Pro

    For LabJack Communication Protocol, refer to LabJackPython [1] and the U6-Pro
    User Guide [2]

    [1] https://github.com/labjack/LabJackPython
    [2] https://labjack.com/sites/default/files/2014/06/U6_UG_Export_20140604.pdf

    Parameters
    ----------
    GainIndex : int
        The GainIndex used in recording measurements. See `u6.U6().getFeedback()`
        documentation.
    """
    def __init__(self, GainIndex=0):
        self.connect()
        self.config = self.sensor.configU6()
        self.gainindex = GainIndex
        self.last_read = None
        # define read commands
        self.comm = {'LJTemp': u6.AIN24(14),
                     'pH': u6.AIN24(2, ResolutionIndex=12, GainIndex=self.gainindex),
                     'Temp': u6.AIN24(0, ResolutionIndex=9, GainIndex=self.gainindex)}

    def connect(self):
        """
        Connect to U6 LabJack.
        """
        try:
            self.sensor = u6.U6()
        except TypeError:
            print("Can't find LabJack. Is it connected?")

    def disconnect(self):
        """
        Close the LabJack Connection.
        """
        self.sensor.close()

    def read(self):
        """
        Read Durafit pH and Temperature voltage, and LabJack Temperature.

        Returns
        -------
        [time, pH voltage, probe temperature voltage, LabJack temperature Kelvin]
        """
        # time at start of measurement
        tnow = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())

        # record bits from LabJack
        bLJ_temp, bpH_temp, bpH = self.sensor.getFeedback(self.comm['LJTemp'], self.comm['Temp'], self.comm['pH'])

        # convert to temperature / voltage
        LJ_temp = self.sensor.binaryToCalibratedAnalogTemperature(bLJ_temp)
        pH_temp = self.sensor.binaryToCalibratedAnalogVoltage(self.gainindex, bpH_temp)
        pH = self.sensor.binaryToCalibratedAnalogVoltage(self.gainindex, bpH)

        self.last_read = [tnow, pH, pH_temp, LJ_temp]

        return self.last_read

    def read_multi(self, n, wait=1.):
        """
        Read Durafit pH and Temperature voltage, and LabJack Temperature.

        Returns
        -------
        n * [time, pH voltage, probe temperature voltage, LabJack temperature Kelvin]
        """

        out = []
        for i in range(n):
            out.append(self.read())
            time.sleep(wait)
        self.last_read = out
        return out