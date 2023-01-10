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
board. The following example call is valid for ESP32 boards.

```bash
esptool.py --chip esp32 --port /dev/tty.SLAB_USBtoUART erase_flash
esptool.py --chip esp32 --port /dev/tty.SLAB_USBtoUART --baud 921600 write_flash -z 0x1000 esp32spiram-20220117-v1.18.bin
```

<!-- Links -->
[ref-github-be-python-modules]: https://github.com/brainelectronics/python-modules
[ref-upy-firmware-download]: https://micropython.org/download/
