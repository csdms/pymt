from cmt.grids.raster import UniformRectilinear, UniformRectilinearPoints
from cmt.grids.rectilinear import Rectilinear, RectilinearPoints
from cmt.grids.structured import Structured, StructuredPoints
from cmt.grids.unstructured import Unstructured, UnstructuredPoints
from cmt.grids.field import (RasterField, RectilinearField, StructuredField,
                             UnstructuredField)

from cmt.grids.assertions import (is_uniform_rectilinear, is_rectilinear,
                                  is_structured, is_unstructured)

from cmt.grids.igrid import DimensionError

