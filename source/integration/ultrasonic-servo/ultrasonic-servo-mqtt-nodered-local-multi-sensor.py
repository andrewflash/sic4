from paho.mqtt import client as mqtt_client
import time
import random
import json
import pigpio
import RPi.GPIO as GPIO
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER_1 = 23
GPIO_ECHO_1 = 24

GPIO_TRIGGER_2 = 18
GPIO_ECHO_2 = 25

GPIO_TRIGGER_3 = 4
GPIO_ECHO_3 = 12
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER_1, GPIO.OUT)
GPIO.setup(GPIO_ECHO_1, GPIO.IN)

GPIO.setup(GPIO_TRIGGER_2, GPIO.OUT)
GPIO.setup(GPIO_ECHO_2, GPIO.IN)

GPIO.setup(GPIO_TRIGGER_3, GPIO.OUT)
GPIO.setup(GPIO_ECHO_3, GPIO.IN)
 
broker = 'localhost'
port = 1883

# Topic Servo
topic_servo_1 = "sic4/aktuator/servo_1"
topic_servo_2 = "sic4/aktuator/servo_2"

# Topic Info
topic_info_servo = "sic4/info/servo"
topic_info_ulrasonic = "sic4/info/ultrasonic"

# Topic Ultrasonic Distance Sensor
topic_sensor_distance_1 = "sic4/sensor/ultrasonic_1"
topic_sensor_distance_2 = "sic4/sensor/ultrasonic_2"
topic_sensor_distance_3 = "sic4/sensor/ultrasonic_3"

# Client ID - Random
client_id = f'py-mqtt-{random.randint(0, 1000)}'
 
# duty cycle, calibrate if needed
MIN_DUTY = 500
MAX_DUTY = 2500

#set GPIO Pins
servo_signal_pin_1 = 3
servo_signal_pin_2 = 2

# Setup Servo
pwm_1 = pigpio.pi()
pwm_2 = pigpio.pi()
pwm_1.set_mode(servo_signal_pin_1, pigpio.OUTPUT)
pwm_2.set_mode(servo_signal_pin_2, pigpio.OUTPUT)
pwm_1.set_PWM_frequency(servo_signal_pin_1, 50)
pwm_2.set_PWM_frequency(servo_signal_pin_2, 50)
pwm_1.set_servo_pulsewidth(servo_signal_pin_1, MIN_DUTY)
pwm_2.set_servo_pulsewidth(servo_signal_pin_2, MIN_DUTY)

def distance_1():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER_1, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER_1, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO_1) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO_1) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance_1 = (TimeElapsed * 34300) / 2
 
    return distance_1

def distance_2():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER_2, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER_2, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO_2) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO_2) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance_2 = (TimeElapsed * 34300) / 2
 
    return distance_2

def distance_3():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER_3, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER_3, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO_3) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO_3) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance_3 = (TimeElapsed * 34300) / 2
 
    return distance_3
    
def deg_to_duty(deg):
    return (deg - 0) * (MAX_DUTY- MIN_DUTY) / 180 + MIN_DUTY
    
def servo_putar_1(derajat):
    duty_cycle = deg_to_duty(derajat)
    pwm_1.set_servo_pulsewidth(servo_signal_pin_1, duty_cycle)

def servo_putar_2(derajat):
    duty_cycle = deg_to_duty(derajat)
    pwm_2.set_servo_pulsewidth(servo_signal_pin_2, duty_cycle)
	
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, topic, msg):
    client.publish(topic, msg)
    
def subscribe(client):
    client.subscribe(topic_servo_1)
    client.subscribe(topic_servo_2)

def on_message(client, userdata, message):
    topic = message.topic
    msg = json.loads(str(message.payload.decode("utf-8", "ignore")))
    
    if topic == topic_servo_1:
        status_putar = bool(msg["deteksi_sampah"])
        if status_putar == True:
            servo_putar_1(180)
            print("Servo putar 180 derajat")
            status_send = json.dumps({"status": "servo 1 putar 180 derajat"})

        else:
            servo_putar_1(0)
            print("Servo putar 0 derajat")
            status_send = json.dumps({"status": "servo 1 putar 0 derajat"})
        publish(client, topic_info_servo, status_send)

    elif topic == topic_servo_2:
        status_putar = bool(msg["deteksi_sampah"])
        if status_putar == True:
            servo_putar_2(180)
            print("Servo putar 180 derajat")
            status_send = json.dumps({"status": "servo 2 putar 180 derajat"})

        else:
            servo_putar_2(0)
            print("Servo putar 0 derajat")
            status_send = json.dumps({"status": "servo 2 putar 0 derajat"})
        publish(client, topic_info_servo, status_send)
    
def run():
    client.loop_start()
#    publish(client, topic_sensor_distance_1, json.dumps({"distance_1": distance_1})
 #   publish(client, topic_sensor_distance_2, json.dumps({"distance_2": distance_2})
  #  publish(client, topic_sensor_distance_3, json.dumps({"distance_2": distance_3})
    # Test using random number
    publish(client, topic_sensor_distance_1, json.dumps({"distance": random.randint(2, 100)}))
    publish(client, topic_sensor_distance_2, json.dumps({"distance": random.randint(2, 100)}))
    publish(client, topic_sensor_distance_3, json.dumps({"distance": random.randint(2, 100)}))
    client.loop_stop()

if __name__ == '__main__':
    try:
        client = connect_mqtt()
        subscribe(client)
        client.on_message = on_message
        while True:
            run()
            time.sleep(1)
         
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
