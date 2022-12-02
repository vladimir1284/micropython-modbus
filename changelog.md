# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [x.y.z] - yyyy-mm-dd
### Added
### Changed
### Removed
### Fixed
-->

<!-- ## [Unreleased] -->

## Released
## [2.0.0] - 2022-12-02
### Added
- Perform MicroPython based unittests on every `Test` workflow run
- Add usage description of docker based MicroPython unittest framework in [USAGE](USAGE.md)
- Add [docker compose file](docker-compose.yaml) based in MicroPython 1.18 image
- Add [TCP client Dockerfile](Dockerfile.client), [TCP host Dockerfile](Dockerfile.host), [unittest Dockerfile](Dockerfile.tests) and [TCP unittest specific Dockerfile](Dockerfile.test_tcp_example). All based on MicroPython 1.18 image
- Add initial test, testing the unittest itself
- Add [unittest](unittest.py) implementation based on pfalcon's [micropython-unittest](https://github.com/pfalcon/pycopy-lib/blob/56ebf2110f3caa63a3785d439ce49b11e13c75c0/unittest/unittest.py)
- Docstrings available for all functions of [functions.py](umodbus/functions.py), see #27
- Typing hints available for all functions of [functions.py](umodbus/functions.py), [serial.py](umodbus/serial.py) and [tcp.py](umodbus/tcp.py), see #27
- Unittest for [functions.py](umodbus/functions.py), see #16
- Unittest for [const.py](umodbus/const.py), see #16

### Changed
- Use default values for all registers defined in the [example JSON](examples/example.json)
- [TCP host example](examples/tcp_host_example.py) and [TCP client example](examples/tcp_client_example.py) define a static IP address and skip further WiFi setup steps in case a Docker usage is detected by a failing import of the `network` module, contributes to #16
- Define all Modbus function codes as `const()` to avoid external modifications, contributes to #18
- Remove dependency to `Serial` and `requests` from `umodbus.modbus`, see #18
- `ModbusRTU` class is part of [serial.py](umodbus/serial.py), see #18
- `ModbusTCP` class is part of [tcp.py](umodbus/tcp.py), see #18
- `ModbusRTU` and `ModbusTCP` classes and related functions removed from [modbus.py](umodbus/modbus.py), see #18
- Imports changed from:
    - `from umodbus.modbus import ModbusRTU` to `from umodbus.serial import ModbusRTU`
    - `from umodbus.modbus import ModbusTCP` to `from umodbus.tcp import ModbusTCP`

### Fixed
- `write_multiple_coils` function works as specified. Constructed outputs value was incorrect, see #22

## [1.2.0] - 2022-11-13
### Added
- [TCP host example script](examples/tcp_host_example.py)
- JSON file to set registers on TCP/RTU device
- Bash script to wrap manipulation of TCP modbus register data
- [Example boot script](examples/boot.py)
- TOC in [README](README.md)
- Use [changelog-based-release action](https://github.com/brainelectronics/changelog-based-release) to create a draft release with every merge to develop
- Use [changelog-based-release action](https://github.com/brainelectronics/changelog-based-release) to create a drafted prerelease release with every PR build, see #20
- [USAGE](USAGE.md) and [SETUP](SETUP.md) files with more details

### Changed
- Add more info to [TCP client example script](examples/tcp_client_example.py)
- Update [modules submodule](https://github.com/brainelectronics/python-modules/tree/43bad716b7db27db07c94c2d279cee57d0c8c753) to `1.3.0`
- Line breaks are no longer used in this changelog for enumerations
- Issues are referenced as `#123` instead of `[#123][ref-issue-123]` to avoid explicit references at the bottom or some other location in the file
- Scope of contents permissions in release and test release workflow is now `write` to use auto release creation

### Fixed
- Typo in [RTU client example script](examples/rtu_client_example.py)

## [1.1.1] - 2022-11-09
### Fixed
- Default value of `setup_registers` function parameter `use_default_vals`
  changed to `False` to avoid confusion behaviour if not explicitly defined,
  see [issue 13][ref-issue-13]
- Missing function docstring added to `setup_registers` function
- `write_single_coil` allows `0`, `1`, `False`, `True`, `0x0` or `0xFF00`
  instead of `0x0` and `0xFF00` only as set value, see [issue 14][ref-issue-14]

## [1.1.0] - 2022-11-03
### Added
- `float_to_bin`, `bin_to_float`, `int_to_bin` functions added to
  [`umodbus/functions.py`](umodbus/functions.py)
- Deploy to [Test Python Package Index](https://test.pypi.org/) on every PR
  build with a [PEP440][ref-pep440] compliant `-rc<BUILDNUMBER>.dev<PR_NUMBER>`
  meta data extension
- [Test release workflow](.github/workflows/test-release.yaml) running only on
  PRs is archiving and uploading built artifacts to
  [Test Python Package Index](https://test.pypi.org/)

### Changed
- Author is explicitly mentioned in [`setup.py`](setup.py) instead of used by
  `__author__` variable which has been previously defined in
  [`version.py`](umodbus/version.py) but no longer available with autodeploy.

### Fixed
- All uncovered flake8 warnings of [`umodbus`](umodbus)

## [1.0.0] - 2022-02-26
### Added
- [`setup.py`](setup.py) and [`sdist_upip.py`](sdist_upip.py) taken from
  [pfalcon's picoweb repo][ref-pfalcon-picoweb-sdist-upip] and PEP8 improved
- [`MIT License`](LICENSE)
- [`version.py`](umodbus/version.py) storing current library version
- [`typing.py`](umodbus/typing.py) enabling type hints

### Changed
- Moved all uModbus files from `lib/uModbus` into [`umodbus`](umodbus)
- Update import statements of all files of [`umodbus`](umodbus)
- Update [`README`](README.md) usage description of MicroPython lib deploy to
  [PyPi][ref-pypi]
- Usage examples in [`README`](README.md) updated with new import path
- Update [`boot`](boot.py) and [`main`](main.py) files to use `be_helpers`
- Enable setting of `max_connections` to TCP socket in
  [`modbus ModbusTCP bind function`](umodbus/modbus.py) and [`tcp TCPServer bind function`](umodbus/tcp.py)

### Removed
- MicroPython helpers module no longer used
- MicroPython ESP WiFi Manager module no longer used
- Lib folder of dependency modules no longer used
- Commented print debug messages in several files of umodbus

## [0.1.0] - 2022-02-20
### Added
- This changelog file
- [`.gitignore`](.gitignore) file
- [`requirements.txt`](requirements.txt) file to setup tools for board
  interactions
- Creation header to all files of [`lib/uModbus`](lib/uModbus) in order to
  provide proper credits to [Pycom](https://www.pycom.io)
- `get_is_bound()` function added to [`lib/uModbus/tcp.py`](lib/uModbus/tcp.py)
  to check status of socket binding for the Modbus TCP Server (host)
- [Example register files](registers) to show basic usage with a MyEVSE board

### Changed
- Reworked [`boot.py`](boot.py) and [`main.py`](main.py) for simple usage
- [`README`](README.md) file with usage examples
- Replaced WiPy specific calls in [`lib/uModbus`](lib/uModbus) files with
  MicroPython 1.16 or higher calls
- Limit number of concurrent socket connections to the Modbus TCP Server (host)
  to 10
- Return on `_accept_request()` in case of an `OSError` as MicroPython raises
  this type of error in case a socket timeout occured. `TimeoutError` is not
  available on MicroPython compared to WiPy

### Fixed
- PEP8 style issues on all files of [`lib/uModbus`](lib/uModbus)

<!-- Links -->
[Unreleased]: https://github.com/brainelectronics/micropython-modbus/compare/2.0.0...develop

[2.0.0]: https://github.com/brainelectronics/micropython-modbus/tree/2.0.0
[1.2.0]: https://github.com/brainelectronics/micropython-modbus/tree/1.2.0
[1.1.1]: https://github.com/brainelectronics/micropython-modbus/tree/1.1.1
[1.1.0]: https://github.com/brainelectronics/micropython-modbus/tree/1.1.0
[1.0.0]: https://github.com/brainelectronics/micropython-modbus/tree/1.0.0
[0.1.0]: https://github.com/brainelectronics/micropython-modbus/tree/0.1.0

[ref-issue-13]: https://github.com/brainelectronics/micropython-modbus/issues/13
[ref-issue-14]: https://github.com/brainelectronics/micropython-modbus/issues/14
[ref-pep440]: https://peps.python.org/pep-0440/
[ref-pypi]: https://pypi.org/
[ref-pfalcon-picoweb-sdist-upip]: https://github.com/pfalcon/picoweb/blob/b74428ebdde97ed1795338c13a3bdf05d71366a0/sdist_upip.py
[ref-be-micropython-module]: https://github.com/brainelectronics/micropython-modules/tree/1.1.0
