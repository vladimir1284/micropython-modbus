#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
main script, do your stuff here, similar to the loop() function on Arduino
"""

from machine import UART
import json
import led_helper
import network
import os
import sys
import _thread
import time
import uos

# libraries
from modbus import ModbusRTU
from uModbus.serial import Serial as ModbusRTUMaster
from modbus import ModbusTCP
from uModbus.tcp import TCP as ModbusTCPMaster
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
_active_threads = dict()
stop_threads = False


def _print_ex(msg, e):
    print('== [Exception] ====================')
    print(msg)
    sys.print_exception(e)
    # print('---------------------')
    # micropython.mem_info()
    print('===================================')


def _modbus_rtu_thread():
    global _active_threads
    global _modbus
    global stop_threads

    _active_threads['_modbus_rtu_thread'] = _thread.get_ident()

    while stop_threads is False:
        try:
            _modbus.process()
        except KeyboardInterrupt:
            print('KeyboardInterrupt, killing this thread: {} ({})'.
                  format('_modbus_rtu_thread', _thread.get_ident()))
            break
        except Exception as e:
            _print_ex(msg='_modbus_rtu_thread() error', e=e)

    # remove this thread ID from the _active_threads dict
    _active_threads.pop('_modbus_rtu_thread', None)


def _modbus_tcp_thread():
    global _active_threads
    global _modbus
    global stop_threads
    global _web

    _active_threads['_modbus_tcp_thread'] = _thread.get_ident()

    while stop_threads is False:
        try:
            # always assuming device is connected
            _modbus.process()

            if _web.get_status():
                _web.process(0)
            else:
                print('(Re)starting WebServer ...')
                _web.start()
                print('WebServer (re)started')
        except KeyboardInterrupt:
            print('KeyboardInterrupt, killing this thread: {} ({})'.
                  format('_modbus_tcp_thread', _thread.get_ident()))
            break
        except Exception as e:
            _print_ex(msg='_modbus_tcp_thread() error', e=e)

    # remove this thread ID from the _active_threads dict
    _active_threads.pop('_modbus_tcp_thread', None)


def get_active_threads() -> dict:
    global _active_threads

    return _active_threads


"""
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
"""


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


def print_modbus_response(register: dict, response) -> None:
    print('{description}: {content}'.format(
            description=register['description'],
            content=' '.join('{:d}'.format(x) for x in response)))


def add_response_to_dict(response_dict: dict,
                         key: str,
                         register: int,
                         response) -> None:
    if len(response) == 1:
        # only a single value
        response_dict[key] = {'register': register, 'val': response[0]}
    else:
        # convert the tuple to list to be JSON conform
        response_dict[key] = {'register': register, 'val': list(response)}


def read_slave_registers(modbus_registers: dict) -> dict:
    global _modbus

    response_dict = dict()
    slave_addr = 0
    starting_address = 0
    register_quantity = 0
    description = ''
    signed = False

    try:
        slave_addr = modbus_registers['CONNECTION']['unit']
    except Exception as e:
        print('Failed to load connection unit address from modbus_registers')
        return response_dict

    if len(modbus_registers):
        if 'COILS' in modbus_registers:
            response_dict['COILS'] = dict()

            for register, val in modbus_registers['COILS'].items():
                starting_address = val['register']
                register_quantity = val['len']

                coil_status = _modbus.read_coils(
                    slave_addr=slave_addr,
                    starting_addr=starting_address,
                    coil_qty=register_quantity)

                add_response_to_dict(response_dict=response_dict['COILS'],
                                     key=register,
                                     register=starting_address,
                                     response=coil_status)
                print_modbus_response(register=val, response=coil_status)
        else:
            print('No COILS defined in given modbus_registers')

        if 'HREGS' in modbus_registers:
            response_dict['HREGS'] = dict()

            for register, val in modbus_registers['HREGS'].items():
                starting_address = val['register']
                register_quantity = val['len']

                register_value = _modbus.read_holding_registers(
                    slave_addr=slave_addr,
                    starting_addr=starting_address,
                    register_qty=register_quantity,
                    signed=signed)

                add_response_to_dict(response_dict=response_dict['HREGS'],
                                     key=register,
                                     register=starting_address,
                                     response=register_value)
                print_modbus_response(register=val, response=register_value)
        else:
            print('No HREGS defined in given modbus_registers')

        if 'ISTS' in modbus_registers:
            response_dict['ISTS'] = dict()

            for register, val in modbus_registers['ISTS'].items():
                starting_address = val['register']
                register_quantity = val['len']

                input_status = _modbus.read_discrete_inputs(
                    slave_addr=slave_addr,
                    starting_addr=starting_address,
                    input_qty=register_quantity)

                add_response_to_dict(response_dict=response_dict['ISTS'],
                                     key=register,
                                     register=starting_address,
                                     response=input_status)
                print_modbus_response(register=val, response=input_status)
        else:
            print('No ISTS defined in given modbus_registers')

        if 'IREGS' in modbus_registers:
            response_dict['IREGS'] = dict()

            for register, val in modbus_registers['IREGS'].items():
                starting_address = val['register']
                register_quantity = val['len']

                register_value = _modbus.read_input_registers(
                    slave_addr=slave_addr,
                    starting_addr=starting_address,
                    register_qty=register_quantity,
                    signed=signed)

                add_response_to_dict(response_dict=response_dict['IREGS'],
                                     key=register,
                                     register=starting_address,
                                     response=register_value)
                print_modbus_response(register=val, response=register_value)
        else:
            print('No IREGS defined in given modbus_registers')
    else:
        print('No registers defined')

    return response_dict


def load_register_files(file_path='registers/modbusRegisters.json') -> dict:
    modbus_registers = dict()

    # if os.path.exists(file_path):
    if path_helper.exists(path=file_path):
        with open(file_path) as json_file:
            # json module does not preserve the order of the items in the file
            modbus_registers = json.load(json_file)
            print('Loaded these registers: {}'.format(modbus_registers))
    else:
        print('No register file "{}" available'.format(file_path))

    return modbus_registers


def setup_modbus_registers(modbus_registers: dict = dict(),
                           default_vals: bool = True) -> None:
    global _modbus

    if len(modbus_registers):
        if 'COILS' in modbus_registers:
            for register, val in modbus_registers['COILS'].items():
                starting_address = val['register']

                print('Adding COIL at {}'.format(starting_address))

                if default_vals:
                    if 'len' in val:
                        value = [True] * val['len']
                    else:
                        value = True
                else:
                    value = val['val']

                _modbus.add_coil(address=starting_address,
                                 value=value)
        else:
            print('No COILS defined in given modbus_registers')

        if 'HREGS' in modbus_registers:
            for register, val in modbus_registers['HREGS'].items():
                starting_address = val['register']

                print('Adding HREG at {}'.format(starting_address))

                if default_vals:
                    if 'len' in val:
                        value = [999] * val['len']
                    else:
                        value = 999
                else:
                    value = val['val']

                _modbus.add_hreg(address=starting_address,
                                 value=value)
        else:
            print('No HREGS defined in given modbus_registers')

        if 'ISTS' in modbus_registers:
            for register, val in modbus_registers['ISTS'].items():
                starting_address = val['register']

                print('Adding IST at {}'.format(starting_address))

                if default_vals:
                    if 'len' in val:
                        value = [True] * val['len']
                    else:
                        value = True
                else:
                    value = val['val']

                _modbus.add_ist(address=starting_address,
                                value=value)
        else:
            print('No ISTS defined in given modbus_registers')

        if 'IREGS' in modbus_registers:
            for register, val in modbus_registers['IREGS'].items():
                starting_address = val['register']

                print('Adding IREG at {}'.format(starting_address))

                if default_vals:
                    if 'len' in val:
                        value = [999] * val['len']
                    else:
                        value = 999
                else:
                    value = val['val']

                _modbus.add_ireg(address=starting_address,
                                 value=value)
        else:
            print('No IREGS defined in given modbus_registers')


def setup_modbus_rtu(connection_setting: dict = dict(),
                     is_master: bool = False,
                     pins: tuple = (1, 3)) -> bool:
    global _modbus

    result = False

    if 'unit' in connection_setting and 'baudrate' in connection_setting:
        if is_master:
            # master, get Modbus data from other device
            _modbus = ModbusRTUMaster(
                baudrate=connection_setting['baudrate'],
                data_bits=config.MB_RTU_DATA_BITS,
                stop_bits=config.MB_RTU_STOP_BITS,
                parity=None,
                pins=pins,
                # ctrl_pin=MODBUS_PIN_TX_EN
            )
        else:
            # slave, provide Modbus data for device
            _modbus = ModbusRTU(
                addr=connection_setting['unit'],
                baudrate=connection_setting['baudrate'],
                data_bits=config.MB_RTU_DATA_BITS,
                stop_bits=config.MB_RTU_STOP_BITS,
                parity=None,
                pins=pins,
                # ctrl_pin=MODBUS_PIN_TX_EN
            )

        print('Modbus RTU {type} started on addr {address} with config {cfg}'.
              format(type='Master' if is_master else 'Slave',
                     address=connection_setting['unit'],
                     cfg=connection_setting))
        result = True
    else:
        if is_master:
            # master, get Modbus data from other device
            _modbus = ModbusRTUMaster(
                baudrate=config.MB_RTU_BAUDRATE,
                data_bits=config.MB_RTU_DATA_BITS,
                stop_bits=config.MB_RTU_STOP_BITS,
                parity=None,
                pins=pins,
                # ctrl_pin=MODBUS_PIN_TX_EN
            )
        else:
            # slave, provide Modbus data for device
            _modbus = ModbusRTU(
                addr=config.MB_RTU_ADDRESS,
                baudrate=config.MB_RTU_BAUDRATE,
                data_bits=config.MB_RTU_DATA_BITS,
                stop_bits=config.MB_RTU_STOP_BITS,
                parity=None,
                pins=pins,
                # ctrl_pin=MODBUS_PIN_TX_EN
            )

        print('Modbus RTU {type} started on addr {address}'.
              format(type='Master' if is_master else 'Slave',
                     address=config.MB_RTU_ADDRESS))
        result = True

    return result


def setup_modbus_tcp(connection_setting: dict = dict(),
                     is_master: bool = False) -> bool:
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
        if is_master:
            # master, get Modbus data from other device
            if 'address' in connection_setting:
                slave_ip = connection_setting['address']

            if 'unit' in connection_setting:
                try:
                    port = int(connection_setting['unit'])
                except Exception as e:
                    print('Failed, no valid "unit" in connection dict: {}'.
                          format(e))

                _modbus = ModbusTCPMaster(slave_ip=slave_ip, slave_port=port)
            else:
                _modbus = ModbusTCPMaster(slave_ip=slave_ip)

            result = True
        else:
            # slave, provide Modbus data for device
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
    global stop_threads
    global _web

    setup_webserver()

    modbus_registers = load_register_files(
        # file_path='registers/modbusRegisters.json')
        file_path='registers/modbusRegisters-MyEVSE.json')
    setup_result = False

    """
    #
    # request data from MyEVSE and provide them via Modbus TCP on port 180
    #
    if 'CONNECTION' in modbus_registers:
        print('CONNECTION content: {}'.
              format(modbus_registers['CONNECTION']))

        setup_result = setup_modbus_rtu(
            connection_setting=modbus_registers['CONNECTION'],
            is_master=True,   # configure as Master to collect data (from EVSE)
            pins=(12, 13)     # (TX, RX) use other pins for testing
        )

        response_dict = read_slave_registers(modbus_registers=modbus_registers)
        print('Received this content: {}'.format(response_dict))

        # global _modbus is overwritten onwards, RTU can't be used anymore
        setup_result = setup_modbus_tcp(
            connection_setting={'unit': 180},
            is_master=False   # configure as Slave to provide data
        )

        # _modbus_process = _modbus_tcp_process
        _modbus_thread = _modbus_tcp_thread

        if setup_result:
            print('Modbus setup successful, setup modbus registers...')

            setup_modbus_registers(modbus_registers=response_dict,
                                   default_vals=False)
        else:
            print('Modbus setup failed')
            return
    else:
        print('No CONNECTION config element in the modbus register json file')
        return
    """

    # """
    #
    # setup Modbus RTU slave
    #
    if 'CONNECTION' in modbus_registers:
        setup_result = setup_modbus_rtu(
            connection_setting=modbus_registers['CONNECTION'],
            is_master=False,   # configure as Slave to provide data
            pins=(12, 13)      # (TX, RX) use other pins for testing
        )
    else:
        setup_result = setup_modbus_rtu(is_master=False)

    # _modbus_process = _modbus_rtu_process
    _modbus_thread = _modbus_rtu_thread

    if setup_result:
        print('Modbus setup successful, setup modbus registers...')
        setup_modbus_registers(modbus_registers=modbus_registers)
    else:
        print('Modbus setup failed')
        return
    # """

    """
    #
    # general testing
    #
    if ((config.MB_RTU_ADDRESS > 0) or
       (config.MB_TCP_IP is True)):
        if config.MB_RTU_ADDRESS > 0:
            print('MB_RTU_ADDRESS available: {}'.format(config.MB_RTU_ADDRESS))

            if 'CONNECTION' in modbus_registers:
                setup_result = setup_modbus_rtu(
                    connection_setting=modbus_registers['CONNECTION'],
                    is_master=False,   # configure as Slave to provide data
                    pins=(12, 13)      # (TX, RX) use other pins for testing
                )
            else:
                setup_result = setup_modbus_rtu(is_master=False)

            # _modbus_process = _modbus_rtu_process
            _modbus_thread = _modbus_rtu_thread
        else:
            print('No MB_RTU_ADDRESS, using TCP')

            if 'CONNECTION' in modbus_registers:
                print('CONNECTION content: {}'.
                      format(modbus_registers['CONNECTION']))
                setup_result = setup_modbus_tcp(
                    connection_setting=modbus_registers['CONNECTION'],
                    is_master=False   # configure as Slave to provide data
                )
            else:
                print('No connection specified in modbus_registers')
                setup_result = setup_modbus_tcp(is_master=False)

            # _modbus_process = _modbus_tcp_process
            _modbus_thread = _modbus_tcp_thread

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
    """

    _thread.start_new_thread(_modbus_thread, ())
    print('Successfully started _modbus_thread')
    time.sleep(1.0)

    print('Currently active threads: {}'.format(get_active_threads()))

    # show activity
    while True:
        try:
            led_helper.neopixel_fade(finally_clear=False,
                                     delay_ms=250,
                                     maximum_intensity=30)
        except KeyboardInterrupt:
            print('KeyboardInterrupt, killing all active threads...')
            break
        except Exception as e:
            print('Catched exception: {}'.format(e))

    print('While loop left. These threads are still running: {}'.
          format(get_active_threads()))

    print('Stopping all threads now ...')
    stop_threads = True
    time.sleep(1.0)

    print('Active threads after stop: {}'.format(get_active_threads()))
    print('Goodbye :)')

    """
    # using specific modbus thread instead of this while loop
    # common part
    print('Success, entering while loop')
    while True:
        try:
            _modbus_process()
        except Exception as e:
            _print_ex(msg='_modbus_process() error', e=e)

    print('While loop left ...')
    """


if __name__ == '__main__':
    main()
