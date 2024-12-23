import network

import time
import utime
from ntptime import settime
import schedule

import urequests
import asyncio
import json

import logging

#from machine import I2C, Pin
#from lcddriver import LCD_I2C
from machine import Pin, SoftI2C
import ssd1306

from model import RateInfo
from utility import util

logging.basicConfig(level=logging.INFO, format='%(levelname)-6s %(message)s')
log = logging.getLogger(__name__)

wifi = network.WLAN(network.STA_IF)
wifi.active(True) #active WIFI interface
wifi.connect("B3-204-4G", "gna732KS")

settime()
rtc = machine.RTC()

#You can choose any other combination of I2C pins
i2c = SoftI2C(scl=Pin(1), sda=Pin(0))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

day_of_week = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
days_of_week = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
month_of_year = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def clear_line(oled, line_num, char_width=6):
    oled.fill_rect(0, line_num, oled.width, 8, 0)  # Clear the line with black pixels
    oled.show()


def display_str(text, line):
    line = line * 10
    clear_line(oled, line, 10)
    oled.text(text, 0, line)
    oled.show()

    
def display_clear():
    oled.fill(0)
    oled.show()


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
        display_str ("Gold22:  " + rate_info.get_gold22(), 3)
        display_str ("Gold24:  " + rate_info.get_gold24(), 4)
        display_str ("Silver:  " + str(rate_info.get_silver()), 5)
    response.close()


def schedule_gold_api():
    log.debug("schedule_gold_api")
    data = asyncio.run(get_gold_rates())
    #asyncio.run(print_gold_data(data))


def every_second():
    (year, month, mday, hour, minute, second, weekday, yearday) = utime.localtime()
    
    date_f = "   {:02d}:{:02d}:{:02d}"
    date_time = date_f.format(hour, minute, second)
    display_str(date_time, 0)
    
    
def every_day():
    (year, month, mday, hour, minute, second, weekday, yearday) = utime.localtime()
    
    date_f = "{:2d}.{} {}"
    date_time = date_f.format(mday, month_of_year[month-1], days_of_week[weekday])
    #date_time = date_f.format(mday, month_of_year[month-1], days_of_week[second % 6])
    display_str(date_time, 1)


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
    
    schedule.every().day.at("00:00").do(every_day)
    
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
        #lcd.backlight_on()
        display_clear()
        log.info ("main started")
        log.info ("Hello, Raspberry Pi Pico 2W [RP2350]: network status [%s] ip %s", wifi.status(), wifi.ifconfig())
        connect_network()
        get_time()
        
        every_second()
        every_day()
        init_schedulers()
        schedule_gold_api()
        
        while True:
            schedule.run_pending()
            time.sleep(1)
        
        log.info ("main END")
    except OSError:
        display_clear()
        display_str ('OS Error', 0)
    except Exception as ex:
        log.error (f'Error: {repr(ex)}')
        display_clear()
        display_str (f'Error: {repr(ex)}', 0)

#wifi.disconnect();