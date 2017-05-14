#! /usr/bin/env python
import matplotlib.pyplot as plt


def quick_plot(bmi, name, **kwds):
    gid = bmi.get_var_grid(name)
    gtype = bmi.get_grid_type(gid)
    grid = bmi.grid[gid]

    x, y = grid.node_x.values, grid.node_y.values
    z = bmi.get_value(name)

    x_label = '{name} ({units})'.format(name=grid.node_x.standard_name,
                                        units=grid.node_x.units)
    y_label = '{name} ({units})'.format(name=grid.node_y.standard_name,
                                        units=grid.node_y.units)

    if gtype in ('unstructured_triangular', ):
        tris = bmi.get_grid_face_node_connectivity(gid).reshape((-1, 3))
        plt.tripcolor(x, y, tris, z, **kwds)
    elif gtype in ('uniform_rectilinear', 'structured_quad'):
        shape = bmi.get_grid_shape(gid)
        plt.pcolormesh(x, y, z.reshape(shape), **kwds)
    else:
        raise ValueError('no plotter for {gtype}'.format(gtype=gtype))

    plt.gca().set_aspect('equal')
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    cbar = plt.colorbar()
    cbar.ax.set_ylabel(
        '{name} ({units})'.format(name=name, units=bmi.get_var_units(name)))
