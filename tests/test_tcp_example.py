#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Unittest for testing functions of umodbus"""

import json
import ulogging as logging
import unittest
from umodbus.tcp import TCP as ModbusTCPMaster


class TestTcpExample(unittest.TestCase):
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

        self._client_tcp_port = 502     # port of client
        self._client_addr = 10          # bus address of client
        self._client_ip = '172.24.0.2'  # static Docker IP address
        self._host = ModbusTCPMaster(
            slave_ip=self._client_ip,
            slave_port=self._client_tcp_port,
            timeout=5.0)

        with open('tests/test-registers.json', 'r') as file:
            self._register_definitions = json.load(file)

    def test_setup(self) -> None:
        self.assertIsInstance(self._register_definitions, dict)

        for reg_type in ['COILS', 'HREGS', 'ISTS', 'IREGS']:
            with self.subTest(reg_type=reg_type):
                self.assertIn(reg_type, self._register_definitions.keys())
                self.assertIsInstance(self._register_definitions[reg_type],
                                      dict)
                self.assertGreaterEqual(
                    len(self._register_definitions[reg_type]), 1)

    @unittest.skip('Test not yet implemented')
    def test__create_mbap_hdr(self) -> None:
        pass

    @unittest.skip('Test not yet implemented')
    def test__bytes_to_bool(self) -> None:
        pass

    @unittest.skip('Test not yet implemented')
    def test__to_short(self) -> None:
        pass

    @unittest.skip('Test not yet implemented')
    def test__validate_resp_hdr(self) -> None:
        pass

    @unittest.skip('Test not yet implemented')
    def test__send_receive(self) -> None:
        pass

    def test_read_coils(self) -> None:
        """Test reading coils of client"""
        coil_address = \
            self._register_definitions['COILS']['EXAMPLE_COIL']['register']
        coil_qty = self._register_definitions['COILS']['EXAMPLE_COIL']['len']
        expectation_list = [
            False, False, False, False, False, False, False, False
        ]
        expectation_list[0] = \
            bool(self._register_definitions['COILS']['EXAMPLE_COIL']['val'])

        coil_status = self._host.read_coils(
            slave_addr=self._client_addr,
            starting_addr=coil_address,
            coil_qty=coil_qty)

        self.test_logger.debug('Status of COIL {}: {}, expectation: {}'.
                               format(coil_address,
                                      coil_status,
                                      expectation_list))
        self.assertIsInstance(coil_status, list)
        self.assertEqual(len(coil_status), 8)
        self.assertTrue(all(isinstance(x, bool) for x in coil_status))
        self.assertEqual(coil_status, expectation_list)

    def test_read_discrete_inputs(self) -> None:
        """Test reading discrete inputs of client"""
        ist_address = \
            self._register_definitions['ISTS']['EXAMPLE_ISTS']['register']
        input_qty = self._register_definitions['ISTS']['EXAMPLE_ISTS']['len']
        expectation_list = [
            False, False, False, False, False, False, False, False
        ]
        expectation_list[0] = \
            bool(self._register_definitions['ISTS']['EXAMPLE_ISTS']['val'])

        input_status = self._host.read_discrete_inputs(
            slave_addr=self._client_addr,
            starting_addr=ist_address,
            input_qty=input_qty)

        self.test_logger.debug('Status of IST {}: {}, expectation: {}'.
                               format(ist_address,
                                      input_status,
                                      expectation_list))
        self.assertIsInstance(input_status, list)
        self.assertEqual(len(input_status), 8)
        self.assertTrue(all(isinstance(x, bool) for x in input_status))
        self.assertEqual(input_status, expectation_list)

    def test_read_holding_registers(self) -> None:
        """Test reading holding registers of client"""
        hreg_address = \
            self._register_definitions['HREGS']['EXAMPLE_HREG']['register']
        register_qty = \
            self._register_definitions['HREGS']['EXAMPLE_HREG']['len']
        expectation = \
            (self._register_definitions['HREGS']['EXAMPLE_HREG']['val'], )

        register_value = self._host.read_holding_registers(
            slave_addr=self._client_addr,
            starting_addr=hreg_address,
            register_qty=register_qty)

        self.test_logger.debug('Status of IST {}: {}, expectation: {}'.
                               format(hreg_address,
                                      register_value,
                                      expectation))
        self.assertIsInstance(register_value, tuple)
        self.assertEqual(len(register_value), register_qty)
        self.assertTrue(all(isinstance(x, int) for x in register_value))
        self.assertEqual(register_value, expectation)

    def test_read_input_registers(self) -> None:
        """Test reading input registers of client"""
        ireg_address = \
            self._register_definitions['IREGS']['EXAMPLE_IREG']['register']
        register_qty = \
            self._register_definitions['IREGS']['EXAMPLE_IREG']['len']
        expectation = \
            (self._register_definitions['IREGS']['EXAMPLE_IREG']['val'], )

        register_value = self._host.read_input_registers(
            slave_addr=self._client_addr,
            starting_addr=ireg_address,
            register_qty=register_qty,
            signed=False)

        self.test_logger.debug('Status of IREG {}: {}, expectation: {}'.
                               format(ireg_address,
                                      register_value,
                                      expectation))
        self.assertIsInstance(register_value, tuple)
        self.assertEqual(len(register_value), register_qty)
        self.assertTrue(all(isinstance(x, int) for x in register_value))
        self.assertEqual(register_value, expectation)

    def test_write_single_coil(self) -> None:
        """Test updating single coil of client"""
        coil_address = \
            self._register_definitions['COILS']['EXAMPLE_COIL']['register']
        coil_qty = self._register_definitions['COILS']['EXAMPLE_COIL']['len']
        expectation_list = [
            False, False, False, False, False, False, False, False
        ]
        expectation_list[0] = \
            bool(self._register_definitions['COILS']['EXAMPLE_COIL']['val'])

        #
        # Check clean system (client register data is as initially defined)
        #
        # verify current state by reading coil states
        coil_status = self._host.read_coils(
            slave_addr=self._client_addr,
            starting_addr=coil_address,
            coil_qty=coil_qty)

        self.test_logger.debug(
            'Initial status of COIL {}: {}, expectation: {}'.format(
                coil_address,
                coil_status,
                expectation_list))
        self.assertIsInstance(coil_status, list)
        self.assertEqual(len(coil_status), 8)
        self.assertTrue(all(isinstance(x, bool) for x in coil_status))
        self.assertEqual(coil_status, expectation_list)

        #
        # Test setting coil to True
        #
        # update coil state of client with a different than the current state
        new_coil_val = not expectation_list[0]
        expectation_list[0] = new_coil_val

        operation_status = self._host.write_single_coil(
            slave_addr=self._client_addr,
            output_address=coil_address,
            output_value=new_coil_val)

        self.test_logger.debug(
            '1. Result of setting COIL {} to {}: {}, expectation: {}'.format(
                coil_address, new_coil_val, operation_status, True))
        self.assertIsInstance(operation_status, bool)
        self.assertTrue(operation_status)

        # verify setting of state by reading data back again
        coil_status = self._host.read_coils(
            slave_addr=self._client_addr,
            starting_addr=coil_address,
            coil_qty=coil_qty)

        self.test_logger.debug('1. Status of COIL {}: {}, expectation: {}'.
                               format(coil_address,
                                      coil_status,
                                      expectation_list))
        self.assertIsInstance(coil_status, list)
        self.assertEqual(len(coil_status), 8)
        self.assertTrue(all(isinstance(x, bool) for x in coil_status))
        self.assertEqual(coil_status, expectation_list)

        #
        # Test setting coil to False
        #
        # update coil state of client again with/to original state
        new_coil_val = not expectation_list[0]
        expectation_list[0] = new_coil_val

        operation_status = self._host.write_single_coil(
            slave_addr=self._client_addr,
            output_address=coil_address,
            output_value=new_coil_val)

        self.test_logger.debug(
            '2. Result of setting COIL {} to {}: {}, expectation: {}'.format(
                coil_address, new_coil_val, operation_status, True))
        self.assertIsInstance(operation_status, bool)
        self.assertTrue(operation_status)

        # verify setting of state by reading data back again
        coil_status = self._host.read_coils(
            slave_addr=self._client_addr,
            starting_addr=coil_address,
            coil_qty=coil_qty)

        self.test_logger.debug('2. Status of COIL {}: {}, expectation: {}'.
                               format(coil_address,
                                      coil_status,
                                      expectation_list))
        self.assertIsInstance(coil_status, list)
        self.assertEqual(len(coil_status), 8)
        self.assertTrue(all(isinstance(x, bool) for x in coil_status))
        self.assertEqual(coil_status, expectation_list)

    @unittest.skip('Test not yet implemented')
    def test_write_single_register(self) -> None:
        pass

    @unittest.skip('Test not yet implemented')
    def test_write_multiple_coils(self) -> None:
        pass

    @unittest.skip('Test not yet implemented')
    def test_write_multiple_registers(self) -> None:
        pass

    def tearDown(self) -> None:
        """Run after every test method"""
        pass


if __name__ == '__main__':
    unittest.main()
