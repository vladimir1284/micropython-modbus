#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create a Modbus TCP client (slave) which can be requested for data or set with
specific values by a host device.

The TCP port and IP address can be choosen freely. The register definitions of
the client can be defined by the user.
"""

# system packages
import time

# import modbus client classes
from umodbus.tcp import ModbusTCP

IS_DOCKER_MICROPYTHON = False
try:
    import network
except ImportError:
    IS_DOCKER_MICROPYTHON = True


# ===============================================
if IS_DOCKER_MICROPYTHON is False:
    # connect to a network
    station = network.WLAN(network.STA_IF)
    if station.active() and station.isconnected():
        station.disconnect()
        time.sleep(1)
    station.active(False)
    time.sleep(1)
    station.active(True)

    # station.connect('SSID', 'PASSWORD')
    station.connect('TP-LINK_FBFC3C', 'C1FBFC3C')
    time.sleep(1)

    while True:
        print('Waiting for WiFi connection...')
        if station.isconnected():
            print('Connected to WiFi.')
            print(station.ifconfig())
            break
        time.sleep(2)

# ===============================================
# TCP Slave setup
tcp_port = 502              # port to listen to

if IS_DOCKER_MICROPYTHON:
    local_ip = '172.24.0.2'     # static Docker IP address
else:
    # set IP address of the MicroPython device explicitly
    # local_ip = '192.168.4.1'    # IP address
    # or get it from the system after a connection to the network has been made
    local_ip = station.ifconfig()[0]

# ModbusTCP can get TCP requests from a host device to provide/set data
client = ModbusTCP()
is_bound = False

# check whether client has been bound to an IP and port
is_bound = client.get_bound_status()

if not is_bound:
    client.bind(local_ip=local_ip, local_port=tcp_port)

# commond slave register setup, to be used with the Master example above
register_definitions = {
    "COILS": {
        "RESET_REGISTER_DATA_COIL": {
            "register": 42,
            "len": 1,
            "val": 0
        },
        "EXAMPLE_COIL": {
            "register": 123,
            "len": 1,
            "val": 1
        }
    },
    "HREGS": {
        "EXAMPLE_HREG": {
            "register": 93,
            "len": 1,
            "val": 19
        }
    },
    "ISTS": {
        "EXAMPLE_ISTS": {
            "register": 67,
            "len": 1,
            "val": 0
        }
    },
    "IREGS": {
        "EXAMPLE_IREG": {
            "register": 10,
            "len": 2,
            "val": 60001
        }
    }
}

"""
# alternatively the register definitions can also be loaded from a JSON file
import json

with open('registers/example.json', 'r') as file:
    register_definitions = json.load(file)
"""

print('Setting up registers ...')
# use the defined values of each register type provided by register_definitions
client.setup_registers(registers=register_definitions)
# alternatively use dummy default values (True for bool regs, 999 otherwise)
# client.setup_registers(registers=register_definitions, use_default_vals=True)
print('Register setup done')

print('Serving as TCP client on {}:{}'.format(local_ip, tcp_port))

reset_data_register = \
    register_definitions['COILS']['RESET_REGISTER_DATA_COIL']['register']

while True:
    try:
        result = client.process()
        if reset_data_register in client.coils:
            if client.get_coil(address=reset_data_register):
                print('Resetting register data to default values ...')
                client.setup_registers(registers=register_definitions)
                print('Default values restored')
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping TCP client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))

print("Finished providing/accepting data as client")
