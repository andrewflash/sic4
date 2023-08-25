import RPi.GPIO as GPIO
import time
import requests

# Gas Detector Pin Setup
GPIO_MQ135 = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_MQ135, GPIO.IN)

# Buzzer
GPIO_BUZZER = 15
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_BUZZER, GPIO.OUT)

# Ubidots
TOKEN = "BBFF-x836iAfLt0skRMskQM7SsY1srsSZpd"  # Put your TOKEN here
DEVICE_LABEL = "raspi-sic4-mq135"  # Put your device label here 
VARIABLE_LABEL_1 = "gas_detector"  # Put your first variable label here
VARIABLE_CONTROL_1 = "buzzer"

# Gas Detector
def detect_gas():
	result = False
	result = not bool(GPIO.input(GPIO_MQ135))
	
	return result

# Buzzer
def buzzer_on():
    GPIO.output(GPIO_BUZZER, True)

def buzzer_off():
    GPIO.output(GPIO_BUZZER, False)    
    
# Ubidots
def build_payload(variable_1):
    value_1 = int(detect_gas())
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
   
def main():
    # Sending data humidity and temperature
    payload = build_payload(VARIABLE_LABEL_1)
    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished")

    # Reading status temperature
    status_buzzer = get_var(DEVICE_LABEL, VARIABLE_CONTROL_1)
    if bool(status_buzzer) == True:
        buzzer_on()
        print("[INFO] Buzzer ON")
    else:
        buzzer_off()
        print("[INFO] Buzzer OFF")
        
if __name__ == '__main__':
    try:
        while True:
            main()
            time.sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
