#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
modbus script
"""

from uModbus.serial import Serial
from uModbus.tcp import TCPServer
import uModbus.const as ModbusConst
from machine import UART


class Modbus(object):
    def __init__(self, itf, addr_list):
        self._itf = itf
        self._addr_list = addr_list
        self._register_dict = dict()
        self._register_dict['COILS'] = dict()
        self._register_dict['HREGS'] = dict()
        self._register_dict['ISTS'] = dict()
        self._register_dict['IREGS'] = dict()

    def add_coil(self, address, value=False, numregs=1):
        """
        Add a coil to the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    bool, optional
        :param      numregs:  The number of registers
        :type       numregs:  int, optional
        """
        self._add_reg_to_dict(reg_type='COILS',
                              address=address,
                              value=value,
                              numregs=numregs)

    def add_hreg(self, address, value=0, numregs=1):
        """
        Add a holding register to the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    int, optional
        :param      numregs:  The number of registers
        :type       numregs:  int, optional
        """
        self._add_reg_to_dict(reg_type='HREGS',
                              address=address,
                              value=value,
                              numregs=numregs)

    def add_ist(self, address, value=False, numregs=1):
        """
        Add a discrete input register to the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    bool, optional
        :param      numregs:  The number of registers
        :type       numregs:  int, optional
        """
        self._add_reg_to_dict(reg_type='ISTS',
                              address=address,
                              value=value,
                              numregs=numregs)

    def add_ireg(self, address, value=0, numregs=1):
        """
        Add an input register to the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    int, optional
        :param      numregs:  The number of registers
        :type       numregs:  int, optional
        """
        self._add_reg_to_dict(reg_type='IREGS',
                              address=address,
                              value=value,
                              numregs=numregs)

    def _add_reg_to_dict(self, reg_type, address, value, numregs):
        """
        Add a register to the modbus registerdictionary.

        :param      reg_type:  The register type
        :type       reg_type:  str
        :param      address:   The address (ID) of the register
        :type       address:   int
        :param      value:     The default value
        :type       value:     int or bool
        :param      numregs:   The number of registers
        :type       numregs:   int
        """
        self._register_dict[reg_type][address] = value

    def process(self) -> bool:
        """
        Process the modbus requests.

        :returns:   Result of processing, True on success, False otherwise
        :rtype:     bool
        """
        reg_type = None

        request = self._itf.get_request(unit_addr_list=self._addr_list,
                                        timeout=0)
        if request is None:
            return False

        if request.function == ModbusConst.READ_COILS:
            # Coils (setter+getter) [0, 1]
            # function 01 - read single register
            reg_type = 'COILS'
        elif request.function == ModbusConst.READ_DISCRETE_INPUTS:
            # Ists (only getter) [0, 1]
            # function 02 - read input status (discrete inputs/digital input)
            reg_type = 'ISTS'
        elif request.function == ModbusConst.READ_HOLDING_REGISTERS:
            # Hregs (setter+getter) [0, 65535]
            # function 03 - read holding register
            reg_type = 'HREGS'
        elif request.function == ModbusConst.READ_INPUT_REGISTER:
            # Iregs (only getter) [0, 65535]
            # function 04 - read input registers
            reg_type = 'IREGS'
        elif request.function == ModbusConst.WRITE_SINGLE_COIL:
            # Coils (setter+getter) [0, 1]
            # function 05 - write single register
            reg_type = 'COILS'
        elif request.function == ModbusConst.WRITE_SINGLE_REGISTER:
            # Hregs (setter+getter) [0, 65535]
            # function 06 - write holding register
            reg_type = 'HREGS'
        else:
            request.send_exception(ModbusConst.ILLEGAL_FUNCTION)

        if reg_type:
            self._process_read_access(request=request, reg_type=reg_type)

        return True

    def _create_response(self, request, reg_type) -> list:
        """
        Create a response.

        :param      request:   The request
        :type       request:   Request
        :param      reg_type:  The register type
        :type       reg_type:  str

        :returns:   Values of this register
        :rtype:     list
        """
        return [self._register_dict[reg_type][request.register_addr]]

    def _process_read_access(self, request, reg_type):
        """
        Process read access to register

        :param      request:   The request
        :type       request:   Request
        :param      reg_type:  The register type
        :type       reg_type:  str
        """
        print('READ_{} of ID #{}'.format(reg_type, request.register_addr))

        if request.register_addr in self._register_dict[reg_type]:
            vals = self._create_response(request=request, reg_type=reg_type)
            request.send_response(vals)
        else:
            request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

    def _process_write_access(self, request, reg_type):
        """
        Process write access to register

        :param      request:   The request
        :type       request:   Request
        :param      reg_type:  The register type
        :type       reg_type:  str
        """
        print('WRITE_SINGLE_{} of ID #{}'.
              format(request.register_addr, reg_type))
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

    """
    def _process_req(self, request):
        if request.function == ModbusConst.WRITE_SINGLE_COIL:
            print('WRITE_SINGLE_COIL of ID #{}'.format(request.register_addr))
            print('Request data: {}'.format(request.data))

            if request.register_addr == 5:
                val = request.data_as_registers(signed=False)[0]
                print('Set register to {}'.format(val))

                if request.data[0] == 0xFF:
                    print('Set coil to 0xFF')
                    request.send_response()
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_VALUE)
                return
            else:
                pass

                # let it be processed by Modbus (super) call function
                # request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

        super()._process_req(request)
    """


class ModbusTCP(Modbus):
    def __init__(self):
        super().__init__(
            # set itf to TCPServer object, addr_list to None
            TCPServer(),
            None
        )

    def bind(self, local_ip, local_port=502):
        self._itf.bind(local_ip, local_port)

    def get_bound_status(self):
        try:
            return self._itf.get_is_bound()
        except Exception as e:
            print('Unable to access _is_bound flag')
            return False
