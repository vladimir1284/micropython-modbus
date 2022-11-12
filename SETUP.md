# Setup

Setup the development environment and the MicroPython board

---------------

<!-- MarkdownTOC -->

- [Development environment](#development-environment)
	- [Update submodule](#update-submodule)
	- [Install required tools](#install-required-tools)
- [MicroPython](#micropython)
	- [Flash firmware](#flash-firmware)
	- [Install package with pip](#install-package-with-pip)
	- [Without network connection](#without-network-connection)

<!-- /MarkdownTOC -->

## Development environment

This section describes the necessary steps on the computer to get ready to
test and run the examples.

### Update submodule

[brainelectronics python modules submodule][ref-github-be-python-modules] have
to be cloned as well. A standard clone command won't clone the submodule.

```bash
git submodule update --init --recursive
cd modules
git fetch

# maybe checkout a newer version with the following command
git checkout x.y.z

# or use the latest develop branch
git checkout develop
git pull
```

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
pip install -r modules/requirements.txt
```

## MicroPython

This section describes the necessary steps on the MicroPython device to get
ready to test and run the examples.

### Flash firmware

Flash the [MicroPython firmware][ref-upy-firmware-download] to the MicroPython
board with this call

```bash
esptool.py --chip esp32 --port /dev/tty.SLAB_USBtoUART erase_flash
esptool.py --chip esp32 --port /dev/tty.SLAB_USBtoUART --baud 921600 write_flash -z 0x1000 esp32spiram-20220117-v1.18.bin
```

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

### Without network connection

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

cp umodbus/* /pyboard/lib/umodbus
```

<!-- Links -->
[ref-github-be-python-modules]: https://github.com/brainelectronics/python-modules
[ref-upy-firmware-download]: https://micropython.org/download/
[ref-remote-upy-shell]: https://github.com/dhylands/rshell
