import os
import serial
import time
from .helpers import fmt, portscan


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
            pass
        elif self.ID is not None:
            # identify usb port using ID
            self.port = portscan(self.ID)

            if not isinstance(self.port, str):
                raise serial.SerialException("Can't find ifport with ID: {}".format(self.ID))
        else:
            raise ValueError('Either ID or port must be specified')

        self.label = "O2 sensor {} ({}) on port {}\n".format(self.name, self.ID, self.port)
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
        for i in xrange(n):
            out.append(self.read(P=P, S=S))
            time.sleep(wait)
        self.last_read = out
        return out

    def write_TempO2_batch(self, Tpath='Temp.csv', O2path='O2.csv', mode='water'):
        """
        Write last read batches of Temp and O2 to separate files in useful units.

        Parameters
        ----------
        mode : str
            'air' or 'water' - switches output between percentO2 and umol/L
        """
        if mode == 'water':
            o2ind = 3
            o2unit = 'umol/L'
        elif mode == 'air':
            o2ind = 13
            o2unit = '% O2'
        else:
            raise ValueError("mode must be either 'water' or 'air'")
        # create headers, if files don't exist
        if not os.path.exists(Tpath):
            with open(Tpath, 'a+') as f:
                f.write('# Temp-O2 Sensor ID: {}\n# Time,Temperature (C)\n'.format(self.ID))
        if not os.path.exists(O2path):
            with open(O2path, 'a+') as f:
                f.write('# Temp-O2 Sensor ID: {}\n# Time,O2 ({}, {})\n'.format(self.ID, mode, o2unit))
        # construct write strings
        if isinstance(self.last_read[0], list):
            Time = [r[0] for r in self.last_read]
            Temp = [r[6] / 1000. for r in self.last_read]
            O2 = [r[o2ind] / 1000. for r in self.last_read]
            Tstr = fmt([Time[0]] + Temp, 2, ',') + '\n'
            # Time[0] + ',' + ','.join(['{:.2f}'.format(t) for t in Temp]) + '\n'
            O2str = fmt([Time[0]] + O2, 2, ',') + '\n'
            # Time[0] + ',' + ','.join(['{:.2f}'.format(o) for o in O2]) + '\n'
        else:
            Time = [self.last_read[0] / 1000.]
            Temp = [self.last_read[6] / 1000.]
            O2 = [self.last_read[13] / 1000.]
            Tstr = fmt(Time + Temp, 2, ',') + '\n'
            # Time + ',' + ','.join(['{:.2f}'.format(t) for t in Temp]) + '\n'
            O2str = fmt(Time + O2, 2, ',') + '\n'
            # Time + ',' + ','.join(['{:.2f}'.format(o) for o in O2]) + '\n'

        # write and save data
        self.write_str = 'Temp: ' + Tstr + 'O2: ' + O2str
        with open(Tpath, 'a+') as tf:
            tf.write(Tstr)
        with open(O2path, 'a+') as of:
            of.write(O2str)
        return

    def write(self, path):
        """
        Write last read data to file.
        """
        # if file doesn't already exist, write column names in a header
        if not os.path.exists(path):
            with open(path, 'a+') as f:
                f.write('# time,status,dphi,umolar,mbar,airSat,tempSample,tempCase,signalIntensity,ambientLight,pressure,humidity,resistorTemp,percentO2\n')
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


if __name__ == '__main__':

    sens = O2_sensor()

    print(sens.read_multi_Sensor(3, wait=.1))

    sens.disconnect()
