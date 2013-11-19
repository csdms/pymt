import cmt.grids.utils as gutils

from cmt.grids.assertions import (is_rectilinear, is_structured,
                                  is_unstructured)

_NP_TO_NC_TYPE = {
    'float32': 'f4',
    'float64': 'f8',
    'int8': 'i1',
    'int16': 'i2',
    'int32': 'i4',
    'int64': 'i8',
    'uint8': 'u1',
    'uint16': 'u2',
    'uint32': 'u4',
    'uint64': 'u8',
}


def set_netcdf_topology(root, field):
    mesh = root.createVariable('mesh', 'i8')
    mesh.cf_role = 'mesh_topology'
    mesh.topology_dimension = 2
    mesh.node_coordinates = "node_x node_y"
    mesh.face_connectivity = "face_nodes"


def set_netcdf_attributes(root, attributes):
    for (key, val) in attributes.items():
        setattr(root, key, val)


def set_netcdf_rectilinear_dimensions(root, field):
    dimension_sizes = gutils.non_singleton_shape(field)
    dimension_names = gutils.non_singleton_dimension_names(field)

    for (name, size) in zip(dimension_names, dimension_sizes):
        try:
            if name not in root.dimensions:
                root.createDimension(name, size)
        except IndexError:
            pass


def get_var_or_create(root, name, args):
    try:
        var = root.variables[name]
    except KeyError:
        var = root.createVariable(name, *args)


def set_netcdf_rectilinear_coordinates(root, field, long_name={}):
    axis_name = gutils.non_singleton_coordinate_names(field)
    axis_dimensions = gutils.non_singleton_dimension_shape(field)

    for axis in gutils.non_singleton_axes(field):
        var = get_var_or_create(root, axis_name[axis], 'f8',
                                axis_dimensions[axis])
        var[:] = field.get_axis_coordinates(axis=axis)
        var.units = field.get_coordinate_units(axis)
        var.long_name = long_name.get(axis_name[axis],
                                      field.get_coordinate_name(axis))


def set_netcdf_structured_dimensions(root, field):
    set_netcdf_rectilinear_dimensions(root, field)

    node_count = field.get_point_count()
    for name in gutils.non_singleton_dimension_names(field):
        dim_name = 'node_' + name
        try:
            if dim_name not in root.dimensions:
                root.createDimension(dim_name, node_count)
        except IndexError:
            pass


def set_netcdf_structured_coordinates(root, field, long_name={}):
    axis_name = gutils.non_singleton_coordinate_names(field)
    axis_dimensions = gutils.non_singleton_dimension_shape(field)

    for axis in gutils.non_singleton_axes(field):
        dim_name = 'node_' + axis_name[axis]
        var = get_var_or_create(root, dim_name, 'f8', (dim_name, ))
        var[:] = field.get_coordinate(axis=axis)
        var.units = field.get_coordinate_units(axis)
        var.long_name = long_name.get(axis_name[axis],
                                      field.get_coordinate_name(axis))


def set_netcdf_unstructured_dimensions(root, field):
    for name in gutils.non_singleton_dimension_names(field):
        try:
            if name not in root.dimensions:
                root.createDimension('node_' + name, field.get_point_count())
        except IndexError:
            pass

    if 'n_face' not in root.dimensions:
        root.createDimension('n_face', field.get_cell_count())

    if 'n_vertex' not in root.dimensions and field.get_vertex_count() > 0:
        root.createDimension('n_vertex', field.get_vertex_count())


def set_netcdf_unstructured_coordinates(root, field, long_name={}):
    set_netcdf_structured_coordinates(root, field, long_name=long_name)

    face_nodes = get_var_or_create(root, 'face_nodes', 'i8',  ('n_vertex', ))
    face_nodes[:] = field.get_connectivity()
    face_nodes.cf_role = 'face_node_connectivity'
    face_nodes.long_name = 'Maps every face to its corner nodes.'

    offsets = get_var_or_create(root, 'face_nodes_offset', 'i8',  ('n_face', ))
    offsets[:] = field.get_offset()
    offsets.cf_role = 'face_node_offset'
    offsets.long_name = 'Maps face index into connectivity array'


def add_netcdf_data_variable(root, var_name, array, attrs={}):
    var = get_var_or_create(root, var_name, _NP_TO_NC_TYPE[str(array.dtype)],
                            ('time', 'n_node'))

    n_times = get_number_of_times(root)
    if array.size > 1:
        var[n_times,:] = array.flat
    else:
        var[n_times] = array[0]

    for (attr, value) in attrs.items():
        setattr(var, attr, value)


def set_netcdf_unstructured_data(root, field):
    n_times = get_number_of_times(root)

    axis_dimension_names = gutils.non_singleton_dimension_names(field)

    point_fields = field.get_point_fields()
    for (var_name, array) in point_fields.items():
        add_netcdf_data_variable(root, var_name, array,
                                 attrs={
                                     'units': field.get_field_units(var_name),
                                     'standard_name': var_name,
                                     'long_name': var_name,
                                     'location': 'node',
                                     'coordinates': ' '.join(axis_dimension_names)
                                 })


def get_number_of_times(root):
    try:
        return len(root.variables['time']) - 1
    except KeyError:
        return 0


def set_netcdf_time_dimension(root):
    if not 'time' in root.dimensions:
        nt = root.createDimension('time', None)


def set_netcdf_dimensions(root, field):
    """
    Add dimensions for the grid. A structured grid will have dimensions
    nx, ny, and nz that define the shape of the grid. Only dimensions
    less than the rank of the grid are defined. For instance a 2D grid
    will only define nx, and ny.

    In addition, regardless of the grid type, define dimensions n_points and
    n_cells. These give the number of grid points and cells, respectively.
    """

    if is_structured(field, strict=False):
        dimension_sizes = gutils.non_singleton_shape(field)
        dimension_names = gutils.non_singleton_dimension_names(field)

        for (name, size) in zip(dimension_names, dimension_sizes):
            try:
                if name not in root.dimensions:
                    root.createDimension(name, size)
            except IndexError:
                pass

    if not 'time' in root.dimensions:
        nt = root.createDimension('time', None)

    # TODO: We don't really need all of these for some grid types.
    if 'n_node' not in root.dimensions and field.get_point_count() > 1:
        root.createDimension('n_node', field.get_point_count())
    if 'n_cells' not in root.dimensions and field.get_cell_count() > 0:
        root.createDimension('n_cells', field.get_cell_count())
    if 'n_vertices' not in root.dimensions and field.get_vertex_count() > 0:
        root.createDimension('n_vertices', field.get_vertex_count())


def set_netcdf_variables(root, field, time, **kwds):
    kwds['units'] = kwds.pop('time_units', 'days')
    kwds['reference'] = kwds.pop('time_reference', '00:00:00 UTC')
    kwds['time'] = kwds.pop('time', None)
    
    _add_time_variable(root, **kwds)
    _add_spatial_variables(root, field)
    _add_variables_at_points(root, field)
    _add_variables_at_cells(root, field)
    _add_dummy_variable(root)


def _add_time_variable(root, **kwds):
    time = kwds.get('time', None)
    units = kwds.get('units', 'days')
    reference = kwds.get('reference', '00:00:00 UTC')

    try:
        t = root.variables['time']
    except KeyError:
        t = root.createVariable('time', 'f8', ('time', ))
        t.units = ' '.join([units, 'since', reference])
        t.long_name = 'time'
        n_times = 0
    else:
        n_times = len(t)

    if time is not None:
        t[n_times] = time
    else:
        t[n_times] = n_times


def _add_rectilinear_mesh_variables(root, field, long_name={}):
    (vars, dims) = (root.variables, root.dimensions)

    axis_name = gutils.non_singleton_coordinate_names(field)
    axis_dimensions = gutils.non_singleton_dimension_shape(field)

    for axis in gutils.non_singleton_axes(field):
        try:
            var = vars[axis_name[axis]]
        except KeyError:
            var = root.createVariable(axis_name[axis], 'f8',
                                      axis_dimensions[axis])
        finally:
            var[:] = field.get_axis_coordinates(axis=axis)

            var.units = field.get_coordinate_units(axis)
            try:
                var.long_name = long_name[axis_name[axis]]
            except KeyError:
                var.long_name = field.get_coordinate_name(axis)


def _add_structured_mesh_variables(root, field, long_name={}):
    axis_name = gutils.non_singleton_coordinate_names(field)
    axis_dimensions = gutils.non_singleton_dimension_shape(field)

    for axis in gutils.non_singleton_axes(field):
        try:
            var = root.variables['node_' + axis_name[axis]]
        except KeyError:
            var = root.createVariable(axis_name[axis], 'f8',
                                      ('node_' + axis_name[axis], ))
        finally:
            var[:] = field.get_coordinate(axis=axis)

            var.units = field.get_coordinate_units(axis)
            try:
                var.long_name = long_name[axis_name[axis]]
            except KeyError:
                var.long_name = field.get_coordinate_name(axis)


def _add_unstructured_mesh_variables(root, field, long_name={}):
    _add_structured_mesh_variables(root, field, long_name)

    try:
        c = vars['face_nodes']
    except KeyError:
        c = root.createVariable('face_nodes', 'i8', ('n_vertex', ))
    finally:
        c[:] = field.get_connectivity ()
        c.cf_role = 'face_node_connectivity'
        c.long_name = 'Maps every face to its corner nodes.'

    try:
        o = vars['face_nodes_offset']
    except KeyError:
        o = root.createVariable ('face_nodes_offset', 'i8', ('n_face', ))
    finally:
        o[:] = field.get_offset ()
        c.cf_role = 'face_node_offset'
        c.long_name = 'Maps face index into connectivity array'


def _add_spatial_variables(root, field, long_name={}):
    """
    Add variables that define the spatial grid. These include x, y, and z
    coordinates of grid nodes as well as cell connectivity, if necessary.
    """
    (vars, dims) = (root.variables, root.dimensions)

    axis_name = gutils.non_singleton_coordinate_names(field)
    axis_dimensions = gutils.non_singleton_dimension_shape(field)

    for axis in gutils.non_singleton_axes(field):
        try:
            var = vars[axis_name[axis]]
        except KeyError:
            var = root.createVariable(axis_name[axis], 'f8',
                                      axis_dimensions[axis])

        var[:] = field.get_axis_coordinates(axis=axis)

        var.units = field.get_coordinate_units(axis)
        try:
            var.long_name = long_name[axis_name[axis]]
        except KeyError:
            var.long_name = field.get_coordinate_name(axis)

    if is_unstructured(field):
        try:
            c = vars['connectivity']
        except KeyError:
            c = root.createVariable ('connectivity', 'i8', ('n_vertices', ))
            c[:] = field.get_connectivity ()

        try:
            o = vars['offset']
        except KeyError:
            o = root.createVariable ('offset', 'i8', ('n_cells', ))
            o[:] = field.get_offset ()


def _add_variables_at_points(root, field):
    vars = root.variables

    try:
        n_times = len(vars['time']) - 1
    except KeyError:
        n_times = 0

    axis_dimension_names = gutils.non_singleton_dimension_names(field)

    point_fields = field.get_point_fields()
    for (var_name, array) in point_fields.items():
        try:
            var = vars[var_name]
        except KeyError:
            var = root.createVariable(var_name,
                                      _NP_TO_NC_TYPE[str(array.dtype)],
                                      ['time'] + list(axis_dimension_names))

        if array.size > 1:
            var[n_times,:] = array.flat
        else:
            var[n_times] = array[0]

        var.units = field.get_field_units(var_name)
        var.long_name = var_name


def _add_variables_at_cells(root, field):
    vars = root.variables

    try:
        n_times = len(vars['time']) - 1
    except KeyError:
        n_times = 0

    axis_dimension_names = gutils.non_singleton_dimension_names(field)

    cell_fields = field.get_cell_fields()
    for (var_name, array) in cell_fields.items():
        try:
            var = vars[var_name]
        except KeyError:
            var = root.createVariable(var_name,
                                      _NP_TO_NC_TYPE[str(array.dtype)],
                                      ['time'] + ['n_cells'])

        if array.size > 1:
            var[n_times,:] = array.flat
        else:
            var[n_times] = array[0]

        var.units = field.get_field_units(var_name)
        var.long_name = var_name


# TODO: Double-check that this function is still needed.
def _add_dummy_variable(root):
    """
    Add a dummy variable to a netCDF file. This was required to make
    the netCDF file readable by VisIT. It should not be necessary.
    """
    vars = root.variables

    try:
        var = vars['dummy']
    except KeyError:
        var = root.createVariable ('dummy', 'f8', ())
    var[0] = 0.
    var.units = '-'
    var.long_name = 'dummy'
