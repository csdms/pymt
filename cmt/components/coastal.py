#! /bin/env python

import os
import ConfigParser
from urlparse import urlparse, urlunparse

import numpy as np

from cmt.bmi import BMI
#from cmt import VTKGridUniformRectilinear
#from cmt.bov import fromfile
from cmt.nc import fromfile

class BMIError (Exception):
    pass
class BadOutputVarName (BMIError):
    def __init__ (self, var):
        self.var = var
    def __str__ (self):
        return '%s: Bad variable name' % var

class Error (Exception):
    pass
class MissingRequiredOption (Error):
    def __init__ (self, opt):
        self.opt = opt
    def __str__ (self):
        return '%s: Missing required option' % self.opt
class MissingRequiredSection (Error):
    def __init__ (self, section):
        self.section = section
    def __str__ (self):
        return '%s: Missing required section' % self.section

class CoastalEnvironment (BMI):
    """
    >>> file = 'http://csdms.colorado.edu/thredds/dodsC/benchmark/sample/ramp_bathymetry.nc'

    >>> env = CoastalEnvironment ()
    >>> env.initialize (file)

    >>> print env.get_grid_shape ('Basement')
    [82 42]

    >>> x = env.get_grid_x ('Basement')
    >>> x.shape
    (3444,)
    >>> (x.min (), x.max ())
    (-500.0, 20000.0)

    >>> y = env.get_grid_y ('Basement')
    >>> y.shape
    (3444,)
    >>> (y.min (), y.max ())
    (-500.0, 40000.0)

    >>> env.run (10.)
    >>> env.get_current_time ()
    10.0
    >>> env.run (20.)
    >>> env.get_current_time ()
    20.0

    >>> data = env.get_values ('Basement')
    >>> data.shape
    (3444,)

    >>> env.finalize ()

    >>> env = CoastalEnvironment ()
    >>> env.initialize ('coastal.cfg')
    """
    def get_name (self):
        return 'CoastalEnvironment'
    def initialize (self, file):
        (base, ext) = os.path.splitext (file)
        if ext=='.cfg':
            file = self._scan_cfg (file)

        fields = fromfile (file, allow_singleton=False)

        assert (len (fields)==1)

        (t, field) = fields[0]
        self._field = field

        assert (field.has_field ('Basement'))

        self.grids = {}
        self.grids['Basement'] = field

        #self.grids[attr['VARIABLE']] = grid
        ##self.grids[bov['VARIABLE']] = bov

        self.time = self.get_start_time ()

    def run (self, time):
        self.time = time
    def finalize (self):
        pass

    def get_start_time (self):
        return 1e-32
    def get_end_time (self):
        return 1e32
    def get_current_time (self):
        return self.time

    def get_input_var_names (self):
        return []
    def get_output_var_names (self):
        return ['Basement']

    def get_grid_x (self, var):
        try:
            return self.grids[var].get_x ()
        except KeyError:
            raise BadOutputVarName (var)

    def get_grid_y (self, var):
        try:
            return self.grids[var].get_y ()
        except KeyError:
            raise BadOutputVarName (var)

    def get_values (self, var):
        try:
            #return self.grids[var].point_data (var)
            return self.grids[var].get_field (var)
        except KeyError:
            raise BadOutputVarName (var)

    def get_grid_spacing (self, var):
        try:
            return self.grids[var].get_spacing ()
        except KeyError:
            raise BadOutputVarName (var)
    def get_grid_origin (self, var):
        try:
            return self.grids[var].get_origin ()
        except KeyError:
            raise BadOutputVarName (var)
    def get_grid_shape (self, var):
        try:
            return self.grids[var].get_shape ()
        except KeyError:
            raise BadOutputVarName (var)

    def _scan_cfg (self, file):
        parser = ConfigParser.ConfigParser (dict (input_dir=''))
        parser.read (file)

        try:
            input_dir = parser.get ('CoastalEnvironment', 'input_dir')
        except ConfigParser.NoSectionError:
            raise MissingRequiredSection ('CoastalEnvironment')

        try:
            input_file = parser.get ('CoastalEnvironment', 'elevation_file')
        except ConfigParser.NoOptionError:
            raise MissingRequiredOption ('elevation_file')

        o = urlparse (input_file.strip ())
        if o.scheme in ['file', '']:
            if os.path.isabs (o.path):
                return o.path
            else:
                return os.path.join (input_dir.strip (), o.path)
        else:
            return urlunparse (o)

        #return os.path.join (input_dir.strip (), input_file.strip ())

if __name__ == "__main__":
    import doctest
    doctest.testmod()                                                                                                           

