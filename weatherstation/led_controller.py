import RPi.GPIO as GPIO
import time
import os

leds = {
        "green": 26,
        "red": 19,
        "yellow": 13,
        "blue": 6
}

GPIO.setmode(GPIO.BCM)

for pin in leds.values():
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, GPIO.LOW)

cmd_map = {
	"green_on": (leds["green"], True),
	"green_off": (leds["green"], False),
	"yellow_on": (leds["yellow"], True),
	"yellow_off": (leds["yellow"], False),
	"blue_on": (leds["blue"], True),
	"blue_off": (leds["blue"], False),
	"red_on": (leds["red"], True),
	"red_off": (leds["red"], False),
}

print("LED Master running")
GPIO.output(6, GPIO.HIGH)
time.sleep(0.2)
GPIO.output(6, GPIO.LOW)

try:
	while True:
		for cmd_file in ["led_cmd.txt"]:
			if os.path.exists(cmd_file):
				with open(cmd_file, "r") as f:
					cmd = f.read().strip()
				os.remove(cmd_file)
				if cmd in cmd_map:
					pin, state = cmd_map[cmd]
					GPIO.output(pin, state)
		time.sleep(0.05)
except KeyboardInterrupt:
	GPIO.cleanup()
