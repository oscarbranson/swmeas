from swmeas.utils import check_usb_mounted
from swmeas.sensors import CO2_sensor as Sensor
from swmeas.logger import log

# ------------------------------------------
# Configuration
# ------------------------------------------
period = 20  # time between measurements, in seconds
n_meas = 5  # repeat measurements per period
n_wait = 1.5  # wait between repeat measurements

out_dir = '/home/pi/log_data/'  # folder to save the data to
log_file = 'log_CO2.csv'  # log file name

# shouldn't need to modify this
usb_dir = '/home/usb/log_data'  # removable folder to save the data

# ------------------------------------------
# Logging
# ------------------------------------------
log(Sensor=Sensor, log_file=log_file,
    period=period, n_meas=n_meas, n_wait=n_wait,
    out_dir=out_dir, usb_dir=usb_dir, usb_save=check_usb_mounted())
