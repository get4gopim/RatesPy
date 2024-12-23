# Main LCD 20x4 I2C - Forecast API Python Script
import sys
import threading
import asyncio
import logging
import os
import schedule
import datetime
import time

from lcddriver import lcddriver

from service import Forecast
from utility import util

from queue import Queue

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcddriver.lcd()

lcd_disp_length = 20
service_start_time_in_secs = 10
DEFAULT_LOC_UUID = '4ef51d4289943c7792cbe77dee741bff9216f591eed796d7a5d598c38828957d'

jobqueue = Queue()


# get current system time
def get_time():
    return datetime.datetime.now()


# general solution with a tool function
def run_with_callback(co):
    def wrapper(callback):
        task = asyncio.get_event_loop().create_task(co)
        task.add_done_callback(lambda t: callback(t.result()))
        return callback
    return wrapper

def call_apis_async():
    start = time.time()

    gold_data = asyncio.run(Forecast.get_gold_price())
    asyncio.run(callback_gold(gold_data))

    fuel_data = asyncio.run(Forecast.get_fuel_price())
    asyncio.run(callback_fuel(fuel_data))

    LOGGER.info(f'Total Time Taken {time.time() - start}')
    print()


def call_weather_api(location):
    LOGGER.info("call_weather_api")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        f1 = asyncio.Future()

        f1.add_done_callback(callback_weather)

        tasks = [Forecast.get_weather(f1, location)]
        loop.run_until_complete(asyncio.wait(tasks))

        loop.close()
        print()
    except Exception as ex:
        LOGGER.error(f'call_weather_api : {repr(ex)}')


def call_gold_api():
    LOGGER.info("call_gold_api")

    data = asyncio.run(Forecast.get_gold_price())
    asyncio.run(callback_gold(data))

    print()


def call_fund_api():
    LOGGER.info("call_fund_api")

    data = asyncio.run(Forecast.get_fuel_price())
    asyncio.run(callback_fuel(data))

    print()


def call_fuel_api():
    LOGGER.info("call_fuel_api")

    data = asyncio.run(Forecast.get_fuel_price())
    asyncio.run(callback_fuel(data))

    print()


def callback_weather(future):
    global weather
    weather = future.result()
    # update_weather_temp()
    update_weather_preciption_line2()

#@run_with_callback(Forecast.get_gold_price())
async def callback_gold(data):
    global rate_info
    rate_info = data
    update_rate_line_3_4()


def callback_fund(future):
    global fund_info
    fund_info = future.result()
    update_fund_line_3_4()

#@run_with_callback(Forecast.get_fuel_price())
async def callback_fuel(data):
    global fuel_info
    fuel_info = data
    update_fuel_line_3_4()


# update display line strings
def update_weather_cond_line2():
    global line2

    if weather is not None:
        # Make string right justified of length 4 by padding 3 spaces to left
        condition = str(weather.get_condition())[0:lcd_disp_length]
        line2 = condition.ljust(lcd_disp_length, ' ')


# update display line strings
def update_weather_location_line2():
    global line2

    if weather is not None:
        location = weather.get_location()
        delimiter_idx = util.index_of(location, ',')
        if delimiter_idx > 0:
            location = location[0:delimiter_idx]

        # Make string 20 chars only and left justify with space if length is less.
        line2 = location[0:lcd_disp_length]
        # Make string right justified of length 4 by padding 3 spaces to left
        justl = lcd_disp_length - 4
        location = location[0:justl]
        location = location.ljust(justl, ' ')
        line2 = location + ' ' + str(weather.get_temp()) + 'c'
        # line2 = line2.ljust(lcd_disp_length, ' ')


# update humidity line strings
def update_weather_humidity_line2():
    global line2

    if weather.get_humidity() is not None:
        # Make string right justified of length 4 by padding 3 spaces to left
        justl = lcd_disp_length - 4
        humidity ='Humidity'
        humidity = humidity.ljust(justl, ' ')
        line2 = humidity + ' ' + str(weather.get_humidity())

        line2 = line2.ljust(lcd_disp_length, ' ')
    else:
        update_weather_cond_line2()


# update preciption line strings
def update_weather_preciption_line2():
    global line2

    preciption = str(weather.get_preciption())
    if len(preciption) > 0:
        idx = util.index_of(preciption, 'until')
        if idx > 0:
            preciption = preciption[0:idx]

        # Make string 20 chars only and left justify with space if length is less.
        line2 = preciption[0:lcd_disp_length]
        line2 = line2.ljust(lcd_disp_length, ' ')
    else:
        update_weather_location_line2()


# update display line rate strings
def update_rate_line_3_4():
    global line3
    global line4

    just = lcd_disp_length - 5
    prefix_p = 'Gold'
    prefix_d = 'Silver'

    line3 = prefix_p.ljust(just, ' ') + ' ' + str(rate_info.get_gold22())
    line4 = prefix_d.ljust(just, ' ') + str(rate_info.get_silver())


def update_fund_line_3_4():
    global line3
    global line4

    just = lcd_disp_length - 7
    prefix_p = fund_info.get_scheme()[0:just]
    prefix_d = fund_info.get_last_updated_time()[0:just]

    line3 = prefix_p.ljust(just, ' ') + ' ' + str(fund_info.get_nav())
    line4 = prefix_d.ljust(just, ' ') + str(fund_info.get_change_value())


# update display fuel price line
def update_fuel_line_3_4():
    global line5
    global line6

    pet_len = len(str(fuel_info.get_petrol()))
    die_len = len(str(fuel_info.get_diesel()))

    prefix_p = 'Petrol'
    prefix_d = 'Diesel'

    just = lcd_disp_length - pet_len
    line5 = prefix_p.ljust(just, ' ') + str(fuel_info.get_petrol())
    just = lcd_disp_length - die_len
    line6 = prefix_d.ljust(just, ' ') + str(fuel_info.get_diesel())


def update_time_line1(currentTime):
    global line1

    line1 = currentTime.strftime("%b %d %a  %H:%M:%S")


def print_line1():
    display.lcd_display_string(line1, 1)


def print_line2():
    if weather.get_error() is None:
        display.lcd_display_string(line2, 2)


# print line 3 and 4
def print_line3_and_4_rate():
    if rate_info.get_error() is None:
        display.lcd_display_string(line3, 3)
        display.lcd_display_string(line4, 4)


# print line 3 and 4
def print_line3_and_4_fund():
    if fund_info.get_error() is None:
        display.lcd_display_string(line3, 3)
        display.lcd_display_string(line4, 4)


# print line 3 and 4
def print_line3_and_4_fuel():
    if fuel_info.get_error() is None:
        display.lcd_display_string(line5, 3)
        display.lcd_display_string(line6, 4)


def every_second():
    global counter
    global rand_bool
    global _bool_20

    current_time = get_time()
    update_time_line1(current_time)
    print_line1()

    if counter == 0:
        #print_line2()
        print_line3_and_4_rate()
        counter = counter + 1
        return

    change_every_x_secs = 10
    if counter % change_every_x_secs == 0:
        if _bool_20:
            #update_weather_location_line2()
            update_rate_line_3_4()
            print_line3_and_4_rate()
            _bool_20 = False
        else:
            #update_weather_humidity_line2()
            update_fuel_line_3_4()
            print_line3_and_4_fuel()
            _bool_20 = True
        #print_line2()
        counter = counter + 1
        return

    counter = counter + 1

    # Refresh the data every 5 mins (300 seconds once)
    # if counter == 300:
    #     counter = 0


def worker_main():
    while 1:
        try:
            job_func, job_args = jobqueue.get()
            job_func(*job_args)
            jobqueue.task_done()
        except BaseException as ex:
            LOGGER.error(f'worker_main : {repr(ex)}')


def welcome_date_month():
    current_time = get_time()
    day = current_time.strftime("%d")
    month = current_time.strftime("%B")
    week_day = current_time.strftime("%A")

    if current_time.month == 9 and current_time.weekday() in [2, 3, 5]:
        month = current_time.strftime("%b")

    # Format: 29 August Sunday, 22 Sep Wednesday
    wel_date = str(day + ' ' + month + ' ' + week_day)
    return wel_date.center(lcd_disp_length, ' ')


def run_weather_thread(job_vars):
    job_func, job_args = job_vars
    job_thread = threading.Thread(target=job_func, args=job_args)
    job_thread.start()


# not used ??
def run_gold_thread(job_vars):
    job_func, job_args = job_vars
    job_thread = threading.Thread(target=job_func, args=job_args)
    job_thread.start()


def add_scheduler(location):
    # Update time every second
    schedule.every(1).seconds.do(jobqueue.put, (every_second, []))

    # test scheduler
    #schedule.every(10).seconds.do(jobqueue.put, (call_fuel_api, []))

    # Update weather every 15 mins once
    #schedule.every().hour.at(':00').do(run_weather_thread, (call_weather_api, [location]))
    #schedule.every().hour.at(':15').do(run_weather_thread, (call_weather_api, [location]))
    #schedule.every().hour.at(':30').do(run_weather_thread, (call_weather_api, [location]))
    #schedule.every().hour.at(':45').do(run_weather_thread, (call_weather_api, [location]))

    # Update gold rate every 1 hour except sunday from 10 AM to 5 PM
    gold_times = ["00:00", "05:00", "06:00", "09:00", "10:00", "11:00", "16:00"]
    for x in gold_times:
        schedule.every().monday.at(x).do(jobqueue.put, (call_gold_api, []))
        schedule.every().tuesday.at(x).do(jobqueue.put, (call_gold_api, []))
        schedule.every().wednesday.at(x).do(jobqueue.put, (call_gold_api, []))
        schedule.every().thursday.at(x).do(jobqueue.put, (call_gold_api, []))
        schedule.every().friday.at(x).do(jobqueue.put, (call_gold_api, []))
        schedule.every().saturday.at(x).do(jobqueue.put, (call_gold_api, []))

    # Update fuel rate from 6 to 8 AM except sunday
    fuel_times = ["06:00", "06:30", "07:00", "07:30", "08:00"]
    for x in fuel_times:
        schedule.every().monday.at(x).do(jobqueue.put, (call_fuel_api, []))
        schedule.every().tuesday.at(x).do(jobqueue.put, (call_fuel_api, []))
        schedule.every().wednesday.at(x).do(jobqueue.put, (call_fuel_api, []))
        schedule.every().thursday.at(x).do(jobqueue.put, (call_fuel_api, []))
        schedule.every().friday.at(x).do(jobqueue.put, (call_fuel_api, []))
        schedule.every().saturday.at(x).do(jobqueue.put, (call_fuel_api, []))


# main starts here
if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
    logging.getLogger('schedule').propagate = False

    LOGGER = logging.getLogger(__name__)

    LOGGER.info('Display 20x4 LCD Module Start')

    display.lcd_display_string("Welcome".center(lcd_disp_length, ' '), 1)
    display.lcd_display_string(welcome_date_month(), 2)
    display.lcd_display_string("Starting Now ...".center(lcd_disp_length, ' '), 4)

    location = DEFAULT_LOC_UUID
    if len(sys.argv) > 1:
        location = sys.argv[1]

    counter = 0
    rand_bool = True
    _bool_20 = True
    #time.sleep(service_start_time_in_secs)

    try:
        worker_thread = threading.Thread(target=worker_main)
        worker_thread.start()

        #_all = asyncio.gather(*asyncio.all_tasks(asyncio.get_event_loop()))
        #asyncio.get_event_loop().run_until_complete(_all)

        call_apis_async()

        #update_weather_location_line2()
        #update_rate_line_3_4()
        #update_fund_line_3_4()
        #update_fuel_line_3_4()

        add_scheduler(location)

        display.lcd_clear()
        while 1:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        LOGGER.info('Cleaning up !')
        display.lcd_clear()
