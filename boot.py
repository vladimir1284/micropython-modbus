#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Boot script

Do initial stuff here, similar to the setup() function on Arduino

Start WiFi Manager and connect to network, create an AccessPoint otherwise
"""

import esp
import gc
import machine
import network
import time

# custom modules
from helpers.generic_helper import GenericHelper
from helpers.led_helper import Led, Neopixel
from wifi_manager import WiFiManager


# set clock speed to 240MHz instead of default 160MHz
# import machine
# machine.freq(240000000)

# disable ESP os debug output
esp.osdebug(None)

led = Led()
pixel = Neopixel()
# turn Neopixel and onboard LED off
led.turn_off()
pixel.clear()

# flash onboard LED 3 times
led.flash(amount=3, delay_ms=50)

# turn onboard LED on
led.turn_on()

station = network.WLAN(network.STA_IF)
if station.active() and station.isconnected():
    station.disconnect()
    time.sleep(1)
station.active(False)
time.sleep(1)
station.active(True)

wm = WiFiManager()
result = wm.load_and_connect()

# force an accesspoint creation
# result = False

if result is False:
    # wm.start_config()

    # disconnect as/from station and disable WiFi for it
    station.disconnect()
    station.active(False)
    time.sleep(1)

    # create a true AccessPoint without any active Station mode
    wm.wh.create_ap(ssid='WiFiManager', password='', channel=11, timeout=5)
    print('Created Accesspoint "WiFiManager"')
else:
    print('Successfully connected to a network :)')

# turn Neopixel and onboard LED off
led.turn_off()
pixel.clear()

print('Restart cause: {}'.format(machine.reset_cause()))
print('RAM info: {}'.format(GenericHelper.free(full=True)))

# run garbage collector at the end to clean up
gc.collect()
