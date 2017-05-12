from collections import OrderedDict

import numpy as np
import xarray as xr


COORDINATE_NAMES = ['z', 'y', 'x']
INDEX_NAMES = ['i', 'j', 'k']


def index_names(rank):
    return ['node_' + ind for ind in INDEX_NAMES[:rank]]


def coordinate_names(rank):
    return ['node_' + d for d in COORDINATE_NAMES[-rank:]]


def dataset_from_bmi_grid(bmi, grid_id):
    grid_type = bmi.get_grid_type(grid_id)
    if grid_type == 'points':
        grid = dataset_from_bmi_points(bmi, grid_id)
    elif grid_type == 'uniform_rectilinear':
        grid = dataset_from_bmi_uniform_rectilinear(bmi, grid_id)
    elif grid_type == 'scalar':
        grid = dataset_from_bmi_scalar(bmi, grid_id)
    # elif grid_type == 'unstructured':
    elif grid_type.startswith('unstructured'):
        grid = dataset_from_bmi_unstructured(bmi, grid_id)
    else:
        raise ValueError(
            'grid type not understood ({gtype})'.format(gtype=grid_type))

    return grid


def dataset_from_bmi_scalar(bmi, grid_id):
    rank = bmi.get_grid_rank(grid_id)

    if rank != 0:
        raise ValueError('scalar must be rank 0')

    attrs=OrderedDict([
        ('cf_role', 'grid_topology'),
        ('long_name', 'scalar value'),
        ('topology_dimension', rank),
        ('type', 'scalar'),
    ])

    return xr.Dataset( {'mesh': xr.DataArray(data=grid_id, attrs=attrs), })


def dataset_from_bmi_uniform_rectilinear(bmi, grid_id):
    rank = bmi.get_grid_rank(grid_id)
    shape = bmi.get_grid_shape(grid_id)
    spacing = bmi.get_grid_spacing(grid_id)
    origin = bmi.get_grid_origin(grid_id)

    if rank < 1 or rank > 3:
        raise ValueError('uniform rectilinear grids must be rank 1, 2, or 3')

    attrs=OrderedDict([
        ('cf_role', 'grid_topology'),
        ('long_name',
         'Topology data of {rank}D structured quadrilateral'.format(rank=rank)),
        ('topology_dimension', rank),
        ('node_coordinates', ' '.join(coordinate_names(rank))),
        ('node_dimensions', ' '.join(index_names(rank))),
        ('node_spacing', 'node_spacing'),
        ('node_origin', 'node_origin'),
        ('type', 'structured_quad'),
    ])
    dataset = xr.Dataset(
        {'mesh': xr.DataArray(data=grid_id, attrs=attrs),
         'node_shape': xr.DataArray(data=shape, dims=('rank', )),
         'node_spacing': xr.DataArray(data=spacing, dims=('rank', )),
         'node_origin': xr.DataArray(data=origin, dims=('rank', )),
        })

    dim_names = dataset.mesh.attrs['node_dimensions'].split()
    coord_names = dataset.mesh.attrs['node_coordinates'].split()
    for dim in xrange(rank):
        data = np.arange(shape[dim], dtype=float) * spacing[dim] + origin[dim]
        dataset = dataset.update({
            coord_names[dim]: xr.DataArray(
                data=data, dims=(dim_names[dim], ),
                attrs={'standard_name': coord_names[dim], 'units': 'm'})
        })

    return dataset


def dataset_from_bmi_points(bmi, grid_id):
    rank = bmi.get_grid_rank(grid_id)
    attrs=OrderedDict([
        ('cf_role', 'mesh_topology'),
        ('long_name', 'Topology data of 2D unstructured points'),
        ('topology_dimension', rank),
        ('node_coordinates', 'node_x node_y'),
        ('type', 'points'),
    ])

    ugrid = xr.Dataset({'mesh': xr.DataArray(data=grid_id, attrs=attrs)})

    coords = {}
    for dim_name in COORDINATE_NAMES[:-(rank + 1):-1]:
        data=getattr(bmi, 'get_grid_' + dim_name)(grid_id)
        coord = xr.DataArray(
            data=data,
            dims=('n_node', ),
            attrs={'standard_name': dim_name, 'units': 'm'})
        coords['node_' + dim_name] = coord

    ugrid.update(coords)

    return ugrid


def dataset_from_bmi_unstructured(bmi, grid_id):
    rank = bmi.get_grid_rank(grid_id)
    attrs=OrderedDict([
        ('cf_role', 'mesh_topology'),
        ('long_name', 'Topology data of 2D unstructured points'),
        ('topology_dimension', rank),
        ('node_coordinates', 'node_x node_y'),
        ('type', 'unstructured'),
    ])

    ugrid = xr.Dataset({'mesh': xr.DataArray(data=grid_id, attrs=attrs)})

    coords = {}
    for dim_name in COORDINATE_NAMES[:-(rank + 1):-1]:
        data=getattr(bmi, 'get_grid_' + dim_name)(grid_id)
        coord = xr.DataArray(
            data=data,
            dims=('n_node', ),
            attrs={'standard_name': dim_name, 'units': 'm'})
        coords['node_' + dim_name] = coord

    ugrid.update(coords)

    face_node_connectivity = xr.DataArray(
        data=bmi.get_grid_face_node_connectivity(grid_id),
        dims=('n_vertices', ),
        attrs={'standard_name': 'Face-node connectivity'})
    ugrid.update({'face_node_connectivity': face_node_connectivity})

    return ugrid
