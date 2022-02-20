#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
boot script, do initial stuff here, similar to the setup() function on Arduino
"""

import esp
import gc
import machine
import network
# import os
import time
# import uos

# custom modules
from helpers.generic_helper import GenericHelper
from helpers.led_helper import Led, Neopixel
# from helpers.wifi_helper import WifiHelper as wifi_helper
# from helpers.update_helper import UpdateHelper as update_helper
from wifi_manager import WiFiManager

"""
try:
    # import config_network
    from config import config_network
    create_ap = False
except Exception as e:
    print('No "config_network" file found, using AccessPoint, exception: {}'.
          format(e))
    create_ap = True
"""

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
if result is False:
    # wm.start_config()
    wm.wh.create_ap(ssid='WiFiManager', password='', channel=11, timeout=5)
    print('Created Accesspoint "WiFiManager"')
else:
    print('Successfully connected to a network :)')

"""
if create_ap:
    print('Creating AccessPoint ...')
    try:
        defined_accesspoint_ssid = config_network.AP_SSID
        defined_accesspoint_password = config_network.AP_PASSWORD
        defined_accesspoint_channel = config_network.AP_CHANNEL
        print('Using defined AccessPoint parameters')
    except Exception as e:
        defined_accesspoint_ssid = 'Setup-Micropython'
        defined_accesspoint_password = ''
        # defined_accesspoint_password = '123456789'
        defined_accesspoint_channel = 11
        print('Failed to load AccessPoint parameters, exception: {}'.format(e))
        print('Using default SSID "{}" and password "{}" for Accesspoint'.
              format(defined_accesspoint_ssid, defined_accesspoint_password))

    result = wifi_helper.create_ap(ssid=defined_accesspoint_ssid,
                                   password=defined_accesspoint_password,
                                   channel=defined_accesspoint_channel)
    print('Accesspoint created: {}'.format(result))
    # if result:
    #     # accesspoint successfully created
    #     pixel.green()
    # else:
    #     # failed to create an accesspoint
    #     pixel.blue()
else:
    try:
        defined_networks = config_network.networks
        defined_ssid = None
        defined_password = None
        print('Using dict of defined_networks')
    except Exception as e:
        defined_networks = None
        defined_ssid = config_network.ssid
        defined_password = config_network.password
        print('No networks dictionary defined, exception: {}'.format(e))
        print('Using SSID and password string or list of strings')

    result = wifi_helper.connect(ssid=defined_ssid,
                                 password=defined_password,
                                 networks=defined_networks)

    print('Connection to network established: {}'.format(result))

    if result:
        # connection successfully established
        pixel.green()
    else:
        # failed to connect to network
        pixel.blue()

        result = wifi_helper.create_ap(ssid='Backup-Accesspoint',
                                       password='123456789',
                                       channel=11)
"""

# turn Neopixel and onboard LED off
led.turn_off()
pixel.clear()

print('Restart cause: {}'.format(machine.reset_cause()))
print('RAM info: {}'.format(GenericHelper.free(full=True)))

# run garbage collector at the end to clean up
gc.collect()
