import network

import time
import utime
from ntptime import settime
import schedule

import urequests
import asyncio
import json

import logging

from machine import I2C, Pin
from lcddriver import LCD_I2C

from model import RateInfo
from utility import util

logging.basicConfig(level=logging.INFO, format='%(levelname)-6s %(message)s')
log = logging.getLogger(__name__)

wifi = network.WLAN(network.STA_IF)
wifi.active(True) #active WIFI interface
wifi.connect("ssid", "*****")

settime()
rtc = machine.RTC()

# The I2C address of your LCD (Update if different)
I2C_ADDR = 0x27  # Use the address found using the I2C scanner
# Define the number of rows and columns on your LCD
LCD_ROWS = 4
LCD_COLS = 20
# Initialize I2C
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
# Initialize LCD
lcd = LCD_I2C(i2c, I2C_ADDR, LCD_ROWS, LCD_COLS)

day_of_week = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
month_of_year = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def display_str(text, line):
    lcd.set_cursor(0, line)
    lcd.print(text)


def parse_gold_info(response):
    x = json.loads(response.content)
    log.debug (x)
    info = RateInfo.RateInfo(x['gold22'], x['gold24'], x['silver'], x['date'], x['lastUpdated'], x['currentDateTime'])
    return info


async def get_gold_rates():
    global rate_info
    response = urequests.get("https://api.saganavis.xyz/v1/rates/goldRates")
    if (response.status_code == 200):
        rate_info = parse_gold_info(response)
        log.info (rate_info)
        display_str ("Gold22          " + rate_info.get_gold22(), 2)
        display_str ("Gold24          " + rate_info.get_gold24(), 3)
    response.close()


def schedule_gold_api():
    log.debug("schedule_gold_api")
    data = asyncio.run(get_gold_rates())
    #asyncio.run(print_gold_data(data))


def every_second():
    (year, month, mday, hour, minute, second, weekday, yearday) = utime.localtime()
    date_f = "{:2d}.{} {}  {:02d}:{:02d}:{:02d}"
    date_time = date_f.format(mday, month_of_year[month-1], day_of_week[weekday], hour, minute, second)
    display_str(date_time, 0)


def connect_network():
    while not wifi.isconnected() and wifi.status() >= 0:
        log.info ("Wifi configuring...")
        time.sleep(1)
    log.info ("network status: %s", wifi.status())


def get_time():
    #global dow
    # for time convert to second
    tampon1=utime.time() 
    # for gmt. For me gmt+5.5. 
    tampon2=tampon1+19800
    # for second to convert time
    (year, month, mday, hour, minute, second, weekday, yearday)=utime.localtime(tampon2)
    # first 0 = week of year
    # second 0 = milisecond
    rtc.datetime((year, month, mday, 0, hour, minute, second, 0))
    #dow = day_of_week[weekday]
    #log.info (dow)


def init_schedulers():
    # Update time every second
    schedule.every(1).seconds.do(every_second)
    
    #schedule.every(30).seconds.do(schedule_gold_api)

    # Update gold rate every 1 hour except sunday from 10 AM to 5 PM
    gold_times = ["00:00", "05:00", "06:00", "09:00", "10:00", "11:00", "16:00"]
    for x in gold_times:
        schedule.every().monday.at(x).do(schedule_gold_api)
        schedule.every().tuesday.at(x).do(schedule_gold_api)
        schedule.every().wednesday.at(x).do(schedule_gold_api)
        schedule.every().thursday.at(x).do(schedule_gold_api)
        schedule.every().friday.at(x).do(schedule_gold_api)
        schedule.every().saturday.at(x).do(schedule_gold_api)

if __name__ == '__main__':
    try:
        lcd.backlight_on()
        lcd.clear()
        log.info ("main started")
        log.info ("Hello, Raspberry Pi Pico 2W [RP2350]: network status [%s] ip %s", wifi.status(), wifi.ifconfig())
        connect_network()
        get_time()
        
        every_second()
        init_schedulers()
        schedule_gold_api()
        
        while True:
            schedule.run_pending()
            time.sleep(1)
        
        log.info ("main END")
    except OSError:
        lcd.clear()
        display_str ('OS Error', 0)
    except Exception as ex:
        log.error (f'Error: {repr(ex)}')
        lcd.clear()
        display_str (f'Error: {repr(ex)}', 0)

#wifi.disconnect();
