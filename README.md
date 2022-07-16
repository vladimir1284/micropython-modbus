# MicroPython Modbus library

[![Downloads](https://pepy.tech/badge/micropython-modbus)](https://pepy.tech/project/micropython-modbus)
![Release](https://img.shields.io/github/v/release/brainelectronics/micropython-modbus?include_prereleases&color=success)
![MicroPython](https://img.shields.io/badge/micropython-Ok-green.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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
# import modbus host classes
from umodbus.tcp import TCP as ModbusTCPMaster
from umodbus.serial import Serial as ModbusRTUMaster

# RTU Master setup
# act as host, get Modbus data via RTU from a client device
# ModbusRTUMaster can make serial requests to a client device to get/set data
rtu_pins = (25, 26)         # (TX, RX)
slave_addr = 10             # bus address of client
host = ModbusRTUMaster(
    baudrate=9600,          # optional, default 9600
    data_bits=8,            # optional, default 8
    stop_bits=1,            # optional, default 1
    parity=None,            # optional, default None
    pins=rtu_pins)

# TCP Master setup
# act as host, get Modbus data via TCP from a client device
# ModbusTCPMaster can make TCP requests to a client device to get/set data
host = ModbusTCPMaster(
    slave_ip=192.168.178.34,
    slave_port=180,
    timeout=5)              # optional, default 5

# READ COILS
coil_address = 123
coil_status = host.read_coils(
    slave_addr=slave_addr,
    starting_addr=coil_address,
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
operation_status = host.write_single_register(
                    slave_addr=slave_addr,
                    register_address=hreg_address,
                    register_value=new_hreg_val,
                    signed=False)
print('Result of setting hreg {} to {}'.format(hreg_address, operation_status))

# READ ISTS
ist_address = 67
input_status = host.read_discrete_inputs(
    slave_addr=slave_addr,
    starting_addr=ist_address,
    input_qty=1)
print('Status of ist {}: {}'.format(ist_address, input_status))

# READ IREGS
ireg_address = 10
register_value = host.read_input_registers(
                    slave_addr=slave_addr,
                    starting_addr=ireg_address,
                    register_qty=2,
                    signed=False)
print('Status of ireg {}: {}'.format(ireg_address, register_value))
```

### Slave implementation

Act as client, provide Modbus data via RTU or TCP to a host device.

See [Modbus TCP Client example](examples/tcp_client_example.py) and
[Modbus RTU Client example](examples/rtu_client_example.py)

Both examples are using [example register definitions](examples/example.json)

Use the provided example scripts [read RTU](examples/read_registers_rtu.sh) or
[read TCP](examples/read_registers_tcp.sh) to read the data from the devices.
This requires the [modules submodule][ref-github-be-python-modules] to be
cloned as well and the required packages being installed as described in the
modules README file.

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
[ref-github-be-python-modules]: https://github.com/brainelectronics/python-modules
[ref-myevse-be]: https://brainelectronics.de/
[ref-myevse-tindie]: https://www.tindie.com/stores/brainelectronics/
[ref-giampiero7]: https://github.com/giampiero7
