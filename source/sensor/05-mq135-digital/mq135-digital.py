import RPi.GPIO as GPIO
import time

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
# set GPIO Pins
GPIO_MQ135 = 14
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_MQ135, GPIO.IN)

def detect_gas():
	result = False
	result = not bool(GPIO.input(GPIO_MQ135))
	
	return result
	
if __name__ == '__main__':
    try:
        while True:
            print ("Apakah gas terdeteksi? {}".format(detect_gas()))
            time.sleep(1)
 
    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup() 
