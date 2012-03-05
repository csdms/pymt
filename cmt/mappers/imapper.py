#! /bin/env python

class IGridMapper (object):
    """Interface for a grid mapper."""
    def initialize (self, dest_grid, src_grid):
        """Initialize the mapper to map from a source grid to a destination grid."""
        pass
    def run (self, src_values):
        """Map values on the source grid to the destination grid."""
        pass

if __name__ == "__main__":
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)

