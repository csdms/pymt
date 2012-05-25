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

import numpy

from cmt.grids import DimensionError, NonUniformGridError, NonStructuredGridError
from cmt.grids import RasterField, StructuredField, UnstructuredField
import cmt.vtk
import cmt.bov

from cmt.bov import Database as BovDatabase
from cmt.vtk import Database as VtkDatabase
from cmt.nc import Database as NcDatabase

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

class PrintQueue (object):
    """A print queue for a collection of fields
    """
    #def __init__ (self, fields, template='${var}_${count}', format='vtk', prefix='.'):
    def __init__ (self, fields, template='${var}', format='vtk', prefix='.'):
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
        print 'PQ: Getting printer for %s' % self._format
        try:
            self._printer = format_to_printer (self._format)
        except FormatError:
            self._printer = format_to_printer ('vtk')
            self._format = 'vtk'
        print 'PQ: Printer format is %s' % self._format

        self._queue = []

    def push (self, var_name, template=None, format=None, prefix=None):
        """ Push a variable onto the print queue.

        :param var_name: Name of the variable to print
        :type var_name: string

        """
        print 'PQ: Pushing var %s' % var_name
        try:
            print 'PQ: Raster?'
            shape = self._fields.get_grid_shape (var_name)
            print 'PQ: Shape is ', shape
            if shape is None:
                raise NonStructuredGridError
            spacing = self._fields.get_grid_spacing (var_name)
            print 'PQ: Spacing is ', spacing
            if spacing is None:
                raise NonUniformGridError
            try:
                origin = self._fields.get_grid_origin (var_name)
            except AttributeError:
                origin = self._fields.get_grid_lower_left (var_name)
            print 'PQ: Shape is ', shape
            print 'PQ: Spacing is ', spacing
            print 'PQ: Origin is ', origin
            try:
                field = RasterField (shape, spacing, origin, indexing='ij')
            except Exception as e:
                print 'PQ: There was an error: %s' % e
            print 'PQ: Field is ', field
        except NonUniformGridError:
            print 'PQ: Structured?'
            shape = self._fields.get_grid_shape (var_name)
            print 'PQ: Shape is ', shape
            x = self._fields.get_grid_x (var_name)
            y = self._fields.get_grid_y (var_name)
            field = StructuredField (x, y, shape)
        except NonStructuredGridError:
            print 'PQ: Untructured?'
            x = self._fields.get_grid_x (var_name)
            print 'PQ: x is ', x
            y = self._fields.get_grid_y (var_name)
            print 'PQ: y is ', y
            c = self._fields.get_grid_connectivity (var_name)
            print 'PQ: c is ', c
            o = self._fields.get_grid_offset (var_name)
            print 'PQ: o is ', o
            field = UnstructuredField (x, y, c, o)
            print 'PQ: field is', field

        #x = self._fields.get_grid_x (var_name)
        #y = self._fields.get_grid_y (var_name)
        #c = self._fields.get_grid_connectivity (var_name)
        #o = self._fields.get_grid_offset (var_name)
        #field = UnstructuredField (x, y, c, o)

        data = self._fields.get_grid_values (var_name)
        print 'PQ: data is', data
        try:
            field.add_field (var_name, data, centering='zonal')
        except DimensionError:
            field.add_field (var_name, data, centering='point')

        if template is not None:
            file = Template (template).safe_substitute (var=var_name)
        else:
            file = self._template.safe_substitute (var=var_name)

        if format is None:
            format = self._format
        (root, ext) = os.path.splitext (file)
        if len (ext)==0:
            ext = format_to_ext (format, default='')

        if not os.path.isabs (file):
            try:
                file = os.path.join (prefix, root+ext)
            except (AttributeError, TypeError):
                file = os.path.join (self._prefix, root+ext)
        else:
            file = root+ext

        try:
            printer = format_to_printer (format)
        except FormatError:
            printer = format_to_printer (self._format)
        db = printer ()

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

        #self._queue.append ((field, file))
        self._queue.append ((db, field))

    def print_all (self, **kwargs):
        """ Print each variable in the queue
        """
        #for (field, file) in self._queue:
        #    file = Template (file).substitute (count=self._count)
        #    self._printer (field, file, **kwargs)
        #self._count += 1
        print 'PQ: printing each var in database'
        for (db, field) in self._queue:
            print 'PQ: printing var'
            print 'PQ: field is ', field
            print 'PQ: db is ', db

            for var_name in field.keys ():
                print 'PQ: resetting variable %s' % var_name
                data = self._fields.get_grid_values (var_name)
                try:
                    field.add_field (var_name, data, centering='zonal')
                except DimensionError:
                    field.add_field (var_name, data, centering='point')

            print 'PQ: writing field to file'
            db.write (field)
        print 'PQ: done printing each var in database'
    def close (self):
        pass

import numpy as np
_TIMER_EPS = np.finfo (np.float64).eps

class TimedPrintQueue (PrintQueue):
    def __init__ (self, *args, **kwargs):
        try:
            self._interval = kwargs['interval']
        except KeyError:
            self._interval = 0.
        else:
            del kwargs['interval']

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
        print 'TPQ: Printing at %f' % time
        if time>=self._next:
            print 'TPQ: Old print time %f' % self._next
            super (TimedPrintQueue, self).print_all (**kwargs)
            try:
                self._next = time - time%self._interval + self._interval
            except ZeroDivisionError:
                self._next = time + _TIMER_EPS
            print 'TPQ: New print time %f' % self._next

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
        format = globs.get ('FileFormat', 'vtk')
        prefix = globs.get ('Dir', '.')
        template = '${var}'

        base = globs.get ('SimulationName', '')
        if len (base)>0:
            template = base + '_' + template

        self._globs = globs
        self._fields = fields
        self._vars = []

        #super (CmiTimedPrintQueue, self).__init__ (fields, format=format,
        #                                           prefix=prefix, template=template)
    def push (self, locals):
        # Look for variables in this namespace. The namespace is 'Var', so
        # look for keys that look like Var/<var_name>
        vars = []
        for key in locals.keys ():
            (head, tail) = ns.split (key)
            if head=='Var':
                vars.append (tail)
        print 'PQ: found vars: %s' % ','.join (vars)

        # Look for variables to print. Look at the values for Var/<var_name>
        # keys. If the value doesn't indicate not to print, then use the
        # value as a file name.
        vars_to_print = []
        for var in vars:
            file = locals[ns.join ('Var', var)]
            print 'PQ: The var %s' % ns.join ('Var', var) 
            print 'PQ: Is this a file %s' % file
            if file.lower () not in ['off', 'no', 'false']:
                vars_to_print.append (var)
        print 'PQ: found vars to print: %s' % ','.join (vars_to_print)

        # Variable specific attributes. Use global attributes if specific ones are
        # not found.
        template = '${var}'
        prefix = locals.get ('Dir', None)
        format = locals.get ('FileFormat', None)
        base = locals.get ('SimulationName', '')
        if len (base)>0:
            template = base + '_' + template
        print 'PQ: found vars template: %s' % template

        interval = locals.get ('Interval', 0.)
        print 'PQ: found interval: %s' % interval
        print 'PQ: found format: %s' % format
        print 'PQ: found prefix: %s' % prefix

        # Add each variable to print to the queue.
        #for var in vars_to_print:
        #    super (CmiTimedPrintQueue, self).push (var, template=template, format=format,
        #                                           prefix=prefix)

        try:
            q = TimedPrintQueue (self._fields, format=format, prefix=prefix,
                                 template=template, interval=interval)
        except Exception as e:
            print e
        print 'PQ: created time print queue'

        for var in vars_to_print:
            print 'PQ: push var: %s' % var
            q.push (var, format=format, prefix=prefix, template=template)
        print 'PQ: append vars'
        self._vars.append (q)
        print 'PQ: done'

    def add_files (self, var_prefix):
        locals = ns.extract_base (self._globs, var_prefix)
        self.push (locals)

    def print_all (self, time, **kwargs):
        print 'PQ: Printing everything'
        for q in self._vars:
            print 'PQ: Printing at %f' % time
            q.print_all (time)

    def next_print_time (self):
        return min ([q.next_print_time () for q in self._vars])

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


