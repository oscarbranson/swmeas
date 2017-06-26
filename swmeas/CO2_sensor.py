import serial
import time
import glob


class CO2_sensor(object):
    """
    Connect to and take measurements from a K-30 CO2 Sensor.

    Parameters
    ----------
    SN : str
        The serial number of the CO2 Sensor
    msg : byte str
        The message sent to the sensor to retrieve
        a measurement (should not need to be changed).
    """

    def __init__(self, SN='FTHBSQZ9', msg=b"\xFE\x44\x00\x08\x02\x9F\x25"):
        self.SN = SN
        self.msg = msg
        self.sensor = self.connect()

    def connect(self):
        """
        Connects to CO2 Sensor identified by Serial Number.
        """
        # identify usb port using SN
        mpath = [g for g in glob.glob('/dev/tty*') if self.SN in g][0]

        if not isinstance(mpath, str):
            raise serial.SerialException("Can't find tty port containing SN: {}".format(self.SN))

        print("********************" + '*' * len(self.SN) + '\n' +
              "K-30 CO2 meter (SN: {})\n".format(self.SN) +
              "********************" + '*' * len(self.SN) + '\n')

        return serial.Serial(mpath, baudrate=9600, timeout=.5)

    def read_CO2(self):
        """
        Read CO2 measurement from sensor.

        Returns
        -------
        float : ppm CO2
        """
        self.sensor.flushInput()
        self.sensor.write(self.msg)
        # read measurement from sensor
        resp = self.sensor.read(7)
        high = ord(resp[3])
        low = ord(resp[4])
        co2 = (high * 256.) + low
        return co2

    def read_multi_CO2(self, n, wait=2.):
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
        for i in xrange(n):
            out.append(self.read_CO2())
            time.sleep(wait)
        return out

    def save_CO2(self, file='CO2dat.csv', n=5, wait=2.):
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
        # time at start of measurement
        tnow = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())
        # measurement
        if n > 1:
            co2 = self.read_multi_CO2(n, wait=wait)
        else:
            co2 = [self.read_CO2()]

        with open(file, 'a+') as f:
            f.write(tnow + ',' + ','.join(['{:.1f}'.format(i) for i in co2]) + '\n')

        return

    def disconnect(self):
        """
        Close connection to sensor. Shouldn't be necessary.
        """
        self.sensor.close()


if __name__ == '__main__':
    # serial number of CO2 meter
    SN = 'FTHBSQZ9'
    # establish connection
    sens = CO2_sensor(SN)
    # save 10 measurements
    for i in xrange(10):
        print('Measurement {}...'.format(i))
        sens.save_CO2('explot.csv')
        print('   Done.')
    print('Done')