# MicroPython Modbus library

[![Downloads](https://pepy.tech/badge/micropython-modbus)](https://pepy.tech/project/micropython-modbus)
![Release](https://img.shields.io/github/v/release/brainelectronics/micropython-modbus?include_prereleases&color=success)
![MicroPython](https://img.shields.io/badge/micropython-Ok-green.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/brainelectronics/micropython-modbus/actions/workflows/release.yml/badge.svg)](https://github.com/brainelectronics/micropython-modbus/actions/workflows/release.yml)
[![Test Python package](https://github.com/brainelectronics/micropython-modbus/actions/workflows/test.yml/badge.svg)](https://github.com/brainelectronics/micropython-modbus/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/micropython-modbus/badge/?version=latest)](https://micropython-modbus.readthedocs.io/en/latest/?badge=latest)

MicroPython ModBus TCP and RTU library supporting client and host mode

---------------

## General

Forked from [Exo Sense Py][ref-sferalabs-exo-sense], based on
[PyCom Modbus][ref-pycom-modbus] and extended with other functionalities to
become a powerfull MicroPython library

The latest documentation is available at
[MicroPython Modbus ReadTheDocs][ref-rtd-micropython-modbus]

<!-- MarkdownTOC -->

- [Quickstart](#quickstart)
    - [Install package on board with pip](#install-package-on-board-with-pip)
    - [Request coil status](#request-coil-status)
        - [TCP](#tcp)
        - [RTU](#rtu)
    - [Install additional MicroPython packages](#install-additional-micropython-packages)
- [Usage](#usage)
- [Supported Modbus functions](#supported-modbus-functions)
- [Credits](#credits)

<!-- /MarkdownTOC -->

## Quickstart

This is a quickstart to install the `micropython-modbus` library on a
MicroPython board.

A more detailed guide of the development environment can be found in
[SETUP](SETUP.md). Further details about the usage can be found in
[USAGE](USAGE.md)

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install 'rshell>=0.0.30,<1.0.0'
```

### Install package on board with pip

```bash
rshell -p /dev/tty.SLAB_USBtoUART --editor nano
```

Inside the [rshell][ref-remote-upy-shell] open a REPL and execute these
commands inside the REPL

```python
import machine
import network
import time
import upip
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect('SSID', 'PASSWORD')
time.sleep(1)
print('Device connected to network: {}'.format(station.isconnected()))
upip.install('micropython-modbus')
print('Installation completed')
machine.soft_reset()
```

### Request coil status

After a successful installation of the package and reboot of the system as
described in the [installation section](#install-package-on-board-with-pip)
the following commands can be used to request a coil state of a target/client
device. Further usage examples can be found in the
[examples folder][ref-examples-folder] and in the
[Micropython section of USAGE](USAGE.md)

#### TCP

```python
from ummodbus.tcp import ModbusTCPMaster

tcp_device = ModbusTCPMaster(
    slave_ip='172.24.0.2',  # IP address of the target/client/slave device
    slave_port=502,         # TCP port of the target/client/slave device
    # timeout=5.0           # optional, timeout in seconds, default 5.0
)

# address of the target/client/slave device on the bus
slave_addr = 10
coil_address = 123
coil_qty = 1

coil_status = host.read_coils(
    slave_addr=slave_addr,
    starting_addr=coil_address,
    coil_qty=coil_qty)
print('Status of coil {}: {}'.format(coil_status, coil_address))
```

#### RTU

```python
from umodbus.serial import ModbusRTU

host = ModbusRTU(
    addr=1,             # address of this Master/Host on bus
    # baudrate=9600,    # optional, default 9600
    # data_bits=8,      # optional, default 8
    # stop_bits=1,      # optional, default 1
    # parity=None,      # optional, default None
    pins=(25, 26)       # (TX, RX)
)

# address of the target/client/slave device on the bus
slave_addr = 10
coil_address = 123
coil_qty = 1

coil_status = host.read_coils(
    slave_addr=slave_addr,
    starting_addr=coil_address,
    coil_qty=coil_qty)
print('Status of coil {}: {}'.format(coil_status, coil_address))
```

### Install additional MicroPython packages

To use this package with the provided [`boot.py`][ref-package-boot-file] and
[`main.py`][ref-package-boot-file] file, additional modules are required,
which are not part of this repo/package. To install these modules on the
device, connect to a network and install them via `upip` as follows

```python
import upip
upip.install('micropython-brainelectronics-helpers')
```

Check also the README of the
[brainelectronics MicroPython modules][ref-github-be-mircopython-modules]
and the [SETUP guide](SETUP.md)

## Usage

See [USAGE](USAGE.md)

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
* **pfalcon** - *Initial MicroPython unittest module* - [micropython-unittest][ref-pfalcon-unittest]

<!-- Links -->
[ref-sferalabs-exo-sense]: https://github.com/sfera-labs/exo-sense-py-modbus
[ref-pycom-modbus]: https://github.com/pycom/pycom-modbus
[ref-rtd-micropython-modbus]: https://micropython-modbus.readthedocs.io/en/latest/
[ref-remote-upy-shell]: https://github.com/dhylands/rshell
[ref-examples-folder]: https://github.com/brainelectronics/micropython-modbus/tree/develop/examples
[ref-package-boot-file]: https://github.com/brainelectronics/micropython-modbus/blob/c45d6cc334b4adf0e0ffd9152c8f08724e1902d9/boot.py
[ref-package-main-file]: https://github.com/brainelectronics/micropython-modbus/blob/c45d6cc334b4adf0e0ffd9152c8f08724e1902d9/main.py
[ref-github-be-mircopython-modules]: https://github.com/brainelectronics/micropython-modules
[ref-giampiero7]: https://github.com/giampiero7
[ref-pfalcon-unittest]: https://github.com/pfalcon/pycopy-lib/blob/56ebf2110f3caa63a3785d439ce49b11e13c75c0/unittest/unittest.py
