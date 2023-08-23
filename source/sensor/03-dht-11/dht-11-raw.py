import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import requests

# DHT
sensor = Adafruit_DHT.DHT11
GPIO_DHT = 14

def main():
    # Sending data humidity and temperature
    humidity, temperature = Adafruit_DHT.read_retry(sensor, GPIO_DHT)
    print("Humidity: {}".format(humidity))
    print("Temperature: {}".format(temperature))

if __name__ == '__main__':
    try:
        while True:
            main()
            time.sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
