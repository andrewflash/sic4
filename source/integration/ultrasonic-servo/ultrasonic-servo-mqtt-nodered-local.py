from paho.mqtt import client as mqtt_client
import time
import random
import json
import pigpio
import RPi.GPIO as GPIO
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
broker = 'localhost'
port = 1883
topic_servo = "sic4/aktuator/servo_pindahkan_sampah"
topic_info = "sic4/info/servo_hasil_perintah"
topic_sensor_distance = "sic4/sensor/deteksi_sampah"
client_id = f'py-mqtt-{random.randint(0, 1000)}'
 
# duty cycle, calibrate if needed
MIN_DUTY = 500
MAX_DUTY = 2500

#set GPIO Pins
servo_signal_pin = 3

pwm = pigpio.pi()
pwm.set_mode(servo_signal_pin, pigpio.OUTPUT)
pwm.set_PWM_frequency(servo_signal_pin, 50)
pwm.set_servo_pulsewidth(servo_signal_pin, MIN_DUTY)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
    
def deg_to_duty(deg):
    return (deg - 0) * (MAX_DUTY- MIN_DUTY) / 180 + MIN_DUTY
    
def servo_putar(derajat):
    duty_cycle = deg_to_duty(derajat)
    pwm.set_servo_pulsewidth(servo_signal_pin, duty_cycle)
	
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
    client.subscribe(topic_servo)

def on_message(client, userdata, message):
    topic = message.topic
    msg = json.loads(str(message.payload.decode("utf-8", "ignore")))
    
    if topic == topic_servo:
        status_putar = bool(msg["deteksi_sampah"])
        if status_putar == True:
            servo_putar(180)
            print("Servo putar 180 derajat")
            status_send = json.dumps({"status": "putar 180 derajat"})

        else:
            servo_putar(0)
            print("Servo putar 0 derajat")
            status_send = json.dumps({"status": "putar 0 derajat"})
        publish(client, topic_info, status_send)
    
def run():
    client.loop_start()
    publish(client, topic_sensor_distance, json.dumps({"distance": distance()}))
    # Test using random number
    #publish(client, topic_sensor_distance, json.dumps({"distance": random.randint(2, 100)}))
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
