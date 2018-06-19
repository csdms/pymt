from __future__ import print_function
import sys

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# See https://github.com/numpy/numpy/blob/master/doc/release/1.14.0-notes.rst#many-changes-to-array-printing-disableable-with-the-new-legacy-printing-mode
import numpy as np
try:
    np.set_printoptions(legacy='1.13')
except TypeError:
    pass
del np


from .plugin import load_pymt_plugins


plugins = load_pymt_plugins(include_old_style=True)

del load_pymt_plugins
