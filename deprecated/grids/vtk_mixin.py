#! /usr/bin/env python
import warnings

import numpy as np

try:
    from tvtk.api import tvtk
except ImportError:
    warnings.warn("vtk is not installed")

    class VtkGridMixIn:
        pass


else:

    class VtkGridMixIn:
        _EDGE_COUNT_TO_TYPE = {
            1: tvtk.Vertex().cell_type,
            2: tvtk.Line().cell_type,
            3: tvtk.Triangle().cell_type,
            4: tvtk.Quad().cell_type,
        }

        def to_vtk(self):
            points = self.vtk_points()
            cell_types = self.vtk_cell_types()
            cell_array = self.vtk_cell_array()
            offsets = self.vtk_offsets()

            vtk_grid = tvtk.UnstructuredGrid(points=points)
            vtk_grid.set_cells(cell_types, offsets, cell_array)

            return vtk_grid

        def vtk_points(self):
            pad = np.zeros((3 - self._coords.shape[0], self._coords.shape[1]))
            return np.vstack([self._coords, pad]).T

        def vtk_cell_array(self):
            cell_array = tvtk.CellArray()
            cell_array.set_cells(self.get_cell_count(), self.vtk_connectivity())
            return cell_array

        def vtk_cell_types(self):
            cell_types = np.empty(self.get_cell_count(), dtype=int)
            for (id_, n_nodes) in enumerate(self.nodes_per_cell()):
                try:
                    cell_types[id_] = self._EDGE_COUNT_TO_TYPE[n_nodes]
                except KeyError:
                    cell_types[id_] = tvtk.Polygon().cell_type
            return cell_types

        def vtk_connectivity(self):
            cells = np.empty(self.get_vertex_count() + self.get_cell_count(), dtype=int)

            cell_nodes = self.get_connectivity()

            offset = 0
            for n_nodes in self.nodes_per_cell():
                cells[offset] = n_nodes
                offset += n_nodes + 1

            offset = 1
            for cell in self.vtk_offsets():
                n_nodes = cells[offset - 1]
                cells[offset : offset + n_nodes] = cell_nodes[cell : cell + n_nodes]

                offset += n_nodes + 1

            return cells

        def vtk_offsets(self):
            offsets = np.empty(self.get_cell_count(), dtype=int)
            (offsets[0], offsets[1:]) = (0, self._offset[:-1])
            return offsets

        def vtk_write(self, file_name):
            writer = tvtk.XMLUnstructuredGridWriter()
            writer.set_input(self.to_vtk())
            writer.file_name = file_name
            writer.write()
