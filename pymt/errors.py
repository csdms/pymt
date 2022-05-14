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
        return f"unknown unit ({self._unit!r})"


class IncompatibleUnitsError(PymtError):
    def __init__(self, src, dst):
        self._src = src
        self._dst = dst

    def __str__(self):
        return f"incompatible units ({self._src!r}, {self._dst!r})"
