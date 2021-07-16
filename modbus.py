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

    def process(self):
        request = self._itf.get_request(unit_addr_list=self._addr_list,
                                        timeout=0)
        if request is None:
            return False

        self._process_req(request=request)

        return True

    def _process_req(self, request):
        if request.function == ModbusConst.READ_COILS:
            self._process_read_coils(request=request)
        elif request.function == ModbusConst.READ_DISCRETE_INPUTS:
            self._process_read_ists(request=request)
        elif request.function == ModbusConst.READ_HOLDING_REGISTERS:
            self._process_read_hregs(request=request)
        elif request.function == ModbusConst.READ_INPUT_REGISTER:
            self._process_read_iregs(request=request)
        elif request.function == ModbusConst.WRITE_SINGLE_COIL:
            self._process_write_coils(request=request)
        elif request.function == ModbusConst.WRITE_SINGLE_REGISTER:
            self._process_write_hregs(request=request)
        else:
            request.send_exception(ModbusConst.ILLEGAL_FUNCTION)

    def _process_read_coils(self, request):
        """
        Process access to coil register

        Coils (only getter) [0, 1], function 01 - read single register

        :param      request:  The request
        :type       request:  Request
        """
        print('READ_COIL of ID #{}'.format(request.register_addr))

        if request.register_addr == 101:
            request.send_response([1])
        elif request.register_addr == 102:
            request.send_response([1])
        else:
            request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

    def _process_read_ists(self, request):
        """
        Process access to discrete input register

        Ists (only getter) [0, 1], function 02 - read input status (discrete
        inputs/digital input)

        :param      request:  The request
        :type       request:  Request
        """
        print('READ_DISCRETE_INPUTS of ID #{}'.format(request.register_addr))

        if request.register_addr >= 101 and request.register_addr <= 102:
            vals = []
            upper_limit = request.register_addr + request.quantity
            for i in range(request.register_addr, upper_limit):
                if i == 101:
                    vals.append(1)
                elif i == 102:
                    vals.append(1)
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
                    break
            request.send_response(vals)
        else:
            request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

    def _process_read_hregs(self, request):
        """
        Process access to holding register

        Hregs (setter+getter) [0, 65535], function 03 - read holding register

        :param      request:  The request
        :type       request:  Request
        """
        print('READ_HOLDING_REGISTERS of ID #{}'.format(request.register_addr))

        if request.register_addr >= 101 and request.register_addr <= 102:
            vals = []
            signed = []
            for i in range(request.register_addr, request.register_addr + request.quantity):
                if i == 101:
                    vals.append(101)
                    signed.append(True)
                elif i == 102:
                    vals.append(102)
                    signed.append(False)
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
                    break
            request.send_response(vals, signed=signed)
        else:
            request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

    def _process_read_iregs(self, request):
        """
        Process access to input register

        Iregs (only getter) [0, 65535], function 04 - read input registers

        :param      request:  The request
        :type       request:  Request
        """
        print('READ_INPUT_REGISTER of ID #{}'.format(request.register_addr))

        if request.register_addr >= 101 and request.register_addr <= 102:
            vals = []
            signed = []
            for i in range(request.register_addr, request.register_addr + request.quantity):
                if i == 101:
                    vals.append(101)
                    signed.append(True)
                elif i == 102:
                    vals.append(102)
                    signed.append(False)
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
                    break
            request.send_response(vals, signed=signed)
        else:
            request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

    def _process_write_coils(self, request):
        """
        Process setting of coil register

        Coils (only getter) [0, 1], function 05 - write single register

        :param      request:  The request
        :type       request:  Request
        """
        print('WRITE_SINGLE_COIL of ID #{}'.format(request.register_addr))
        print('Request data: {}'.format(request.data))

        if request.register_addr == 101:
            val = request.data_as_registers(signed=False)[0]
            print('Set register to {}'.format(val))

            if request.data[0] == 0x00:
                print('Set coil to 0x0')
                request.send_response()
            elif request.data[0] == 0xFF:
                print('Set coil to 0xFF')
                request.send_response()
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_VALUE)
        elif request.register_addr == 102:
            val = request.data_as_registers(signed=False)[0]
            print('Set register to {}'.format(val))

            if request.data[0] == 0x00:
                print('Set coil to 0x0')
                request.send_response()
            elif request.data[0] == 0xFF:
                print('Set coil to 0xFF')
                request.send_response()
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_VALUE)
        else:
            request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)

    def _process_write_hregs(self, request):
        """
        Process setting of holding register

        Hregs (setter+getter) [0, 65535], function 06 - write holding register

        :param      request:  The request
        :type       request:  Request
        """
        print('WRITE_SINGLE_REGISTER of ID #{}'.format(request.register_addr))
        print('Request data: {}'.format(request.data))

        if request.register_addr == 101:
            val = request.data_as_registers(signed=False)
            print('Set holding register to {}'.format(val))
            request.send_response()
        elif request.register_addr == 102:
            val = request.data_as_registers(signed=False)
            print('Set holding register to {}'.format(val))
            request.send_response()
        else:
            request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)


class ModbusRTU(Modbus):
    def __init__(self,
                 addr,
                 baudrate=9600,
                 data_bits=8,
                 stop_bits=1,
                 pins=None,
                 ctrl_pin=None):
        super().__init__(
            # set itf to Serial object, addr_list to [addr]
            Serial(uart_id=1,
                   baudrate=baudrate,
                   data_bits=data_bits,
                   stop_bits=stop_bits,
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
