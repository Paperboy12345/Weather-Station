import RPi.GPIO as GPIO
import time

HALL_PIN = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
	while True:
		state = GPIO.input(HALL_PIN)
		if state == GPIO.LOW:
			print("detedec")
		else:
			print("nope")
		time.sleep(0.1)
except KeyboardInterrupt:
	GPIO.cleanup()
