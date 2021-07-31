#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
main script, do your stuff here, similar to the loop() function on Arduino
"""

from machine import UART
import network
import os
import sys
import time
import uos

# libraries
from modbus import ModbusRTU
from modbus import ModbusTCP
from webserver import WebServer

# custom modules
import time_helper
import wifi_helper

try:
    import config
    config_WEB_USER = config.WEB_USER
    config_WEB_PASSWORD = config.WEB_PASSWORD
except Exception as e:
    config_WEB_USER = 'admin'
    config_WEB_PASSWORD = 'admin'

    print('Failed to load "config.py" due to {}'.format(e))
    print('Using default web user "{}" with password "{}"'.
          format(config_WEB_USER, config_WEB_PASSWORD))

_modbus = None
_web = None


def _print_ex(msg, e):
    print('== [Exception] ====================')
    print(msg)
    sys.print_exception(e)
    # print('---------------------')
    # micropython.mem_info()
    print('===================================')


def _modbus_rtu_process():
    global _modbus

    _modbus.process()


def _modbus_tcp_process():
    global _modbus
    global _web

    # always assuming device is connected
    _modbus.process()

    if _web.get_status():
        _web.process(0)
    else:
        print('(Re)starting WebServer ...')
        _web.start()
        print('WebServer (re)started')


def setup_webserver():
    global _web

    print('Performing Webserver setup ...')
    _web = WebServer(user=config_WEB_USER,
                     password=config_WEB_PASSWORD,
                     port=80,
                     maximum_connections=10)

    if _web.get_status() is False:
        print('Starting WebServer ...')
        _web.start()
        print('WebServer started')
    else:
        print('WebServer already running')

    print('Webserver setup done')


def setup_modbus_registers():
    global _modbus

    # set+get
    _modbus.add_coil(address=101, value=True)
    _modbus.add_coil(address=102, value=False)

    # get only
    _modbus.add_ist(address=101, value=True)
    _modbus.add_ist(address=102, value=False)

    # set+get
    _modbus.add_hreg(address=101, value=101)
    _modbus.add_hreg(address=102, value=102)

    # get only
    _modbus.add_ireg(address=101, value=101)
    _modbus.add_ireg(address=102, value=102)


def setup_modbus_rtu():
    global _modbus

    _modbus = ModbusRTU(
        addr=config.MB_RTU_ADDRESS,
        baudrate=config.MB_RTU_BAUDRATE,
        data_bits=config.MB_RTU_DATA_BITS,
        stop_bits=config.MB_RTU_STOP_BITS,
        parity=None,
        pins=(1, 3),
        # ctrl_pin=MODBUS_PIN_TX_EN
    )
    print('Modbus RTU Master started - addr:', config.MB_RTU_ADDRESS)


def setup_modbus_tcp() -> bool:
    global _modbus
    network_connection = False
    is_bound = False
    result = False

    # check for network connection, either as Client or AccessPoint
    station = network.WLAN(network.STA_IF)
    accesspoint = network.WLAN(network.AP_IF)

    if station.active():
        _net = station
        if _net.isconnected():
            network_connection = True
    elif accesspoint.active():
        _net = accesspoint
        network_connection = True

    if network_connection:
        _modbus = ModbusTCP()

        try:
            is_bound = _modbus.get_bound_status()
        except Exception as e:
            print('No get_bound_status function available')

        if is_bound is False:
            print('Modbus TCP is not yet bound to IP and Port ...')

            local_ip = _net.ifconfig()[0]
            print('Local IP of device: {}'.format(local_ip))

            print('Binding device to IP "{}" and Port "{}"'.
                  format(local_ip, config.MB_TCP_PORT))
            _modbus.bind(local_ip=local_ip,
                         local_port=config.MB_TCP_PORT)

            print('Modbus TCP Server binding done')
            result = True
    else:
        # @TODO resolve happy case, try to (re)connect here
        print('Device not connected to network')
        print('Stopping here, resolve happy case later')

    return result


def main():
    global _modbus
    global _web

    setup_webserver()

    if ((config.MB_RTU_ADDRESS > 0) or
       (config.MB_TCP_IP > 0)):
        if config.MB_RTU_ADDRESS > 0:
            print('MB_RTU_ADDRESS available')

            setup_modbus_rtu()
            setup_modbus_registers()
            _modbus_process = _modbus_rtu_process
        else:
            print('No MB_RTU_ADDRESS, using TCP')

            if setup_modbus_tcp():
                setup_modbus_registers()
                _modbus_process = _modbus_tcp_process
            else:
                return

    print('Entering while loop')
    while True:
        try:
            _modbus_process()
        except Exception as e:
            _print_ex(msg='_modbus_process() error', e=e)

    print('While loop left ...')


if __name__ == '__main__':
    main()
