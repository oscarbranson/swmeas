import serial
import time
import os
from .helpers import fmt, portscan


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

    def __init__(self, ID=None, port=None, name='', msg=b"\xFE\x44\x00\x08\x02\x9F\x25"):
        self.ID = ID
        self.msg = msg
        self.name = name
        self.port = port
        self.connect()
        return

    def connect(self):
        """
        Connects to CO2 Sensor identified by Serial Number.
        """
        if self.port is not None:
            pass
        elif self.ID is not None:
            # identify usb port using ID
            self.port = portscan(self.ID)
            if not isinstance(self.port, str):
                raise serial.SerialException("Can't find tty port containing ID: {}".format(self.ID))

        self.label = "CO2 sensor {} ({}) on port {}\n".format(self.name, self.ID, self.port)
        print("\n" + '*' * len(self.label) + '\n' +
              self.label +
              '*' * len(self.label) + '\n')

        self.sensor = serial.Serial(self.port, baudrate=9600, timeout=.5)
        return

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
        self.sensor.write(self.msg)
        # read measurement from sensor
        resp = self.sensor.read(7)
        high = ord(resp[3])
        low = ord(resp[4])
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
        for i in xrange(n):
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
                f.write('# CO2 Sensor ID: {}\n# Time,CO2 (ppm)\n'.format(self.ID))
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
                f.write('# CO2 Sensor ID: {}\n# Time,CO2 (ppm)\n'.format(self.ID))
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


if __name__ == '__main__':
    # serial number of CO2 meter
    ID = 'FTHBSQZ9'
    # establish connection
    sens = CO2_sensor(ID)
    # save 10 measurements
    for i in xrange(10):
        print('Measurement {}...'.format(i))
        sens.save_CO2('explot.csv')
        print('   Done.')
    print('Done')
