import contextlib
import os


@contextlib.contextmanager
def suppress_stdout():
    null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
    # Save the actual stdout (1) and stderr (2) file descriptors.
    save_fds = [os.dup(1), os.dup(2)]

    os.dup2(null_fds[0], 1)
    os.dup2(null_fds[1], 2)

    yield

    # Re-assign the real stdout/stderr back to (1) and (2)
    os.dup2(save_fds[0], 1)
    os.dup2(save_fds[1], 2)
    # Close the null files
    for fd in null_fds + save_fds:
        os.close(fd)


with suppress_stdout():
    from ._udunits2 import _UnitConverter, _Unit


class UnitConverter(_UnitConverter):

    def __init__(self, src, dst):
        self._src = src
        self._dst = dst

    @property
    def src_units(self):
        return self._src

    @property
    def dst_units(self):
        return self._dst

    @property
    def units(self):
        return self._src, self._dst

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "UnitConverter({0!r}, {1!r})".format(self.src_units, self.dst_units)


class Unit(_Unit):

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self._name

    def __repr__(self):
        return "Unit({0!r})".format(str(self))
