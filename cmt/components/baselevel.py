#! /bin/env python

import os
import ConfigParser
import bisect
import glob
from types import StringTypes

import numpy as np

from cmt.bmi import BMI
from cmt import VTKGridUniformRectilinear
from cmt.bov import fromfile

class BaseLevel (BMI):
    """
    >>> bl = BaseLevel ()
    >>> bl.initialize (['bl_01.bov', 'bl_02.bov'])

    The model is only valid between the start and end times.

    >>> bl.get_current_time ()
    1.0
    >>> bl.get_end_time ()
    2.0

    The initial values

    >>> vals = bl.get_values ('BaseLevel')
    >>> np.all (vals==5.)
    True

    Still the initial values

    >>> bl.run (1.0)
    >>> np.all (vals==5.)
    True

    Run until time=1.1. We have a reference to the data so
    we don't have to do another get_values call.

    >>> bl.run (1.1)
    >>> bl.get_current_time ()
    1.1
    >>> np.all (vals==5.5)
    True

    Run until the last time.

    >>> bl.run (2.0)
    >>> bl.get_current_time ()
    2.0
    >>> np.all (vals==10.)
    True


    It's OK to run backwards in time.

    >>> bl.run (1.5)
    >>> bl.get_current_time ()
    1.5
    >>> np.all (vals==7.5)
    True

    It's an error to try to run outside of the start or end times.

    >>> bl.run (2.0001)
    Traceback (most recent call last):
        ...
    AssertionError

    File globbing also works

    >>> bl = BaseLevel ()
    >>> bl.initialize ('bl_*bov')

    The model is only valid between the start and end times.

    >>> bl.get_current_time ()
    1.0
    >>> bl.get_end_time ()
    2.0
    >>> vals = bl.get_values ('BaseLevel')
    >>> np.all (vals==5.)
    True

    >>> bl = BaseLevel ()
    >>> bl.initialize ('baselevel.cfg')
    >>> bl.get_current_time ()
    1.0
    >>> bl.get_end_time ()
    2.0
    >>> vals = bl.get_values ('BaseLevel')
    >>> np.all (vals==5.)
    True
    """
    def initialize (self, files):
        if isinstance (files, StringTypes):
            (base, ext) = os.path.splitext (files)
            if ext=='.cfg':
                files = self._scan_cfg (files)
            else:
                files = [files]
        matched_files = []
        for file in files:
            matched_files.extend (glob.glob (file))

        grids = []
        for file in matched_files:
            #var = BovFile ()
            #var.frombov (file)
            #grids.append ((var['TIME'], var))

            (grid, attr) = fromfile (file, allow_singleton=False)
            #grids.append ((bov.get_attr('TIME'), bov))
            grids.append ((attr['TIME'], grid))
        grids.sort ()

        if len (grids)==1:
            grids = [(1e-32, grids[0]), (1e32, grids[1])]

        self.times = [i[0] for i in grids]
        self.grids = [i[1].point_data ('BaseLevel').copy () for i in grids]

        self.base_level = grids[0][1]

        self.start_time = self.times[0]
        self.end_time = self.times[-1]
        self.time = self.start_time

    def run (self, time):
        assert (time>=self.times[0])
        assert (time<=self.times[-1])

        self.time = time
        times = self.times
        
        val = self.base_level.point_data ('BaseLevel')
        i = bisect.bisect_right (times, time)
        try:
            m = (self.grids[i]-self.grids[i-1])/(times[i]-times[i-1])
            b = self.grids[i-1]
        except IndexError:
            val[:] = self.grids[-1]
        else:
            val[:] = m*(time-times[i-1]) + b

    def finalize (self):
        pass

    def get_start_time (self):
        return self.start_time
    def get_end_time (self):
        return self.end_time
    def get_current_time (self):
        return self.time

    def get_input_var_names (self):
        return []
    def get_output_var_names (self):
        return ['BaseLevel']

    #def get_grid_spacing (self, var):
    #    return self.base_level.get_spacing ()
    #def get_grid_origin (self, var):
    #    return self.base_level.get_origin ()
    #def get_grid_shape (self, var):
    #    return self.base_level.get_shape ()
    def get_values (self, var):
        return self.base_level.point_data (var)
    def get_grid_x (self, var):
        return self.base_level.get_x ()
    def get_grid_y (self, var):
        return self.base_level.get_y ()

    def _scan_cfg (self, file):
        parser = ConfigParser.ConfigParser ()
        parser.read (file)
        input_dir = parser.get ('BaseLevel', 'input_dir')
        input_files = parser.get ('BaseLevel', 'input_files')
        files = []
        for file in input_files.split (','):
            files.append (os.path.join (input_dir, file.strip ()))
        return files

if __name__ == "__main__":
    import doctest
    doctest.testmod()                                                                                                           

