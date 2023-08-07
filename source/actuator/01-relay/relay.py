import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_RELAY_1 = 18
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_RELAY_1, GPIO.OUT)

status = False

def relay_on():
	GPIO.output(GPIO_RELAY_1, True)
	status = True
	
def relay_off():
	GPIO.output(GPIO_RELAY_1, False)
	status = False

if __name__ == '__main__':
    try:
        while True:
            if status == False:
                relay_on()
                status = True
                print("Relay on")
            else:
                relay_off()
                status = False
                print("Relay off")
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
