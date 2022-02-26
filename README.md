# MicroPython Modbus library

MicroPython ModBus TCP and RTU library supporting client and host mode

---------------

## General

Forked from [Exo Sense Py][ref-sferalabs-exo-sense], based on
[PyCom Modbus][ref-pycom-modbus] and extended with other functionalities to
become a powerfull MicroPython library

## Installation

<!--
The current implementation does only run on a board with external SPI RAM. As
of now up to 300kB of RAM are required. This is more than an ESP32-D4 Pico
provides by default.

`esp32spiram-20220117-v1.18.bin` is used as MicroPython firmware
-->

### Install required tools

Python3 must be installed on your system. Check the current Python version
with the following command

```bash
python --version
python3 --version
```

Depending on which command `Python 3.x.y` (with x.y as some numbers) is
returned, use that command to proceed.

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Setup

### Install package with pip

Connect to a network

```python
import network
station = network.WLAN(network.STA_IF)
station.connect('SSID', 'PASSWORD')
station.isconnected()
```

and install this lib on the MicroPython device like this

```python
import upip
upip.install('micropython-modbus')
```

### Manually

#### Upload files to board

Copy the module to the MicroPython board and import them as shown below
using [Remote MicroPython shell][ref-remote-upy-shell]

Open the remote shell with the following command. Additionally use `-b 115200`
in case no CP210x is used but a CH34x.

```bash
rshell -p /dev/tty.SLAB_USBtoUART --editor nano
```

Perform the following command to copy all files and folders to the device

```bash
mkdir /pyboard/lib
mkdir /pyboard/lib/umodbus
mkdir /pyboard/registers

cp registers/modbusRegisters-MyEVSE.json /pyboard/registers/
cp umodbus/* /pyboard/lib/umodbus

cp main.py /pyboard
cp boot.py /pyboard
```

### Install additional MicroPython packages

To use this package with the provided [`boot.py`](boot.py) and
[`main.py`](main.py) file, additional modules are required, which are not part
of this repo/package. To install these modules on the device, connect to a
network and install them via `upip` as follows

```python
import upip
upip.install('micropython-brainelectronics-helper')
```

or check the README of the
[brainelectronics MicroPython modules][ref-github-be-mircopython-modules]

## Usage

Start a REPL (may perform a soft reboot), wait for network connection and
start performing Modbus requests to the device.

For further details about a TCP-RTU bridge implementation check the header
comment of [`main.py`](main.py).

### Master implementation

Act as host, get Modbus data via RTU or TCP from a client device

```python
# RTU Master setup
# act as host, get Modbus data via RTU from a client device
rtu_pins = (25, 26)         # (TX, RX)
slave_addr = 10             # bus address of client
host = ModbusRTUMaster(
    baudrate=9600,          # optional, default 9600
    data_bits=8,            # optional, default 7
    stop_bits=1,            # optional, default 1
    parity=None,            # optional, default None
    pins=rtu_pins)

# TCP Master setup
# act as host, get Modbus data via TCP from a client device
host = ModbusTCPMaster(
    slave_ip=192.168.178.34,
    slave_port=180,
    timeout=5)              # optional, default 5

# READ COILS
coil_address = 123
coil_status = host.read_coils(
    slave_addr=slave_addr,
    starting_addr=123,
    coil_qty=1)
print('Status of coil {}: {}'.format(coil_status, coil_address))

# WRITE COILS
new_coil_val = 0
operation_status = host.write_single_coil(
    slave_addr=slave_addr,
    output_address=coil_address,
    output_value=new_coil_val)
print('Result of setting coil {} to {}'.format(coil_address, operation_status))

# READ HREGS
hreg_address = 93
register_value = host.read_holding_registers(
    slave_addr=slave_addr,
    starting_addr=hreg_address,
    register_qty=1,
    signed=False)
print('Status of hreg {}: {}'.format(hreg_address, register_value))

# WRITE HREGS
new_hreg_val = 44
operation_status = self.host.write_single_register(
                    slave_addr=slave_addr,
                    register_address=hreg_address,
                    register_value=new_hreg_val,
                    signed=False)
print('Result of setting hreg {} to {}'.format(hreg_address, operation_status))

# READ ISTS
ist_address = 67
input_status = self.host.read_discrete_inputs(
    slave_addr=slave_addr,
    starting_addr=ist_address,
    input_qty=1)
print('Status of ist {}: {}'.format(ist_address, input_status))

# READ IREGS
ireg_address = 10
register_value = self.host.read_input_registers(
                    slave_addr=slave_addr,
                    starting_addr=ireg_address,
                    register_qty=2,
                    signed=False)
print('Status of ireg {}: {}'.format(ireg_address, register_value))
```

### Slave implementation

Act as client, provide Modbus data via RTU or TCP to a host device

```python
# RTU Slave setup
# act as client, provide Modbus data via RTU to a host device
rtu_pins = (25, 26)         # (TX, RX)
slave_addr = 10             # address on bus as client
client = ModbusRTU(
    addr=slave_addr,        # address on bus
    baudrate=9600,          # optional, default 9600
    data_bits=8,            # optional, default 7
    stop_bits=stop_bits,    # optional, default 1
    parity=parity,          # optional, default None
    pins=rtu_pins)

# TCP Slave setup
# act as client, provide Modbus data via TCP to a host device
local_ip = '192.168.4.1'    # IP address
tcp_port = 502              # port to listen to

"""
# to get from MicroPython core functions use this
import network
station = network.WLAN(network.STA_IF)
if station.active():
    if station.isconnected():
        local_ip = station.ifconfig()[0]
"""

client = ModbusTCP()
is_bound = False

# check whether client has been bound to an IP and port
is_bound = client.get_bound_status()

if not is_bound:
    client.bind(local_ip=local_ip, local_port=tcp_port)

# commond slave register setup, to be used with the Master example above
register_definitions = {
    "COILS": {
        "EXAMPLE_COIL": {
            "register": 123,
            "len": 1,
        }
    },
    "HREGS": {
        "EXAMPLE_HREG": {
            "register": 93,
            "len": 1,
        }
    },
    "ISTS": {
        "EXAMPLE_ISTS": {
            "register": 67,
            "len": 1,
        }
    },
    "IREGS": {
        "EXAMPLE_IREG": {
            "register": 10,
            "len": 2,
        }
    }
}

"""
# alternatively the register definitions can also be loaded from a JSON file
import json

with open('registers/modbusRegisters-MyEVSE.json', 'r') as file:
    register_definitions = json.load(file)
"""

client.setup_registers(registers=register_definitions, use_default_vals=True)
```

### Register configuration

The available registers are defined by a JSON file, placed inside the
`/pyboard/registers` folder on the board and selected in [`main.py`](main.py).

As an [example the registers](registers/modbusRegisters-MyEVSE.json) of a
[brainelectronics MyEVSE][ref-myevse-be], [MyEVSE on Tindie][ref-myevse-tindie]
board is provided with this repo.

## Supported Modbus functions

Refer to the following table for the list of supported Modbus functions.

| ID | Description |
|----|-------------|
| 1  | Read coils |
| 2  | Read discrete inputs |
| 3  | Read holding registers |
| 4  | Read input registers |
| 5  | Write single coil |
| 6  | Write single register |
| 15 | Write multiple coils |
| 16 | Write multiple registers |

## Credits

Big thank you to [giampiero7][ref-giampiero7] for the initial implementation
of this library.

* **sfera-labs** - *Initial work* - [giampiero7][ref-sferalabs-exo-sense]
* **pycom** - *Initial Modbus work* - [pycom-modbus][ref-pycom-modbus]

<!-- Links -->
[ref-sferalabs-exo-sense]: https://github.com/sfera-labs/exo-sense-py-modbus
[ref-pycom-modbus]: https://github.com/pycom/pycom-modbus
[ref-remote-upy-shell]: https://github.com/dhylands/rshell
[ref-github-be-mircopython-modules]: https://github.com/brainelectronics/micropython-modules
[ref-myevse-be]: https://brainelectronics.de/
[ref-myevse-tindie]: https://www.tindie.com/stores/brainelectronics/
[ref-giampiero7]: https://github.com/giampiero7
