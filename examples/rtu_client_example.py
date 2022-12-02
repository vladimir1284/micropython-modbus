#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create a Modbus RTU client (slave) which can be requested for data or set with
specific values by a host device.

The RTU communication pins can be choosen freely. The register definitions of
the client as well as its connection settings like bus address and UART
communication speed can be defined by the user.
"""

# import modbus client classes
from umodbus.serial import ModbusRTU

# ===============================================
# RTU Slave setup
# act as client, provide Modbus data via RTU to a host device
# ModbusRTU can get serial requests from a host device to provide/set data
rtu_pins = (25, 26)         # (TX, RX)
slave_addr = 10             # address on bus as client
baudrate = 9600
client = ModbusRTU(
    addr=slave_addr,        # address on bus
    baudrate=baudrate,      # optional, default 9600
    # data_bits=8,            # optional, default 8
    # stop_bits=1,            # optional, default 1
    # parity=None,            # optional, default None
    pins=rtu_pins)

# common slave register setup, to be used with the Master example above
register_definitions = {
    "COILS": {
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

# use the defined values of each register type provided by register_definitions
client.setup_registers(registers=register_definitions)
# alternatively use dummy default values (True for bool regs, 999 otherwise)
# client.setup_registers(registers=register_definitions, use_default_vals=True)

while True:
    result = client.process()

print("Finished providing/accepting data as client")
