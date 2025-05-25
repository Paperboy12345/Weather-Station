from datetime import datetime
import csv
import os
import json
import time

def send_cmd(cmd):
        with open("led_cmd.txt", "w") as f:
                f.write(cmd)

csv_path = "/home/pi/Weather-Station/weatherlog/weather_log.csv"
json_path = "/home/pi/Weather-Station/weatherlog/live_data.json"

try:
	with open(json_path, "r") as f:
		data = json.load(f)
		print("open start")
except FileNotFoundError:
	print("live data not found dummy")
	exit()

empty = os.path.getsize(csv_path) == 0

test = True
logged = False
send_cmd("blue_on")
time.sleep(0.3)
send_cmd("blue_off")
time.sleep(0.1)
try:
	while True:
		now = datetime.now()
		time.sleep(1)
		send_cmd("red_on")
		time.sleep(0.1)
		send_cmd("red_off")
		time.sleep(0.1)
		if now.hour in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23] and now.minute == 0 and not logged:
			try:
				with open(json_path, "r") as f:
					data = json.load(f)
					print("open again")
			except FileNotFoundError:
				print("live data not found dummy")
				exit()
			time.sleep(1)
			send_cmd("red_on")
			time.sleep(0.1)
			send_cmd("red_off")
			time.sleep(0.1)
			os.makedirs(os.path.dirname(csv_path), exist_ok=True)
			file_exists = os.path.isfile(csv_path)
			print("filing")
			with open(csv_path, "a", newline="") as f:
				writer = csv.writer(f)
				if empty:
					writer.writerow(["Date", "Time", "temp", "humidity", "pressure", "light", "rain", "wind"])
				if file_exists:
					print("writing...")
					send_cmd("blue_on")
					time.sleep(2)
					send_cmd("blue_off")
					time.sleep(0.1)
					writer.writerow([
					now.strftime("%Y-%m-%d"),
					now.strftime("%H:%M"),
					data["temp"],
					data["hum"],
					data["press"],
					data["light"],
					data["rain"],
					data["wind"],

				])
			logged = True
		elif now.minute != 0:
			logged = False
except KeyboardInterrupt:
	exit()
