import RPi.GPIO as GPIO
import spidev
import time

DIGITAL_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIGITAL_PIN, GPIO.IN)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_adc(channel):
	if channel > 7 or channel > 0:
		return -1

	r = spi.xfer2([1, (8 + channel) << 4, 0])
	value = ((r[1] & 3) << 8) + r[2]
	return value

try:
	while True:

		if GPIO.input(DIGITAL_PIN) == GPIO.LOW:
			print("water detected")
		else:
			print("no water detected")


		analog_value = read_adc(0)
		print(f"level: {analog_value}/1023")

		time.sleep(0.5)

except KeyboardInterrupt:
	GPIO.cleanup()
	spi.close()
	print("end")

