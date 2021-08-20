#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
boot script, do initial stuff here, similar to the setup() function on Arduino
"""

import esp
import gc

# custom modules
import led_helper
import wifi_helper

try:
    # import config_network
    from config import config_network
    create_ap = False
except Exception as e:
    print('No "config_network" file found, using AccessPoint, exception: {}'.
          format(e))
    create_ap = True

# set clock speed to 240MHz instead of default 160MHz
# import machine
# machine.freq(240000000)

# disable ESP os debug output
esp.osdebug(None)

# turn Neopixel and onboard LED off
led_helper.onboard_led_off()
led_helper.neopixel_clear()

# flash onboard LED 3 times
led_helper.flash_led(amount=3)

# turn onboard LED on
led_helper.onboard_led_on()

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
        print('No networks dictionary defined, exception: {}'.format(e))
        print('Using SSID and password string or list of strings')

    result = wifi_helper.connect(ssid=defined_ssid,
                                 password=defined_password,
                                 networks=defined_networks)

    if result:
        # connection successfully established
        led_helper.neopixel_green()
    else:
        # failed to connect to network
        led_helper.neopixel_blue()

# turn onboard LED off
led_helper.onboard_led_off()

# run garbage collector at the end to clean up
gc.collect()
