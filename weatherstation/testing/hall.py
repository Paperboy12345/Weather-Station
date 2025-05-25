import RPi.GPIO as GPIO
import time
import math

SENSOR_PIN = 4
pulse_count = 0

shaft_diameter_m = 0.075
circumference_m = math.pi * shaft_diameter_m

min_pulse_interval = 0.01
last_pulse_time = 0
last_state = 1

GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("reading")

try:
	while True:
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


		rotations_per_sec = pulse_count / 30
		wind_mps = rotations_per_sec * circumference_m
		wind_kph = wind_mps * 3.6

		print(f"Pulses: {pulse_count} | Wind speed: {wind_kph:.2f} km/h")

except KeyboardInterrupt:
	GPIO.cleanup()
	print("end")
