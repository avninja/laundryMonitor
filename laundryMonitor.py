from sense_hat import SenseHat
import time, sys, os, numpy, subprocess
from random import randint
import sendtext
import pifi
from multiprocessing import Process, Queue
from evdev import InputDevice, list_devices, categorize, ecodes

def joystickSetup():
	devices = [InputDevice(fn) for fn in list_devices()]
	for dev in devices:
		if dev.name == "Raspberry Pi Sense HAT Joystick":
			dev = InputDevice(dev.fn)
			print "Listenting to " + dev.name
			break

	return dev

def getCurrentIp():
    getIPCommand = "ifconfig eth0 | grep inet | awk '{print $2}' | cut -d':' -f2"
    process = subprocess.Popen(getIPCommand, stdout=subprocess.PIPE, shell=True)
    ipAddr = process.communicate()[0]
    if (ipAddr == ""): # no wired; check wireless connection
        getIPCommand = "ifconfig wlan0 | grep inet | awk '{print $2}' | cut -d':' -f2"
    process = subprocess.Popen(getIPCommand, stdout=subprocess.PIPE, shell=True)
    ipAddr = process.communicate()[0]
    if (ipAddr == ""): # no connection at all, try to connect to WiFi?
        process = subprocess.Popen(getIPCommand, stdout=subprocess.PIPE, shell=True)
        ipAddr = process.communicate()[0]
        if (ipAddr == ""): # no connection at all?
            ipAddr = "unknown"
    return ipAddr.rstrip()

def stdGet(data_dict):
	std_dict = {}
	for key in data_dict:
		std_dict[key]=numpy.std(data_dict[key])

	return std_dict

def avgGet(data_dict):
	avg_dict = {}
	for key in data_dict:
		avg_dict[key]=numpy.mean(data_dict[key])

	return avg_dict

class laundryMonitor(object):
	def __init__(self, sensor):
		super(laundryMonitor, self).__init__()
		self.sense = sensor()
		self.sense.clear()
		self.std_dict = {}
		self.avg_dict = {}
		self.last_hit_time = time.time()
		self.lastAverageTime = time.time()
		self.vibration = 0
		self.attack_time = 20
		self.release_time = 600
		self.packets = 24
		self.multiplier = 4

		# initialize data stream
		self.stream = {}
		self.realtimeAvg = {}

		self.raw_data = self.sense.get_accelerometer_raw()
		for key in self.raw_data:
			self.stream[key] = []
			self.realtimeAvg[key] = []

	def getStatus(self):
		self.raw_data = self.sense.get_accelerometer_raw()
		for key in self.raw_data:
			self.stream[key].append(self.raw_data[key])

		if len(self.stream['x']) > self.packets:
			self.std_dict = stdGet(self.stream)
			self.avg_dict = avgGet(self.realtimeAvg)

			self.axis_hit_count = 0

			# sense motion and get axis hits; otherwise, append to the stream
			for key in self.stream:
				if self.std_dict[key] > self.avg_dict[key] * self.multiplier:
					self.axis_hit_count += 1
				elif not self.vibration:
					averageTime = time.time() - self.lastAverageTime
					if averageTime < 30:
						self.realtimeAvg[key].append(self.std_dict[key])
					else:
						self.realtimeAvg[key][1:]
						self.realtimeAvg[key].append(self.std_dict[key])

				self.stream[key] = []

			self.elapsed_time = time.time() - self.last_hit_time

			if self.axis_hit_count > 1 and self.elapsed_time > self.attack_time and not self.vibration == 1:
				self.vibration = 1
			elif self.axis_hit_count <= 1 and self.elapsed_time > self.release_time and not self.vibration == 0:
				self.vibration = 0
			elif self.axis_hit_count <= 1 and self.elapsed_time < self.release_time and self.vibration == 1:
				self.vibration = 2
				self.last_hit_time = time.time()
			elif self.axis_hit_count > 1 and self.vibration == 2:
				self.vibration = 1
			elif self.axis_hit_count > 1 and self.vibration:
				self.last_hit_time = time.time()
			elif self.axis_hit_count <= 1 and not self.vibration:
				self.last_hit_time = time.time()


if __name__ == "__main__":
	white = [128,128,128]
	red = [128,0,0]
	green = [0,128,0]
	blue = [0,0,128]
	washer_led_color = red
	led_update_time = 2
	
	sms_dict = {'Kirk': '6169147981', 'Derek': '6162592214', 'Annie': '6167067666', 'Brandan': '6169141238'}
	sms_names = ['Kirk', 'Derek', 'Annie', 'Brandan']
	sms_index = 0
	sms_len = len(sms_names)

	washer = laundryMonitor(SenseHat)
	washer_on = False
	sense = SenseHat()
	sense.set_rotation(180)
	sense.low_light = True
	sense.clear(blue)
	joystick = joystickSetup()
	start_time = time.time()

	wifiResult = pifi.connect('wlan0','SMURF_VILLAGE',psk='6655752404', quiet=False)
	if not wifiResult:
		sense.clear(red)
		time.sleep(1)
		sense.show_message('WiFi Failed To connect', scroll_speed=0.07, text_colour=red)
		sys.exit(0)
	else:
		sense.clear(green)
		time.sleep(1)
		sense.show_message(getCurrentIp(), scroll_speed=0.07, text_colour=green)

	sms_number = sms_dict[sms_names[sms_index]]
	print sms_number
	sense.show_message(sms_names[sms_index], scroll_speed=0.07, text_colour=white)

	try:
		while True:
			washer.getStatus()
			key_in = joystick.active_keys()
			if key_in:
				if sms_index + 1 == sms_len:
					sms_index = 0
				else:
					sms_index += 1
				sms_number = sms_dict[sms_names[sms_index]]
				print sms_number
				sense.show_message(sms_names[sms_index], scroll_speed=0.07, text_colour=white)
				key_in = None

			elapsed_time = time.time() - start_time
			if washer.vibration == 1 and not washer_on:
				print "washer started"
				led_update_time = 0.5
				sense.show_message('Wash Started', scroll_speed=0.07, text_colour=green)
				washer_on = True
			elif washer.vibration == 0 and washer_on:
				print "washer stopped"
				led_update_time = 2
				sense.show_message('Wash Stopped', scroll_speed=0.07, text_colour=red)
				print sms_number
				sendtext.sendText(sms_number, 'washer', 'washer stopped')
				washer_on = False

			if washer.vibration == 0 and not washer_on:
				washer_led_color = red
			elif washer.vibration == 1 and washer_on:
				washer_led_color = green
			elif washer.vibration == 2 and washer_on:
				washer_led_color = blue

			if elapsed_time > led_update_time:
				sense.clear()
				for i in range(48):
					sense.set_pixel(randint(0,7), randint(0,7), washer_led_color)
				start_time = time.time()
			time.sleep(0.01)
	except(KeyboardInterrupt):
		sense.clear()
		joystick.close()
		sys.exit(0)
