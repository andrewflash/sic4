from gpiozero import MCP3008
import time
import requests

soil_sensor = MCP3008(0)

TOKEN = "BBFF-x836iAfLt0skRMskQM7SsY1srsSZpd"  # Put your TOKEN here
DEVICE_LABEL = "raspi-sic4"  # Put your device label here 
VARIABLE_LABEL_1 = "humidity"  # Put your first variable label here

def build_payload(variable_1, value_1):
    payload = {variable_1: value_1}

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

def main():
    humidity = (1 - soil_sensor.value) * 100
    payload = build_payload(VARIABLE_LABEL_1, humidity)
    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished")

if __name__ == '__main__':
	while True:
		main()
		time.sleep(1)
