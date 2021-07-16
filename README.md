# Micropython Modbus library

Forked from [Exo Sense Py](https://github.com/sfera-labs/exo-sense-py-modbus),
based on [PyCom Modbus](https://github.com/pycom/pycom-modbus) and extended
with other functionalities to become a powerfull micropython library

---------------

## Installation

### Change network settings

The network settings are defined in the [config_network.py](config_network.py)
file. It is possible to use a single network, trying to connect to different
networks or creating an AccessPoint.

### Copy files

Copy all python files (plus index.html) in this repo to the device.

#### ampy

*ampy has several drawbacks compared to rshell, consider using rshell*

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install adafruit-ampy
```

Place a file named `.ampy` in the local directory, as proposed on the
[ampy README](https://github.com/scientifichackers/ampy)

```bash
nano .ampy
```

```
# Please fill in your own port, baud rate, and delay
AMPY_PORT=/dev/cu.wchusbserial1410

AMPY_BAUD=115200

# Fix for macOS users' "Could not enter raw repl"; try 2.0 and lower from there:
AMPY_DELAY=0.5
```

Perform the following command to copy all files and folders to the device

```bash
ampy mkdir lib
ampy mkdir lib/uModbus

ampy put lib/uModbus/*.py lib/uModbus

ampy put boot.py
ampy put config.py
ampy put config_network.py
ampy put index.html
ampy put main.py
ampy put modbus.py
ampy put time_helper.py
ampy put webserver.py
ampy put wifi_helper.py
```

#### rshell

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install rshell
```

Open the remote shell with the following command

```bash
rshell -p /dev/tty.wchusbserial1410 -b 115200 --editor nano
```

Perform the following command to copy all files and folders to the device
```bash
mkdir /pyboard/lib
mkdir /pyboard/lib/uModbus

cp lib/uModbus/* /pyboard/lib/uModbus
cp *.py /pyboard
cp index.html /pyboard
```

<!--
#### uPIP

Connect to the device, setup the WiFi connection as recommended and install
this package with the following two lines

```python
# WiFi connection must be established before of course
import upip
upip.install('micropython-modbus')
```
-->

## Usage

Start a REPL (may perform a soft reboot), wait for network connection and
start performing Modbus requests to the device

### Device configuration

All configuration parameters are in the [config.py](config.py) file.

To access this file on the module join its WiFi network or AccessPoint. A Web
server will be enabled by default. Use a Web browser to connect to
[`192.168.4.1`](http://192.168.4.1/) using the credentials specified in the
[config.py](config.py) configuration file.

Refer to [config_network.py](config_network.py) for the default WiFi and
AccessPoint credentials.

Download the configuration file, edit it and re-upload it. If using the Web
interface, after the upload, the device will automatically restart using the
new configuration, otherwise, on the next power-on, it will start with the new
configuration.

### Register configuration

The available registers are defined by a JSON file, which can be up/downloaded
from the device by a simple and lightweight webserver.

Configure it to work as Modbus RTU slave **or** Modbus TCP server, by setting
`MB_RTU_ADDRESS` **or** `MB_TCP_IP` to a valid value. If both are set, the TCP
configuration will be ignored. If neither are, it will boot as
*not configured* and endup in the REPL.

When configured as Modbus TCP server, the configuration Web interface will be
available at the configured IP address.

## Modbus functions

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
