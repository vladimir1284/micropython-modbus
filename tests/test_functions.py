#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Unittest for testing functions of umodbus"""

import ulogging as logging
import unittest
from umodbus import functions
from umodbus import const as Const


class TestFunctions(unittest.TestCase):
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

    def test_read_coils(self) -> None:
        """Test creation of Modbus Protocol Data Unit for coil reading"""
        modbus_pdu = functions.read_coils(starting_address=19, quantity=11)

        self.assertIsInstance(modbus_pdu, bytes)
        self.assertEqual(len(modbus_pdu), 5)
        self.assertEqual(modbus_pdu, b'\x01\x00\x13\x00\x0b')

        with self.assertRaises(ValueError):
            functions.read_coils(starting_address=42, quantity=0)

        with self.assertRaises(ValueError):
            functions.read_coils(starting_address=69, quantity=2001)

    def test_read_discrete_inputs(self) -> None:
        """
        Test creation of Modbus Protocol Data Unit for discrete inputs reading
        """
        modbus_pdu = functions.read_discrete_inputs(starting_address=196,
                                                    quantity=22)

        self.assertIsInstance(modbus_pdu, bytes)
        self.assertEqual(len(modbus_pdu), 5)
        self.assertEqual(modbus_pdu, b'\x02\x00\xC4\x00\x16')

        with self.assertRaises(ValueError):
            functions.read_discrete_inputs(starting_address=42, quantity=0)

        with self.assertRaises(ValueError):
            functions.read_discrete_inputs(starting_address=69, quantity=2001)

    def test_read_holding_registers(self) -> None:
        """
        Test creation of Modbus Protocol Data Unit for holding register reading
        """
        modbus_pdu = functions.read_holding_registers(starting_address=107,
                                                      quantity=3)

        self.assertIsInstance(modbus_pdu, bytes)
        self.assertEqual(len(modbus_pdu), 5)
        self.assertEqual(modbus_pdu, b'\x03\x00\x6B\x00\x03')

        with self.assertRaises(ValueError):
            functions.read_holding_registers(starting_address=42, quantity=0)

        with self.assertRaises(ValueError):
            functions.read_holding_registers(starting_address=69, quantity=126)

    def test_read_input_registers(self) -> None:
        """
        Test creation of Modbus Protocol Data Unit for input registers reading
        """
        modbus_pdu = functions.read_input_registers(starting_address=8,
                                                    quantity=1)

        self.assertIsInstance(modbus_pdu, bytes)
        self.assertEqual(len(modbus_pdu), 5)
        self.assertEqual(modbus_pdu, b'\x04\x00\x08\x00\x01')

        with self.assertRaises(ValueError):
            functions.read_input_registers(starting_address=42, quantity=0)

        with self.assertRaises(ValueError):
            functions.read_input_registers(starting_address=69, quantity=126)

    def test_write_single_coil(self) -> None:
        """
        Test creation of Modbus Protocol Data Unit for single coil writing
        """
        for on_state in [1, 0xFF00, True]:
            with self.subTest(on_state=on_state):
                modbus_pdu = functions.write_single_coil(output_address=172,
                                                         output_value=on_state)

                self.assertIsInstance(modbus_pdu, bytes)
                self.assertEqual(len(modbus_pdu), 5)
                self.assertEqual(modbus_pdu, b'\x05\x00\xAC\xFF\x00')

        for off_state in [0, 0x0000, False]:
            with self.subTest(off_state=off_state):
                modbus_pdu = functions.write_single_coil(output_address=199,
                                                         output_value=off_state)

                self.assertIsInstance(modbus_pdu, bytes)
                self.assertEqual(len(modbus_pdu), 5)
                self.assertEqual(modbus_pdu, b'\x05\x00\xC7\x00\x00')

        for valid_state in [0, 1, 0x0000, 0xFF00, False, True]:
            with self.subTest(valid_state=valid_state):
                try:
                    modbus_pdu = functions.write_single_coil(
                        output_address=142,
                        output_value=valid_state)

                    self.assertIsInstance(modbus_pdu, bytes)
                    self.assertEqual(len(modbus_pdu), 5)
                except ValueError:
                    self.fail("write_single_coil() raised unexpected \
                        ValueError")

        with self.assertRaises(ValueError):
            functions.write_single_coil(output_address=69, output_value='on')

        with self.assertRaises(ValueError):
            functions.write_single_coil(output_address=69, output_value=0xFF01)

    def test_write_single_register(self) -> None:
        """
        Test creation of Modbus Protocol Data Unit for single registers writing
        """
        # test signed value
        modbus_pdu = functions.write_single_register(register_address=1,
                                                     register_value=3)

        self.assertIsInstance(modbus_pdu, bytes)
        self.assertEqual(len(modbus_pdu), 5)
        self.assertEqual(modbus_pdu, b'\x06\x00\x01\x00\x03')

        # test signed value
        modbus_pdu = functions.write_single_register(register_address=1,
                                                     register_value=-3)

        self.assertIsInstance(modbus_pdu, bytes)
        self.assertEqual(len(modbus_pdu), 5)
        self.assertEqual(modbus_pdu, b'\x06\x00\x01\xFF\xFD')

        # test unsigned value
        modbus_pdu = functions.write_single_register(register_address=1,
                                                     register_value=3,
                                                     signed=False)

        self.assertIsInstance(modbus_pdu, bytes)
        self.assertEqual(len(modbus_pdu), 5)
        self.assertEqual(modbus_pdu, b'\x06\x00\x01\x00\x03')

    def test_write_multiple_coils(self) -> None:
        """
        Test creation of Modbus Protocol Data Unit for multiple coils writing
        """
        # write 11 coils starting at coil 20
        value_list_int = [1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1]
        #                  27 26 25 24 23 22 21 20  -  -  -  -  -  - 29 28
        # value_list_int = [1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1]
        value_list_bool = [
            True, True, False, False, True, True, False, True, False, True,
            True
        ]

        for value_list in [value_list_int, value_list_bool]:
            with self.subTest(value_list=value_list):
                modbus_pdu = functions.write_multiple_coils(
                    starting_address=19,
                    value_list=value_list)

                self.assertIsInstance(modbus_pdu, bytes)
                self.assertEqual(len(modbus_pdu), 8)
                self.assertEqual(modbus_pdu,
                                 b'\x0F\x00\x13\x00\x0B\x02\xCD\x03')

    def test_write_multiple_registers(self) -> None:
        """
        Test creation of Modbus Protocol Data Unit for single registers writing
        """
        # test signed value
        register_values = [10, 258]
        modbus_pdu = functions.write_multiple_registers(
            starting_address=1,
            register_values=register_values)

        self.assertIsInstance(modbus_pdu, bytes)
        self.assertEqual(len(modbus_pdu), 10)
        self.assertEqual(modbus_pdu,
                         b'\x10\x00\x01\x00\x02\x04\x00\x0A\x01\x02')

        # test signed value
        register_values = [10, -258]
        modbus_pdu = functions.write_multiple_registers(
            starting_address=1,
            register_values=register_values)

        self.assertIsInstance(modbus_pdu, bytes)
        self.assertEqual(len(modbus_pdu), 10)
        self.assertEqual(modbus_pdu,
                         b'\x10\x00\x01\x00\x02\x04\x00\x0A\xFE\xFE')

        # test unsigned value
        register_values = [10, 258]
        modbus_pdu = functions.write_multiple_registers(
            starting_address=1,
            register_values=register_values,
            signed=False)

        self.assertIsInstance(modbus_pdu, bytes)
        self.assertEqual(len(modbus_pdu), 10)
        self.assertEqual(modbus_pdu,
                         b'\x10\x00\x01\x00\x02\x04\x00\x0A\x01\x02')

        register_values = [7] * 124
        with self.assertRaises(ValueError):
            functions.write_multiple_registers(starting_address=42,
                                               register_values=register_values)

    def test_validate_resp_data_single_coil(self) -> None:
        """Test response data validation of writing single coil"""
        # test response of writing single coil to ON
        starting_address = 172
        output_value = 0xFF00
        resp_data = b'\x05\x00\xAC\xFF\x00'[1:]
        result = functions.validate_resp_data(
            data=resp_data,
            function_code=Const.WRITE_SINGLE_COIL,
            address=starting_address,
            value=output_value,
            signed=False
        )

        self.assertIsInstance(result, bool)
        self.assertTrue(result)

        # test response of writing single coil to OFF
        starting_address = 199
        output_value = 0x0000
        resp_data = b'\x05\x00\xC7\x00\x00'[1:]
        result = functions.validate_resp_data(
            data=resp_data,
            function_code=Const.WRITE_SINGLE_COIL,
            address=starting_address,
            value=output_value,
            signed=False
        )

        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_validate_resp_data_single_register(self) -> None:
        """Test response data validation of writing single register"""
        # test response of writing single register to 3
        starting_address = 1
        output_value = 3
        resp_data = b'\x06\x00\x01\x00\x03'[1:]
        result = functions.validate_resp_data(
            data=resp_data,
            function_code=Const.WRITE_SINGLE_REGISTER,
            address=starting_address,
            value=output_value,
            signed=True
        )

        self.assertIsInstance(result, bool)
        self.assertTrue(result)

        # test response of writing single register to -3
        starting_address = 1
        output_value = -3
        resp_data = b'\x06\x00\x01\xFF\xFD'[1:]
        result = functions.validate_resp_data(
            data=resp_data,
            function_code=Const.WRITE_SINGLE_REGISTER,
            address=starting_address,
            value=output_value,
            signed=True
        )

        self.assertIsInstance(result, bool)
        self.assertTrue(result)

        # test response of writing single register to -3 unsigned
        starting_address = 1
        output_value = 3
        resp_data = b'\x06\x00\x01\x00\x03'[1:]
        result = functions.validate_resp_data(
            data=resp_data,
            function_code=Const.WRITE_SINGLE_REGISTER,
            address=starting_address,
            value=output_value,
            signed=False
        )

        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_validate_resp_data_multiple_coils(self) -> None:
        """Test response data validation of writing multiple coils"""
        # test response of writing multiple coils
        value_list_int = [1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1]
        #                  27 26 25 24 23 22 21 20  -  -  -  -  -  - 29 28
        # value_list_int = [1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1]
        value_list_bool = [
            True, True, False, False, True, True, False, True, False, True,
            True
        ]
        starting_address = 19
        resp_data = b'\x0F\x00\x13\x00\x0B'[1:]

        for value_list in [value_list_int, value_list_bool]:
            with self.subTest(value_list=value_list):
                result = functions.validate_resp_data(
                    data=resp_data,
                    function_code=Const.WRITE_MULTIPLE_COILS,
                    address=starting_address,
                    quantity=len(value_list)
                )

                self.assertIsInstance(result, bool)
                self.assertTrue(result)

    def test_validate_resp_data_multiple_register(self) -> None:
        """Test response data validation of writing multiple registers"""
        starting_address = 1

        # test response of writing multiple registers with signed value
        register_values = [10, 258]
        resp_data = b'\x10\x00\x01\x00\x02\x04\x00\x0A\x01\x02'[1:]
        result = functions.validate_resp_data(
            data=resp_data,
            function_code=Const.WRITE_MULTIPLE_REGISTERS,
            address=starting_address,
            quantity=len(register_values)
        )

        self.assertIsInstance(result, bool)
        self.assertTrue(result)

        # test response of writing multiple registers with signed value
        register_values = [10, -258]
        resp_data = b'\x10\x00\x01\x00\x02\x04\x00\x0A\xFE\xFE'[1:]
        result = functions.validate_resp_data(
            data=resp_data,
            function_code=Const.WRITE_MULTIPLE_REGISTERS,
            address=starting_address,
            quantity=len(register_values)
        )

        self.assertIsInstance(result, bool)
        self.assertTrue(result)

        # test response of writing multiple registers with unsigned value
        register_values = [10, 258]
        resp_data = b'\x10\x00\x01\x00\x02\x04\x00\x0A\x01\x02'[1:]
        result = functions.validate_resp_data(
            data=resp_data,
            function_code=Const.WRITE_MULTIPLE_REGISTERS,
            address=starting_address,
            quantity=len(register_values),
            signed=False
        )

        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    @unittest.skip('Test not yet implemented')
    def test_response(self) -> None:
        pass

    def test_exception_response(self) -> None:
        """Test exception responses"""
        function_code = Const.READ_COILS
        exception_code = Const.ILLEGAL_DATA_ADDRESS

        result = functions.exception_response(function_code=function_code,
                                              exception_code=exception_code)

        self.assertIsInstance(result, bytes)
        self.assertEqual(len(result), 2)
        self.assertEqual(result, b'\x81\x02')

    def test_bytes_to_bool(self) -> None:
        """Convert bytes list to boolean list"""
        possibilities = [
            # response, qty, expectation
            (b'\x00', 1, [False]),
            (b'\x01', 1, [True]),

            (b'\x00', 2, [False, False]),
            (b'\x01', 2, [True, False]),
            (b'\x02', 2, [False, True]),
            (b'\x03', 2, [True, True]),

            (b'\x00', 3, [False, False, False]),
            (b'\x01', 3, [True, False, False]),
            (b'\x02', 3, [False, True, False]),
            (b'\x03', 3, [True, True, False]),
            (b'\x04', 3, [False, False, True]),
            (b'\x05', 3, [True, False, True]),
            (b'\x06', 3, [False, True, True]),
            (b'\x07', 3, [True, True, True]),

            (b'\x00', 4, [False, False, False, False]),
            # (b'\x05', 4, [False, True, False, True]),
            (b'\x05', 4, [True, False, True, False]),
            (b'\x0A', 4, [False, True, False, True]),
            (b'\x0F', 4, [True, True, True, True]),

            (b'\x0A', 5, [False, True, False, True, False]),
        ]
        for pair in possibilities:
            with self.subTest(pair=pair):
                byte_list = pair[0]
                bit_qty = pair[1]
                expectation = pair[2]

                result = functions.bytes_to_bool(byte_list=byte_list,
                                                 bit_qty=bit_qty)
                self.assertIsInstance(result, list)
                self.assertEqual(len(result), len(expectation))
                self.assertTrue(all(isinstance(x, bool) for x in result))
                self.assertEqual(result, expectation)

    def test_to_short(self) -> None:
        """Convert bytes list to integer tuple"""
        possibilities = [
            # response, signed, expectation
            (b'\x00\x00', True, (0,)),
            (b'\x00\x14', True, (20,)),

            (b'\x00\x00\x00\x00', True, (0, 0)),
            (b'\x00\x00\x00\x07', True, (0, 7)),
            (b'\x00\x17\x00\x00', True, (23, 0)),
            (b'\x00\x0c\x00\x13', True, (12, 19)),

            (b'\x00\x00\x00\x00\x00\x00', True, (0, 0, 0)),
            (b'\x00\x09\x00\x00\x00\x00', True, (9, 0, 0)),
            (b'\x00\x00\x00\x01\x00\x00', True, (0, 1, 0)),
            (b'\x00\x00\x00\x00\x00\x07', True, (0, 0, 7)),
            (b'\x00\x1d\x00\x26\x00\x00', True, (29, 38, 0)),
            (b'\x00\x11\x00\x00\x00\x04', True, (17, 0, 4)),
            (b'\x09\x29\x00\x25\x11\x5c', True, (2345, 37, 4444)),
        ]
        for pair in possibilities:
            with self.subTest(pair=pair):
                byte_array = pair[0]
                signed = pair[1]
                expectation = pair[2]

                result = functions.to_short(byte_array=byte_array,
                                            signed=signed)
                self.assertIsInstance(result, tuple)
                self.assertEqual(len(result), len(expectation))
                self.assertTrue(all(isinstance(x, int) for x in result))
                self.assertEqual(result, expectation)

    def test_float_to_bin(self) -> None:
        """Test conversion of float to bin according to IEEE 754"""
        float_val = 10.27
        expectation = '01000001001001000101000111101100'

        result = functions.float_to_bin(num=float_val)
        self.assertIsInstance(result, str)
        self.assertEqual(result, expectation)

    def test_bin_to_float(self) -> None:
        """Test conversion of binary string to float"""
        binary = '01000001001001000101000111101100'
        expectation = 10.27

        result = functions.bin_to_float(binary=binary)
        self.assertIsInstance(result, float)
        self.assertAlmostEqual(result, expectation, delta=0.01)

    def test_int_to_bin(self) -> None:
        """Test conversion of integer to binary"""
        number = 123
        expectation = '1111011'

        result = functions.int_to_bin(num=number)
        self.assertIsInstance(result, str)
        self.assertEqual(result, expectation)

    def tearDown(self) -> None:
        """Run after every test method"""
        pass


if __name__ == '__main__':
    unittest.main()
