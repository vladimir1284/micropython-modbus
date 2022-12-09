# Upgrade Guide

Detailed upgrade guide for upgrading between breaking versions

---------------

## Intro

As this package adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
this document thereby describes the necessary steps to upgrade between two
major versions.

## Upgrade from major version 1 to 2

### Overview

This is a compressed extraction of the changelog

> - Remove dependency to `Serial` and `requests` from `umodbus.modbus`, see [#18](https://github.com/brainelectronics/micropython-modbus/issues/18)
> - `ModbusRTU` class is part of [serial.py](umodbus/serial.py), see [#18](https://github.com/brainelectronics/micropython-modbus/issues/18)
> - `ModbusTCP` class is part of [tcp.py](umodbus/tcp.py), see [#18](https://github.com/brainelectronics/micropython-modbus/issues/18)
> - `ModbusRTU` and `ModbusTCP` classes and related functions removed from [modbus.py](umodbus/modbus.py), see [#18](https://github.com/brainelectronics/micropython-modbus/issues/18)
> - Imports changed from:
>     - `from umodbus.modbus import ModbusRTU` to `from umodbus.serial import ModbusRTU`
>     - `from umodbus.modbus import ModbusTCP` to `from umodbus.tcp import ModbusTCP`
>  - `read_coils` and `read_discrete_inputs` return a list with the same length as the requested quantity instead of always 8, see [#12](https://github.com/brainelectronics/micropython-modbus/issues/12) and [#25](https://github.com/brainelectronics/micropython-modbus/issues/25)
> - `read_holding_registers` returns list with amount of requested registers, see [#25](https://github.com/brainelectronics/micropython-modbus/issues/25)

### Steps to be performed

#### Update imports

The way of importing `ModbusRTU` and `ModbusTCP` changed. Update the imports
according to the following table. For further details check [#18](https://github.com/brainelectronics/micropython-modbus/issues/18)

| Version 1 | Version 2 |
| --------- | --------- |
| `from umodbus.modbus import ModbusRTU` | `from umodbus.serial import ModbusRTU` |
| `from umodbus.modbus import ModbusTCP` | `from umodbus.tcp import ModbusTCP` |

#### Return values changed

The functions `read_coils`, `read_discrete_inputs` and `read_holding_registers`
return now a list with the same length as the requested register quantity.

##### Coil registers

All major version 1 releases of this package returned a list with 8 elements
on a coil register request.

```python
# example usage only, non productive code example

# reading one coil returned a list of 8 boolean elements
>>> host.read_coils(slave_addr=10, starting_addr=123, coil_qty=1)
[True, False, False, False, False, False, False, False]
# expectation is [True]

# reading 3 coils returned a list of 8 boolean elements
>>> host.read_coils(slave_addr=10, starting_addr=126, coil_qty=3)
[False, False, False, False, False, False, False, False]
# expectation is [False, True, False]
```

With the fixes of major version 2 a list with the expected length is returned

```python
# example usage only, non productive code example

# reading one coil returns a list of 1 boolean element
>>> host.read_coils(slave_addr=10, starting_addr=123, coil_qty=1)
[True]

# reading 3 coils returns a list of 3 boolean elements
>>> host.read_coils(slave_addr=10, starting_addr=126, coil_qty=3)
[False, True, False]
```

##### Discrete input registers

All major version 1 releases of this package returned a list with 8 elements
on a discrete input register request.

```python
# example usage only, non productive code example

# reading one discrete input register returned a list of 8 boolean elements
>>> host.read_discrete_inputs(slave_addr=10, starting_addr=123, input_qty=1)
[True, False, False, False, False, False, False, False]
# expectation is [True]

# reading 3 discrete input register returned a list of 8 boolean elements
>>> host.read_discrete_inputs(slave_addr=10, starting_addr=126, input_qty=3)
[False, False, False, False, False, False, False, False]
# expectation is [False, True, False]
```

With the fixes of major version 2 a list with the expected length is returned

```python
# example usage only, non productive code example

# reading one discrete input register returns a list of 1 boolean element
>>> host.read_discrete_inputs(slave_addr=10, starting_addr=123, input_qty=1)
[True]

# reading 3 discrete input registers returns a list of 3 boolean elements
>>> host.read_discrete_inputs(slave_addr=10, starting_addr=126, input_qty=3)
[False, True, False]
```

##### Holding registers

In all major version 1 releases of this package returned a tuple with only one
element on a holding register request.

```python
# example usage only, non productive code example

# reading one register only worked as expected
>>> host.read_holding_registers(slave_addr=10, starting_addr=93, register_qty=1, signed=False)
(19,)
# expectation is (19,)

# reading multiple registers did not work as expected
# register values of register 93 + 94 should be returned
>>> host.read_holding_registers(slave_addr=10, starting_addr=93, register_qty=2, signed=False)
(19,)
# expectation is (19, 29)
```

With the fixes of major version 2 a list with the expected length is returned

```python
# example usage only, non productive code example

# reading one register only worked as expected
>>> host.read_holding_registers(slave_addr=10, starting_addr=93, register_qty=1, signed=False)
(19,)

# reading multiple registers did not work as expected
# register values of register 93 + 94 should be returned
>>> host.read_holding_registers(slave_addr=10, starting_addr=93, register_qty=2, signed=False)
(19, 29)
```
