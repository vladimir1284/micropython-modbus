#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
modbus script
"""

from uModbus.serial import Serial
from uModbus.tcp import TCPServer
import uModbus.const as ModbusConst
# not natively supported on micropython, see lib/typing.py
from typing import List
from typing import Union


class Modbus(object):
    def __init__(self, itf, addr_list: list):
        self._itf = itf
        self._addr_list = addr_list
        self._register_dict = dict()
        self._register_dict['COILS'] = dict()
        self._register_dict['HREGS'] = dict()
        self._register_dict['ISTS'] = dict()
        self._register_dict['IREGS'] = dict()
        self._available_register_types = ['HREGS', 'IREGS', 'COILS', 'ISTS']

    def add_coil(self,
                 address: int,
                 value: Union[bool, List[bool]] = False) -> None:
        """
        Add a coil to the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    Union[bool, List[bool]], optional
        """
        self._set_reg_in_dict(reg_type='COILS',
                              address=address,
                              value=value)

    def remove_coil(self, address: int) -> Union[None, bool, List[bool]]:
        """
        Remove a coil from the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Register value, None if register did not exist in dict
        :rtype:     Union[None, bool, List[bool]]
        """
        return self._remove_reg_from_dict(reg_type='COILS', address=address)

    def set_coil(self,
                 address: int,
                 value: Union[bool, List[bool]] = False) -> None:
        """
        Set the coil value.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    Union[bool, List[bool]], optional
        """
        self._set_reg_in_dict(reg_type='COILS',
                              address=address,
                              value=value)

    def get_coil(self, address: int) -> Union[bool, List[bool]]:
        """
        Get the coil value.

        :param      address:  The address (ID) of the register
        :type       address:  bool

        :returns:   Coil value
        :rtype:     Union[bool, List[bool]]
        """
        return self._get_reg_in_dict(reg_type='COILS',
                                     address=address)

    @property
    def coils(self) -> dict_keys:
        """
        Get the configured coils.

        :returns:   The dictionary keys.
        :rtype:     dict_keys
        """
        return self._get_regs_of_dict(reg_type='COILS')

    def add_hreg(self, address: int, value: Union[int, List[int]] = 0) -> None:
        """
        Add a holding register to the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    Union[int, List[int]], optional
        """
        self._set_reg_in_dict(reg_type='HREGS',
                              address=address,
                              value=value)

    def remove_hreg(self, address: int) -> Union[None, int, List[int]]:
        """
        Remove a holding register from the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Register value, None if register did not exist in dict
        :rtype:     Union[None, int, List[int]]
        """
        return self._remove_reg_from_dict(reg_type='HREGS', address=address)

    def set_hreg(self, address: int, value: Union[int, List[int]] = 0) -> None:
        """
        Set the holding register value.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    int or list of int, optional
        """
        self._set_reg_in_dict(reg_type='HREGS',
                              address=address,
                              value=value)

    def get_hreg(self, address: int) -> Union[int, List[int]]:
        """
        Get the holding register value.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Holding register value
        :rtype:     Union[int, List[int]]
        """
        return self._get_reg_in_dict(reg_type='HREGS',
                                     address=address)

    @property
    def hregs(self) -> dict_keys:
        """
        Get the configured holding registers.

        :returns:   The dictionary keys.
        :rtype:     dict_keys
        """
        return self._get_regs_of_dict(reg_type='HREGS')

    def add_ist(self,
                address: int,
                value: Union[bool, List[bool]] = False) -> None:
        """
        Add a discrete input register to the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    bool or list of bool, optional
        """
        self._set_reg_in_dict(reg_type='ISTS',
                              address=address,
                              value=value)

    def remove_ist(self, address: int) -> Union[None, bool, List[bool]]:
        """
        Remove a holding register from the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Register value, None if register did not exist in dict
        :rtype:     Union[None, bool, List[bool]]
        """
        return self._remove_reg_from_dict(reg_type='ISTS', address=address)

    def set_ist(self, address: int, value: bool = False) -> None:
        """
        Set the discrete input register value.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    bool or list of bool, optional
        """
        self._set_reg_in_dict(reg_type='ISTS',
                              address=address,
                              value=value)

    def get_ist(self, address: int) -> Union[bool, List[bool]]:
        """
        Get the discrete input register value.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Discrete input register value
        :rtype:     Union[bool, List[bool]]
        """
        return self._get_reg_in_dict(reg_type='ISTS',
                                     address=address)

    @property
    def ists(self) -> dict_keys:
        """
        Get the configured discrete input registers.

        :returns:   The dictionary keys.
        :rtype:     dict_keys
        """
        return self._get_regs_of_dict(reg_type='ISTS')

    def add_ireg(self, address: int, value: Union[int, List[int]] = 0) -> None:
        """
        Add an input register to the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    Union[int, List[int]], optional
        """
        self._set_reg_in_dict(reg_type='IREGS',
                              address=address,
                              value=value)

    def remove_ireg(self, address: int) -> Union[None, int, List[int]]:
        """
        Remove an input register from the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Register value, None if register did not exist in dict
        :rtype:     Union[None, int, List[int]]
        """
        return self._remove_reg_from_dict(reg_type='IREGS', address=address)

    def set_ireg(self, address: int, value: Union[int, List[int]] = 0) -> None:
        """
        Set the input register value.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    Union[int, List[int]], optional
        """
        self._set_reg_in_dict(reg_type='IREGS',
                              address=address,
                              value=value)

    def get_ireg(self, address: int) -> Union[int, List[int]]:
        """
        Get the input register value.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Input register value
        :rtype:     Union[int, List[int]]
        """
        return self._get_reg_in_dict(reg_type='IREGS',
                                     address=address)

    @property
    def iregs(self) -> dict_keys:
        """
        Get the configured input registers.

        :returns:   The dictionary keys.
        :rtype:     dict_keys
        """
        return self._get_regs_of_dict(reg_type='IREGS')

    def _set_reg_in_dict(self, reg_type: str, address: int, value) -> None:
        """
        Set the register value in the dictionary of registers.

        :param      reg_type:  The register type
        :type       reg_type:  str
        :param      address:   The address (ID) of the register
        :type       address:   int
        :param      value:     The default value
        :type       value:     int, bool, list of int or list of bool

        :raise      KeyError:  No register at specified address found
        :returns:   Register value
        :rtype:     Union[bool, int, List[bool], List[int]]
        """
        if not self._check_valid_register(reg_type=reg_type):
            raise KeyError('{} is not a valid register type of {}'.
                           format(reg_type, self._available_register_types))

        self._register_dict[reg_type][address] = value

    def _remove_reg_from_dict(self,
                              reg_type: str,
                              address: int) -> Union[None, bool, int, List[bool], List[int]]:
        """
        Remove the register from the dictionary of registers.

        :param      reg_type:  The register type
        :type       reg_type:  str
        :param      address:   The address (ID) of the register
        :type       address:   int

        :raise      KeyError:  No register at specified address found
        :returns:   Register value, None if register did not exist in dict
        :rtype:     Union[None, bool, int, List[bool], List[int]]
        """
        if not self._check_valid_register(reg_type=reg_type):
            raise KeyError('{} is not a valid register type of {}'.
                           format(reg_type, self._available_register_types))

        return self._register_dict[reg_type].pop(address, None)

    def _get_reg_in_dict(self,
                         reg_type: str,
                         address: int) -> Union[bool, int, List[bool], List[int]]:
        """
        Get the register value from the dictionary of registers.

        :param      reg_type:  The register type
        :type       reg_type:  str
        :param      address:   The address (ID) of the register
        :type       address:   int

        :raise      KeyError:  No register at specified address found
        :returns:   Register value
        :rtype:     Union[bool, int, List[bool], List[int]]
        """
        if not self._check_valid_register(reg_type=reg_type):
            raise KeyError('{} is not a valid register type of {}'.
                           format(reg_type, self._available_register_types))

        if address in self._register_dict[reg_type]:
            return self._register_dict[reg_type][address]
        else:
            raise KeyError('No {} available for the register address {}'.
                           format(reg_type, address))

    def _get_regs_of_dict(self, reg_type: str) -> dict_keys:
        """
        Get all configured registers of specified register type.

        :param      reg_type:  The register type
        :type       reg_type:  str

        :raise      KeyError:  No register at specified address found
        :returns:   The configured registers of the specified register type.
        :rtype:     dict_keys
        """
        if not self._check_valid_register(reg_type=reg_type):
            raise KeyError('{} is not a valid register type of {}'.
                           format(reg_type, self._available_register_types))

        return self._register_dict[reg_type].keys()

    def _check_valid_register(self, reg_type: str) -> bool:
        """
        Check register type to be a valid modbus register

        :param      reg_type:  The register type
        :type       reg_type:  str

        :returns:   Flag whether register type is valid
        :rtype:     bool
        """
        if reg_type in self._available_register_types:
            return True
        else:
            return False

    def process(self) -> bool:
        """
        Process the modbus requests.

        :returns:   Result of processing, True on success, False otherwise
        :rtype:     bool
        """
        reg_type = None
        req_type = None

        request = self._itf.get_request(unit_addr_list=self._addr_list,
                                        timeout=0)
        if request is None:
            return False

        if request.function == ModbusConst.READ_COILS:
            # Coils (setter+getter) [0, 1]
            # function 01 - read single register
            reg_type = 'COILS'
            req_type = 'READ'
        elif request.function == ModbusConst.READ_DISCRETE_INPUTS:
            # Ists (only getter) [0, 1]
            # function 02 - read input status (discrete inputs/digital input)
            reg_type = 'ISTS'
            req_type = 'READ'
        elif request.function == ModbusConst.READ_HOLDING_REGISTERS:
            # Hregs (setter+getter) [0, 65535]
            # function 03 - read holding register
            reg_type = 'HREGS'
            req_type = 'READ'
        elif request.function == ModbusConst.READ_INPUT_REGISTER:
            # Iregs (only getter) [0, 65535]
            # function 04 - read input registers
            reg_type = 'IREGS'
            req_type = 'READ'
        elif request.function == ModbusConst.WRITE_SINGLE_COIL:
            # Coils (setter+getter) [0, 1]
            # function 05 - write single register
            reg_type = 'COILS'
            req_type = 'WRITE'
        elif request.function == ModbusConst.WRITE_SINGLE_REGISTER:
            # Hregs (setter+getter) [0, 65535]
            # function 06 - write holding register
            reg_type = 'HREGS'
            req_type = 'WRITE'
        else:
            request.send_exception(ModbusConst.ILLEGAL_FUNCTION)

        if reg_type:
            if req_type == 'READ':
                self._process_read_access(request=request, reg_type=reg_type)
            elif req_type == 'WRITE':
                self._process_write_access(request=request, reg_type=reg_type)

        return True

    def _create_response(self, request: Request, reg_type: str):
        """
        Create a response.

        :param      request:   The request
        :type       request:   Request
        :param      reg_type:  The register type
        :type       reg_type:  str

        :returns:   Values of this register
        :rtype:     Union[bool, int, List[int], List[bool]]
        """
        if type(self._register_dict[reg_type][request.register_addr]) is list:
            return self._register_dict[reg_type][request.register_addr]
        else:
            return [self._register_dict[reg_type][request.register_addr]]

    def _process_read_access(self, request: Request, reg_type: str) -> None:
        """
        Process read access to register

        :param      request:   The request
        :type       request:   Request
        :param      reg_type:  The register type
        :type       reg_type:  str
        """
        # print('READ_{} of ID #{}'.format(reg_type, request.register_addr))

        if request.register_addr in self._register_dict[reg_type]:
            vals = self._create_response(request=request, reg_type=reg_type)
            request.send_response(vals)
        else:
            request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

    def _process_write_access(self, request: Request, reg_type: str) -> None:
        """
        Process write access to register

        :param      request:   The request
        :type       request:   Request
        :param      reg_type:  The register type
        :type       reg_type:  str
        """
        print('WRITE_{} of ID #{}'.format(reg_type, request.register_addr))
        print('Request data: {}'.format(request.data))

        if request.register_addr in self._register_dict[reg_type]:
            val = request.data_as_registers(signed=False)[0]
            print('Set register to {}'.format(val))

            if reg_type == 'COILS':
                if request.data[0] == 0x00:
                    print('Set coil to 0x0')
                    request.send_response()
                elif request.data[0] == 0xFF:
                    print('Set coil to 0xFF')
                    request.send_response()
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_VALUE)
            elif reg_type == 'HREGS':
                print('Set holding register to {}'.format(val))
                request.send_response()
            else:
                print('No steps to set {}'.format(reg_type))
        else:
            request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)


class ModbusRTU(Modbus):
    def __init__(self,
                 addr,
                 baudrate=9600,
                 data_bits=8,
                 stop_bits=1,
                 parity=None,
                 pins=None,
                 ctrl_pin=None):
        super().__init__(
            # set itf to Serial object, addr_list to [addr]
            Serial(uart_id=1,
                   baudrate=baudrate,
                   data_bits=data_bits,
                   stop_bits=stop_bits,
                   parity=parity,
                   pins=pins,
                   ctrl_pin=ctrl_pin),
            [addr]
        )


class ModbusTCP(Modbus):
    def __init__(self):
        super().__init__(
            # set itf to TCPServer object, addr_list to None
            TCPServer(),
            None
        )

    def bind(self, local_ip: str, local_port: int = 502) -> None:
        self._itf.bind(local_ip, local_port)

    def get_bound_status(self) -> bool:
        try:
            return self._itf.get_is_bound()
        except Exception as e:
            print('Unable to access _is_bound flag, exception: {}'.format(e))
            return False
