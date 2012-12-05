#! /usr/bin/env python
"""
Examples
========

An unstructured grid
--------------------

Define a grid that consists of two trianges that share two points.

::

       (2) - (3)
      /   \  /
    (0) - (1)

Create two fields on this grid,

    >>> from cmt.grids import UnstructuredField
    >>> f = UnstructuredField ([0, 2, 1, 3], [0, 0, 1, 1], [0, 2, 1, 2, 3, 1], [3, 6])

    >>> f.add_field ('Elevation', [1., 2., 3, 4], centering='point')
    >>> f.add_field ('Temperature', [10., 20., 30., 40.], centering='point')
    >>> f.add_field ('Thickness', [10., 20.], centering='zonal')

    >>> g = UnstructuredField ([0, 2, 1, 3], [0, 0, 1, 1], [0, 2, 1, 2, 3, 1], [3, 6])
    >>> g.add_field ('Temperature', [-1., -2., -3, -4], centering='point')

Create a print queue for variable Elevation and Thickness on the first grid, and
Temperature on the second grid.

    >>> grids = FieldCollection (dict (Elevation=f, Temperature=g, Thickness=f))
    >>> pq = PrintQueue (grids)
    >>> pq.push ('Elevation')
    >>> pq.push ('Temperature')
    >>> pq.push ('Thickness')

Print each of the fields.

    >>> pq.print_all (encoding='base64', format='appended')

Create a TimedPrintQueue for the same collection of grids.

    >>> grids = FieldCollection (dict (Elevation=f, Temperature=g, Thickness=f))
    >>> pq = TimedPrintQueue (grids, interval=10)
    >>> pq.push ('Elevation')
    >>> pq.push ('Temperature')
    >>> pq.push ('Thickness')

The TimedPrintQueue will only print at intervals of 10 (excluding 0). Every time
something is printed, the queue is updated to print at the next interval.

    >>> pq.print_all (1.)
    >>> pq.print_all (10.)
    >>> pq.print_all (11.)
    >>> pq.print_all (30.)

The default interval is zero. In this case, fields are printed once for every
increasing time.

    >>> pq = TimedPrintQueue (grids, template='timed_${var}')
    >>> pq.push ('Elevation')
    >>> pq.push ('Temperature')
    >>> pq.push ('Thickness')

The TimedPrintQueue will only print at intervals of 10 (excluding 0). Every time
something is printed, the queue is updated to print at the next interval.

    >>> pq.print_all (1.)
    >>> pq.print_all (10.)
    >>> pq.print_all (11.)
    >>> pq.print_all (30.)

The default interval is zero. In this case, fields are printed once for every
increasing time.

    >>> pq = TimedPrintQueue (grids, template='timed_${var}')

For instance, the following two lines result in only one set of fields printed.
    >>> pq.print_all (1.)
    >>> pq.print_all (1.)

Print another set of fields...
    >>> pq.print_all (1.1)

... and another set.

For instance, the following two lines result in only one set of fields printed.
    >>> pq.print_all (1.)
    >>> pq.print_all (1.)

Print another set of fields...
    >>> pq.print_all (1.1)

... and another set.
    >>> pq.print_all (1.2)
"""

import os
import sys
from string import Template
from collections import namedtuple

import numpy

from cmt.grids import DimensionError, NonUniformGridError, NonStructuredGridError
from cmt.grids import RasterField, StructuredField, UnstructuredField
from cmt.verbose import CMTLogger
import cmt.vtk
import cmt.bov

from cmt.bov import Database as BovDatabase
from cmt.vtk import Database as VtkDatabase
from cmt.nc import Database as NcDatabase

logger = CMTLogger ('printqueue', 20)

class Error (Exception):
    pass
class FormatError (Error):
    def __init__ (self, format):
        self._format = format
    def __str__ (self):
        return '%s: Unknown format' % self._format

_printers = {'vtk': VtkDatabase, 'nc': NcDatabase, 'bov': BovDatabase}
_format_extension = {'nc': '.nc', 'vtk': '.vtu', 'bov': '.bov'}

def format_to_ext (format, default=None):
    try:
        return _format_extension[format.lower ()]
    except (KeyError, AttributeError):
        if default is None:
            raise FormatError (format)
        else:
            return default
def format_to_printer (format):
    try:
        return _printers[format.lower ()]
    except (KeyError, AttributeError):
        raise FormatError (format)

class FieldCollection (object):
    def __init__ (self, fields={}):
        self._fields = fields
    def add_field (self, field, name):
        self._fields[name] = field
    def get_grid_shape (self, name):
        return self._fields[name].get_shape ()
    def get_grid_spacing (self, name):
        return self._fields[name].get_spacing ()
    def get_grid_origin (self, name):
        return self._fields[name].get_origin ()
    def get_grid_x (self, name):
        return self._fields[name].get_x ()
    def get_grid_y (self, name):
        return self._fields[name].get_y ()
    def get_grid_connectivity (self, name):
        return self._fields[name].get_connectivity ()
    def get_grid_offset (self, name):
        return self._fields[name].get_offset ()
    def get_grid_values (self, name):
        return self._fields[name].get_field (name)

def fix_unknown_shape (shape, size):
    """
    >>> print fix_unknown_shape ((4, 3), 12)
    [4 3]
    >>> print fix_unknown_shape ((4, -1), 12)
    [4 3]
    """
    new_shape = np.array (shape, dtype=np.int64)

    if -1 in new_shape:
        known_dims = [dim_len for dim_len in shape if dim_len>0]

        # Allow only 1 unknown dimension, and ensure the size of the unknown
        # dimension is an integer.
        assert (len (known_dims) == len (shape)-1)
        assert (size % np.prod (known_dims) == 0)

        new_shape[new_shape<=0] = size / np.prod (known_dims)

    return new_shape

#PrintItem = namedtuple ('PrintItem', 'db field')
class PrintItem (object):
    def __init__ (self, db, field):
        self.db = db
        self.field = field


class PrintQueue (object):
    """A print queue for a collection of fields
    """
    def __init__ (self, fields, template='${var}', format='vtk',
                  prefix='.'):
        """
        :param fields: A collection of fields
        :type fields: Field-collection

        *fields* is an object that implements the following methods:
            * get_grid_x
            * get_grid_y
            * get_grid_connectivity
            * get_grid_offset
            * get_grid_values

        """
        self._fields = fields

        #self._count = 0
        self._prefix = prefix
        self._format = format
        self._template = Template (template)
        self._format = format
        self._suffix = '.vtu'
        #self._printer = _printers[self._format]
        logger.debug ('Getting printer for %s' % self._format)
        try:
            self._printer = format_to_printer (self._format)
        except FormatError:
            self._printer = format_to_printer ('vtk')
            self._format = 'vtk'
        logger.debug ('Printer format is %s' % self._format)

        self._queue = []

    def _construct_print_field (self, var_name):
        logger.debug ('calling get_grid_values')
        try:
            data = self._fields.get_grid_values (var_name)
        except Exception as e:
            logger.error ('Unable to get values (%s)' % e)

        logger.debug ('called get_grid_values')
        logger.debug ('data shape is %s' % np.array (data.shape))
        logger.debug ('data is %s' % data)

        try:
            logger.debug ('Checking if grid is raster...')

            shape = self._fields.get_grid_shape (var_name)
            if shape is None:
                raise NonStructuredGridError
            logger.debug ('Shape is %s' % shape)

            if len (shape) == 1 and shape[0] == 1:
                spacing = np.array ([1.])
            else:
                spacing = self._fields.get_grid_spacing (var_name)
                if spacing is None:
                    raise NonUniformGridError
            logger.debug ('Spacing is %s' % spacing)

            if len (shape) == 1 and shape[0] == 1:
                origin = np.array ([0.])
            else:
                try:
                    origin = self._fields.get_grid_origin (var_name)
                except AttributeError:
                    origin = self._fields.get_grid_lower_left (var_name)

            logger.debug ('Shape is %s' % shape)
            logger.debug ('Spacing is %s' % spacing)
            logger.debug ('Origin is %s' % origin)

            shape = fix_unknown_shape (shape, data.size)
            logger.debug ('Shape is %s' % shape)

            try:
                field = RasterField (shape, spacing, origin, indexing='ij')
            except Exception as e:
                logger.error ('There was an error: %s' % e)
        except NonUniformGridError:
            logger.debug ('Checking if grid is structured...')
            shape = self._fields.get_grid_shape (var_name)
            logger.debug ('Shape is %s' % shape)
            x = self._fields.get_grid_x (var_name)
            y = self._fields.get_grid_y (var_name)
            field = StructuredField (x, y, shape)
        except NonStructuredGridError:
            logger.debug ('Checking if grid is unstructured...')
            x = self._fields.get_grid_x (var_name)
            y = self._fields.get_grid_y (var_name)
            c = self._fields.get_grid_connectivity (var_name)
            o = self._fields.get_grid_offset (var_name)
            field = UnstructuredField (x, y, c, o)

        logger.debug ('Adding variable %s to field...' % var_name)
        try:
            try:
                field.add_field (var_name, data, centering='zonal')
            except DimensionError:
                field.add_field (var_name, data, centering='point')
        except Exception as e:
            logger.error ('Unable to add varaible to field (%s)' % e)
        else:
            logger.debug ('Variable added')

        return field

    def _reconstruct_print_field (self, item):
        """
        Reconstruct a PrintItem's field with new data. If the size of the
        new data no longer matches the number of points or cell in the grid,
        then reconstruct the entire field as it has changed size.
        """
        logger.debug ('var names are %s', ', '.join (item.field.keys ()))
        for var_name in item.field.keys ():
            logger.debug ('resetting variable %s' % var_name)
            data = self._fields.get_grid_values (var_name)

            if data.size == item.field.get_point_count ():
                item.field.add_field (var_name, data, centering='point')
            elif data.size == item.field.get_cell_count ():
                item.field.add_field (var_name, data, centering='zonal')
            else:
                logger.debug ('mesh size has changed')
                logger.debug ('%d != %d or %d' % (data.size, item.field.get_point_count (), item.field.get_cell_count ()))
                item.field = self._construct_print_field (var_name)
                logger.debug ('new var names are %s', ', '.join (item.field.keys ()))
                return
        return

    def _construct_file_name (self, var_name, template=None, format=None, prefix=None):
        logger.debug ('var is %s' % var_name)
        logger.debug ('template is %s' % template)
        if template is None:
            file = self._template.safe_substitute (var=var_name)
        else:
            file = Template (template).safe_substitute (var=var_name)
        logger.debug ('file name is %s' % file)

        if format is None:
            format = self._format

        (root, ext) = os.path.splitext (file)
        if len (ext) == 0:
            ext = format_to_ext (format, default='')
        logger.debug ('file extension is %s' % ext)
        logger.debug ('file root is %s' % root)

        logger.debug ('prefix is %s' % prefix)
        logger.debug ('_prefix is %s' % self._prefix)
        if not os.path.isabs (file):
            try:
                file = os.path.join (prefix, root+ext)
            except (AttributeError, TypeError):
                file = os.path.join (self._prefix, root+ext)
        else:
            file = root+ext
        logger.debug ('file name is %s' % file)

        return file

    def push (self, var_name, template=None, format=None, prefix=None):
        """ Push a variable onto the print queue.

        :param var_name: Name of the variable to print
        :type var_name: string

        """
        logger.debug ('Pushing var %s onto queue' % var_name)

        if format is None:
            format = self._format

        logger.debug ('Constructing file name')
        file = self._construct_file_name (var_name, template, format, prefix)
        logger.debug ('File name is %s' % file)

        #if template is not None:
        #    file = Template (template).safe_substitute (var=var_name)
        #else:
        #    file = self._template.safe_substitute (var=var_name)

        #if format is None:
        #    format = self._format
        #(root, ext) = os.path.splitext (file)
        #if len (ext)==0:
        #    ext = format_to_ext (format, default='')

        #if not os.path.isabs (file):
        #    try:
        #        file = os.path.join (prefix, root+ext)
        #    except (AttributeError, TypeError):
        #        file = os.path.join (self._prefix, root+ext)
        #else:
        #    file = root+ext

        try:
            printer = format_to_printer (format)
        except FormatError:
            printer = format_to_printer (self._format)
        db = printer ()
        logger.debug ('Created database')

        #try:
        #    db = _printers[format] ()
        #except KeyError:
        #    db = _printers[self._format] ()
        #db = self._printer ()
        path = os.path.dirname (file)
        try:
            os.makedirs (path)
        except os.error:
            pass
        finally:
            db.open (file, var_name)
        logger.debug ('Opened database')

        field = self._construct_print_field (var_name)
        logger.debug ('Constructed print field')

        #self._queue.append ((db, field))
        self._queue.append (PrintItem (db, field))
        logger.debug ('Added to queue')

    def print_all (self, **kwargs):
        """ Print each variable in the queue
        """
        #for (field, file) in self._queue:
        #    file = Template (file).substitute (count=self._count)
        #    self._printer (field, file, **kwargs)
        #self._count += 1
        logger.debug ('printing each var in database')
        #for (db, field) in self._queue:
        for item in self._queue:
            logger.debug ('printing var')

            #for var_name in item.field.keys ():
            #    print 'PQ: resetting variable %s' % var_name
            #    data = self._fields.get_grid_values (var_name)

            #    if data.size == item.field.get_point_count ():
            #        field.add_field (var_name, data, centering='point')
            #    elif data.size == item.field.get_cell_count ():
            #        field.add_field (var_name, data, centering='zonal')
            #    else:
            #        item.field = self._construct_field (var_name)

            #    try:
            #        field.add_field (var_name, data, centering='zonal')
            #    except DimensionError:
            #        field.add_field (var_name, data, centering='point')

            self._reconstruct_print_field (item)
            logger.debug ('writing field to file')
            try:
                item.db.write (item.field)
            except Exception as e:
                logger.error ('error writing field to file (%s)' % e)
        logger.debug ('done printing each var in database')

    def close (self):
        pass

import numpy as np
_TIMER_EPS = np.finfo (np.float64).eps

class TimedPrintQueue (PrintQueue):
    def __init__ (self, *args, **kwargs):
        self._interval = kwargs.pop ('interval', 0.)
        self._next = self._interval

        super (TimedPrintQueue, self).__init__ (*args, **kwargs)

    def push (self, var_name, **kwargs):
        try:
            interval = kwargs['interval']
        except KeyError:
            interval = 0.
        else:
            del kwargs['interval']

        super (TimedPrintQueue, self).push (var_name, **kwargs)

    def print_all (self, time, **kwargs):
        logger.debug ('Printing at %f' % time)
        if time>=self._next:
            logger.debug ('Old print time %f' % self._next)
            super (TimedPrintQueue, self).print_all (**kwargs)
            try:
                self._next = time - time%self._interval + self._interval
            except ZeroDivisionError:
                self._next = time + _TIMER_EPS
            logger.debug ('New print time %f' % self._next)

    def next_print_time (self):
        return self._next

from cmt import namespace as ns

class CmiTimedPrintQueue (TimedPrintQueue):
    """
    >>> from cmt.grids import RasterField

    >>> f = RasterField ((3,2), (1,1), (0,0))
    >>> f.add_field ('Elevation', [1., 2., 3, 4, 5, 6], centering='point')
    >>> f.add_field ('Thickness', [10., 20.], centering='zonal')

    >>> g = RasterField ((3,3), (1,1), (0,0))
    >>> g.add_field ('Temperature', -1*np.arange (9.), centering='point')

Create a print queue for variable Elevation and Thickness on the first grid, and
Temperature on the second grid.

    >>> port = FieldCollection (dict (Elevation=f, Temperature=g, Thickness=f))
    >>> d = {'Dir': '.', 'SimulationName': 'Test', 'FileFormat': 'vtk',
    ... 'Var/Elevation': 'on', 'Var/Temperature': 'on', 'Var/Depth': 'off'}

    >>> globs = {'Dir': '/tmp', 'SimulationName': '', 'FileFormat': 'NC'}
    >>> locals = {'Dir': '.', 'SimulationName': 'Test', 'FileFormat': 'VTK',
    ... 'Var/Elevation': 'on', 'Var/Temperature': 'on', 'Var/Depth': 'off'}
    >>> pq = CmiTimedPrintQueue (port, globs)

    >>> pq.push (locals)
    >>> pq.print_all (1.)

    >>> os.path.isfile ('./Test_Elevation_0000.vtu')
    True
    >>> os.path.isfile ('./Test_Temperature_0000.vtu')
    True
    >>> os.path.isfile ('./Test_Depth_0000.vtu')
    False

When appending data to a VTK database, a new file is created with the suffix incremented
by one.

    >>> os.path.isfile ('./Test_Elevation_0001.vtu')
    False
    >>> pq.print_all (2.)
    >>> os.path.isfile ('./Test_Elevation_0001.vtu')
    True

    >>> attrs = {'/Model/SimulationName': '', '/Model/FileFormat': 'nc',
    ... '/Model/Output/Grid/Dir': '.', '/Model/Output/Grid/Interval': 1.,
    ... '/Model/Output/Grid/SimulationName': 'Test1', '/Model/Output/Grid/FileFormat': 'nc',
    ... '/Model/Output/Grid/Var/Elevation': 'on', '/Model/Output/Grid/Var/Temperature': 'on',
    ... '/Model/Output/Grid/Var/Depth': 'off'}
    >>> globs = ns.extract_base (attrs, '/Model/')
    >>> pq = CmiTimedPrintQueue (port, globs)
    >>> pq.add_files ('Output/Grid/')
    >>> pq.print_all (1.)
    Imported Nio version: 1.4.0
    Imported Nio version: 1.4.0

    >>> os.path.isfile ('./Test1_Elevation.nc')
    True
    >>> os.path.isfile ('./Test1_Temperature.nc')
    True
    >>> os.path.isfile ('./Test1_Depth.nc')
    False

When appending data to a NetCDF file, the data are appended to the existing file and so
there is no counter in the file name.

    >>> os.path.isfile ('./Test_Elevation_0000.nc')
    False
    >>> pq.print_all (2.)
    >>> os.path.isfile ('./Test_Elevation_0001.nc')
    False

    """
    def __init__ (self, fields, globs={}):
        """Add files to the queue based on entries of a dictionary.

        :param fields: A collection of fields
        :type fields: Field-collection
        :keyword globs: Dictionary of global variables for the print queue.
        :type globs: Dictionary-like

        """
        logger.debug ('creating timed print queue')
        format = globs.get ('FileFormat', 'vtk')
        prefix = globs.get ('Dir', '.')
        template = '${var}'

        base = globs.get ('SimulationName', '')
        if len (base)>0:
            template = base + '_' + template

        self._globs = globs
        self._fields = fields
        self._vars = []
        logger.debug ('prefix is %s' % prefix)
        logger.debug ('created timed print queue')

        super (CmiTimedPrintQueue, self).__init__ (
            fields, format=format, prefix=prefix, template=template)

    def push (self, locals):
        # Look for variables in this namespace. The namespace is 'Var', so
        # look for keys that look like Var/<var_name>
        vars = []
        for key in locals.keys ():
            (head, tail) = ns.split (key)
            if head=='Var':
                vars.append (tail)
        for var in vars:
            logger.debug ('found vars: %s' % var)

        # Look for variables to print. Look at the values for
        # Var/<var_name> keys. If the value doesn't indicate not to print,
        # then use the value as a file name.
        vars_to_print = []
        for var in vars:
            file = locals[ns.join ('Var', var)]
            if file.lower () not in ['off', 'no', 'false']:
                vars_to_print.append (var)
        for var in vars_to_print:
            logger.debug ('found var to print: %s' % var)

        # Variable specific attributes. Use global attributes if specific
        # ones are not found.
        template = '${var}'
        base = locals.get ('SimulationName', '')
        if len (base)>0:
            template = base + '_' + template
        logger.debug ('found vars template: %s' % template)

        if len (vars_to_print) == 0:
            locals['interval'] = sys.float_info.max
            logger.info ('No variables to print.')

        # Translate keys to kwds for TimedPrintQueue.__init__
        kwds = dict (template=template)
        for (kwd, key) in zip (['format', 'prefix', 'interval'],
                               ['FileFormat', 'Dir', 'Interval']):
            try:
                kwds[kwd] = locals[key]
            except KeyError:
                pass

        try:
            q = TimedPrintQueue (self._fields, **kwds)
        except Exception as e:
            logger.error ('%s' % e)
        logger.debug ('created time print queue')

        for var in vars_to_print:
            logger.debug ('Pushing var onto queue: %s' % var)
            q.push (var)
        self._vars.append (q)

    def add_files (self, var_prefix):
        locals = ns.extract_base (self._globs, var_prefix)
        self.push (locals)

    def print_all (self, time, **kwargs):
        logger.debug ('Printing everything')
        for q in self._vars:
            logger.debug ('Printing at %f' % time)
            q.print_all (time)

    def next_print_time (self):
        if self._vars:
            return min ([q.next_print_time () for q in self._vars])
        else:
            return sys.float_info.max
            #return None

class CmiPrintQueue (object):
    def __init__ (self, fields, globs={}):
        """Add files to the queue based on entries of a dictionary.

        :param fields: A collection of fields
        :type fields: Field-collection
        :keyword globs: Dictionary of global variables for the print queue.
        :type globs: Dictionary-like

        """
        format = globs.get ('FileFormat', 'vtk')
        prefix = globs.get ('Dir', '.')
        template = '${var}'

        base = globs.get ('SimulationName', '')
        if len (base)>0:
            template = base + '_' + template

        self._globs = globs

        super (CmiTimedPrintQueue, self).__init__ (fields, format=format,
                                                   prefix=prefix, template=template)


class FieldPrintQueue (object):
    """A print queue for a single field
    """
    def __init__ (self, field, template='${var}', format='vtk', prefix='.'):
        """
        :param field: Field of values to print
        :type field: A field-like object
        """
        self._field = field

        self._prefix = prefix
        self._format = format
        self._template = Template (template)
        self._suffix = '.vtu'
        #self._printer = _printers[self._format]
        try:
            self._printer = format_to_printer (self._format)
        except FormatError:
            raise

    def push (self, var_name):
        """ Push a variable onto the print queue.

        :param var_name: Name of the variable to print
        :type var_name: string
        :param file: Name of the file to print to
        :type file: string

        """
        file = self._template.substitute (var=var_name)
        (root, ext) = os.path.splitext (file)
        if len (ext)==0:
            ext = self._suffix
        if not os.path.isabs (file):
            file = os.path.join (self._prefix, root+ext)
        else:
            file = root+ext
        self._queue.prepend ((var_name, file))

    def print_all (self):
        """ Print each variable in the queue
        """
        for (var, file) in self._queue:
            path = os.path.dirname (file)
            try:
                os.makedirs (path)
            except os.error:
                pass
            else:
                self._printer (self._field, file, var=var)

if __name__ == "__main__":
    import doctest
    doctest.testmod()


