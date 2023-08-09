from paho.mqtt import client as mqtt_client
import RPi.GPIO as GPIO
import time
import random
import json

broker = 'localhost'
port = 1883
topic_control = "sic4demo/control/relay1"
topic_info = "sic4demo/info/relay1"
client_id = f'py-mqtt-{random.randint(0, 1000)}'
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_RELAY_1 = 18
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_RELAY_1, GPIO.OUT)

status = False

def relay_on():
    GPIO.output(GPIO_RELAY_1, True)
    print("Relay on")
    status = True
	
def relay_off():
    GPIO.output(GPIO_RELAY_1, False)
    print("Relay off")
    status = False

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

def publish(client, msg):
    client.publish(topic_info, msg)
    
def subscribe(client):
    client.subscribe(topic_control)

def on_message(client, userdata, message):
    topic = message.topic
    msg = json.loads(str(message.payload.decode("utf-8", "ignore")))
    
    if topic == topic_control:
        control = bool(msg["status"])
        status_info = False
        if control == True:
            relay_on()
            status_info = True
        else:
            relay_off()
            status_info = False
        status_send = json.dumps({"status": status_info})
        publish(client, status_send)
    
def run():
    relay_off()

    client = connect_mqtt()
    subscribe(client)
    client.on_message = on_message
    client.loop_forever()

if __name__ == '__main__':
    try:
        run()
         
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        relay_off()
        GPIO.cleanup()
