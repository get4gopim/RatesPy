# MicroPython - Raspberry Pi Pico RP 2350

## Communication Protocols
I2C (Inter-Integrated Circuit) communication protocols used in embedded systems and IoT devices.
I2C uses two wires, SDA and SCL, for data transmission and synchronization.

### I2C
Use I2C when you want to control multiple peripherals with intermittent data transfers, or when speed isn't a major concern. I2C is also a good choice when you want to focus on simplicity and power consumption.
### SPI
Use SPI when you want to transfer a large amount of data at a high speed, or when you want to use a small number of peripherals. SPI is ideal for applications that require rapid data exchange.

## Required Libs
Use [thonny](https://thonny.org/) to install required libs from Tools - Manage Packages.

- logging
- ntptime
- ssd1306
- time
- threading (optional)
- functools (optional)

![plot](./docs/Screenshot%202024-12-23%20at%201.59.01%E2%80%AFPM.png)

## What is main.py
Starting program should be in the name of "main.py". There are 2 main programs:

- lcd_main.py (based on hardware 20x4 LCD display)
- main.py (based on hardware 0.96" 128x64 OLED display)

## Raspberry Pi Pico 2350 Pinout Diagram

- Use the GP0 and GP1 as SDA and SCL respectively 
- For power source use the below GPIO pins
  - Use the VBUS as a power spirce (5V) for 20x4 LCD display.
  - For OLED 0.96" display use the 3V3 (OUT) GPIO pin to power up the display.
- For ground use the GND (black colour) GPIO pin.

![plot](./docs/pico-2-r4-pinout.svg)


