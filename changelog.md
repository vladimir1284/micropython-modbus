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
[Unreleased]: https://github.com/brainelectronics/micropython-modbus/compare/0.1.0...develop

[0.1.0]: https://github.com/brainelectronics/micropython-modbus/tree/0.1.0
