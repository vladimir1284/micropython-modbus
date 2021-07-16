#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
boot script, do initial stuff here, similar to the setup() function on Arduino
"""

import esp
import gc
from machine import Pin
import time
import wifi_helper

try:
    import config_network
    create_ap = False
except Exception as e:
    print('No "config_network" file found, creating AccessPoint')
    create_ap = True

# set clock speed to 240MHz instead of default 160MHz
# import machine
# machine.freq(240000000)

# disable ESP os debug output
esp.osdebug(None)

# set pin D4 as output (blue LED)
led_pin = Pin(4, Pin.OUT)

# flash LED 3 times
for x in range(1, 3 + 1):
    led_pin.value(1)
    time.sleep(0.05)
    led_pin.value(0)
    time.sleep(0.05)

# turn LED on
led_pin.value(1)

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
        print('Failed to load AccessPoint parameters')
        print('Using default SSID "{}" and password "{}" for Accesspoint'.
              format(defined_accesspoint_ssid, defined_accesspoint_password))

    wifi_helper.create_ap(ssid=defined_accesspoint_ssid,
                          password=defined_accesspoint_password,
                          channel=defined_accesspoint_channel)
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
        print('No networks dictionary defined')
        print('Using SSID and password string or list of strings')

    wifi_helper.connect(ssid=defined_ssid,
                        password=defined_password,
                        networks=defined_networks)

led_pin.value(0)

# run garbage collector at the end to clean up
gc.collect()
