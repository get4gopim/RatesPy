import ntptime
import network
import time

wifi = network.WLAN(network.STA_IF)
wifi.active(True) #active WIFI interface
wifi.connect("B3-204-4G", "gna732KS")
ntptime.host = "in.pool.ntp.org"

def connect_network():
    while not wifi.isconnected() and wifi.status() >= 0:
        print ("Wifi configuring...")
        time.sleep(1)
    print (f"network status: %s", wifi.status())
    
print (time.localtime())
connect_network()
ntptime.settime()
print (time.localtime())

days_of_week = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
day_of_week = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
month_of_year = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

(year, month, mday, hour, minute, second, weekday, yearday) = time.localtime()

dow = day_of_week[weekday]
date_f = "{:2d}.{} {} {:02d}:{:02d}:{:02d}"
date_time = date_f.format(mday, month_of_year[month-1], dow, hour, minute, second)
print (date_time)
