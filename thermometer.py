#!/usr/bin/env python

### CPUTemp class is from https://github.com/martinohanlon/CPUTemp.git 

from sense_hat import SenseHat
from time import sleep
import math

class CPUTemp:
	SENSEHAT_WIDTH = 8

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

	def calc_real_temp(self, sense):
		#Initialize SenseHat

		#Algorithm to adjust impact of the CPU temp on the temperature sensor readings
		#Code snippet from https://github.com/astro-pi/watchdog

		# CALCULATIoNS FoR TEMPERATURE To CoMPENSATE FoR CPU_TEMP AFFECTING TEMPERATURE READINGS
		t = sense.get_temperature()
		p = sense.get_temperature_from_pressure()
		h = sense.get_temperature_from_humidity()
		with CPUTemp() as cpu_temp:
			c = cpu_temp.get_temperature()
		print("temp from pressure -> ", p)
		print("temp from humidity -> ",h)
		temp = ((t+p+h)/3) - (c/5)
		print(temp)
		return temp

	# CALCULATIoN FoR CoRRECTING FoR THE CPU TEMPERATURE AFFECT oN TEMPERATURE SENSoRS
	# VERIFIED AGAINST A STANDALoNE TEMPERATURE GAUGE FoR RASPBERRYPI B+
	def color_gen(self, temp):
		# temp = self.calc_real_temp(sense)
		#Color code the display based on temperature range
		if temp >= 40:
			x = [255, 0, 0]
		elif temp >= 30:
			x = [255, 128, 0]
		elif temp >= 20:
			x = [255, 255, 0]
		elif temp >= 10:
			x = [0, 255, 0]
		elif temp >= 0:
			x = [0, 255, 128]
		elif temp >= -10:
			x = [0, 255, 255]
		elif temp >= -20:
			x = [0, 191, 255]
		elif temp >= -30:
			x = [0, 127, 255]
		elif temp >= -40:
			x = [0, 64, 255]
		else:
			x = [0, 0, 255]
		return x

	def display_temp(self, sense):
		# sense.clear()
		temp = self.calc_real_temp(sense)
		x = self.color_gen(temp)
		if abs(temp) <= 31:
			#int part
			temp_in_bin = "{0:b}".format(int(temp))
			for index, val in enumerate(temp_in_bin):
				if val == "1":
					sense.set_pixel(index, 0, x)
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
		else:
			error_color = (255, 255, 255)
			for i in range (0, self.SENSEHAT_WIDTH):
				sense.set_pixel(i, 0, error_color)

	def clear_temp_row(self, sense):
		for i in range (0, self.SENSEHAT_WIDTH):
			sense.set_pixel(i, 0, 0, 0, 0)

	def start_climate_station(self, interval=60, nightly=False, rotation=0):
		"""
		:param interval: refresh rate of checking temperature
		:param nightly: dim the light if value is true
		:param rotation: rotate the Sense Hat LED to fit proper direction
		:return: no return value. Start the climate station in daemon mode.
		"""
		sense = SenseHat()
		# sense.clear()
		sense.rotation = rotation
		sense.low_light = nightly
		while True:
			self.clear_temp_row(sense)
			self.display_temp(sense)
			sleep(interval)
