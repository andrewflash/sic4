import RPi.GPIO as GPIO
import time

# duty cycle, calibrate if needed
MIN_DUTY = 5
MAX_DUTY = 10

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#set GPIO Pins
servo_signal_pin = 3

#set GPIO direction (IN / OUT)
GPIO.setup(servo_signal_pin, GPIO.OUT)

# set pwm signal to 50Hz
servo = GPIO.PWM(servo_signal_pin, 50)
servo.start(0)

def deg_to_duty(deg):
    return (deg - 0) * (MAX_DUTY- MIN_DUTY) / 180 + MIN_DUTY
    
def run():
    duty_cycle = deg_to_duty(90)
    servo.ChangeDutyCycle(duty_cycle)
	# loop from 0 to 180
#	for deg in range(181):
#		duty_cycle = deg_to_duty(deg)
#		servo.ChangeDutyCycle(duty_cycle)

if __name__ == '__main__':
    try:
        while True:
            run()
            time.sleep(1)
        
    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        relay_off()
        GPIO.cleanup()
