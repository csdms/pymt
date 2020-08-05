from ._version import get_versions
from ._udunits2 import UnitSystem


__all__ = ["UnitSystem"]

__version__ = get_versions()["version"]
del get_versions
