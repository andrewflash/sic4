import time
import requests
import pigpio

TOKEN = "BBFF-x836iAfLt0skRMskQM7SsY1srsSZpd"  # Put your TOKEN here
DEVICE_LABEL = "raspi-sic4-servo"  # Put your device label here 
VARIABLE_LABEL_1 = "position"  # Put your first variable label here

# duty cycle, calibrate if needed
MIN_DUTY = 500
MAX_DUTY = 2500
 
#set GPIO Pins
servo = 3

#set GPIO direction (IN / OUT)
pwm = pigpio.pi()
pwm.set_mode(servo, pigpio.OUTPUT)
pwm.set_PWM_frequency(servo, 50)

pwm.set_servo_pulsewidth(servo, MIN_DUTY)

position = 0

def deg_to_duty(deg):
    return (deg - 0) * (MAX_DUTY- MIN_DUTY) / 180 + MIN_DUTY

def rotate(deg):
    duty_cycle = deg_to_duty(deg)
    pwm.set_servo_pulsewidth(servo, duty_cycle)
        
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
    global position

    # Reading status relay
    pos_read = get_var(DEVICE_LABEL, VARIABLE_LABEL_1)
    if int(pos_read) != int(position):
        position = pos_read
        rotate(position)
        
        # Send status only when changes
        payload = build_payload(VARIABLE_LABEL_1, position)
        print("[INFO] Attemping to send data")
        post_request(payload)
        print("[INFO] finished")

if __name__ == '__main__':
    try:
        while True:
            main()
            time.sleep(1)

    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        pass
        
