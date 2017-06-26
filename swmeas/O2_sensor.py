import glob
import serial
import time
import numpy as np


class O2_sensor(object):
    """
    Connect to and take measurements from a Piccolo2 Pyro O2 / Temperature meter.

    Parameters
    ----------
    SN : str
        The serial number of the Sensor.
    """

    def __init__(self, SN='FT1HQ4GE'):
        self.SN = SN
        self.connect()

    def connect(self):
        """
        Connects to O2 Sensor identified by Serial Number.
        """
        # identify usb port using SN
        mpath = [g for g in glob.glob('/dev/tty*') if self.SN in g][0]

        if not isinstance(mpath, str):
            raise serial.SerialException("Can't find tty port containing SN: {}".format(self.SN))

        print("\n********************" + '*' * len(self.SN) + '\n' +
              "Pyro O2 meter (SN: {})".format(self.SN))

        # open serial
        self.sensor = serial.Serial(mpath,
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

        print("********************" + '*' * len(self.SN))
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
            0: status
            1: dphi (m)
            2: umolar (nmol / L, liquid only)
            3: mbar (ubar, liquid & gas)
            4: airSat (e-3 % air sat, liquid only)
            5: tempSample (e-3 C)
            6: tempCase (e-3 C)
            7: signalIntensity (uV)
            8: ambientLight (uV)
            9: pressure (not returned)
            10: humidity (not returned)
            11: resistorTemp (mOhm (uV))
            12: percentO2 (e-3 %O2)
        """
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

        return res

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
        numpy array of dimensions (n, 13), where the second index term corresponds to:
            0: status
            1: dphi (m)
            2: umolar (nmol / L, liquid only)
            3: mbar (ubar, liquid & gas)
            4: airSat (e-3 % air sat, liquid only)
            5: tempSample (e-3 C)
            6: tempCase (e-3 C)
            7: signalIntensity (uV)
            8: ambientLight (uV)
            9: pressure (not returned)
            10: humidity (not returned)
            11: resistorTemp (mOhm (uV))
            12: percentO2 (e-3 %O2)
        """
        out = []
        for i in xrange(n):
            out.append(self.read(P=P, S=S))
            time.sleep(wait)
        return np.array(out, dtype=float)

    def readTempO2(self, n=5, wait=1., P=1013000, S=35000):
        if n > 1:
            read = self.read_multi(n=n, wait=wait, P=P, S=S)
        else:
            read = np.array(self.read(P=P, S=S), ndmin=1, dtype=float)
        return read[:, 5] / 1000., read[:, 12] / 1000.

    def power_off(self):
        """
        Turn off the power to the meter (saves power).
        """
        print('Powering down O2 Meter ({})...'.format(self.SN))
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
        print('Powering up O2 Meter ({})...'.format(self.SN))
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
