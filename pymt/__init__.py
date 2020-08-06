import pkg_resources

from ._udunits2 import UnitSystem

__version__ = pkg_resources.get_distribution("pymt").version
__all__ = ["UnitSystem"]

del pkg_resources
