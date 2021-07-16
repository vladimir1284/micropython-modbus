#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
modbus script
"""

from uModbus.serial import Serial
from uModbus.tcp import TCPServer
import uModbus.const as ModbusConst
from machine import UART
from machine import Pin
import _thread
import time


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
        if request.function == ModbusConst.READ_DISCRETE_INPUTS:
            print('READ_DISCRETE_INPUTS on {}'.format(request.register_addr))

            if request.register_addr >= 101 and request.register_addr <= 102:
                vals = []
                upper_limit = request.register_addr + request.quantity
                for i in range(request.register_addr, upper_limit):
                    if i == 101:
                        # vals.append(self._exo.DI1())
                        vals.append(101)
                    elif i == 102:
                        # vals.append(self._exo.DI2())
                        vals.append(102)
                    else:
                        request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
                        break
                request.send_response(vals)
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
        elif request.function == ModbusConst.READ_COILS:
            print('READ_COILS on {}'.format(request.register_addr))

            if request.register_addr == 201:
                # request.send_response([self._exo.DO1()])
                request.send_response([201])
            elif request.register_addr == 151:
                # ttl1 = Pin(self._exo.PIN_TTL1, mode=Pin.IN, pull=None)
                # request.send_response([ttl1()])
                request.send_response([151])
            elif request.register_addr == 152:
                # ttl2 = Pin(self._exo.PIN_TTL2, mode=Pin.IN, pull=None)
                # request.send_response([ttl2()])
                request.send_response([152])
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
        elif request.function == ModbusConst.WRITE_SINGLE_COIL:
            print('WRITE_SINGLE_COIL on {}'.format(request.register_addr))

            if request.register_addr == 151:
                # ttl1 = Pin(self._exo.PIN_TTL1, mode=Pin.OUT)
                if request.data[0] == 0x00:
                    print('Set coil to 0x0')
                    # ttl1(0)
                    request.send_response()
                elif request.data[0] == 0xFF:
                    print('Set coil to 0xFF')
                    # ttl1(1)
                    request.send_response()
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_VALUE)
            elif request.register_addr == 152:
                # ttl2 = Pin(self._exo.PIN_TTL2, mode=Pin.OUT)
                if request.data[0] == 0x00:
                    print('Set coil to 0x0')
                    # ttl2(0)
                    request.send_response()
                elif request.data[0] == 0xFF:
                    print('Set coil to 0xFF')
                    # ttl2(1)
                    request.send_response()
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_VALUE)
            elif request.register_addr == 201:
                if request.data[0] == 0x0:
                    print('Set coil to 0x0')
                    # self._exo.DO1(0)
                    request.send_response()
                elif request.data[0] == 0xFF:
                    print('Set coil to 0xFF')
                    # self._exo.DO1(1)
                    request.send_response()
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_VALUE)
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
        elif request.function == ModbusConst.READ_INPUT_REGISTER:
            print('READ_INPUT_REGISTER on {}'.format(request.register_addr))

            if request.register_addr >= 301 and request.register_addr <= 307:
                vals = []
                signed = []
                for i in range(request.register_addr, request.register_addr + request.quantity):
                    if i == 301:
                        # vals.append(int(self._exo.thpa.temperature() * 10))
                        vals.append(301)
                        signed.append(True)
                    elif i == 302:
                        # vals.append(int(self._exo.thpa.humidity() * 10))
                        vals.append(302)
                        signed.append(False)
                    elif i == 303:
                        # vals.append(int(self._exo.thpa.pressure() * 10))
                        vals.append(303)
                        signed.append(False)
                    elif i == 304:
                        # vals.append(int(self._exo.thpa.gas_resistance() / 1000))
                        vals.append(304)
                        signed.append(False)
                    elif i == 305:
                        # vals.append(int(self._exo.light.lux() * 10))
                        vals.append(305)
                        signed.append(False)
                    elif i == 306:
                        # vals.append(self._exo.sound.avg())
                        vals.append(306)
                        signed.append(False)
                    elif i == 307:
                        vals.append(307)
                        # vals.append(self._exo.sound.peak())
                        signed.append(False)
                    elif i == 308:
                        vals.append(308)
                        # vals.append(self._exo.thpa.iaq())
                        signed.append(False)
                    elif i == 309:
                        vals.append(309)
                        # vals.append(self._exo.thpa.iaq_trend())
                        signed.append(True)
                    else:
                        request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
                        break
                request.send_response(vals, signed=signed)
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
        elif request.function == ModbusConst.WRITE_SINGLE_REGISTER:
            print('WRITE_SINGLE_REGISTER on {}'.format(request.register_addr))

            if request.register_addr == 401:
                val = request.data_as_registers(signed=False)[0]
                print('Set register to {}'.format(val))
                # _thread.start_new_thread(self._beep, (val,))
                request.send_response()
            elif request.register_addr == 211:
                val = request.data_as_registers(signed=False)[0]
                print('Set register to {}'.format(val))
                # _thread.start_new_thread(self._do1_pulse, (val,))
                request.send_response()
            else:
                request.send_exception(ModbusConst.ILLEGAL_DATA_ADDRESS)
        else:
            request.send_exception(ModbusConst.ILLEGAL_FUNCTION)


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
        # self._enable_ap = enable_ap_func

    def _process_req(self, request):
        if request.function == ModbusConst.WRITE_SINGLE_COIL:
            print('WRITE_SINGLE_COIL on {}'.format(request.register_addr))

            if request.register_addr == 5:
                if request.data[0] == 0xFF:
                    print('Set coil to 0xFF')
                    # _thread.start_new_thread(self._enable_ap, ())
                    request.send_response()
                else:
                    request.send_exception(ModbusConst.ILLEGAL_DATA_VALUE)
                return

        super()._process_req(request)


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
            print('Unable to access is_bound flag')
            return False
