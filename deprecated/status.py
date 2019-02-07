#! /bin/env python
"""
>>> from __future__ import print_function
>>> a = CREATED
>>> print(a)
Created
>>> b = INITIALIZING
>>> print(b)
Initializing
>>> c = INITIALIZED
>>> print(c)
Initialized
>>> (a>b, a==b, a<b)
(False, False, True)
>>> (a>=a, a==a, a<=a)
(True, True, True)
"""


class Status(object):
    def __init__(self, string, val):
        self.string = string
        self.val = val

    def __str__(self):
        return self.string

    def __gt__(self, other):
        return self.val > other.val

    def __ge__(self, other):
        return self.val >= other.val

    def __eq__(self, other):
        return self.val == other.val

    def __lt__(self, other):
        return self.val < other.val

    def __le__(self, other):
        return self.val <= other.val


class StatusConst(Status):
    def __init__(self):
        pass


class StatusCreated(StatusConst):
    (string, val) = ("Created", 0)


class StatusInitializing(StatusConst):
    (string, val) = ("Initializing", 10)


class StatusInitialized(StatusConst):
    (string, val) = ("Initialized", 20)


class StatusUpdating(StatusConst):
    (string, val) = ("Updating", 30)


class StatusUpdated(StatusConst):
    (string, val) = ("Updated", 40)


class StatusFinalizing(StatusConst):
    (string, val) = ("Finalizing", 50)


class StatusFinalized(StatusConst):
    (string, val) = ("Finalized", 60)


CREATED = StatusCreated()
INITIALIZING = StatusInitializing()
INITIALIZED = StatusInitialized()
UPDATING = StatusUpdating()
UPDATED = StatusUpdated()
FINALIZING = StatusFinalizing()
FINALIZED = StatusFinalized()

if __name__ == "__main__":
    import doctest

    doctest.testmod()
