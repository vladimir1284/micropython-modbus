#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
main script, do your stuff here, similar to the loop() function on Arduino
"""

from machine import UART
import json
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
import path_helper
import time_helper
import wifi_helper

try:
    from config import config
    config_WEB_USER = config.WEB_USER
    config_WEB_PASSWORD = config.WEB_PASSWORD
    config_TCP_PORT = config.MB_TCP_PORT
except Exception as e:
    config_WEB_USER = 'admin'
    config_WEB_PASSWORD = 'admin'
    config_TCP_PORT = 502

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


def load_register_files(file_path='registers/modbusRegisters.json') -> dict:
    modbus_registers = dict()

    # if os.path.exists(file_path):
    if path_helper.exists(path=file_path):
        with open(file_path) as json_file:
            modbus_registers = json.load(json_file)
            print('Loaded these registers: {}'.format(modbus_registers))
    else:
        print('No register file "{}" available'.format(file_path))

    return modbus_registers


def setup_modbus_registers(modbus_registers: dict = dict()):
    global _modbus

    if len(modbus_registers):
        if 'COILS' in modbus_registers:
            for register, val in modbus_registers['COILS'].items():
                print('Adding COIL at {}'.format(val['register']))
                _modbus.add_coil(address=val['register'],
                                 value=True)
        else:
            print('No COILS defined in modbus_registers')

        if 'HREGS' in modbus_registers:
            for register, val in modbus_registers['HREGS'].items():
                print('Adding HREG at {}'.format(val['register']))
                _modbus.add_hreg(address=val['register'],
                                 value=999)
        else:
            print('No HREGS defined in modbus_registers')

        if 'ISTS' in modbus_registers:
            for register, val in modbus_registers['ISTS'].items():
                print('Adding IST at {}'.format(val['register']))
                _modbus.add_ist(address=val['register'],
                                value=True)
        else:
            print('No ISTS defined in modbus_registers')

        if 'IREGS' in modbus_registers:
            for register, val in modbus_registers['IREGS'].items():
                print('Adding IREG at {}'.format(val['register']))
                _modbus.add_ireg(address=val['register'],
                                 value=999)
        else:
            print('No IREGS defined in modbus_registers')
    else:
        print('No registers defined, using default')

        # set+get
        _modbus.add_coil(address=101, value=True)
        _modbus.add_coil(address=102, value=False)

        # set+get
        _modbus.add_hreg(address=101, value=101)
        _modbus.add_hreg(address=102, value=102)

        # get only
        _modbus.add_ist(address=101, value=True)
        _modbus.add_ist(address=102, value=False)

        # get only
        _modbus.add_ireg(address=101, value=101)
        _modbus.add_ireg(address=102, value=102)


def setup_modbus_rtu(connection_setting: dict = dict(), pins: tuple = (1, 3)):
    global _modbus
    result = False

    if 'unit' in connection_setting and 'baudrate' in connection_setting:
        _modbus = ModbusRTU(
            addr=connection_setting['unit'],
            baudrate=connection_setting['baudrate'],
            data_bits=config.MB_RTU_DATA_BITS,
            stop_bits=config.MB_RTU_STOP_BITS,
            parity=None,
            pins=pins,
            # ctrl_pin=MODBUS_PIN_TX_EN
        )
        print('Modbus RTU Master started on addr: {} with config: {} '.
              format(connection_setting['unit'], connection_setting))
        result = True
    else:
        _modbus = ModbusRTU(
            addr=config.MB_RTU_ADDRESS,
            baudrate=config.MB_RTU_BAUDRATE,
            data_bits=config.MB_RTU_DATA_BITS,
            stop_bits=config.MB_RTU_STOP_BITS,
            parity=None,
            pins=pins,
            # ctrl_pin=MODBUS_PIN_TX_EN
        )
        print('Modbus RTU Master started - addr:', config.MB_RTU_ADDRESS)
        result = True

    return result


def setup_modbus_tcp(connection_setting: dict = dict()) -> bool:
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

            print('Connection settings: {}'.format(connection_setting))
            port = config_TCP_PORT
            if 'unit' in connection_setting:
                try:
                    port = int(connection_setting['unit'])
                except Exception as e:
                    print('Failed, no valid "unit" in connection dict: {}'.
                          format(e))

            print('Binding device to IP "{}" on port "{}"'.
                  format(local_ip, port))
            _modbus.bind(local_ip=local_ip,
                         local_port=port)

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

    modbus_registers = load_register_files(
        file_path='registers/modbusRegisters.json')
    setup_result = False

    if ((config.MB_RTU_ADDRESS > 0) or
       (config.MB_TCP_IP is True)):
        if config.MB_RTU_ADDRESS > 0:
            print('MB_RTU_ADDRESS available')

            if 'CONNECTION' in modbus_registers:
                setup_result = setup_modbus_rtu(
                    connection_setting=modbus_registers['CONNECTION'],
                    pins=(12, 13)     # use other pins for testing
                )
            else:
                setup_result = setup_modbus_rtu()

            _modbus_process = _modbus_rtu_process
        else:
            print('No MB_RTU_ADDRESS, using TCP')

            if 'CONNECTION' in modbus_registers:
                print('CONNECTION content: {}'.
                      format(modbus_registers['CONNECTION']))
                setup_result = setup_modbus_tcp(
                    connection_setting=modbus_registers['CONNECTION']
                )
            else:
                print('No connection specified in modbus_registers')
                setup_result = setup_modbus_tcp()

            _modbus_process = _modbus_tcp_process

        if setup_result:
            print('Modbus setup successful, setup modbus registers...')
            setup_modbus_registers(modbus_registers=modbus_registers)
        else:
            print('Modbus setup failed')
            return
    else:
        print('Neither TCP nor RTU Modbus setup performed due to missing '
              'config in config.py')
        return

    print('Success, entering while loop')
    while True:
        try:
            _modbus_process()
        except Exception as e:
            _print_ex(msg='_modbus_process() error', e=e)

    print('While loop left ...')


if __name__ == '__main__':
    main()
