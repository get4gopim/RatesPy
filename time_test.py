import network
import time
import utime
import machine
from ntptime import settime

settime()
rtc=machine.RTC()

def get_time():
    # for time convert to second
    tampon1=utime.time() 
    # for gmt. For me gmt+5.5. 
    tampon2=tampon1+19800
    # for second to convert time
    (year, month, mday, hour, minute, second, weekday, yearday)=utime.localtime(tampon2)
    # first 0 = week of year
    # second 0 = milisecond
    rtc.datetime((year, month, mday, 0, hour, minute, second, 0))

get_time()
print (rtc.datetime())
print (utime.localtime())