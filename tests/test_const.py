#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Unittest for testing const definitions of umodbus"""

from umodbus.typing import List
import ulogging as logging
import unittest
from umodbus import const as Const


class TestConst(unittest.TestCase):
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

    def test_function_codes(self) -> None:
        """Test Modbus function codes"""
        self.assertEqual(Const.READ_COILS, 0x01)
        self.assertEqual(Const.READ_DISCRETE_INPUTS, 0x02)
        self.assertEqual(Const.READ_HOLDING_REGISTERS, 0x03)
        self.assertEqual(Const.READ_INPUT_REGISTER, 0x04)

        self.assertEqual(Const.WRITE_SINGLE_COIL, 0x05)
        self.assertEqual(Const.WRITE_SINGLE_REGISTER, 0x06)
        self.assertEqual(Const.WRITE_MULTIPLE_COILS, 0x0F)
        self.assertEqual(Const.WRITE_MULTIPLE_REGISTERS, 0x10)

        self.assertEqual(Const.MASK_WRITE_REGISTER, 0x16)
        self.assertEqual(Const.READ_WRITE_MULTIPLE_REGISTERS, 0x17)

        self.assertEqual(Const.READ_FIFO_QUEUE, 0x18)

        self.assertEqual(Const.READ_FILE_RECORD, 0x14)
        self.assertEqual(Const.WRITE_FILE_RECORD, 0x15)

        self.assertEqual(Const.READ_EXCEPTION_STATUS, 0x07)
        self.assertEqual(Const.DIAGNOSTICS, 0x08)
        self.assertEqual(Const.GET_COM_EVENT_COUNTER, 0x0B)
        self.assertEqual(Const.GET_COM_EVENT_LOG, 0x0C)
        self.assertEqual(Const.REPORT_SERVER_ID, 0x11)
        self.assertEqual(Const.READ_DEVICE_IDENTIFICATION, 0x2B)

    def test_exception_codes(self) -> None:
        """Test Modbus exception codes"""
        self.assertEqual(Const.ILLEGAL_FUNCTION, 0x01)
        self.assertEqual(Const.ILLEGAL_DATA_ADDRESS, 0x02)
        self.assertEqual(Const.ILLEGAL_DATA_VALUE, 0x03)
        self.assertEqual(Const.SERVER_DEVICE_FAILURE, 0x04)
        self.assertEqual(Const.ACKNOWLEDGE, 0x05)
        self.assertEqual(Const.SERVER_DEVICE_BUSY, 0x06)
        self.assertEqual(Const.MEMORY_PARITY_ERROR, 0x08)
        self.assertEqual(Const.GATEWAY_PATH_UNAVAILABLE, 0x0A)
        self.assertEqual(Const.DEVICE_FAILED_TO_RESPOND, 0x0B)

    def test_pdu_constants(self) -> None:
        """Test Modbus Protocol Data Unit constants"""
        self.assertEqual(Const.CRC_LENGTH, 0x02)
        self.assertEqual(Const.ERROR_BIAS, 0x80)
        self.assertEqual(Const.RESPONSE_HDR_LENGTH, 0x02)
        self.assertEqual(Const.ERROR_RESP_LEN, 0x05)
        self.assertEqual(Const.FIXED_RESP_LEN, 0x08)
        self.assertEqual(Const.MBAP_HDR_LENGTH, 0x07)

    def test_crc16_table(self):
        """Test CRC16-Modbus table"""
        def generate_crc16_table() -> List[int, ...]:
            crc_table = []
            for byte in range(256):
                crc = 0x0000
                for _ in range(8):
                    if (byte ^ crc) & 0x0001:
                        crc = (crc >> 1) ^ 0xa001
                    else:
                        crc >>= 1
                    byte >>= 1
                crc_table.append(crc)
            return crc_table

        crc16_table = generate_crc16_table()
        self.assertEqual(len(crc16_table), 256)
        self.assertEqual(len(Const.CRC16_TABLE), 256)
        for idx, ele in enumerate(crc16_table):
            with self.subTest(ele=ele, idx=idx):
                self.assertEqual(ele, Const.CRC16_TABLE[idx])

    def tearDown(self) -> None:
        """Run after every test method"""
        pass


if __name__ == '__main__':
    unittest.main()
