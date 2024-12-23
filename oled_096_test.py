import ssd1306big
import time

# The default wiring is SDA to GP8 and SCL to GP9 for Rasberry Pi Pico
# currently only 128x64 px display is supported. 

write = ssd1306big


while True:
 
    write.clear()
    write.flow('Sunday is holiday in India')
    #write.line2('Monday')
    #write.line3('Tuesday')
    #write.line4('Wednesday')

    time.sleep(5)