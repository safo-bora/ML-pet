import time

from lib import ArduinoLCD


lcd = ArduinoLCD()
lcd. send_to_lcd('Hello!\nHow are you?')
time.sleep(2)
lcd.clear_lcd()
lcd. send_to_lcd('Buy!')
lcd.close_connection()
