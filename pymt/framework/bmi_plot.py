#! /usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np


def quick_plot(bmi, name, **kwds):
    if bmi.var_location(name) == "none":
        raise ValueError(f"{name} does not have an associated grid to plot")

    gid = bmi.var_grid(name)
    gtype = bmi.grid_type(gid)
    grid = bmi.grid[gid]

    x_label = "{name} ({units})".format(
        name=grid.node_x.standard_name, units=grid.node_x.units
    )
    y_label = "{name} ({units})".format(
        name=grid.node_y.standard_name, units=grid.node_y.units
    )

    z = bmi.get_value(name)

    if gtype.startswith("unstructured"):
        x, y = grid.node_x.values, grid.node_y.values
        nodes_per_face = bmi.grid_nodes_per_face(gid)
        if np.all(nodes_per_face == 3):
            tris = bmi.grid_face_nodes(gid).reshape((-1, 3))
            # tris = bmi.grid_face_node_connectivity(gid).reshape((-1, 3))
            plt.tripcolor(x, y, tris, z, **kwds)
        else:
            raise ValueError("quickplot is only able to plot unstructured meshes of triangles")
    elif gtype in ("uniform_rectilinear", "structured_quad"):
        shape = bmi.grid_shape(gid)
        spacing = bmi.grid_spacing(gid)
        origin = bmi.grid_origin(gid)
        x = np.arange(shape[-1]) * spacing[-1] + origin[-1]
        y = np.arange(shape[-2]) * spacing[-2] + origin[-2]
        plt.pcolormesh(x, y, z.reshape(shape), **kwds)
    else:
        raise ValueError("no plotter for {gtype}".format(gtype=gtype))

    plt.axis("tight")
    plt.gca().set_aspect("equal")
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    cbar = plt.colorbar()
    cbar.ax.set_ylabel("{name} ({units})".format(name=name, units=bmi.var_units(name)))
