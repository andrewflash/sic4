import time
import sys
import RPi.GPIO as GPIO
from hx711 import HX711

# GPIO in BCM Mode
GPIO_DOUT = 5
GPIO_DSCK = 6
hx = HX711(GPIO_DOUT, GPIO_DSCK)
hx.set_reading_format("MSB", "MSB")

referenceUnit = 1

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)
hx.set_reference_unit(referenceUnit)

hx.reset()
hx.tare()

print("Tare done! Add weight now...")

if __name__ == '__main__':
    while True:
        try:
            # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
            # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
            # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
            
            # np_arr8_string = hx.get_np_arr8_string()
            # binary_string = hx.get_binary_string()
            # print binary_string + " " + np_arr8_string
            
            # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
            val = hx.get_weight(5)
            print(val)

            # To get weight from both channels (if you have load cells hooked up 
            # to both channel A and B), do something like this
            #val_A = hx.get_weight_A(5)
            #val_B = hx.get_weight_B(5)
            #print "A: %s  B: %s" % ( val_A, val_B )

            hx.power_down()
            hx.power_up()
            time.sleep(0.1)

        # Reset by pressing CTRL + C
        except KeyboardInterrupt:
            print("Measurement stopped by User")
            GPIO.cleanup() 
