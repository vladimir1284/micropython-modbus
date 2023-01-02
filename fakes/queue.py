#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
queue.py: adapted from uasyncio V2

Copyright (c) 2018-2020 Peter Hinch
Released under the MIT License (MIT) - see LICENSE file

Code is based on Paul Sokolovsky's work.
This is a temporary solution until uasyncio V3 gets an efficient official
version
"""

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


class QueueEmpty(Exception):
    """Exception raised by get_nowait()"""
    pass


class QueueFull(Exception):
    """Exception raised by put_nowait()"""
    pass


class Queue:
    """AsyncIO based Queue"""
    def __init__(self, maxsize: int = 0):
        self.maxsize = maxsize
        self._queue = []
        self._evput = asyncio.Event()  # Triggered by put, tested by get
        self._evget = asyncio.Event()  # Triggered by get, tested by put

    def _get(self):
        """
        Remove and return an item from the queue without blocking

        :returns:   Return an item if one is immediately available
        :rtype:     Any
        """
        # Schedule all tasks waiting on get
        self._evget.set()
        self._evget.clear()
        return self._queue.pop(0)

    async def get(self):
        """
        Remove and return an item from the queue in async blocking mode

        Usage: item = await queue.get()

        :returns:   Return an item if one is immediately available
        :rtype:     Any
        """
        # May be multiple tasks waiting on get()
        while self.empty():
            # Queue is empty, suspend task until a put occurs
            # 1st of N tasks gets, the rest loop again
            await self._evput.wait()
        return self._get()

    def get_nowait(self):
        """
        Remove and return an item from the queue without blocking

        :returns:   Return an item if one is immediately available
        :rtype:     Any

        :raises     QueueEmpty:  Queue is empty
        :raises     QueueFull:   Queue is full
        """
        if self.empty():
            raise QueueEmpty()
        return self._get()

    def _put(self, val) -> None:
        """
        Put an item into the queue without blocking

        :param      val:        The value
        :type       val:        Any
        """
        # Schedule tasks waiting on put
        self._evput.set()
        self._evput.clear()
        self._queue.append(val)

    async def put(self, val) -> None:
        """
        Put an item into the queue in async blocking mode

        Usage: await queue.put(item)

        :param      val:        The value
        :type       val:        Any

        :raises     QueueFull:  Queue is full
        """
        while self.full():
            # Queue full
            await self._evget.wait()
            # Task(s) waiting to get from queue, schedule first Task
        self._put(val)

    def put_nowait(self, val) -> None:
        """
        Put an item into the queue without blocking

        :param      val:        The value
        :type       val:        Any

        :raises     QueueFull:  Queue is full
        """
        if self.full():
            raise QueueFull()
        self._put(val)

    def qsize(self) -> int:
        """
        Get number of items in the queue

        :returns:   Number of items in the queue
        :rtype:     int
        """
        return len(self._queue)

    def empty(self) -> bool:
        """
        Check is queue is empty

        :returns:   Return True if the queue is empty, False otherwise
        :rtype:     bool
        """
        return len(self._queue) == 0

    def full(self) -> bool:
        """
        Check if queue is full

        Note: if the Queue was initialized with maxsize=0 (the default) or
        any negative number, then full() is never True.

        :returns:   Return True if there are maxsize items in the queue.
        :rtype:     bool
        """
        return self.maxsize > 0 and self.qsize() >= self.maxsize
