#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
main script, do your stuff here, similar to the loop() function on Arduino
"""

import gc
import json
import network
import sys
import _thread
import time

# libraries
from uModbus.serial import Serial as ModbusRTUMaster
from uModbus.tcp import TCP as ModbusTCPMaster
# not natively supported on micropython, see lib/typing.py
from typing import Tuple, Union

# custom modules
from helpers.led_helper import Neopixel
from helpers.path_helper import PathHelper
from modbus import ModbusRTU
from modbus import ModbusTCP
from webserver import WebServer

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

_active_threads = dict()
stop_threads = False
rtu_response_dict = dict()
tcp_changed_dict = dict()
rtu_response_lock = _thread.allocate_lock()


def _print_ex(msg: str, e) -> None:
    print('== [Exception] ====================')
    print(msg)
    sys.print_exception(e)
    # print('---------------------')
    # micropython.mem_info()
    print('===================================')


def _modbus_rtu_thread(_modbus: Union[ModbusRTU, ModbusRTUMaster]) -> None:
    global _active_threads
    global stop_threads

    _active_threads['_modbus_rtu_thread'] = _thread.get_ident()

    while stop_threads is False:
        try:
            _modbus.process()
        except KeyboardInterrupt:
            print('KeyboardInterrupt, killing this thread: {} ({})'.
                  format('_modbus_rtu_thread', _thread.get_ident()))
            stop_threads = True
            break
        except Exception as e:
            _print_ex(msg='_modbus_rtu_thread() error', e=e)

    # remove this thread ID from the _active_threads dict
    _active_threads.pop('_modbus_rtu_thread', None)


def _modbus_rtu_read_thread(_modbus: Union[ModbusRTU, ModbusRTUMaster], modbus_registers: dict, slave_addr: int, read_interval: int = 10000) -> None:
    global _active_threads
    global rtu_response_dict
    global tcp_changed_dict
    global stop_threads

    _active_threads['_modbus_rtu_read_thread'] = _thread.get_ident()

    last_read_rtu_time = time.ticks_ms()

    while stop_threads is False:
        try:
            time_diff = time.ticks_diff(time.ticks_ms(),
                                        last_read_rtu_time)
            if time_diff >= read_interval:
                # remember this timestamp
                last_read_rtu_time = time.ticks_ms()

                # acquire lock to set the RTU registers
                with rtu_response_lock:
                    # do it
                    # print('tcp_changed_dict BEFORE write_slave_registers: {}'.
                    #       format(tcp_changed_dict))
                    write_slave_registers(_modbus=_modbus,
                                          modbus_registers=tcp_changed_dict,
                                          address=slave_addr)
                    # print('tcp_changed_dict AFTER write_slave_registers: {}'.
                    #       format(tcp_changed_dict))

                response = read_slave_registers(
                    _modbus=_modbus,
                    modbus_registers=modbus_registers,
                    address=slave_addr)
                # requires approx. 4.5sec

                # print('Received this content after {}ms: {}'.
                #       format(time.ticks_diff(time.ticks_ms(),
                #                              last_read_rtu_time),
                #              json.dumps(rtu_response_dict)))

                # acquire lock to update/fill the rtu_response_dict
                with rtu_response_lock:
                    # create a real copy of the dict
                    rtu_response_dict = response.copy()
                # requires approx. 20-30ms
            else:
                # wait for a 100th of the read_interval (error is around 1%)
                time.sleep_ms(read_interval // 100)
        except KeyboardInterrupt:
            print('KeyboardInterrupt, killing this thread: {} ({})'.
                  format('_modbus_rtu_read_thread', _thread.get_ident()))
            stop_threads = True
            break
        except Exception as e:
            _print_ex(msg='_modbus_rtu_read_thread() error', e=e)

    # remove this thread ID from the _active_threads dict
    _active_threads.pop('_modbus_rtu_read_thread', None)


def _modbus_tcp_thread(_modbus: Union[ModbusTCP, ModbusTCPMaster], _web: WebServer) -> None:
    global _active_threads
    global rtu_response_dict
    global tcp_changed_dict
    global stop_threads

    _active_threads['_modbus_tcp_thread'] = _thread.get_ident()

    last_register_content_update_time = time.ticks_ms()
    register_update_interval = 10000
    local_response_dict = dict()

    while stop_threads is False:
        try:
            time_diff = time.ticks_diff(time.ticks_ms(),
                                        last_register_content_update_time)
            if time_diff >= register_update_interval:
                with rtu_response_lock:
                    # create a real copy of the dict
                    local_response_dict = rtu_response_dict.copy()
                    tcp_changed_dict = _modbus.changed_registers
                    if tcp_changed_dict != {'HREGS': {}, 'COILS': {}}:
                        print('Changed TCP registers @ _modbus_tcp_thread: {}'.
                              format(tcp_changed_dict))
                # requires approx. 30-40ms

                # update all registers of TCP modbus with the latest RTU data
                for reg_type in ['COILS', 'HREGS', 'ISTS', 'IREGS']:
                    if reg_type in local_response_dict:
                        for reg, val in local_response_dict[reg_type].items():
                            if 'val' in val:
                                address = val['register']
                                value = val['val']

                                if reg_type == 'COILS':
                                    # set register will add it if not yet there
                                    _modbus.set_coil(address=address,
                                                     value=value)
                                elif reg_type == 'HREGS':
                                    # set register will add it if not yet there
                                    _modbus.set_hreg(address=address,
                                                     value=value)
                                elif reg_type == 'ISTS':
                                    # set register will add it if not yet there
                                    _modbus.set_ist(address=address,
                                                    value=value)
                                elif reg_type == 'IREGS':
                                    # set register will add it if not yet there
                                    _modbus.set_ireg(address=address,
                                                     value=value)
                                else:
                                    # invalid register type
                                    pass
                            else:
                                # no value for this register in response dict
                                pass
                    else:
                        print('No {} defined in local_response_dict'.
                              format(reg_type))
                # requires approx. 180-200ms

                last_register_content_update_time = time.ticks_ms()

            # always assuming device is connected to network
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
            stop_threads = True
            break
        except Exception as e:
            _print_ex(msg='_modbus_tcp_thread() error', e=e)

    # remove this thread ID from the _active_threads dict
    _active_threads.pop('_modbus_tcp_thread', None)


def get_active_threads() -> dict:
    global _active_threads

    return _active_threads


"""
def _modbus_rtu_process(_modbus) -> None:
    # global _modbus

    _modbus.process()


def _modbus_tcp_process(_modbus, _web) -> None:
    # global _modbus
    # global _web

    # always assuming device is connected
    _modbus.process()

    if _web.get_status():
        _web.process(0)
    else:
        print('(Re)starting WebServer ...')
        _web.start()
        print('WebServer (re)started')
"""


def setup_webserver(user: str = 'admin', password: str = 'admin', port: int = 80, maximum_connections: int = 10) -> WebServer:
    print('Performing Webserver setup ...')

    _web = WebServer(user=user,
                     password=password,
                     port=port,
                     maximum_connections=maximum_connections)

    if _web.get_status() is False:
        print('Starting WebServer ...')
        _web.start()
        print('WebServer started')
    else:
        print('WebServer already running')

    print('Webserver setup done')

    return _web


def print_modbus_response(register: dict, response) -> None:
    pass
    # print('{content:>15}\t{description}'.
    #       format(description=register['description'],
    #              content=' '.join('{:d}'.format(x) for x in response)))


def add_response_to_dict(response_dict: dict, key: str, register: int, response) -> None:
    if len(response) == 1:
        # only a single value
        response_dict[key] = {'register': register, 'val': response[0]}
    else:
        # convert the tuple to list to be JSON conform
        response_dict[key] = {'register': register, 'val': list(response)}


def read_slave_registers(_modbus: Union[ModbusRTU, ModbusTCP, ModbusRTUMaster, ModbusTCPMaster], modbus_registers: dict, address: int) -> dict:
    response_dict = dict()
    slave_addr = address
    starting_address = 0
    register_quantity = 0
    signed = False

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
        print('No reading registers defined')

    return response_dict


def write_slave_registers(_modbus: Union[ModbusRTU, ModbusTCP, ModbusRTUMaster, ModbusTCPMaster], modbus_registers: dict, address: int) -> None:
    slave_addr = address
    register_address = 0
    signed = False

    if len(modbus_registers):
        if 'COILS' in modbus_registers:
            for register, val in modbus_registers['COILS'].items():
                register_value = val['val']

                print('Set COIL {coil_addr} of slave {rtu_addr} to {val}'.
                      format(coil_addr=register,
                             rtu_addr=slave_addr,
                             val=register_value))

                # @see lib/uModbus/functions.write_single_coil
                if register_value is True:
                    register_value = 0xFF00
                else:
                    register_value = 0x0000

                operation_status = _modbus.write_single_coil(
                    slave_addr=slave_addr,
                    output_address=register,
                    output_value=register_value)

                print('Result of setting COIL {} to {}: {}'.
                      format(register, register_value, operation_status))

                if operation_status:
                    modbus_registers['COILS'].pop(register, None)
        else:
            print('No COILS defined in given modbus_registers')

        if 'HREGS' in modbus_registers:
            for register, val in modbus_registers['HREGS'].items():
                register_value = val['val']

                print('Set HREG {hreg_addr} of slave {rtu_addr} to {val}'.
                      format(hreg_addr=register,
                             rtu_addr=slave_addr,
                             val=register_value))

                operation_status = _modbus.write_single_register(
                    slave_addr=slave_addr,
                    register_address=register,
                    register_value=register_value,
                    signed=signed)

                print('Result of setting HREGS {} to {}: {}'.
                      format(register, register_value, operation_status))

                if operation_status:
                    modbus_registers['HREGS'].pop(register, None)
        else:
            print('No HREGS defined in given modbus_registers')

        if 'ISTS' in modbus_registers:
            print('ISTS can only be read, skipping')

        if 'IREGS' in modbus_registers:
            print('IREGS can only be read, skipping')
    else:
        print('No writing registers defined')


def load_registers_file(file_path: str) -> dict:
    modbus_registers = dict()

    # if os.path.exists(file_path):
    if PathHelper.exists(path=file_path):
        with open(file_path) as json_file:
            # json module does not preserve the order of the items in the file
            modbus_registers = json.load(json_file)
            print('Loaded these registers: {}'.format(modbus_registers))
    else:
        print('No register file "{}" available'.format(file_path))

    return modbus_registers


def get_modbus_connection_settings(modbus_content: dict) -> dict:
    config = dict()

    # type: "rtu", "tcp"
    # unit: 10,
    # address: "/dev/tty.wchusbserial1420", "192.168.178.80"
    # mode: "slave", "master"
    # baudrate: 9600, optional, only required on type RTU
    required_keys = ["type", "unit", "address", "mode"]

    if 'CONNECTION' in modbus_content:
        if all(k in modbus_content['CONNECTION'] for k in required_keys):
            if modbus_content['CONNECTION']['type'] == 'rtu':
                if 'baudrate' not in modbus_content['CONNECTION']:
                    print('Missing "baudrate" key in connection config')

                    # baudrate config is required for RTU connections
                    return config

            config = modbus_content['CONNECTION']
    else:
        print('No key "CONNECTION" found in given modbus_content')

    print('Loaded this connection config: {}'.format(config))

    return config


"""
def setup_modbus_registers(_modbus, modbus_registers: dict = dict(), use_default_vals: bool = True) -> None:
    reg_types = {'COILS': True, 'HREGS': 999, 'ISTS': True, 'IREGS': 999}

    if len(modbus_registers):
        for reg_type in reg_types.keys():
            if reg_type in modbus_registers:
                for reg, val in modbus_registers[reg_type].items():
                    address = val['register']

                    if use_default_vals:
                        if 'len' in val:
                            value = [reg_types[reg_type]] * val['len']
                        else:
                            value = reg_types[reg_type]
                    else:
                        value = val['val']

                    # print('Adding {} at {}'.format(reg_type, address))

                    if reg_type == 'COILS':
                        _modbus.add_coil(address=address,
                                         value=value)
                    elif reg_type == 'HREGS':
                        _modbus.add_hreg(address=address,
                                         value=value)
                    elif reg_type == 'ISTS':
                        _modbus.add_ist(address=address,
                                        value=value)
                    elif reg_type == 'IREGS':
                        _modbus.add_ireg(address=address,
                                         value=value)
                    else:
                        # invalid register type
                        pass
            else:
                print('No {} defined in modbus_registers'.
                      format(reg_type))
"""


def setup_modbus_rtu(connection_setting: dict = dict(), is_master: bool = False, pins: tuple = (1, 3)) -> Tuple[Union[ModbusRTU, ModbusRTUMaster], bool]:
    result = False
    _modbus = None
    bus_address = None
    data_bits = 8
    stop_bits = 1
    parity = None
    # is_master = True if connection_setting['mode'] == 'master' else False

    if not is_master:
        bus_address = connection_setting['unit']

    if 'data_bits' in connection_setting:
        data_bits = connection_setting['data_bits']

    if 'stop_bits' in connection_setting:
        stop_bits = connection_setting['stop_bits']

    if 'parity' in connection_setting:
        parity = connection_setting['parity']

    if is_master:
        # master, get Modbus data from other device
        _modbus = ModbusRTUMaster(
            baudrate=connection_setting['baudrate'],
            data_bits=data_bits,
            stop_bits=stop_bits,
            parity=parity,
            pins=pins,
            # ctrl_pin=MODBUS_PIN_TX_EN
        )
    else:
        _modbus = ModbusRTU(
            addr=bus_address,
            baudrate=connection_setting['baudrate'],
            data_bits=data_bits,
            stop_bits=stop_bits,
            parity=parity,
            pins=pins,
            # ctrl_pin=MODBUS_PIN_TX_EN
        )

    print('Modbus RTU {type} started on addr {address} with config {cfg}'.
          format(type='Master' if is_master else 'Slave',
                 address=bus_address,
                 cfg=connection_setting))
    result = True

    """
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
    """

    return _modbus, result


def setup_modbus_tcp(connection_setting: dict = dict(),
                     is_master: bool = False) -> Tuple[Union[ModbusTCP, ModbusTCPMaster], bool]:
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
                print('No get_bound_status function available: {}'.format(e))

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

    return _modbus, result


def main():
    global rtu_response_dict
    global stop_threads

    pixel = Neopixel()
    pixel.color = [10, 20, 30]
    pixel.intensity = 30

    _web = setup_webserver(user=config_WEB_USER,
                           password=config_WEB_PASSWORD)

    modbus_registers = load_registers_file(
        # file_path='registers/modbusRegisters.json')
        file_path='registers/modbusRegisters-MyEVSE.json')

    modbus_connection_settings = get_modbus_connection_settings(
        modbus_content=modbus_registers)

    # """
    #
    # setup Modbus RTU master and Modbus TCP slave
    # request data from MyEVSE and provide them via Modbus TCP on port 180
    # data of configured modbus_registers are requested from MyEVSE via RTU
    # data of configured modbus_registers can be requested via TCP on port 180
    #
    if bool(modbus_connection_settings):
        slave_addr = modbus_connection_settings['unit']

        _modbus_rtu, setup_result_rtu = setup_modbus_rtu(
            connection_setting=modbus_connection_settings,
            is_master=True,   # configure as Master to collect data (from EVSE)
            pins=(12, 13)     # (TX, RX) use other pins for testing
        )

        if setup_result_rtu:
            print('Modbus RTU master setup successful')

            # remember this timestamp
            start_read_rtu_time = time.ticks_ms()

            rtu_response_dict = read_slave_registers(
                _modbus=_modbus_rtu,
                modbus_registers=modbus_registers,
                address=slave_addr)
            # requires approx. 4.5sec

            print('Received this content after {}ms: {}'.
                  format(time.ticks_diff(time.ticks_ms(), start_read_rtu_time),
                         json.dumps(rtu_response_dict)))

            _thread.start_new_thread(_modbus_rtu_read_thread,
                                     (_modbus_rtu, modbus_registers, slave_addr, 10000))
            print('Successfully started _modbus_rtu_read_thread')
        else:
            print('Modbus RTU setup failed')
            return

        _modbus_tcp, setup_result_tcp = setup_modbus_tcp(
            connection_setting={'unit': 180},
            is_master=False   # configure as Slave to provide data
        )

        if setup_result_tcp:
            print('Modbus TCP slave setup successful')

            print('Setup registers for TCP...')
            # setup_modbus_registers(_modbus=_modbus_tcp,
            #                        modbus_registers=rtu_response_dict,
            #                        use_default_vals=False)
            _modbus_tcp.setup_registers(registers=rtu_response_dict,
                                        use_default_vals=False)
            print('Register setup done')

            _thread.start_new_thread(_modbus_tcp_thread, (_modbus_tcp, _web))
            print('Successfully started _modbus_tcp_thread')
        else:
            print('Modbus TCP setup failed')
            return
    else:
        print('No CONNECTION config element in the modbus register json file')
        return

    # wait some short time, to get all threads started and registered in dict
    time.sleep(0.1)
    # """

    """
    #
    # setup Modbus RTU slave
    # data of configured modbus_registers can be requested from this device
    #
    setup_result = False

    if bool(modbus_connection_settings):
        slave_addr = modbus_connection_settings['unit']

        _modbus, setup_result = setup_modbus_rtu(
            connection_setting=modbus_connection_settings,
            is_master=False,   # configure as Slave to provide data
            pins=(12, 13)      # (TX, RX) use other pins for testing
        )
    else:
        _modbus, setup_result = setup_modbus_rtu(is_master=False)

    # _modbus_process = _modbus_rtu_process
    _modbus_thread = _modbus_rtu_thread

    if setup_result:
        print('Modbus RTU slave setup successful')

        print('Setup registers for RTU...')
        # setup_modbus_registers(_modbus=_modbus,
        #                        modbus_registers=modbus_registers)
        _modbus.setup_registers(registers=modbus_registers)
        print('Register setup done')
    else:
        print('Modbus RTU setup failed')
        return

    _thread.start_new_thread(_modbus_thread, (_modbus, ))
    print('Successfully started _modbus_thread')
    time.sleep(0.1)
    """

    """
    #
    # general testing
    # data of configured modbus_registers can be requested from this device
    #
    setup_result = False

    if ((config.MB_RTU_ADDRESS > 0) or
       (config.MB_TCP_IP is True)):
        if config.MB_RTU_ADDRESS > 0:
            print('MB_RTU_ADDRESS available: {}'.format(config.MB_RTU_ADDRESS))

            if bool(modbus_connection_settings):
                _modbus, setup_result = setup_modbus_rtu(
                    connection_setting=modbus_registers['CONNECTION'],
                    is_master=False,   # configure as Slave to provide data
                    pins=(12, 13)      # (TX, RX) use other pins for testing
                )
            else:
                _modbus, setup_result = setup_modbus_rtu(is_master=False)

            # _modbus_process = _modbus_rtu_process
            _modbus_thread = _modbus_rtu_thread
        else:
            print('No MB_RTU_ADDRESS, using TCP')

            if bool(modbus_connection_settings):
                _modbus, setup_result = setup_modbus_tcp(
                    connection_setting=modbus_registers['CONNECTION'],
                    is_master=False   # configure as Slave to provide data
                )
            else:
                print('No connection specified in modbus_registers')
                _modbus, setup_result = setup_modbus_tcp(is_master=False)

            # _modbus_process = _modbus_tcp_process
            _modbus_thread = _modbus_tcp_thread

        if setup_result:
            print('Modbus slave setup successful'

            print('Setup slave registers...')
            # setup_modbus_registers(_modbus=_modbus,
            #                        modbus_registers=modbus_registers)
            _modbus.setup_registers(registers=modbus_registers)
            print('Register setup done')
        else:
            print('Modbus setup failed')
            return
    else:
        print('Neither TCP nor RTU Modbus setup performed due to missing '
              'config in config.py')
        return

    if config.MB_RTU_ADDRESS > 0:
        _thread.start_new_thread(_modbus_thread, (_modbus, ))
    else:
        _thread.start_new_thread(_modbus_thread, (_modbus, _web))
    print('Successfully started _modbus_thread')
    time.sleep(0.1)
    """

    print('Currently active threads: {}'.format(get_active_threads()))

    last_memory_info_time = time.ticks_ms()
    memory_info_interval = 10000    # milliseconds

    # show activity
    while True:
        try:
            pixel.fade()

            # run garbage collector
            gc.collect()

            """
            time_diff = time.ticks_diff(time.ticks_ms(),
                                        last_memory_info_time)

            if time_diff >= memory_info_interval:
                free = gc.mem_free()
                allocated = gc.mem_alloc()
                total = free + allocated
                percentage = '{0:.2f}%'.format((free / total) * 100)
                print('Total: {total}kB, free: {free}kB ({usage})'.
                      format(free=free / 1023,
                             total=total / 1023,
                             usage=percentage))
                last_memory_info_time = time.ticks_ms()
            """

        except KeyboardInterrupt:
            print('KeyboardInterrupt, killing all active threads...')
            break
        except Exception as e:
            print('Catched exception: {}'.format(e))

        if stop_threads:
            print('Other thread set flag to stop all threads')
            break

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
