from gpiozero import MCP3008
import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import requests

# Soil Sensor
soil_sensor = MCP3008(0)
MAX_HUMIDITY = 0.33  # nilai sensor mentah ketika dicelup ke air
MIN_HUMIDITY = 1    # nilai sensor mentah ketika di udara

# Relay
# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
# set GPIO Pins
GPIO_RELAY_1 = 14
# set GPIO direction (IN / OUT)
GPIO.setup(GPIO_RELAY_1, GPIO.OUT)
status = False

# DHT-11
sensor = Adafruit_DHT.DHT11
GPIO_DHT = 14

# Ubidots
TOKEN = "BBFF-x836iAfLt0skRMskQM7SsY1srsSZpd"  # Put your TOKEN>DEVICE_LABEL = "raspi-sic4"  # Put your device label here
DEVICE_LABEL = "raspi-sic4-soil-dht-relay"  # Put your device label here 
VARIABLE_LABEL_1 = "humidity_soil"  # Put your first variable label >VARIABLE_CONTROL_1 = "relay"
VARIABLE_LABEL_2 = "humidity_air"
VARIABLE_LABEL_3 = "temperature_air"
VARIABLE_CONTROL_1 = "relay"

# Function
def relay_on():
        GPIO.output(GPIO_RELAY_1, True)
        status = True

def relay_off():
        GPIO.output(GPIO_RELAY_1, False)
        status = False

# Ubidots
def build_payload(variable_1, variable_2, variable_3, value_1, value_2, value_3):
    payload = {variable_1: value_1, variable_2: value_2, variable_3: value_3}

    return payload

def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    print(req.status_code, req.json())
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True

def get_var(device, variable):
    try:
        url = "http://industrial.api.ubidots.com/"
        url = url + \
            "api/v1.6/devices/{0}/{1}/".format(device, variable)
        headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
        req = requests.get(url=url, headers=headers)
        return req.json()['last_value']['value']
    except:
        pass

def map_value(in_v, in_min, in_max, out_min, out_max):
    v = (in_v - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if v < out_min:
        v = out_min
    elif v > out_max:
        v = out_max
    return v
    
def main():
    # Sending data humidity
    humidity_soil = map_value(soil_sensor.value, MIN_HUMIDITY, MAX_HUMIDITY, 0, 100)   
    humidity_air, temperature_air = Adafruit_DHT.read_retry(sensor, GPIO_DHT)
    payload = build_payload(VARIABLE_LABEL_1, VARIABLE_LABEL_2, VARIABLE_LABEL_3, humidity_soil, humidity_air, temperature_air)
    print(payload)
    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished")

    # Reading status relay
    status_relay = get_var(DEVICE_LABEL, VARIABLE_CONTROL_1)
    if bool(status_relay) == True:
        relay_on()
        print("[INFO] Relay ON")
    else:
        relay_off()
        print("[INFO] Relay OFF")

if __name__ == '__main__':
    try:
        while True:
            main()
            time.sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

