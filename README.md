# Micropython Modbus library

Forked from [Exo Sense Py][ref-sferalabs-exo-sense], based on
[PyCom Modbus][ref-pycom-modbus] and extended with other functionalities to
become a powerfull micropython library

---------------

## Installation

The current implementation does only run on a board with external SPI RAM. As
of now up to 300kB of RAM are required. This is more than an ESP32-D4 Pico
provides by default.

`esp32spiram-20220117-v1.18.bin` is used as MicroPython firmware

This repo contains submodules (even sub-submodules), sorry for that.
Perform the following steps to clone and update everything to gain the best
usage experience:

```bash
# clone this repo with all submodules
git clone --recurse-submodules https://github.com/brainelectronics/micropython-modbus.git

# init and update all submodules
git submodules update --init --recursive

# enter micropython helper modules submodule
cd helpers
# check available tags
git tag --list
# checkout the latest non breaking tag, choose manually
git checkout x.y.z
# return to root of repo
cd ..

# enter python modules submodule
cd modules
# check available tags
git tag --list
# checkout the latest non breaking tag, choose manually
git checkout x.y.z
# return to root of repo
cd ..

# enter WiFi Manager submodule
cd wifi-manager
# check available tags
git tag --list
# checkout the latest non breaking tag, choose manually
git checkout x.y.z
# return to root of repo
cd ..
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
```

### Copy files

For interaction with the filesystem of the device the
[Remote MicroPython shell][ref-remote-upy-shell] can be used.

Open the remote shell with the following command. Additionally use `-b 115200`
in case no CP210x is used but a CH34x.

```bash
rshell -p /dev/tty.SLAB_USBtoUART --editor nano
```

Perform the following command to copy all files and folders to the device

```bash
mkdir /pyboard/helpers
mkdir /pyboard/lib
mkdir /pyboard/primitives
mkdir /pyboard/registers
mkdir /pyboard/static/
mkdir /pyboard/templates

cp helpers/*.py /pyboard/helpers
cp -r lib/* /pyboard/lib/
cp -r wifi-manager/lib/* /pyboard/lib
cp wifi-manager/primitives/*.py /pyboard/primitives
cp registers/modbusRegisters-MyEVSE.json /pyboard/register/
cp wifi-manager/simulation/static/css/*.gz /pyboard/static/
cp wifi-manager/templates/* /pyboard/templates

cp wifi-manager/wifi_manager.py /pyboard
cp modbus.py /pyboard
cp main.py /pyboard
cp boot.py /pyboard
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

[Micropython lib README](https://github.com/micropython/micropython-lib/blob/3c383f6d2864a4b39bbe4ceb2ae8f29b519c9afe/README.md)

    For example, to add collections.defaultdict, copy collections/collections/__init__.py and collections.defaultdict/collections/defaultdict.py to a directory named lib/collections on your device.

[Micropython PyPI packaging guidelines](https://github.com/micropython/micropython/issues/413)
-->

## Usage

Start a REPL (may perform a soft reboot), wait for network connection and
start performing Modbus requests to the device.

For further details check the header comment of [`main.py`](main.py).

<!--
### Device configuration

All configuration parameters are in the [config.py](config/config.py) file.

To access this file on the module join its WiFi network or AccessPoint. A Web
server will be enabled by default. Use a Web browser to connect to
[`192.168.4.1`](http://192.168.4.1/) using the credentials specified in the
[config.py](config/config.py) configuration file.

Refer to [config_network.py](config/config_network.py) for the default WiFi and
AccessPoint credentials.

Download the configuration file, edit it and re-upload it. If using the Web
interface, after the upload, the device will automatically restart using the
new configuration, otherwise, on the next power-on, it will start with the new
configuration.
-->

### Register configuration

The available registers are defined by a JSON file, placed inside the
`/pyboard/registers` folder on the board and selected in [`main.py`](main.py).

As an [example the registers](registers/modbusRegisters-MyEVSE.json) of a
[Brainelectronics MyEVSE][ref-myevse-be], [MyEVSE on Tindie][ref-myevse-tindie]
board is provided with this repo.

<!--
Configure it to work as Modbus RTU slave **or** Modbus TCP server, by setting
`MB_RTU_ADDRESS` **or** `MB_TCP_IP` to a valid value. If both are set, the TCP
configuration will be ignored. If neither are, it will boot as
*not configured* and endup in the REPL.

When configured as Modbus TCP server, the configuration Web interface will be
available at the configured IP address.
-->

<!--
## Available webpages

| URL | Description |
|-----|-------------|
| / | Config page of device |
| /config | Config JSON of Modbus RTU/TCP |
| /config-network | Config JSON of network |
-->

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

<!-- Links -->
[ref-sferalabs-exo-sense]: https://github.com/sfera-labs/exo-sense-py-modbus
[ref-pycom-modbus]: https://github.com/pycom/pycom-modbus
[ref-remote-upy-shell]: https://github.com/dhylands/rshell
[ref-myevse-be]: https://brainelectronics.de/
[ref-myevse-tindie]: https://www.tindie.com/stores/brainelectronics/
