import time
import board
import busio
import smbus2
from adafruit_bme280 import basic as adafruit_bme280

i2c = busio.I2C(board.SCL, board.SDA)

bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

DEVICE_ADDRESS = 0x23

ONE_TIME_HIGH_RES_MODE = 0x20

bus = smbus2.SMBus(1)

def read_light(addr=DEVICE_ADDRESS):
	bus.write_byte(addr, ONE_TIME_HIGH_RES_MODE)
	time.sleep(0.2)
	data = bus.read_i2c_block_data(addr, 0x00, 2)
	result = (data[0] << 8) + data[1]
	lux = result / 1.2
	return lux

try:
	while True:
		temp = bme280.temperature
		press = bme280.pressure
		hum = bme280.humidity
		lux = read_light()

		print(f"Light: {lux:.2f} lux")
		print(f"Temp: {temp:.2f} C")
		print(f"Pressure: {press:.2f} hPa")
		print(f"Hum: {hum:.2f} %")

		time.sleep(2)
except KeyboardInterrupt:
	bus.close()
