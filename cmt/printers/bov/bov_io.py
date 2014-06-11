#! /bin/env python

import os
import sys

import numpy as np

from ...grids import RasterField


class BovError(Exception):
    pass


class MissingRequiredKeyError(BovError):
    def __init__(self, opt):
        self.opt = opt

    def __str__(self):
        return '%s: Missing required key' % self.opt


class BadKeyValueError(BovError):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return '%s, %s: Bad value' % (self.key, self.value)


class ReadError(BovError):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return '%s: Unable to read' % self.filename


class FileExists(BovError):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return '%s: Unable to write to file' % self.filename


class BadFileExtension(BovError):
    def __init__(self, ext):
        self.ext = ext

    def __str__(self):
        return "%s: Extension should be '.bov' or empty" % self.ext


_BOV_TO_NP_TYPE = {'BYTE': 'uint8', 'SHORT': 'int32', 'INT': 'int64',
                   'FLOAT': 'float32', 'DOUBLE': 'float64'}
_NP_TO_BOV_TYPE = dict(zip(_BOV_TO_NP_TYPE.values(), _BOV_TO_NP_TYPE.keys()))
_SYS_TO_BOV_ENDIAN = {'little': 'LITTLE', 'big': 'BIG'}


def array_to_str(array):
    s = [str(x) for x in array]
    return ' '.join(s)


def fromfile(filename, allow_singleton=True):
    header = {}
    with open(filename, 'r') as f:
        for line in f:
            try:
                (data, comment) = line.split('#')
            except ValueError:
                data = line
            try:
                (key, value) = data.split(':')
                header[key.strip()] = value.strip()
            except ValueError:
                pass

    keys_found = set(header.keys())
    keys_required = {'DATA_SIZE', 'DATA_FORMAT', 'DATA_FILE', 'BRICK_ORIGIN',
                     'BRICK_SIZE', 'VARIABLE'}
    if not keys_required.issubset(keys_found):
        missing = ', '.join(keys_required-keys_found)
        raise MissingRequiredKeyError(missing)

    shape = header['DATA_SIZE'].split()
    header['DATA_SIZE'] = np.array([int(i) for i in shape], dtype=np.int64)

    origin = header['BRICK_ORIGIN'].split()
    header['BRICK_ORIGIN'] = np.array([float(i) for i in origin],
                                      dtype=np.float64)

    size = header['BRICK_SIZE'].split()
    header['BRICK_SIZE'] = np.array([float(i) for i in size], dtype=np.float64)

    if not allow_singleton:
        not_singleton = header['DATA_SIZE'] > 1
        header['DATA_SIZE'] = header['DATA_SIZE'][not_singleton]
        header['BRICK_SIZE'] = header['BRICK_SIZE'][not_singleton]
        header['BRICK_ORIGIN'] = header['BRICK_ORIGIN'][not_singleton]

    type_str = header['DATA_FORMAT']
    try:
        data_type = _BOV_TO_NP_TYPE[type_str]
    except KeyError:
        raise BadKeyValueError('DATA_FORMAT', type_str)

    dat_file = header['DATA_FILE']
    if not os.path.isabs(dat_file):
        dat_file = os.path.join(os.path.dirname(filename), dat_file)

    try:
        data = np.fromfile(dat_file, dtype=data_type)
    except Exception:
        raise 

    try:
        data.shape = header['DATA_SIZE']
    except ValueError:
        raise BadKeyValueError('DATA_SIZE', '%d != %d' %
                               (np.prod(header['DATA_SIZE']), data.size))

    try:
        header['TIME'] = float(header['TIME'])
    except KeyError:
        pass

    shape = header['DATA_SIZE']
    origin = header['BRICK_ORIGIN']
    spacing = header['BRICK_SIZE']/(shape-1)

    grid = RasterField(shape, spacing, origin, indexing='ij')
    if 'CENTERING' in header and header['CENTERING'] == 'zonal':
        grid.add_field(header['VARIABLE'], data, centering='zonal')
    else:
        grid.add_field(header['VARIABLE'], data, centering='point')

    return grid, header


def array_tofile(filename, array, name='', spacing=(1., 1.), origin=(0., 0.),
                 no_clobber=False, options=None):
    files_written = []
    (base, ext) = os.path.splitext(filename)
    if len(ext) > 0 and ext != '.bov':
        raise BadFileExtension(ext)

    spacing = np.array(spacing, dtype=np.float64)
    origin = np.array(origin, dtype=np.float64)
    shape = np.array(array.shape, dtype=np.int64)
    size = shape * spacing

    if len(shape) < 3:
        shape = np.append(shape, [1] * (3 - len(shape)))
    if len(origin) < 3:
        origin = np.append(origin, [1.] * (3 - len(origin)))
    if len(size) < 3:
        size = np.append(size, [1.] * (3 - len(size)))

    for (var, vals) in [(name, array)]:
        dat_file = '%s_%s.dat' % (base, var)
        bov_file = '%s_%s.bov' % (base, var)

        if no_clobber:
            if os.path.isfile(bov_file):
                raise FileExists(bov_file)
            if os.path.isfile(dat_file):
                raise FileExists(dat_file)

        vals.tofile(dat_file)

        header = dict(DATA_FILE=dat_file,
                      DATA_SIZE=array_to_str(shape),
                      BRICK_ORIGIN=array_to_str(origin),
                      BRICK_SIZE=array_to_str(size),
                      DATA_ENDIAN=_SYS_TO_BOV_ENDIAN[sys.byteorder],
                      DATA_FORMAT=_NP_TO_BOV_TYPE[str(vals.dtype)],
                      VARIABLE=var)

        if options is not None:
            header.update(options)

        with open(bov_file, 'w') as f:
            for item in header.items():
                f.write('%s: %s\n' % item)

        files_written.append(bov_file)

    return files_written


def tofile(filename, grid, var_name=None, no_clobber=False, options=None):
    """
    Write a grid-like object to a BOV file.

    Parameters
    ----------
    file : str
        Name of the BOV file to write.
    grid :  Grid-like
        A uniform rectilinear grid.
    var_name : str, optional
        Name of variable contained within *field* to write.
    no_clobber : boolean
        If `True`, and the output file exists, clobber it.
    options : dict
        Additional options to include in the header.

    Returns
    -------
    list
        A list of BOV files written.

    Notes
    -----
    The *grid* object requires the following methods be implemented:
        * get_shape
        * get_origin
        * get_spacing
        * items
        * get_field
    """
    files_written = []
    (base, ext) = os.path.splitext(filename)
    if len(ext) > 0 and ext != '.bov':
        raise BadFileExtension(ext)

    try:
        shape = grid.get_shape()
        origin = grid.get_origin()
        size = grid.get_shape() * grid.get_spacing()
    except (AttributeError, TypeError):
        raise TypeError('\'%s\' object is not grid-like' % type(grid))

    if len(shape) < 3:
        shape = np.append(shape, [1] * (3 - len(shape)))
    if len(origin) < 3:
        origin = np.append(origin, [1.] * (3 - len(origin)))
    if len(size) < 3:
        size = np.append(size, [1.] * (3 - len(size)))

    if var_name is None:
        var_name_and_value = grid.get_point_fields().items()
    else:
        var_name_and_value = (var_name, grid.get_field(var_name))

    for (name, vals) in var_name_and_value:
        dat_file = '%s.dat' % (base, )
        bov_file = '%s.bov' % (base, )

        if no_clobber:
            if os.path.isfile(bov_file):
                raise FileExists(bov_file)
            if os.path.isfile(dat_file):
                raise FileExists(dat_file)

        vals.tofile(dat_file)

        header = dict(DATA_FILE=dat_file,
                      DATA_SIZE=array_to_str(shape),
                      BRICK_ORIGIN=array_to_str(origin),
                      BRICK_SIZE=array_to_str(size),
                      DATA_ENDIAN=_SYS_TO_BOV_ENDIAN[sys.byteorder],
                      DATA_FORMAT=_NP_TO_BOV_TYPE[str(vals.dtype)],
                      VARIABLE=name)

        if options is not None:
            header.update(options)

        with open(bov_file, 'w') as opened_file:
            for item in header.items():
                opened_file.write('%s: %s\n' % item)

        files_written.append(bov_file)

    return files_written


if __name__ == "__main__":
    import doctest
    doctest.testmod() 
