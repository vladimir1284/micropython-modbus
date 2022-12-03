#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Unittest for testing the absolute truth"""

# import sys
import ulogging as logging
import unittest


class TestAbsoluteTruth(unittest.TestCase):
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

    def test_absolute_truth(self) -> None:
        """Test the unittest itself"""
        x = 0
        y = 1
        z = 2
        none_thing = None
        some_dict = dict()
        some_list = [x, y, 40, "asdf", z]

        self.assertTrue(True)
        self.assertFalse(False)

        self.assertEqual(y, 1)
        assert y == 1
        with self.assertRaises(AssertionError):
            self.assertEqual(x, y)

        self.assertNotEqual(x, y)
        assert x != y
        with self.assertRaises(AssertionError):
            self.assertNotEqual(x, x)

        self.assertIs(some_list, some_list)
        self.assertIsNot(some_list, some_dict)

        self.assertIsNone(none_thing)
        self.assertIsNotNone(some_dict)

        self.assertIn(y, some_list)
        self.assertNotIn(12, some_list)

        # self.assertRaises(exc, fun, args, *kwds)
        with self.assertRaises(ZeroDivisionError):
            1 / 0

        self.assertIsInstance(some_dict, dict)
        self.assertNotIsInstance(some_list, dict)

        self.assertGreater(y, x)
        self.assertGreaterEqual(y, x)
        self.assertLess(x, y)
        self.assertLessEqual(x, y)

        self.test_logger.warning('Dummy logger warning')

    def testAssert(self):
        e1 = None
        try:
            def func_under_test(a):
                assert a > 10

            self.assertRaises(AssertionError, func_under_test, 20)
        except AssertionError as e:
            e1 = e

        if not e1 or "not raised" not in e1.args[0]:
            self.fail("Expected to catch lack of AssertionError from assert \
                in func_under_test")

    @unittest.skip('Reasoning for skipping this test')
    def testSkip(self):
        self.fail('this should be skipped')

    def testSkipNoDecorator(self):
        do_skip = True

        if do_skip:
            self.skipTest("External resource triggered skipping this test")

        self.fail('this should be skipped')

    @unittest.skipIf('a' in ['a', 'b'], 'Reasoning for skipping another test')
    def testSkipIf(self):
        self.fail('this should be skipped')

    @unittest.skipUnless(42 == 24, 'Reasoning for skipping test 42')
    def testSkipUnless(self):
        self.fail('this should be skipped')

    @unittest.expectedFailure
    def testExpectedFailure(self):
        self.assertEqual(1, 0)

    def testExpectedFailureNot(self):
        @unittest.expectedFailure
        def testInner():
            self.assertEqual(1, 1)
        try:
            testInner()
        except:     # noqa: E722
            pass
        else:
            self.fail("Unexpected success was not detected")

    @unittest.expectedFailure
    def testSubTest(self):
        for i in range(0, 6):
            with self.subTest(i=i):
                # will fail on 1, 3, 5
                # but expect the failure by using the expectedFailure decorator
                self.assertEqual(i % 2, 0)

    def tearDown(self) -> None:
        """Run after every test method"""
        pass


if __name__ == '__main__':
    unittest.main()
