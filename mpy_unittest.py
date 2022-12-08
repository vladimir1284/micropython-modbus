#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Taken from pfalcon's pycopy-lib, see
# https://github.com/pfalcon/pycopy-lib/blob/56ebf2110f3caa63a3785d439ce49b11e13c75c0/unittest/unittest.py
#
# Copyright (c) 2014-2021 Paul Sokolovsky
# Copyright (c) 2014-2020 pycopy-lib contributors

# Copyright (c) 2022 brainelectronics
# Added:
# - New properties in TestResult class
#   - errors
#   - failures
#   - skipped
#   - testsRun
# - All tests or a specific TestCase can be executed
# - sys exit status can be enabled (default) or disabled
# - assertNotIn, assertNotIsInstance, assertLess, assertGreater
# - Shebang header
#
# Fixed:
# - All flake8 warnings
#

import sys
try:
    import io
    import traceback
except ImportError:
    import uio as io
    traceback = None


class SkipTest(Exception):
    pass


class AssertRaisesContext:

    def __init__(self, exc):
        self.expected = exc

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.exception = exc_value
        if exc_type is None:
            assert False, "%r not raised" % self.expected
        if issubclass(exc_type, self.expected):
            return True
        return False


class NullContext:

    def __enter__(self):
        pass

    def __exit__(self, a, b, c):
        pass


class TestCase:
    """
    This class describes a test case.

    https://docs.python.org/3/library/unittest.html
    """
    def __init__(self):
        pass

    def addCleanup(self, func, *args, **kwargs):
        if not hasattr(self, "_cleanups"):
            self._cleanups = []
        self._cleanups.append((func, args, kwargs))

    def doCleanups(self):
        if hasattr(self, "_cleanups"):
            while self._cleanups:
                func, args, kwargs = self._cleanups.pop()
                func(*args, **kwargs)

    def subTest(self, msg=None, **params):
        return NullContext()

    def skipTest(self, reason):
        raise SkipTest(reason)

    def fail(self, msg=''):
        assert False, msg

    def assertEqual(self, x, y, msg=''):
        if not msg:
            msg = "%r vs (expected) %r" % (x, y)
        assert x == y, msg

    def assertNotEqual(self, x, y, msg=''):
        if not msg:
            msg = "%r not expected to be equal %r" % (x, y)
        assert x != y, msg

    def assertLess(self, x, y, msg=None):
        if msg is None:
            msg = "%r is expected to be < %r" % (x, y)
        assert x < y, msg

    def assertLessEqual(self, x, y, msg=None):
        if msg is None:
            msg = "%r is expected to be <= %r" % (x, y)
        assert x <= y, msg

    def assertGreater(self, x, y, msg=None):
        if msg is None:
            msg = "%r is expected to be > %r" % (x, y)
        assert x > y, msg

    def assertGreaterEqual(self, x, y, msg=None):
        if msg is None:
            msg = "%r is expected to be >= %r" % (x, y)
        assert x >= y, msg

    def assertAlmostEqual(self, x, y, places=None, msg='', delta=None):
        if x == y:
            return
        if delta is not None and places is not None:
            raise TypeError("specify delta or places not both")

        if delta is not None:
            if abs(x - y) <= delta:
                return
            if not msg:
                msg = '%r != %r within %r delta' % (x, y, delta)
        else:
            if places is None:
                places = 7
            if round(abs(y - x), places) == 0:
                return
            if not msg:
                msg = '%r != %r within %r places' % (x, y, places)

        assert False, msg

    def assertNotAlmostEqual(self, x, y, places=None, msg='', delta=None):
        if delta is not None and places is not None:
            raise TypeError("specify delta or places not both")

        if delta is not None:
            if not (x == y) and abs(x - y) > delta:
                return
            if not msg:
                msg = '%r == %r within %r delta' % (x, y, delta)
        else:
            if places is None:
                places = 7
            if not (x == y) and round(abs(y - x), places) != 0:
                return
            if not msg:
                msg = '%r == %r within %r places' % (x, y, places)

        assert False, msg

    def assertIs(self, x, y, msg=''):
        if not msg:
            msg = "%r is not %r" % (x, y)
        assert x is y, msg

    def assertIsNot(self, x, y, msg=''):
        if not msg:
            msg = "%r is %r" % (x, y)
        assert x is not y, msg

    def assertIsNone(self, x, msg=''):
        if not msg:
            msg = "%r is not None" % x
        assert x is None, msg

    def assertIsNotNone(self, x, msg=''):
        if not msg:
            msg = "%r is None" % x
        assert x is not None, msg

    def assertTrue(self, x, msg=''):
        if not msg:
            msg = "Expected %r to be True" % x
        assert x, msg

    def assertFalse(self, x, msg=''):
        if not msg:
            msg = "Expected %r to be False" % x
        assert not x, msg

    def assertIn(self, x, y, msg=''):
        if not msg:
            msg = "Expected %r to be in %r" % (x, y)
        assert x in y, msg

    def assertNotIn(self, x, y, msg=''):
        if not msg:
            msg = "Expected %r to be in %r" % (x, y)
        assert x not in y, msg

    def assertIsInstance(self, x, y, msg=''):
        assert isinstance(x, y), msg

    def assertNotIsInstance(self, x, y, msg=''):
        assert not isinstance(x, y), msg

    def assertRaises(self, exc, func=None, *args, **kwargs):
        if func is None:
            return AssertRaisesContext(exc)

        try:
            func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, exc):
                return
            raise

        assert False, "%r not raised" % exc

    def assertWarns(self, warn):
        return NullContext()


def skip(msg):
    def _decor(fun):
        # We just replace original fun with _inner
        def _inner(self):
            raise SkipTest(msg)
        return _inner
    return _decor


def skipIf(cond, msg):
    if not cond:
        return lambda x: x
    return skip(msg)


def skipUnless(cond, msg):
    if cond:
        return lambda x: x
    return skip(msg)


def expectedFailure(test):

    def test_exp_fail(*args, **kwargs):
        try:
            test(*args, **kwargs)
        except:     # noqa: E722
            pass
        else:
            assert False, "unexpected success"

    return test_exp_fail


class TestSuite:
    def __init__(self):
        self._tests = []

    def addTest(self, cls):
        self._tests.append(cls)

    def run(self, result):
        for c in self._tests:
            run_suite(c, result)
        return result


class TestRunner:
    def run(self, suite):
        res = TestResult()
        suite.run(res)

        res.printErrors()
        print("----------------------------------------------------------------------")     # noqa: E501
        print("Ran {} tests\n".format(res.testsRun))
        if res.failuresNum > 0 or res.errorsNum > 0:
            print("FAILED (failures={}, errors={})".format(res.failuresNum,
                                                           res.errorsNum))
        else:
            msg = "OK"
            if res.skippedNum > 0:
                msg += " (skipped={})".format(res.skippedNum)
            print(msg)

        return res


TextTestRunner = TestRunner


class TestResult:
    def __init__(self):
        self.errorsNum = 0
        self.failuresNum = 0
        self.skippedNum = 0
        self._testsRun = 0
        self._errors = []
        self._failures = []
        self._skipped = []

    @property
    def errors(self):
        return self._errors

    @property
    def failures(self):
        return self._failures

    @property
    def skipped(self):
        return self._skipped

    @property
    def testsRun(self):
        return self._testsRun

    def wasSuccessful(self):
        return self.errorsNum == 0 and self.failuresNum == 0

    def printErrors(self):
        # print()
        self.printErrorList(self.errors)
        self.printErrorList(self.failures)

    def printErrorList(self, lst):
        sep = "----------------------------------------------------------------------"  # noqa: E501
        for c, e in lst:
            print("======================================================================")     # noqa: E501
            print(c)
            print(sep)
            print(e)

    def __repr__(self):
        # Format is compatible with CPython.
        return ("<unittest.result.TestResult run={} errors={} failures={}>".
                format(self._testsRun, self.errorsNum, self.failuresNum))


def capture_exc(e):
    buf = io.StringIO()
    if hasattr(sys, "print_exception"):
        sys.print_exception(e, buf)
    elif traceback is not None:
        traceback.print_exception(None, e, sys.exc_info()[2], file=buf)
    return buf.getvalue()


# TODO: Uncompliant
def run_suite(c, test_result):
    if isinstance(c, TestSuite):
        c.run(test_result)
        return

    if isinstance(c, type):
        o = c()
    else:
        o = c
    set_up = getattr(o, "setUp", lambda: None)
    tear_down = getattr(o, "tearDown", lambda: None)
    exceptions = []

    def run_one(m):
        print("{} ({}) ...".format(name, c.__qualname__), end="")
        set_up()
        try:
            test_result._testsRun += 1
            m()
            print(" ok")
        except SkipTest as e:
            print(" skipped:", e.args[0])
            test_result.skippedNum += 1
            test_result._skipped.append((name, e.args[0]))
        except Exception as ex:
            ex_str = capture_exc(ex)
            if isinstance(ex, AssertionError):
                test_result.failuresNum += 1
                test_result._failures.append(((name, c), ex_str))
                print(" FAIL")
            else:
                test_result.errorsNum += 1
                test_result._errors.append(((name, c), ex_str))
                print(" ERROR")
            # Uncomment to investigate failure in detail
            # raise
        finally:
            tear_down()
            o.doCleanups()

    if hasattr(o, "runTest"):
        name = str(o)
        run_one(o.runTest)
        return

    for name in dir(o):
        if name.startswith("test"):
            m = getattr(o, name)
            if not callable(m):
                continue
            run_one(m)
    return exceptions


def test_cases(m):
    for tn in dir(m):
        c = getattr(m, tn)
        if (isinstance(c, object) and
            isinstance(c, type) and
                issubclass(c, TestCase)):
            yield c


def main(name="__main__", fromlist: bool = list(), do_exit: bool = True):
    # Import the complete module of only a subset, see
    # https://docs.python.org/3/library/functions.html#__import__
    if len(fromlist):
        m = __import__(name, globals(), locals(), fromlist)
    else:
        m = __import__(name) if isinstance(name, str) else name
    suite = TestSuite()
    for c in test_cases(m):
        suite.addTest(c)
    runner = TestRunner()
    result = runner.run(suite)

    if do_exit:
        # Terminate with non zero return code in case of failures
        sys.exit(result.failuresNum or result.errorsNum)
