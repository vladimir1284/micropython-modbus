#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Unittest for testing RTU functions of umodbus"""

import json
import ulogging as logging
import mpy_unittest as unittest
from umodbus.serial import Serial as ModbusRTUMaster


class TestRtuExample(unittest.TestCase):
    def setUp(self) -> None:
        """Run before every test method"""
        # set basic config and level for the logger
        logging.basicConfig(level=logging.INFO)

        # create a logger for this TestSuite
        self.test_logger = logging.getLogger(__name__)

        # set the test logger level
        self.test_logger.setLevel(logging.DEBUG)

        # enable/disable the log output of the device logger for the tests
        # if enabled log data inside this test will be printed
        self.test_logger.disabled = False

        self._client_addr = 10          # bus address of client

        self._host = ModbusRTUMaster(baudrate=9600, pins=(25, 26))  # (TX, RX)

        test_register_file = 'registers/example.json'
        try:
            with open(test_register_file, 'r') as file:
                self._register_definitions = json.load(file)
        except Exception as e:
            self.test_logger.error(
                'Is the test register file available at {}?'.format(
                    test_register_file))
            raise e

    def test_setup(self) -> None:
        """Test successful setup of ModbusRTUMaster and the defined register"""
        # although it is called "Master" the host is here a client connecting
        # to one or more clients/slaves/devices which are providing data
        # The reason for calling it "ModbusRTUMaster" is the status of having
        # the functions to request or get data from other client/slave/devices
        self.assertFalse(self._host._uart._is_server)
        self.assertIsInstance(self._register_definitions, dict)

        for reg_type in ['COILS', 'HREGS', 'ISTS', 'IREGS']:
            with self.subTest(reg_type=reg_type):
                self.assertIn(reg_type, self._register_definitions.keys())
                self.assertIsInstance(self._register_definitions[reg_type],
                                      dict)
                self.assertGreaterEqual(
                    len(self._register_definitions[reg_type]), 1)

        self._read_coils_single()

    def _read_coils_single(self) -> None:
        """Test reading sinlge coil of client"""
        # read coil with state ON/True
        coil_address = \
            self._register_definitions['COILS']['EXAMPLE_COIL']['register']
        coil_qty = self._register_definitions['COILS']['EXAMPLE_COIL']['len']
        expectation_list = [
            bool(self._register_definitions['COILS']['EXAMPLE_COIL']['val'])
        ]

        coil_status = self._host.read_coils(
            slave_addr=self._client_addr,
            starting_addr=coil_address,
            coil_qty=coil_qty)

        self.test_logger.debug('Status of COIL {}: {}, expectation: {}'.
                               format(coil_address,
                                      coil_status,
                                      expectation_list))
        self.assertIsInstance(coil_status, list)
        self.assertEqual(len(coil_status), coil_qty)
        self.assertTrue(all(isinstance(x, bool) for x in coil_status))
        self.assertEqual(coil_status, expectation_list)

        # read coil with state OFF/False
        coil_address = \
            self._register_definitions['COILS']['EXAMPLE_COIL_OFF']['register']
        coil_qty = \
            self._register_definitions['COILS']['EXAMPLE_COIL_OFF']['len']
        expectation_list = [bool(
            self._register_definitions['COILS']['EXAMPLE_COIL_OFF']['val']
        )]

        coil_status = self._host.read_coils(
            slave_addr=self._client_addr,
            starting_addr=coil_address,
            coil_qty=coil_qty)

        self.test_logger.debug('Status of COIL {}: {}, expectation: {}'.
                               format(coil_address,
                                      coil_status,
                                      expectation_list))
        self.assertIsInstance(coil_status, list)
        self.assertEqual(len(coil_status), coil_qty)
        self.assertTrue(all(isinstance(x, bool) for x in coil_status))
        self.assertEqual(coil_status, expectation_list)

    @unittest.skip('Test not yet implemented')
    def test__calculate_crc16(self) -> None:
        """Test calculating Modbus CRC16"""
        pass

    @unittest.skip('Test not yet implemented')
    def test__exit_read(self) -> None:
        """Test validating received response"""
        pass

    @unittest.skip('Test not yet implemented')
    def test__uart_read(self) -> None:
        """Test reading data from UART"""
        pass

    @unittest.skip('Test not yet implemented')
    def test__uart_read_frame(self) -> None:
        """Test reading a Modbus frame"""
        pass

    @unittest.skip('Test not yet implemented')
    def test__send(self) -> None:
        """Test sending a Modbus frame"""
        pass

    @unittest.skip('Test not yet implemented')
    def test__send_receive(self) -> None:
        """Test sending a Modbus frame"""
        pass

    @unittest.skip('Test not yet implemented')
    def test__validate_resp_hdr(self) -> None:
        """Test response header validation"""
        pass

    @unittest.skip('Test not yet implemented')
    def test_send_response(self) -> None:
        """Test sending a response to a client"""
        pass

    @unittest.skip('Test not yet implemented')
    def test_send_exception_response(self) -> None:
        """Test sending a exception response to a client"""
        pass

    @unittest.skip('Test not yet implemented')
    def test_get_request(self) -> None:
        """Test checking for a request"""
        pass

    def tearDown(self) -> None:
        """Run after every test method"""
        self._host._uart._sock.close()
        self.test_logger.debug('Closed ModbusRTUMaster socket at tearDown')


if __name__ == '__main__':
    unittest.main()
