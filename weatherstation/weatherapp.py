from flask import Flask, render_template, request, send_file
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import uuid
import threading
import time
import random
import logging
import os
import json
import board
import busio
import smbus2
from adafruit_bme280 import basic as adafruit_bme280
import RPi.GPIO as GPIO
import math
import spidev
#led
def send_cmd(cmd):
        with open("led_cmd.txt", "w") as f:
                f.write(cmd)
send_cmd("green_on")
time.sleep(0.2)
send_cmd("green_off")
time.sleep(0.1)
app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

GPIO.setmode(GPIO.BCM)

send_cmd("yellow_on")
time.sleep(0.1)
send_cmd("yellow_off")
time.sleep(0.1)
#set values
temp = 0
hum = 0
press = 300
light = 0
rain = 0
pps = 0
light_status = ""
rain_status = ""
rainpercent = 0
wind = 0

send_cmd("yellow_on")
time.sleep(0.1)
send_cmd("yellow_off")
time.sleep(0.1)

#bme
i2c = busio.I2C(board.SCL, board.SDA)

bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
#bh1750
light_device = 0x23

ONE_TIME_HIGH_RES_MODE = 0x20

bus = smbus2.SMBus(1)

def read_light(addr=light_device):
	bus.write_byte(addr, ONE_TIME_HIGH_RES_MODE)
	time.sleep(0.2)
	data = bus.read_i2c_block_data(addr, 0x00, 2)
	result = (data[0] << 8) + data[1]
	lux = result / 1.2
	return lux

send_cmd("yellow_on")
time.sleep(0.1)
send_cmd("yellow_off")
time.sleep(0.1)

#hall sensor
SENSOR_PIN = 4
pulse_count = 0
shaft_diameter_m = 0.075
circumference_m = math.pi * shaft_diameter_m
min_pulse_interval = 0.01
last_pulse_time = 0
last_state = 1
GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#rain sensor
DIGITAL_PIN = 17
GPIO.setup(DIGITAL_PIN, GPIO.IN)
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

#rain
def read_adc(channel):
	if channel > 7 or channel > 0:
		return -1
	r = spi.xfer2([1, (8 + channel) << 4, 0])
	value = ((r[1] & 3) << 8) + r[2]
	return value

send_cmd("green_on")
time.sleep(0.2)
send_cmd("green_off")
time.sleep(0.1)

def updates():
	global pulse_count, shaft_diameter_m, circumference_m, min_pulse_interval, last_pulse_time, last_state, wind, rainpercent, temp, hum, press, light, rain, pps, rain_status, light_status
	try:
		while True:
			#values
			send_cmd("yellow_on")
			time.sleep(0.1)
			send_cmd("yellow_off")
			time.sleep(0.1)
			temp = round(bme280.temperature, 1)
			hum = round(bme280.humidity, 1)
			press = round(bme280.pressure, 1)
			light = round(read_light(), 1)
			rain = round(read_adc(0), -1)
			pulse_count = 0
			start_time = time.time()
			while time.time() - start_time < 30:
				current_state = GPIO.input(SENSOR_PIN)
				now = time.monotonic()
				if last_state == 1 and current_state == 0:
					if now - last_pulse_time > min_pulse_interval:
						pulse_count += 1
						last_pulse_time = now
				last_state = current_state
				time.sleep(0.001)
			pps = round(pulse_count / 30, 2)
			send_cmd("yellow_on")
			time.sleep(0.1)
			send_cmd("yellow_off")
			time.sleep(0.1)
			wind_mps = pps * circumference_m
			wind = round(wind_mps * 3.6, 2)
			rainpercent = round(100 - (rain / 1023 * 100), 1)
			#statuses
			if light <= 50:
				light_status = "Very Dark"
			elif light <= 800:
				light_status = "Dark"
			elif light <= 5000:
				light_status = "Cloudy"
			elif light <= 20000:
				light_status = "Bright"
			else:
				light_status = "Sunny"

			if rainpercent < 10:
				rain_status = "Dry"
			elif rainpercent < 25:
				rain_status = "Wet"
			elif rainpercent < 45:
				rain_status = "Light Rain"
			elif rainpercent < 75:
				rain_status = "Heavy Rain"
			else:
				rain_status = "Lashing"
			send_cmd("yellow_on")
			time.sleep(0.1)
			send_cmd("yellow_off")
			time.sleep(0.1)
			send_cmd("green_on")
			time.sleep(0.2)
			send_cmd("green_off")
			time.sleep(0.1)
			print(temp, "c", hum, "%hum", press, "hPa", light_status, rain_status, wind, "km/h", rain, "rain value", light, "light value", pulse_count)
			send_cmd("red_on")
			time.sleep(0.1)
			send_cmd("red_off")
			time.sleep(0.1)
			data = {
				"temp": temp,
				"hum": hum,
				"press": press,
				"light": light,
				"rain" : rain,
				"wind": wind
			}
			with open("/home/pi/Weather-Station/weatherlog/live_data.json", "w") as f:
				json.dump(data, f)
			time.sleep(2)
			send_cmd("green_on")
			time.sleep(0.2)
			send_cmd("green_off")
			time.sleep(0.1)
			send_cmd("blue_on")
			time.sleep(0.2)
			send_cmd("blue_off")
			time.sleep(0.1)
	except KeyboardInterrupt:
		bus.close()
		GPIO.cleanup()
		spi.close()

def generate_graph(year, month, day, datatype):
	df = pd.read_csv('/home/pi/Weather-Station/weatherlog/weather_log.csv')
	df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
	df.dropna(subset=['DateTime'], inplace=True)
	df.set_index('DateTime', inplace=True)

	send_cmd("yellow_on")
	time.sleep(0.1)
	send_cmd("yellow_off")
	time.sleep(0.1)

	df = df[df.index.year == int(year)]
	if month:
		df = df[df.index.month == int(month)]
	if day:
		df = df[df.index.day == int(day)]

	if df.empty or datatype not in df.columns:
		return None

	if not day and month:
		df = df.resample('D').mean(numeric_only=True)
	elif not month:
		df = df.resample('M').mean(numeric_only=True)

	send_cmd("yellow_on")
	time.sleep(0.1)
	send_cmd("yellow_off")
	time.sleep(0.1)
	print(df.columns)
	fig, ax = plt.subplots()
	ax.plot(df.index, df[datatype], linestyle='-', linewidth=1)
	title = f"{datatype.capitalize()} Over "
	if day:
		title += f"{day}/{month}/{year}"
	elif month:
		title += f"{month}/{year}"
	else:
		title += f"{year}"
	ax.set_title(title)
	ax.set_xlabel("Time")
	ax.set_ylabel(datatype.capitalize())
	fig.autofmt_xdate()


	graph_filename = "latest_graph.png"
	graph_path = os.path.join("/home/pi/Weather-Station/weatherstation/static", graph_filename)
	plt.savefig(graph_path)
	plt.close()
	send_cmd("green_on")
	time.sleep(0.2)
	send_cmd("green_off")
	time.sleep(0.1)
	send_cmd("blue_on")
	time.sleep(0.2)
	send_cmd("blue_off")
	time.sleep(0.1)
	return '/static/' + graph_filename




@app.route('/', methods=['GET', 'POST'])
def home():

	global temp, hum, press, rainpercent, wind, light_status, rain_status

	df = pd.read_csv('/home/pi/Weather-Station/weatherlog/weather_log.csv')
	df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
	df.dropna(subset=['DateTime'], inplace=True)

	years = sorted(df['DateTime'].dt.year.unique())
	months = sorted(df['DateTime'].dt.month.unique())
	days = sorted(df['DateTime'].dt.day.unique())

	graph_url = '/home/pi/Weather-Station/weatherstation/static/latest_graph.png'
	if request.method == 'POST':
		year = request.form.get('year')
		month = request.form.get('month') or None
		day = request.form.get('day') or None
		datatype = request.form.get('datatype')

		graph_url = generate_graph(year, month, day, datatype)

	send_cmd("green_on")
	time.sleep(0.2)
	send_cmd("green_off")
	time.sleep(0.1)

	return render_template('index.html', years=years, months=months, days=days, temp=temp, hum=hum, press=press, rainpercent=rainpercent, wind=wind, light_status=light_status, rain_status=rain_status, graph_url=graph_url)

if __name__ == '__main__':
	threading.Thread(target=updates, daemon=True).start()
	app.run(host='0.0.0.0', port=4000, ssl_context=('/etc/letsencrypt/live/weatherapp.ddns.net/fullchain.pem', '/etc/letsencrypt/live/weatherapp.ddns.net/privkey.pem'))
