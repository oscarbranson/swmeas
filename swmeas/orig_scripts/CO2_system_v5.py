#rpi serial connections
#Python app to run a K-30 Sensor
import serial
import time
import numpy
import statistics
from datetime import date

# important to check port if multiple devices plugged in.

ser = serial.Serial("/dev/CO2meter", baudrate = 9600, timeout = .5)
print ("K-30 CO2 meter\n")

# open port
ser.flushInput()
time.sleep(1)

# setup arrays
CO2_array = []
time_array = []
loop_array = []

# loop
stop = 24*60                      # number of loops (time in seconds)
wait_time = 60                  # wait time (seconds).
total_time = stop * wait_time / 60
print(("total time", total_time, "minutes"))

for ii in range(stop):
    CO2_array_1 = []
    # generate file name
    # save file name and path
    path = "/home/pi/Desktop/CO2_meter/data/CO2_log_file_"  # file path
    time1 = date.today()
    time_ext = time1.strftime("_%d_%b_%Y")
    file_name = path + time_ext
    print(file_name)
    if ii == 0:
        header = "loop CO2(ppm) date-time\r"
        f = open(file_name, "a+")
        f.write(header)
        f.close()
    else:
         print "header file written"           

    # collect data and average 5 measurementsf
    for i in range(0, 5):

        ser.flushInput()
        ser.write("\xFE\x44\x00\x08\x02\x9F\x25")
        time.sleep(2)  # wait time for each meaurement
        resp = ser.read(7)
        high = ord(resp[3])
        low = ord(resp[4])
        co2 = (high * 256) + low
        print(("i = ", i, " CO2 = " + str(co2)))
        time.sleep(.1)

        current_time = time.asctime(time.localtime(time.time()))
        print(current_time)
        CO2_array_1.append(co2)

    # Calculate the average for the innner loops
    average_CO2_1 = numpy.average(CO2_array_1)
    stdev_CO2_1 = numpy.std(CO2_array_1)
    print(("loop_average CO2", average_CO2_1, "loop_stdev", stdev_CO2_1))
    time_1 = current_time

    # write data to file each loop to file
    f = open(file_name, "a+")
    results = numpy.column_stack((ii, average_CO2_1, time_1))
    print(results)
    numpy.savetxt(f, results, delimiter = " ", fmt = "%s")
    f.close()

    # wait between loops
    time.sleep(wait_time)

# close the serial port
ser.close()








