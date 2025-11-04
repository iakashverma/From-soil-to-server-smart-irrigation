import RPi.GPIO as GPIO
from time import sleep
import board
import digitalio
import busio
from adafruit_character_lcd.character_lcd_i2c import Character_LCD_I2C
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn
import blynklib
 
BLYNK_AUTH_TOKEN = "T5gHnLDFMZC9rvsvE355_ZhiQUHpxaIP"
blynk = blynklib.Blynk(BLYNK_AUTH_TOKEN)
GPIO.setmode(GPIO.BCM)
RELAY_PIN1 = 4
RELAY_PIN2 = 5
GPIO.setup(RELAY_PIN1, GPIO.OUT)
GPIO.setup(RELAY_PIN2, GPIO.OUT)
GPIO.output(RELAY_PIN1, GPIO.HIGH)
GPIO.output(RELAY_PIN2, GPIO.HIGH)
 
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP3008(spi, cs)

soil_channel1 = AnalogIn(mcp, 0)
soil_channel2 = AnalogIn(mcp, 1)
water_channel = AnalogIn(mcp, 2)
i2c = busio.I2C(board.SCL, board.SDA)
lcd_columns = 16
lcd_rows = 2
lcd = Character_LCD_I2C(i2c, lcd_columns, lcd_rows)
 
min_moisture = 0
max_moisture = 65535
min_val = 0
max_val = 65535

 V0 = 0
V1 = 1
V2 = 2
V3 = 3
V4 = 4
def read_soil_moisture(channel):
    return (max_moisture - channel.value) * 100 / (max_moisture - min_moisture)
 
def read_water_level():
    value = water_channel.value
    water_level = (max_val - value) * 100 / (max_val - min_val)
    return int(100 - water_level)
 
@blynk.handle_event('write V2')
def relay_control1(pin, value):
    if int(value[0]) == 1:
        GPIO.output(RELAY_PIN1, GPIO.LOW)
        lcd.clear()
        lcd.message = 'Motor1: On'
    else:
        GPIO.output(RELAY_PIN1, GPIO.HIGH)
        lcd.clear()
        lcd.message = 'Motor1: Off'
@blynk.handle_event('write V4')
def relay_control2(pin, value):
    if int(value[0]) == 1:
        GPIO.output(RELAY_PIN2, GPIO.LOW)
        lcd.clear()
        lcd.message = 'Motor2: On'
    else:
        GPIO.output(RELAY_PIN2, GPIO.HIGH)
        lcd.clear()
        lcd.message = 'Motor2: Off'
 
def display_and_control():
    soil_moisture1 = int(read_soil_moisture(soil_channel1))
    soil_moisture2 = int(read_soil_moisture(soil_channel2))
    water_level = read_water_level()
 
    lcd.clear()
    lcd.message = f'SM1:{soil_moisture1}% SM2:{soil_moisture2}%\nWL:{water_level}%'
 blynk.virtual_write(V0, soil_moisture1)
    blynk.virtual_write(V3, soil_moisture2)
    blynk.virtual_write(V1, water_level)
 
    if soil_moisture1 < 45:
        GPIO.output(RELAY_PIN1, GPIO.LOW)
        lcd.clear()
        lcd.message = 'Motor1: On'
        blynk.virtual_write(V2, 1)
    else:
        GPIO.output(RELAY_PIN1, GPIO.HIGH)
        lcd.clear()
        lcd.message = 'Motor1: Off'
        blynk.virtual_write(V2, 0)

if soil_moisture2 < 45:
        GPIO.output(RELAY_PIN2, GPIO.LOW)
        lcd.clear()
        lcd.message = 'Motor2: On'
        blynk.virtual_write(V4, 1)
 else:
        GPIO.output(RELAY_PIN2, GPIO.HIGH)
        lcd.clear()
        lcd.message = 'Motor2: Off'
        blynk.virtual_write(V4, 0)
 
lcd.clear()
lcd.message = 'Starting...'
sleep(2)
lcd.clear()
lcd.message = 'Motor1: Off\nMotor2: Off'
 
try:
    while True:
        display_and_control()
        blynk.run()
        sleep(1)
except KeyboardInterrupt:
    print("Program interrupted")
finally:
    GPIO.cleanup()
    lcd.clear()
    print("Cleanup complete")
