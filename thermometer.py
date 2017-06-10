#!/usr/bin/env python

### CPUTemp class is from https://github.com/martinohanlon/CPUTemp.git 

from sense_hat import SenseHat
import math

class CPUTemp:
    def __init__(self, tempfilename = "/sys/class/thermal/thermal_zone0/temp"):
        self.tempfilename = tempfilename

    def __enter__(self):
        self.open()
        return self

    def open(self):
        self.tempfile = open(self.tempfilename, "r")
    
    def read(self):
        self.tempfile.seek(0)
        return self.tempfile.read().rstrip()

    def get_temperature(self):
        return self.get_temperature_in_c()

    def get_temperature_in_c(self):
        tempraw = self.read()
        return float(tempraw[:-3] + "." + tempraw[-3:])

    def get_temperature_in_f(self):
        return self.convert_c_to_f(self.get_temperature_in_c())
    
    def convert_c_to_f(self, c):
        return c * 9.0 / 5.0 + 32.0

    def __exit__(self, type, value, traceback):
        self.close()
            
    def close(self):
        self.tempfile.close()

#Initialize SenseHat
sense = SenseHat()

#Algorithm to adjust impact of the CPU temp on the temperature sensor readings
#Code snippet from https://github.com/astro-pi/watchdog

# CALCULATIONS FOR TEMPERATURE TO COMPENSATE FOR CPU_TEMP AFFECTING TEMPERATURE READINGS
  
t = sense.get_temperature()
p = sense.get_temperature_from_pressure()
h = sense.get_temperature_from_humidity()
with CPUTemp() as cpu_temp:
    c = cpu_temp.get_temperature()
print(p)
print(t)
print(h)
print(c/5)
temp = ((t+p+h)/3) - (c/5)
print(temp)
# CALCULATION FOR CORRECTING FOR THE CPU TEMPERATURE AFFECT ON TEMPERATURE SENSORS
# VERIFIED AGAINST A STANDALONE TEMPERATURE GAUGE FOR RASPBERRYPI B+ 

#Color code the display based on temperature range
if temp >= 40:
    X = [255, 0, 0]
elif temp >= 30:
    X = [255, 128, 0]
elif temp >= 20:
    X = [255, 255, 0]
elif temp >= 10:
    X = [0, 255, 0]
elif temp >= 0:
    X = [0, 255, 128]
elif temp >= -10:
    X = [0, 255, 255]
elif temp >= -20:
    X = [0, 191, 255]
elif temp >= -30:
    X = [0, 127, 255]
elif temp >= -40:
    X = [0, 64, 255]
else:
    X = [0, 0, 255]

O = [0, 0, 0] #Blue Background color

#Set LED Display to blank by filling array with 64 O characters
#Maybe change this to black color if foreground changes
ledDisplay = []
for i in range(64):
	ledDisplay.append(O)

#Convert numbers to pixel representations starting with 0

digitBits = (X,X,X,X,X,O,O,X,X,O,O,X,X,O,O,X,X,O,O,X,X,O,O,X,X,O,O,X,X,X,X,X,
O,O,X,O,O,O,X,O,O,O,X,O,O,O,X,O,O,O,X,O,O,O,X,O,O,O,X,O,O,O,X,O,
X,X,X,X,O,O,O,X,O,O,O,X,O,O,O,X,X,X,X,X,X,O,O,O,X,O,O,O,X,X,X,X,
X,X,X,X,O,O,O,X,O,O,O,X,O,O,O,X,X,X,X,X,O,O,O,X,O,O,O,X,X,X,X,X,
X,O,O,X,X,O,O,X,X,O,O,X,X,O,O,X,X,X,X,X,O,O,O,X,O,O,O,X,O,O,O,X,
X,X,X,X,X,O,O,O,X,O,O,O,X,O,O,O,X,X,X,X,O,O,O,X,O,O,O,X,X,X,X,X,
X,O,O,O,X,O,O,O,X,O,O,O,X,O,O,O,X,X,X,X,X,O,O,X,X,O,O,X,X,X,X,X,
X,X,X,X,O,O,O,X,O,O,O,X,O,O,O,X,O,O,O,X,O,O,O,X,O,O,O,X,O,O,O,X,
X,X,X,X,X,O,O,X,X,O,O,X,X,O,O,X,X,X,X,X,X,O,O,X,X,O,O,X,X,X,X,X,
X,X,X,X,X,O,O,X,X,O,O,X,X,O,O,X,X,X,X,X,O,O,O,X,O,O,O,X,O,O,O,X)

#Since the display is only big enough for two digits, an exception is made for anything over 99 though it almost certainly would never happen unless converted to Fahrenheit
#If the temp does hit +/- 100 then it will blank out the display given that it still works
if abs(temp) >= 100:
    ledDisplay = []
    for i in range(64):
	    ledDisplay.append(X)
else:
    #Start building the display array
    #Iterates each digit across the row and then down the column
    index = 0
    digitIndex = 0
    for rowLoop in range(8):
            for columnLoop in range(4):
                    #Number 1 starts at position 32. Zero is 0 - 31, so multiply by 32
                    ledDisplay[index] = digitBits[int(abs(temp)/10)*32 + digitIndex] #First digit
                    ledDisplay[index+4] = digitBits[int(abs(temp)%10)*32 + digitIndex] #Second digit
                    index = index + 1
                    digitIndex = digitIndex + 1
            index = index + 4 #Move to the next row

#Send the created array to the LED Display
#sense.set_pixels(ledDisplay)

sense.clear()
sense.rotation = 180
sense.low_light = True
if abs(temp) <= 31:
    #int part
    temp_in_bin = "{0:b}".format(int(temp))
    for index, val in enumerate(temp_in_bin):
        if val == "1":
            sense.set_pixel(index, 0, X)
    #get decimal part
    decimal = "{0:b}".format(int(math.modf(temp)[0]*10))
    if len(decimal) < 2:
        decimal = "00".join(decimal)
    elif len(decimal) < 3:
        decimal = "0".join(decimal)
    elif len(decimal) > 3:
        decimal = "111"
    print(temp, "--", decimal)
    for index, val in enumerate(decimal):
        if val == "1":
            sense.set_pixel(index+5, 0, 0, 0, 255)


