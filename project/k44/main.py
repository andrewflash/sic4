from paho.mqtt import client as mqtt_client
import time
import random
import json
import pigpio
import RPi.GPIO as GPIO
 
# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
## Setting ultrasonik sensor
# Timeout berapa detik jika sensor tidak terbaca
SENS_ULT_TIMEOUT = 1

# Batas minimal sensor (cm)
D1_MIN = 5
D2_MIN = 5
D3_MIN = 5

# jsn-sr04t ultrasonik sensor - mendeteksi sampah di air, putar servo 180 derajat dan kembali
GPIO_TRIGGER_1 = 23
GPIO_ECHO_1 = 24
GPIO.setup(GPIO_TRIGGER_1, GPIO.OUT)
GPIO.setup(GPIO_ECHO_1, GPIO.IN)

# hc-sr04 mendeteksi sampah penuh - muncul di dashboard
GPIO_TRIGGER_2 = 18
GPIO_ECHO_2 = 25
GPIO.setup(GPIO_TRIGGER_2, GPIO.OUT)
GPIO.setup(GPIO_ECHO_2, GPIO.IN)

# hc-sr04 mendeteksi ketinggian air dan muncul di dashboard, akan ada notif jika tinggi air melebihi batas
GPIO_TRIGGER_3 = 4
GPIO_ECHO_3 = 12
GPIO.setup(GPIO_TRIGGER_3, GPIO.OUT)
GPIO.setup(GPIO_ECHO_3, GPIO.IN)
 
## MQTT Node Red
broker = 'localhost'
port = 1883
# Topic Servo
topic_servo_1 = "sic4/aktuator/s1"
# Topic Info
topic_sampah_terdeteksi = "sic4/info/sampah_terdeteksi"
topic_sampah_penuh = "sic4/info/sampah_penuh"
topic_air_tinggi = "sic4/info/air_tinggi"
# Topic Ultrasonic Distance Sensor
topic_sensor_distance_1 = "sic4/sensor/d1"
topic_sensor_distance_2 = "sic4/sensor/d2"
topic_sensor_distance_3 = "sic4/sensor/d3"
# Client ID - Random
client_id = f'py-mqtt-{random.randint(0, 1000)}'

## Servo 
# duty cycle, calibrate if needed
MIN_DUTY = 500
MAX_DUTY = 2500
# set GPIO Pins
servo_signal_pin_1 = 3
# Setup Servo
pwm_1 = pigpio.pi()
pwm_1.set_mode(servo_signal_pin_1, pigpio.OUTPUT)
pwm_1.set_PWM_frequency(servo_signal_pin_1, 50)
pwm_1.set_servo_pulsewidth(servo_signal_pin_1, MIN_DUTY)

## Fungsi Distance
def calc_distance(sensor_number):
    gpio_trigger = GPIO_TRIGGER_1
    gpio_echo = GPIO_ECHO_1
    if sensor_number == 1:
        gpio_trigger = GPIO_TRIGGER_1
        gpio_echo = GPIO_ECHO_1
    elif sensor_number == 2:
        gpio_trigger = GPIO_TRIGGER_2
        gpio_echo = GPIO_ECHO_2
    elif sensor_number == 3:
        gpio_trigger = GPIO_TRIGGER_3
        gpio_echo = GPIO_ECHO_3
    else:
        return -1

    # set Trigger to HIGH
    GPIO.output(gpio_trigger, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(gpio_trigger, False)
 
    StartTime = time.time()
    StopTime = time.time()
    TimeoutTime = time.time()
 
    # save StartTime
    while GPIO.input(gpio_echo) == 0:
        StartTime = time.time()
        if StartTime - TimeoutTime > SENS_ULT_TIMEOUT:
            return -1
 
    # save time of arrival
    TimeoutTime = time.time()
    while GPIO.input(gpio_echo) == 1:
        StopTime = time.time()
        if StopTime - TimeoutTime > SENS_ULT_TIMEOUT:
            return -1
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    d = (TimeElapsed * 34300) / 2
 
    return d

## Fungsi Servo
def deg_to_duty(deg):
    return (deg - 0) * (MAX_DUTY- MIN_DUTY) / 180 + MIN_DUTY
    
def servo_rotate(degree):
    duty_cycle = deg_to_duty(degree)
    pwm_1.set_servo_pulsewidth(servo_signal_pin_1, duty_cycle)

## Fungsi MQTT
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

def on_message(client, userdata, message):
    topic = message.topic
    msg = json.loads(str(message.payload.decode("utf-8", "ignore")))
    
    if topic == topic_servo_1:
        status_putar = bool(msg["deteksi_sampah"])
        if status_putar == True:
            servo_rotate(180)
            print("Servo putar 180 derajat")
            status_send = json.dumps({"status": "servo 1 putar 180 derajat"})
        else:
            servo_rotate(0)
            print("Servo putar 0 derajat")
            status_send = json.dumps({"status": "servo 1 putar 0 derajat"})
        publish(client, topic_info_servo, status_send)

## Fungsi logika
def check_event(d1, d2, d3):
    # Jika sampah terdeteksi di air, maka servo bergerak pindahkan sampah, lalu kembali ke posisi semula
    publish(client, topic_sensor_distance_1, json.dumps({"distance_1": d1}))
    if d1 < D1_MIN and d1 > -1:
        servo_rotate(180)
        publish(client, topic_sampah_terdeteksi, json.dumps({"sampah_terdeteksi": True}))
        print("Sampah terdeteksi")
        time.sleep(1)
    else:
        servo_rotate(0)
        publish(client, topic_sampah_terdeteksi, json.dumps({"sampah_terdeteksi": False}))
    
    # Jika bak sampah penuh, ada alert ke sistem
    publish(client, topic_sensor_distance_2, json.dumps({"distance_2": d2}))
    if d2 < D2_MIN and d2 > -1:
        publish(client, topic_sampah_penuh, json.dumps({"sampah_penuh": True}))
        print("Sampah penuh")
    else:
        publish(client, topic_sampah_penuh, json.dumps({"sampah_penuh": False}))

    # Ketinggian air, kirim setiap saat ke server, jika sudah tinggi, ada alert
    publish(client, topic_sensor_distance_3, json.dumps({"distance_3": d3}))
    if d3 < D3_MIN and d3 > -1:
        publish(client, topic_air_tinggi, json.dumps({"air_tinggi": True}))
        print("Tinggi air melebihi batas")
    else:
        publish(client, topic_air_tinggi, json.dumps({"air_tinggi": False}))

## Fungsi loop
def run():
    client.loop_start()
    # Test using random number
    # d1 = random.randint(2, 100)
    # d2 = random.randint(2, 100)
    # d3 = random.randint(2, 100)
    d1 = calc_distance(1)
    d2 = calc_distance(2)
    d3 = calc_distance(3)
    print("Distance 1: {} cm".format(d1)) 
    print("Distance 2: {} cm".format(d2)) 
    print("Distance 3: {} cm".format(d3)) 
    check_event(d1, d2, d3)
    client.loop_stop()

if __name__ == '__main__':
    try:
        client = connect_mqtt()
        subscribe(client)
        client.on_message = on_message
        servo_rotate(0)
        while True:
            run()
            time.sleep(1)
         
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()