#rpi serial connections
#Python app to run a Pyro sensor
import os, sys, re
import serial
import time
import numpy
import statistics
from datetime import date

ser = serial.Serial(
    port = "/dev/PyroO2",
    baudrate = 19200,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1
)

# oprn serial port
print (ser.isOpen())

# get device version
ver = "#VERS \r"
ser.write(ver)
resp_ver = ser.readline()
print(resp_ver)

# turn on power to O2 sensor
power_on = "#PWUP \r"       # turn on power
print "powering on sensor"
ser.write(power_on)
resp_power_on = ser.readline()

time.sleep(2) # smaall wait time for the system  

# loop for collect multiple data points
stop = 3*10                      # number of loops (time in seconds)
wait_time = 10                  # wait time (seconds).
total_time = stop * wait_time / 60
print(("total time", total_time, "minutes"))


for ii in range(stop):      # data collection loop
    # generate file name
    # save file name and path
    path = "/home/pi/Desktop/Pyro_O2/data/O2_log_file_"  # file path
    time1 = date.today()
    time_ext = time1.strftime("_%d_%b_%Y")
    file_name = path + time_ext
    print(file_name)

    # make O2 measurement
    MSR = "MSR 1 \r"            # make O2 measurement
    ser.write(MSR)
    resp_MSR = ser.readline()

    read_MSR = "RAL 1 \r"            # read O2 measurement
    ser.write(read_MSR)
    resp_read_MSR = ser.readline()
    print(resp_read_MSR)

    # extract O2 data from string array
    sub_1 = resp_read_MSR[5:] # remove the statrt string data
    sub_2 =sub_1[:-1]
    print(sub_2)

    current_time = time.asctime(time.localtime(time.time())) # get time
    print(current_time)
    time_1 = current_time

    # check if fill has a header, if not write a header
    if ii == 0:
        header = "loop status dphi umolar mbar airSat tempSample tempCase signalIntensity ambientLight pressure humidity resistorTemp percentO2, date-time\r"
        f = open(file_name, "a+")
        f.write(header)
        f.close()
    else:
         print "header file written"
         
    # write data to file each loop to file
    f = open(file_name, "a+")
    results = numpy.column_stack((ii, sub_2, time_1))
    print(results)
    numpy.savetxt(f, results, delimiter = " ", fmt = "%s")
    f.close()

    # wait between loops
    time.sleep(wait_time)

# off the O2 system
power_off = "#PDWN \r"       # turn on power
print(power_off)
ser.write(power_off)
resp_power_off = ser.readline()
print(resp_power_off)

# close the serial port
ser.close()
