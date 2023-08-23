from gpiozero import MCP3008
import time

soil_sensor = MCP3008(0)

while True:
	gas = soil_sensor.value
	print(gas)
	time.sleep(1)
