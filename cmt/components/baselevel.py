#! /bin/env python

import os
import ConfigParser
from urlparse import urlparse, urlunparse
import bisect
import glob
from types import StringTypes

import numpy as np

from cmt.bmi import BMI
#from cmt import VTKGridUniformRectilinear
#from cmt.bov import fromfile
from cmt.nc import fromfile

class BaseLevel (BMI):
    """
    >>> file = 'http://csdms.colorado.edu/thredds/dodsC/benchmark/sample/falling_baselevel.nc'

    >>> bl = BaseLevel () #doctest: +REPORT_ONLY_FIRST_FAILURE
    >>> bl.initialize (file)

    #>>> bl.initialize (['Test_0000_BaseLevel.bov', 'Test_0001_BaseLevel.bov'])

    The model is only valid between the start and end times.

    >>> bl.get_current_time ()
    0.0
    >>> bl.get_start_time ()
    0.0
    >>> bl.get_end_time ()
    5000.0

    The initial values

    >>> vals = bl.get_values ('BaseLevel')
    >>> np.all (vals==0.)
    True
    >>> uplift = bl.get_values ('Uplift')
    >>> np.all (uplift==0.)
    True

    Still the initial values

    >>> bl.run (0.0)
    >>> np.all (vals==0.)
    True

    Run until time=110. We have a reference to the data so
    we don't have to do another get_values call.

    >>> bl.run (110)
    >>> bl.get_current_time ()
    110.0
    >>> np.all (np.abs (vals-1.0) < 1e-12)
    True
    >>> np.all (np.abs (uplift-1.0) < 1e-12)
    True

    Run until the last time.

    >>> bl.run (5000.0)
    >>> bl.get_current_time ()
    5000.0
    >>> np.all (vals==10.)
    True
    >>> np.all (uplift==9.0)
    True


    It's OK to run backwards in time.

    >>> bl.run (2.0)
    >>> bl.get_current_time ()
    2.0
    >>> np.all (vals==0.0)
    True

    It's an error to try to run outside of the start or end times.

    >>> bl.run (5000.0001)
    Traceback (most recent call last):
        ...
    AssertionError

    File globbing also works

    >>> bl = BaseLevel ()
    >>> bl.initialize (file)

    The model is only valid between the start and end times.

    >>> bl.get_current_time ()
    0.0
    >>> bl.get_end_time ()
    5000.0
    >>> vals = bl.get_values ('Uplift')
    >>> np.all (vals==0.)
    True

    >>> bl = BaseLevel ()
    >>> bl.initialize ('baselevel.cfg')
    >>> bl.get_current_time ()
    0.0
    >>> bl.get_end_time ()
    5000.0
    >>> vals = bl.get_values ('BaseLevel')
    >>> np.all (vals==0.)
    True
    """
    def initialize (self, file):
        #if isinstance (files, StringTypes):
        #    (base, ext) = os.path.splitext (files)
        #    if ext=='.cfg':
        #        files = self._scan_cfg (files)
        #    else:
        #        files = [files]
        #matched_files = []
        #for file in files:
        #    matched_files.extend (glob.glob (file))

        #grids = []
        #for file in matched_files:
        #    #var = BovFile ()
        #    #var.frombov (file)
        #    #grids.append ((var['TIME'], var))

        #    (grid, attr) = fromfile (file, allow_singleton=False)
        #    #grids.append ((bov.get_attr('TIME'), bov))
        #    grids.append ((attr['TIME'], grid))
        #grids.sort ()



        (base, ext) = os.path.splitext (file)
        if ext=='.cfg':
            file = self._scan_cfg (file)

        fields = fromfile (file, allow_singleton=False)
        fields.sort ()

        #if len (fields)==1:
        #    grids = [(1e-32, grids[0]), (1e32, grids[0])]

        self.times = []
        self.grids = []
        for (time, field) in fields:
            self.times.append (time)
            self.grids.append (field.get_field ('BaseLevel').copy ())

        #self.times = [i[0] for i in grids]
        #self.grids = [i[1].point_data ('Uplift').copy () for i in grids]

        self.base_level = fields[0][1]
        self.base_level.add_field ('Uplift', self.base_level.get_field ('BaseLevel')*0., centering='point')

        self.start_time = self.times[0]
        self.end_time = self.times[-1]
        self.time = self.start_time

    def run (self, time):
        #print 'BMI: Running baselevel'

        assert (time>=self.times[0])
        assert (time<=self.times[-1])

        self.time = float (time)
        times = self.times
        
        val = self.base_level.get_field ('BaseLevel')
        val_save = self.base_level.get_field ('BaseLevel').copy ()
        i = bisect.bisect_right (times, time)
        try:
            m = (self.grids[i]-self.grids[i-1])/(times[i]-times[i-1])
            b = self.grids[i-1]
        except IndexError:
            #val[:] = self.grids[-1]
            val.flat = self.grids[-1].flat
        else:
            val.fill (m*(time-times[i-1]) + b)

        #print 'BMI: Setting uplift'
        uplift = self.base_level.get_field ('Uplift')
        uplift.fill (val-val_save)
        #print 'BMI: Ran baselevel'

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
        return ['Uplift', 'BaseLevel']

    #def get_grid_spacing (self, var):
    #    return self.base_level.get_spacing ()
    #def get_grid_origin (self, var):
    #    return self.base_level.get_origin ()
    #def get_grid_shape (self, var):
    #    return self.base_level.get_shape ()
    def get_values (self, var):
        #print 'BMI: Getting values for baselevel (%s)' % var
        vals = self.base_level.get_field (var)
        #print vals
        return vals
    def get_grid_x (self, var):
        return self.base_level.get_x ()
    def get_grid_y (self, var):
        return self.base_level.get_y ()

    def _scan_cfg (self, file):
        parser = ConfigParser.ConfigParser ()
        parser.read (file)
        input_dir = parser.get ('BaseLevel', 'input_dir')
        input_file = parser.get ('BaseLevel', 'input_file')

        #files = []
        #for file in input_files.split (','):
        #    files.append (os.path.join (input_dir, file.strip ()))

        o = urlparse (input_file.strip ())
        if o.scheme in ['file', '']:
            if os.path.isabs (o.path):
                return o.path
            else:
                return os.path.join (input_dir.strip (), o.path)
        else:
            return urlunparse (o)

if __name__ == "__main__":
    import doctest
    doctest.testmod()                                                                                                           

