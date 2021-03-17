#! /usr/bin/env python


class PymtError(Exception):

    pass


class BmiError(PymtError):
    def __init__(self, fname, status):
        self._fname = fname
        self._status = status

    def __str__(self):
        return "error calling BMI function: {fname} ({code})".format(
            fname=self._fname, code=self._status
        )


class BadUnitError(PymtError):
    def __init__(self, unit):
        self._unit = unit

    def __str__(self):
        return "unknown unit ({0!r})".format(self._unit)


class IncompatibleUnitsError(PymtError):
    def __init__(self, src, dst):
        self._src = src
        self._dst = dst

    def __str__(self):
        return "incompatible units ({0!r}, {1!r})".format(self._src, self._dst)
