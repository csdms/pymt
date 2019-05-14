import os
import sys

import numpy as np

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

# See https://github.com/numpy/numpy/blob/master/doc/release/1.14.0-notes.rst#many-changes-to-array-printing-disableable-with-the-new-legacy-printing-mode

try:
    np.set_printoptions(legacy="1.13")
except TypeError:
    pass
del np


os.environ.setdefault(
    "UDUNITS2_XML_PATH",
    os.path.abspath(
        os.path.join(sys.prefix, "lib/site-packages/cfunits/etc/udunits/udunits2.xml")
    ),
)

del os, sys
