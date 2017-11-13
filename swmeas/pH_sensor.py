import time
import u6

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