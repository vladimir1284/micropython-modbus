# Usage

Overview to use and test this `micropython-modbus` library

---------------

The onwards described steps assume a successful setup as described in
[SETUP.md](SETUP.md)

## MicroPython

This section describes the necessary steps on the MicroPython device to get
ready to test and run the examples.

```bash
# Linux/Mac
source .venv/bin/activate

rshell -p /dev/tty.SLAB_USBtoUART --editor nano
```

On a Windows based system activate the virtual environment and enter the
remote shell like this

```
.venv\Scripts\activate.bat

rshell -p COM9
```

The onwards mentioned commands shall be performed inside the previously entered
remote shell.

### Register configuration

The available registers can be defined by a JSON file, placed inside the
`/pyboard/registers` folder or any other location on the board and loaded in
`main.py` or by defining a dictionary.

As an [example the registers][ref-registers-MyEVSE] of a
[brainelectronics MyEVSE][ref-myevse-be], [MyEVSE on Tindie][ref-myevse-tindie]
board and others are provided with this repo.

#### Structure

If only an interaction with a single register is intended no dictionary needs
to be defined of course. The onwards explanations assume a bigger setup of
registers on the same target/client/slave device.

The JSON file/dictionary shall follow the following pattern/structure

```python
{
    "COILS": {          # this key shall contain all coils
        "COIL_NAME": {  # custom name of a coil
            "register": 42,     # register address of the coil
            "len": 1,           # amount of registers to request aka quantity
            "val": 0,           # used to set a register
            # the onwards mentioned keys are optional
            "description": "Optional description of the coil",
            "range": "[0, 1]",  # may provide a range of the value, only for documentation purpose
            "unit": "BOOL"      # may provide a unit of the value, only for documentation purpose
        }
    },
    "HREGS": {          # this key shall contain all holding registers
        "HREG_NAME": {  # custom name of a holding register
            "register": 93,     # register address of the holding register
            "len": 1,           # amount of registers to request aka quantity
            "val": 19,          # used to set a register
            "description": "Optional description of the holding register",
            "range": "[0, 65535]",
            "unit": "Hz"
        },
    },
    "ISTS": {           # this key shall contain all static input registers
        "ISTS_NAME": {  # custom name of a static input register
            "register": 67,     # register address of the static input register
            "len": 1,           # amount of registers to request aka quantity
            "val": 0,           # used to set a register, not possible for ISTS
            "description": "Optional description of the static input register",
            "range": "[0, 1]",
            "unit": "activated"
        }
    },
    "IREGS": {          # this key shall contain all input registers
        "IREG_NAME": {  # custom name of an input register
            "register": 10,     # register address of the input register
            "len": 1,           # amount of registers to request aka quantity
            "val": 60001,       # used to set a register, not possible for IREGS
            "description": "Optional description of the static input register",
            "range": "[0, 65535]",
            "unit": "millivolt"
        }
    }
}
```

If not all register types are used they can be of course removed from the
JSON file/dictionary. The smallest possible definition for reading a coil
would look like

```python
{
    "COILS": {          # this key shall contain all coils
        "COIL_NAME": {  # custom name of a coil
            "register": 42,     # register address of the coil
            "len": 1            # amount of registers to request aka quantity
        }
    }
}
```

In order to act as client/slave device the same structure can be used. If no
`val` element is found in the structure the default values are

| Type | Function Code | Default value |
| ---- | ------------- | ------------- |
| COILS | 0x01 | False (0x0) |
| ISTS | 0x02 | False (0x0) |
| HREGS | 0x03 | 0 |
| IREGS | 0x04 | 0 |

The value of multiple registers can be set like this

```python
{
    "HREGS": {          # this key shall contain all holding registers
        "HREG_NAME": {  # custom name of a holding register
            "register": 93,     # register address of the holding register
            "len": 3,           # amount of registers to request aka quantity
            "val": [29, 38, 0]  # used to set a register
        }
    }
}
```

> :warning: As of version 2.0.0 of this package it is not possible to request
only the holding register 94, which would hold `38` in the above example.
This is a bug (non implemented feature) of the client/slave implementation.
For further details check [#35](https://github.com/brainelectronics/micropython-modbus/issues/35)

#### Detailed key explanation

The onwards described key explanations are valid for COIL, HREG, IST and IREG

##### Register

The key `register` defines the register to request or manipulate.

According to the Modbus specification the register address has to be in the
range of 0x0000 to 0xFFFF (65535) to be valid.

##### Length

The key `len` defines the amout of registers to be requested starting from/with
the defined `register` address.

According to the Modbus specification the length or amount depends on the type
of the register as summarized in the table below.

| Type | Function Code | Valid range |
| ---- | ------------- | ----------- |
| COILS | 0x01 | 0x1 to 0x7D0 (2000) |
| ISTS | 0x02 | 0x1 to 0x7D0 (2000) |
| HREGS | 0x03 | 0x1 to 0x7D (125) |
| IREGS | 0x04 | 0x1 to 0x7D (125) |

In order to read 5 coils starting at 124 use the following dictionary aka
config

```python
{
    "COILS": {          # this key shall contain all coils
        "COIL_NAME": {  # custom name of a coil
            "register": 124,    # register address of the coil
            "len": 5            # amount of registers to request aka quantity
        }
    }
}
```

The output will be a list of 5 elements like `[True, False, False, True, True]`
depending on the actual device coil states of course.



##### Value

The key `val` defines the value of registers to be set on the target/client
device.

According to the Modbus specification the value (range) depends on the type
of the register as summarized in the table below.

| Type | Function Code | Valid value | Comment |
| ---- | ------------- | ----------- | ------- |
| COILS | 0x05 | 0x0000 or 0xFF00 | This package maps `0` or `False` to `0x0000` and `1` or `True` to `0xFF00` |
| HREGS | 0x06 | 0x0000 to 0xFFFF (65535) |  |

##### Optional description

The optional key `description` can be used to provide an additional
description of the register. This might be helpful if the register name is not
meaninful enough or for any other reason of course.

##### Optional range

The optional key `range` can be used to indicate the possible value range of
this specific target. For example a holding register for setting a PWM output
might only support a range of 0 to 100. This might be especially helpful with
the optional [`unit`](#optional-unit) key.

###### Optional unit

The optional key `unit` can be used to provide further details about the unit
of the register. In case of the PWM output register example of the
[optional range key](#optional-range) the recommended value for this key could
be `percent`.

### TCP

Get two network capable boards up and running, collecting and setting data on
each other.

Adjust the WiFi network name (SSID) and password to be able to connect to your
personal network or remove that section if a wired network connection is used.

#### Client

The client, former known as slave, provides some dummy registers which can be
read and updated by another device.

```bash
cp examples/tcp_client_example.py /pyboard/main.py
cp examples/boot.py /pyboard/boot.py
repl
```

Inside the REPL press CTRL+D to perform a soft reboot. The device will serve
several registers now. The log output might look similar to this

```
MPY: soft reboot
System booted successfully!
Waiting for WiFi connection...
Waiting for WiFi connection...
Connected to WiFi.
('192.168.178.69', '255.255.255.0', '192.168.178.1', '192.168.178.1')
Setting up registers ...
Register setup done
Serving as TCP client on 192.168.178.69:502
```

#### Host

The host, former known as master, requests and updates some dummy registers of
another device.

```bash
cp examples/tcp_host_example.py /pyboard/main.py
cp examples/boot.py /pyboard/boot.py
repl
```

Inside the REPL press CTRL+D to perform a soft reboot. The device will request
and update registers of the Client after a few seconds. The log output might
look similar to this

```
MPY: soft reboot
System booted successfully!
Waiting for WiFi connection...
Waiting for WiFi connection...
Connected to WiFi.
('192.168.178.42', '255.255.255.0', '192.168.178.1', '192.168.178.1')
Requesting and updating data on TCP client at 192.168.178.69:502

Status of COIL 123: [True, False, False, False, False, False, False, False]
Result of setting COIL 123: True
Status of COIL 123: [False, False, False, False, False, False, False, False]

Status of HREG 93: (44,)
Result of setting HREG 93: True
Status of HREG 93: (44,)

Status of IST 67: [False, False, False, False, False, False, False, False]
Status of IREG 10: (60001,)

Finished requesting/setting data on client
MicroPython v1.18 on 2022-01-17; ESP32 module (spiram) with ESP32
Type "help()" for more information.
>>>
```

<!--
### RTU

Get two UART/RS485 capable boards up and running, collecting and setting data
on each other.
-->

### TCP-RTU bridge

This example implementation shows how to act as bridge between an RTU (serial)
connected device and another external TCP device.

For further details about a TCP-RTU bridge implementation check the header
comment of [`main.py`][ref-package-main-file].

## Classic development environment

This section describes the necessary steps on the computer to get ready to
test and run the examples.

```bash
# Linux/Mac
source .venv/bin/activate
```

On a Windows based system activate the virtual environment like this

```
.venv\Scripts\activate.bat
```

The onwards mentioned commands shall be performed inside the previously
activated virtual environment.

### TCP

Read and write the Modbus register data from a MicroPython device with the
[brainelectronics ModbusWrapper][ref-github-be-modbus-wrapper] provided with
the [modules submodule][ref-modules-folder]

#### Read data

```bash
python modules/read_device_info_registers.py \
--file=registers/example.json \
--connection=tcp \
--address=192.168.178.69 \
--port=502 \
--print \
--pretty \
--debug \
--verbose=3
```

Or use the even more convenient wrapper script for the wrapper.

```bash
cd examples
sh read_registers_tcp.sh 192.168.178.69 ../registers/example.json 502
```

#### Write data

```bash
python modules/write_device_info_registers.py \
--file=registers/set-example.json \
--connection=tcp \
--address=192.168.178.69 \
--port=502 \
--print \
--pretty \
--debug \
--verbose=3
```

Or use the even more convenient wrapper script for the wrapper.

```bash
cd examples
sh write_registers_tcp.sh 192.168.178.69 ../registers/set-example.json 502
```

## Docker development environment

### Pull container

Checkout the available
[MicroPython containers](https://hub.docker.com/r/micropython/unix/tags)

```bash
docker pull micropython/unix:v1.18
```

### Spin up container

#### Simple container

Use this command for your first tests or to run some MicroPython commands in
a simple REPL

```bash
docker run -it \
--name micropython-1.18 \
--network=host \
--entrypoint bash \
micropython/unix:v1.18
```

#### Enter MicroPython REPL

Inside the container enter the REPL by running `micropython-dev`. The console
should now look similar to this

```
root@debian:/home#
MicroPython v1.18 on 2022-01-17; linux version
Use Ctrl-D to exit, Ctrl-E for paste mode
>>>
```

#### Manually run unittests

In order to manually execute only a specific set of tests use the following
command inside the container

```bash
# run all unittests defined in "tests" directory and exit with status result
micropython-dev -c "import unittest; unittest.main('tests')"

# run all tests of "TestAbsoluteTruth" defined in tests/test_absolute_truth.py
# and exit with status result
micropython-dev -c "import unittest; unittest.main(name='tests.test_absolute_truth', fromlist=['TestAbsoluteTruth'])"
```

#### Custom container for unittests

```bash
docker build \
--tag micropython-test \
--file Dockerfile.tests .
```

The unittests are executed during the building process. It will exit with a
non-zero status in case of a unittest failure.

The return value can be collected by `echo $?` (on Linux based systems), which
will be either `0` in case all tests passed, or `1` if one or multiple tests
failed.

#### Docker compose

The following command uses the setup defined in the `docker-compose.yaml` file
to act as two MicroPython devices communicating via TCP. The container
`micropython-host` defined by `Dockerfile.host` acts as host and sets/gets
data at/from the client as defined by `tcp_host_example.py`. On the other hand
the container `micropython-client` defined by `Dockerfile.client` acts as
client and provides data for the host as defined by `tcp_client_example.py`.
The port defined in `tcp_host_example.py` and `tcp_client_example.py` has to
be open and optionally exposed in the `docker-compose.yaml` file.

```bash
docker compose up --build --exit-code-from micropython-host
```

The option `--build` can be skipped on the second run, to avoid rebuilds of
the containers. All "dynamic" data is shared via `volumes`

##### Test for TCP example

```bash
docker compose -f docker-compose-tcp-test.yaml up --build --exit-code-from micropython-host
```

## Documentation

The documentation is automatically generated on every merge to the develop
branch and available [here][ref-rtd-micropython-modbus]

### Install required packages

```bash
# create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install and upgrade required packages
pip install -U -r docs/requirements.txt
```

### Create documentation

Some usefull checks have been disabled in the `docs/conf.py` file. Please
check the documentation build output locally before opening a PR.

```bash
# perform link checks
sphinx-build docs/ docs/build/linkcheck -d docs/build/docs_doctree/ --color -blinkcheck -j auto -W

# create documentation
sphinx-build docs/ docs/build/html/ -d docs/build/docs_doctree/ --color -bhtml -j auto -W
```

The created documentation can be found at [`docs/build/html`](docs/build/html).

<!-- Links -->
[ref-registers-MyEVSE]: https://github.com/brainelectronics/micropython-modbus/blob/c45d6cc334b4adf0e0ffd9152c8f08724e1902d9/registers/modbusRegisters-MyEVSE.json
[ref-myevse-be]: https://brainelectronics.de/
[ref-myevse-tindie]: https://www.tindie.com/stores/brainelectronics/
[ref-package-main-file]: https://github.com/brainelectronics/micropython-modbus/blob/c45d6cc334b4adf0e0ffd9152c8f08724e1902d9/main.py
[ref-github-be-modbus-wrapper]: https://github.com/brainelectronics/be-modbus-wrapper
[ref-modules-folder]: https://github.com/brainelectronics/python-modules/tree/43bad716b7db27db07c94c2d279cee57d0c8c753
[ref-rtd-micropython-modbus]: https://micropython-modbus.readthedocs.io/en/latest/
