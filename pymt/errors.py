#! /usr/bin/env python


class PymtError(Exception):

    pass


class BmiError(PymtError):
    def __init__(self, fname, status):
        self._fname = fname
        self._status = status

    def __str__(self):
        return "Error calling BMI function: {fname} ({code})".format(
            fname=self._fname, code=self._status
        )
