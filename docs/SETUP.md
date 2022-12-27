# Setup

Setup the development environment and the MicroPython board

---------------

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
board with this call in case a ESP32 is used.

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

and install this lib with all its dependencies on the MicroPython device like
this

```python
import upip
upip.install('micropython-modbus')
```

### Without network connection

Copy all files of the [umodbus module][ref-umodbus-module] to the MicroPython
board using [Remote MicroPython shell][ref-remote-upy-shell]

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

### Additional MicroPython packages for examples

To use this package with the provided [`boot.py`][ref-package-boot-file] and
[`main.py`][ref-package-boot-file] file, additional modules are required,
which are not part of this repo/package.

```bash
rshell -p /dev/tty.SLAB_USBtoUART --editor nano
```

#### Install additional package with pip

Again connect to a network and install the additional package on the
MicroPython device with

```python
import upip
upip.install('micropython-modbus')
```

#### Without network connection

To install the additional modules on the device, download the
[brainelectronics MicroPython Helpers repo][ref-github-be-mircopython-modules]
and copy them to the device.

Perform the following command to copy all files and folders to the device

```bash
mkdir /pyboard/lib/be_helpers

cp be_helpers/* /pyboard/lib/be_helpers
```

Additionally check the latest instructions of the
[brainelectronics MicroPython modules][ref-github-be-mircopython-modules]
README for further instructions.

<!-- Links -->
[ref-github-be-python-modules]: https://github.com/brainelectronics/python-modules
[ref-upy-firmware-download]: https://micropython.org/download/
[ref-remote-upy-shell]: https://github.com/dhylands/rshell
[ref-umodbus-module]: https://github.com/brainelectronics/micropython-modbus/tree/develop/umodbus
[ref-package-boot-file]: https://github.com/brainelectronics/micropython-modbus/blob/c45d6cc334b4adf0e0ffd9152c8f08724e1902d9/boot.py
[ref-package-main-file]: https://github.com/brainelectronics/micropython-modbus/blob/c45d6cc334b4adf0e0ffd9152c8f08724e1902d9/main.py
[ref-github-be-mircopython-modules]: https://github.com/brainelectronics/micropython-modules
