import serial
import time


class ArduinoLEDController(object):
    def __init__(self, port="/dev/cu.usbserial-11220", baudrate=9600):
        self.ser = serial.Serial(port, baudrate)
        time.sleep(2)

    def toggle_led(self, led_num):
        if 1 <= led_num <= 5:
            self.ser.write(str(led_num).encode())
        else:
            print("Invalid LED number")

    def turn_off(self, led_num):
        pin = ["a", "b", "c", "d", "e"][led_num-1]
        self.ser.write(str(pin).encode())

    def turn_off_all_leds(self):
        self.ser.write('A'.encode())

    def close(self):
        self.ser.close()


class ArduinoLCD(object):
    def __init__(self, port='/dev/cu.usbserial-11240', baud_rate=9600, init_delay=2):
        self.ser = serial.Serial(port, baud_rate)
        # Wait for the Arduino to initialize
        time.sleep(init_delay)

    def send_to_lcd(self, message):
        for line in message.split('\n'):
            self.ser.write(line.encode())
            self.ser.write(b'\n')
            time.sleep(0.1)

    def clear_lcd(self):
        self.ser.write(b'\r')
        time.sleep(0.1)

    def close_connection(self):
        if self.ser.is_open:
            self.ser.close()
