from gpiozero import MCP3008
import time

soil_sensor = MCP3008(0)

while True:
	humidity = soil_sensor.value
	print(humidity)
	time.sleep(1)
