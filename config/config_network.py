#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
network configuration file

Provide the SSID of the WiFi network you want to connect to either as string
or a list of strings. Do the same for the passwords.
Ensure not to mixup the SSID and passwords. The first network in the list will
use the first password in the password list.

The SSID and password(s) can also be given as a dictionary with the SSID as
the key and the password as the value.

The wifi_helper module will use the following order to try to connect to
networks:

1. Single network with SSID string and password string
2. Multiple networks with list of SSID strings and list of password strings
3. (Multiple) Networks as dictionary with SSID as key and password as value
"""


# SSID of the WiFi network to connect to or list of SSIDs
ssid = 'MyNet'  # single network
# ssid = ['MyNet', 'BackupSSID', 'Third WiFi']  # multiple networks

# WiFi password of the WiFi network or list of passwords
password = 'PasswordOfMyNet'    # single network
# password = ['PasswordOfMyNet', '1234asdf', 'securePw']    # multiple networks

# Provide a dict of SSID and password of the WiFi network to connect
# networks = {'MyNet': 'PasswordOfMyNet'}

# or create a dictionary of the SSID and passwords (zip works only with lists)
# networks = dict(zip(ssid, password))


# AccessPoint parameters
AP_SSID = 'Micropython-Modbus'  # AccessPoint WiFi name (SSID)
AP_PASSWORD = '123456789'       # AccessPoint WiFi password
AP_CHANNEL = 7                  # AccessPoint WiFi channel
