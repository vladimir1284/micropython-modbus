#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
device configuration file

Configure username and password of Webserver, Modbus RTU and TCP settings
"""


# Web server credentials
WEB_USER = 'admin'              # username for Webserver access
WEB_PASSWORD = 'admin'          # password for Webserver access


# Modbus RTU parameters
MB_RTU_ADDRESS = 0              # Set to 0 to disable
MB_RTU_BAUDRATE = 9600          # Baudrate of Modbus bus
MB_RTU_DATA_BITS = 8            # Data bits, default 8
MB_RTU_STOP_BITS = 1            # Stop bits, default 1
MB_RTU_PARITY = 1               # 1 = even, 2 = odd, 3 = none


# Modbus TCP parameters
MB_TCP_IP = 1                   # Set to 0 to disable
MB_TCP_PORT = 502               # Port for Modbus TCP requests
