# MicroPython - Raspberry Pi Pico RP 2350
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

Use the GP0 and GP1 as SDA and SCL respectively and use the VBUS as a power spirce (5V) for 20x4 LCD display.
For OLED 0.96" display use the 3V3 (OUT) GPIO pin to power up the display.
For ground use the GND (black colour) GPIO pin.

![plot](./docs/pico-2-r4-pinout.svg)


