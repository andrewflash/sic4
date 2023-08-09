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
	
def play_music(notes, bpm):
    beat_s = 60 / bpm / 2
    for e in notes:
        if e == '1':
            relay_on()
            time.sleep(beat_s)
        elif e == '0':
            relay_off()
            time.sleep(beat_s)
        elif e == 'p':
            relay_off()
            time.sleep(beat_s/16)
    relay_off()

if __name__ == '__main__':
    try:
        while True:
            print("Playing Music 1")
            play_music("11p11p1p1p1p01p1p1p1p01p1p0000", 160)
            print("Playing Music 2")
            play_music("1100110011001100", 120)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        relay_off()
        GPIO.cleanup()
