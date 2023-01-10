# Testing

Testing is done inside MicroPython Docker container

---------------

## Basics

This library is as of now tested with the `v1.18` version of MicroPython

### Pull container

Checkout the available
[MicroPython containers](https://hub.docker.com/r/micropython/unix/tags) and
pull the `v1.18` locally.

```bash
docker pull micropython/unix:v1.18
```

### Spin up container

#### Simple container

Use this command for your first tests or to run some MicroPython commands in
a simple REPL

```bash
docker run -it --name micropython-1.18 --network=host --entrypoint bash micropython/unix:v1.18
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

## Testing

All tests are automatically executed on a push to GitHub and have to be passed
in order to be allowed to merge to the main development branch, see also [CONTRIBUTING](CONTRIBUTING.md).

### Run unittests manually

First build and run the docker image with the following command

```bash
docker build -t micropython-test-manually -f Dockerfile.tests_manually .
docker run -it --name micropython-test-manually micropython-test-manually
```

Run all unittests defined in the `tests` directory and exit with status result

```bash
micropython-dev -c "import mpy_unittest as unittest; unittest.main('tests')"
```

In order to execute only a specific set of tests use the following command
inside the built and running MicroPython container

```bash
# run all tests of "TestAbsoluteTruth" defined in tests/test_absolute_truth.py
# and exit with status result
micropython-dev -c "import mpy_unittest as unittest; unittest.main(name='tests.test_absolute_truth', fromlist=['TestAbsoluteTruth'])"
```

### Custom container for unittests

```bash
docker build --tag micropython-test --file Dockerfile.tests .
```

As soon as the built image is executed all unittests are executed. The
container will exit with a non-zero status in case of a unittest failure.

The return value can be collected by `echo $?` (on Linux based systems) or
`echo %errorlevel%` (on Windows), which will be either `0` in case all tests
passed, or `1` if one or multiple tests failed.

### Docker compose

For more complex unittests and integration tests, several Dockerfiles are
combined into a docker-compose file.

The option `--build` can be skipped on the second run, to avoid rebuilds of
the containers. All "dynamic" data is shared via `volumes`.

#### TCP integration tests

##### Overview

The TCP integration tests defined by `test_tcp_example.py` uses the
`Dockerfile.client_tcp` and `Dockerfile.test_examples`.

A network bridge is created with fixed IPv4 addresses in order to bind the
client to a known IP and let the host reach it on that predefined IP.

The port defined in `tcp_client_example.py`, executed by
`Dockerfile.client_tcp` has to be open, exposed to the `micropython-host`
service running `Dockerfile.test_examples` and optionally exposed in the
`docker-compose-tcp-test.yaml` file.

Finally the tests defined in `TestTcpExample` are executed. The tests read and
write all available register types on the client and check the response with
the expected data.

##### Usage

```bash
docker compose -f docker-compose-tcp-test.yaml up --build --exit-code-from micropython-host --remove-orphans
```

#### RTU integration tests

##### UART interface

As the [MicroPython containers](https://hub.docker.com/r/micropython/unix/tags)
do not have a UART interface, which is additionally anyway not connectable via
two containers, a [`UART fake`](fakes.machine.UART) has been implemented.

The fake [`UART`](fakes.machine.UART) class provides all required functions
like [`any()`](fakes.machine.UART.any), [`read()`](fakes.machine.UART.read) and
[`write()`](fakes.machine.UART.write) to simulate a UART interface.

During the initialisation of the fake UART a simple and very basic socket
request is made to `172.25.0.2`, a predefined IP address, see
`docker-compose-rtu-test.yaml`. In case no response is received, a socket based
server is started. It is thereby important to start the RTU client before the
RTU host. The RTU host will perform the same check during the UART init, but
will reach the (already running) socket server and connect to it.

The data provided to the [`write()`](fakes.machine.UART.write) call of the RTU
host, will be sent to the background socket server of the RTU client and be
read inside the [`get_request()`](umodbus.serial.Serial.get_request) function
which is constantly called by the [`process()`](umodbus.modbus.Modbus.process)
function.

After it has been processed from Modbus perspective, the RTU client response
will then be put by the [`write()`](fakes.machine.UART.write) function into a
queue on RTU client side, picked up by the RTU client background socket server
thread and sent back to the RTU host where it is made available via the
[`read()`](fakes.machine.UART.read) function.

##### Overview

The RTU integration tests defined by `test_rtu_example.py` uses the
`Dockerfile.client_rtu` and `Dockerfile.test_examples`.

A network bridge is created with fixed IPv4 addresses in order to bind the
client to a known IP and let the host reach it on that predefined IP.

The port defined in `rtu_client_example.py`, executed by
`Dockerfile.client_rtu` has to be open, exposed to the `micropython-host`
service running `Dockerfile.test_examples` and optionally exposed in the
`docker-compose-rtu-test.yaml` file.

Finally the tests defined in `TestRtuExample` are executed. The tests read and
write all available register types on the client and check the response with
the expected data.

##### Usage

```bash
docker compose -f docker-compose-rtu-test.yaml up --build --exit-code-from micropython-host-rtu --remove-orphans
```

<!-- Links -->
[ref-fakes]: https://github.com/brainelectronics/micropython-modbus/blob/develop/fakes/machine.py
