#! /bin/env python


class MapperError(Exception):
    """Base class for error in this package."""

    pass


class IncompatibleGridError(MapperError):
    """Error to indicate that the source grid cannot be mapped to the
    destination.
    """

    def __init__(self, dst, src):
        self._src = src
        self._dst = dst

    def __str__(self):
        return "Unable to map {} to {}".format(self._src, self._dst)


class NoMapperError(MapperError):
    def __init__(self, dst, src):
        self._src = src
        self._dst = dst

    def __str__(self):
        return "No mapper to map {} to {}".format(self._src, self._dst)


class IGridMapper:
    """Interface for a grid mapper."""

    def initialize(self, dest_grid, src_grid, **kwds):
        """Initialize the mapper to map from a source grid to a destination
        grid.
        """
        pass

    def run(self, src_values, **kwds):
        """Map values on the source grid to the destination grid."""
        pass
