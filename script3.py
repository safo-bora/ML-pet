import time
from lib import ArduinoLEDController, ArduinoLCD


if __name__ == "__main__":
    led = ArduinoLEDController()
    lcd = ArduinoLCD()
    lcd.clear_lcd()

    for led_pin in range(1, 6):
        led.toggle_led(led_pin)
        lcd.send_to_lcd(str(led_pin))
        time.sleep(0.5)
        lcd.clear_lcd()
        led.turn_off(led_pin)

    led.turn_off_all_leds()
    led.close()

    lcd.send_to_lcd("Done!")
    lcd.close_connection()
