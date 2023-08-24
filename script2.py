import time
from lib import ArduinoLEDController

if __name__ == "__main__":
    controller = ArduinoLEDController('/dev/cu.usbserial-11220')

    for i in range(1, 6):  # LED numbers start from 1
        controller.toggle_led(i)
        time.sleep(1)

    controller.turn_off_all_leds()
    controller.close()
