import pkg_resources

from gimli import UnitSystem
from .model_collection import ModelCollection

MODELS = ModelCollection()

__version__ = pkg_resources.get_distribution("pymt").version
__all__ = ["UnitSystem", "MODELS"]

del pkg_resources
