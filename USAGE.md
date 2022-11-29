# Usage

Using and testing this `micropython-modbus` library

---------------

<!-- MarkdownTOC -->

- [Classic development environment](#classic-development-environment)
	- [TCP](#tcp)
		- [Read data](#read-data)
		- [Write data](#write-data)
- [Docker development environment](#docker-development-environment)
	- [Pull container](#pull-container)
	- [Spin up container](#spin-up-container)
		- [Simple container](#simple-container)
		- [Enter MicroPython REPL](#enter-micropython-repl)
		- [Custom container for unittests](#custom-container-for-unittests)
		- [Docker compose](#docker-compose)
	- [Run unittests](#run-unittests)
		- [Docker compose](#docker-compose-1)
- [MicroPython](#micropython)
	- [TCP](#tcp-1)
		- [Client](#client)
		- [Host](#host)
	- [RTU](#rtu)

<!-- /MarkdownTOC -->

The onwards described steps assume a successful setup as described in
[SETUP.md](SETUP.md)

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
the [modules submodule](modules)

#### Read data

```bash
python modules/read_device_info_registers.py \
--file=examples/example.json \
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
sh read_registers_tcp.sh 192.168.178.69 example.json 502
```

#### Write data

```bash
python modules/write_device_info_registers.py \
--file=examples/set-example.json \
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
sh write_registers_tcp.sh 192.168.178.69 set-example.json 502
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

Use this command for your first tests, or to run some MicroPython commands in
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

In order to manually execute only a specific set of tests use the following
command  inside the container

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
non-zero status on a unittest failure.

<!--
#### Docker compose

The following command uses the setup defined in the `docker-compose.yaml` file
to provide all required MicroPython packages and files within the container

```bash
# spin up container in deamon mode
docker compose up -d

# list all running containers
docker ps

# log into the micropython container afterwards
docker exec -it micropython bash

# finally stop the micropython container again
docker stop micropython
```

### Run unittests

#### Docker compose

Spin up the container with the following command to execute the tests and
report it's result back to the host machine.

```bash
RUN_UNITTESTS=1 docker compose up --exit-code-from micropython
```

The return value can be collected by `echo $?`, which will be either `0` in
case all tests passed, or `1` if one or multiple tests failed.
-->

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

<!-- Links -->
[ref-github-be-modbus-wrapper]: https://github.com/brainelectronics/be-modbus-wrapper
