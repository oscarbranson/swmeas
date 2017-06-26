# Python tools for controlling water monitoring sensors

## Example: CO2 Sensor
Works with [SensAir K30 CO2 Sensor](http://www.senseair.com/products/oem-modules/k30/).

```python
from swmeas import CO2_Sensor

co2 = CO2_Sensor(SN='your_serial_no')

# all reads are [timestamp, value] pairs

# read single CO2 measurement
co2.read()

# read 5 CO2 measurements, 3 seconds apart
co2.read_multi(n=5, wait=3.)

# write the last read value to individual [timestamp, value] rows of a file file
co2.write('data.csv')

# write all the previously read values to a single line in a file [timestamp, value_0, ..., value_n]
co2.write_batch('batch_data.csv')
```

## Example: O2 & Temperature Sensor
Works with a [Pyro Piccolo2 O2 / Temperature meter](http://www.pyro-science.com/piccolo2-optical-oxygen-meter.html)

```python
from swmeas import O2_Sensor

o2 = O2_Sensor(SN='your_serial_no')

# all reads are [timestamp, data_0, ..., data_13] lists

# read a single measurement
o2.read()

# read 5 measurements, 1.3 seconds apart
o2.read_multi(n=5, wait=1.3)

# write the last read values to csv file
o2.write('pyro_data.csv')

# write only the Temp and O2 measurements to batch files (i.e. each row is [timestamp, var_0, ..., var_n])
o2.write_TempO2_batch('temp.csv', 'o2.csv')
```

## Determining Device Serial Number

**Works on Mac/Linux.**

1. Start with the sensor unplugged, open a terminal window and run:

```bash
cd /dev
ls -l | grep usb
```
This should return nothing. 

2. Plug in the sensor, and run:

```bash
ls -l | grep usb 
```

This should return 2 entries, the end of which is the serial number of the sensor. It doesn't actually have to be the serial number - just a unique string which identifies the sensor in the list of tty entries in /dev.

It's possible that this won't work. If you don't see anything the second time, try removing ``| grep usb``. You'll be presented with a long list of files, and you'll need to identify the one that appears / disappears when you connect / disconnect the sensor.