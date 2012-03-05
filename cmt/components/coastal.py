#! /bin/env python

import os
import ConfigParser

import numpy as np

from cmt.bmi import BMI
from cmt import VTKGridUniformRectilinear
from cmt.bov import fromfile

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
class MissingRequiredOption (Error):
    def __init__ (self, section):
        self.section = section
    def __str__ (self):
        return '%s: Missing required section' % self.section

class CoastalEnvironment (BMI):
    """
    >>> env = CoastalEnvironment ()
    >>> env.initialize ('coast.bov')
    >>> x = env.get_grid_x ('Elevation')
    >>> x.shape
    (100,)
    >>> x.min ()
    0.0
    >>> x.max ()
    10.0
    >>> y = env.get_grid_y ('Elevation')
    >>> x.shape
    (100,)
    >>> y.min ()
    -20.0
    >>> y.max ()
    0.0

    >>> env.run (10.)
    >>> env.get_current_time ()
    10.0
    >>> env.run (20.)
    >>> env.get_current_time ()
    20.0

    >>> data = env.get_values ('Elevation')
    >>> data.shape
    (10, 10)
    >>> np.all (data==5.)
    True

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

        (grid, attr) = fromfile (file, allow_singleton=False)
        #bov = BovFile ()
        #bov.frombov (file)

        self.grids = {}
        self.grids[attr['VARIABLE']] = grid
        #self.grids[bov['VARIABLE']] = bov

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
        return ['Elevation']

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
            return self.grids[var].point_data (var)
        except KeyError:
            raise BadOutputVarName (var)

    #def get_grid_spacing (self, var):
    #    try:
    #        return self.grids[var].get_spacing ()
    #    except KeyError:
    #        raise BadOutputVarName (var)
    #def get_grid_origin (self, var):
    #    try:
    #        return self.grids[var].get_origin ()
    #    except KeyError:
    #        raise BadOutputVarName (var)
    #def get_grid_shape (self, var):
    #    try:
    #        return self.grids[var].get_shape ()
    #    except KeyError:
    #        raise BadOutputVarName (var)

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

        return os.path.join (input_dir.strip (), input_file.strip ())

if __name__ == "__main__":
    import doctest
    doctest.testmod()                                                                                                           

