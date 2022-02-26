#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create a ModbusBridge betweeen a RTU client (slave) and act as host (master)
on TCP to provide the data of the client and accept settings of new register
values on it.

The TCP port and RTU communication pins can be choosen freely. The register
definitions of the client as well as its connection settings like bus address
and UART communication speed are defined in the JSON file at
'registers/modbusRegisters-MyEVSE.json'.
"""

# system packages
import time
import machine

# custom packages
from be_helpers.modbus_bridge import ModbusBridge
# from be_helpers.generic_helper import GenericHelper

register_file = 'registers/modbusRegisters-MyEVSE.json'
rtu_pins = (25, 26)     # (TX, RX)
tcp_port = 180          # TCP port for Modbus connection
run_time = 120          # run this example for this amount of seconds

# default level is 'warning', may use custom logger to get initial log data
mb_bridge = ModbusBridge(register_file=register_file)

# for testing use 'debug' level
# for beta testing with full BE32-01 board use 'info' level
# for production use 'warning' level, default
# GenericHelper.set_level(mb_bridge.logger, 'info')

print('##### MAIN TEST PRINT CONTENT BEGIN #####')
print('Register file: {}'.format(mb_bridge.register_file))
print('Connection settings:')
print('\t Host: {}'.format(mb_bridge.connection_settings_host))
print('\t Client: {}'.format(mb_bridge.connection_settings_client))
print('\t Host Unit: {}'.format(mb_bridge.host_unit))
print('\t Client Unit: {}'.format(mb_bridge.client_unit))

# define and apply Modbus TCP host settings
host_settings = {
    'type': 'tcp',
    'unit': tcp_port,
    'address': -1,
    'baudrate': -1,
    'mode': 'master'
}
mb_bridge.connection_settings_host = host_settings

print('Updated connection settings:')
print('\t Host: {}'.format(mb_bridge.connection_settings_host))
print('\t Client: {}'.format(mb_bridge.connection_settings_client))
print('\t Host Unit: {}'.format(mb_bridge.host_unit))
print('\t Client Unit: {}'.format(mb_bridge.client_unit))

# setup Modbus connections to host and client
mb_bridge.setup_connection(pins=rtu_pins)   # (TX, RX)

print('Modbus instances:')
print('\t Act as Host: {} on {}'.format(mb_bridge.host, mb_bridge.host_unit))
print('\t Act as Client: {} on {}'.format(mb_bridge.client,
                                          mb_bridge.client_unit))

# start collecting latest RTU client data in thread and TCP data provision
mb_bridge.collecting_client_data = True
mb_bridge.provisioning_host_data = True

print('Run client and host for {} seconds'.format(run_time))
print('Collect latest client data every {} seconds'.
      format(mb_bridge.collection_interval))
print('Synchronize Host-Client every {} seconds'.
      format(mb_bridge.synchronisation_interval))

print('##### MAIN TEST PRINT CONTENT END #####')

start_time = time.time()
while time.time() < (start_time + run_time):
    try:
        machine.idle()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stop collection + provisioning after {}'.
              format(time.time() - start_time))
        break
    except Exception as e:
        print('Exception: {}'.format(e))

# stop collecting latest client data in thread and data provision via TCP
mb_bridge.collecting_client_data = False
mb_bridge.provisioning_host_data = False

# wait for 5 more seconds to safely finish the may still running threads
time.sleep(5)

print('Returning to REPL')
