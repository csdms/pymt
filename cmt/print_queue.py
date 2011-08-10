"""

>>> import numpy
>>> grid = numpy.random.random ((4,5))
>>> port = GridPort ()
>>> port.add_grid (grid, 'Elevation')
>>> port.add_grid (grid, 'Slope')

>>> attr = {'/SitePrefix': 'beach', '/CasePrefix': '0',
... '/Output/Grid/Interval': 10 , '/Output/Grid/Dir': './test',
... '/Output/Grid/Var/Elevation': '<site>_<case>_Elevation.nc',
... '/Output/Grid/Var/Slope': '<site>_<case>_Slope.nc'}
>>> q = PrintQueue (attr, None, port)
>>> q.add_files ('Output/Grid')
>>> vars = q.in_queue ('Output/Grid')
>>> vars.sort ()
>>> vars
['Elevation', 'Slope']
>>> q.next_print_time ()
10.0
>>> q.print_all (0)
>>> q.next_print_time ()
10.0
>>> q.print_all (33)
Imported Nio version: 1.3.0b1
Imported Nio version: 1.3.0b1
>>> q.next_print_time ()
40.0
>>> os.path.exists ('./test/beach_0_Elevation.nc')
True
>>> os.path.exists ('./test/beach_0_Slope.nc')
True

>>> port.add_grid (grid, 'Density')
>>> port.add_grid (grid, 'GrainSize')
>>> port.add_grid (grid, 'VoidRatio')

>>> attr = {'/SitePrefix': 'beach', '/CasePrefix': '1',
... '/Output/Grid/Interval': 10 , '/Output/Grid/Dir': './test',
... '/Output/Grid/Var/Elevation': '<site>_<case>_Elevation.nc',
... '/Output/Grid/Var/Slope': '<site>_<case>_Slope.nc',
... '/Output/Cube/Interval': 6 , '/Output/Cube/Dir': './test',
... '/Output/Cube/Var/GrainSize': '<site>_<case>_GrainSize.nc',
... '/Output/Cube/Var/VoidRatio': '<site>_<case>_VoidRatio.nc',
... '/Output/Cube/Var/Density': '<site>_<case>_Density.nc'}
>>> q = PrintQueue (attr, None, port)
>>> q.add_files ('Output/Grid')
>>> vars = q.in_queue ('Output/Grid')
>>> vars.sort ()
>>> vars
['Elevation', 'Slope']

>>> q.add_files ('Output/Cube')
>>> vars = q.in_queue ('Output/Cube')
>>> vars.sort ()
>>> vars
['Density', 'GrainSize', 'VoidRatio']

>>> q.next_print_time ()
6.0
>>> q.print_all (0)
>>> q.next_print_time ()
6.0
>>> q.print_all (5)
>>> q.next_print_time ()
6.0
>>> q.print_all (6)
Imported Nio version: 1.3.0b1
Imported Nio version: 1.3.0b1
Imported Nio version: 1.3.0b1
>>> q.next_print_time ()
10.0
>>> q.print_all (10)
Imported Nio version: 1.3.0b1
Imported Nio version: 1.3.0b1
>>> q.next_print_time ()
12.0

>>> os.path.exists ('./test/beach_1_GrainSize.nc')
True
>>> os.path.exists ('./test/beach_1_Density.nc')
True
>>> os.path.exists ('./test/beach_1_VoidRatio.nc')
True
>>> os.path.exists ('./test/beach_1_Elevation.nc')
True
>>> os.path.exists ('./test/beach_1_Slope.nc')
True

>>> port = MeshPort ()
>>> elementSet = RectilinearElementSet ((20,5), (1,4))
>>> port.add_mesh (elementSet)
>>> port.add_value_set (numpy.arange (4*elementSet.getElementCount ()), 'Elevation')
>>> port.add_value_set (numpy.arange (4*elementSet.getElementCount ()), 'Slope')

>>> attr = {'/SitePrefix': 'beach', '/CasePrefix': '2',
... '/Output/Grid/Interval': 10 , '/Output/Grid/Dir': './test',
... '/Output/Grid/FileFormat': 'VTK',
... '/Output/Grid/Var/Elevation': '<site>_<case>_Elevation.vtu',
... '/Output/Grid/Var/Slope': '<site>_<case>_Slope.vtu'}
>>> q = PrintQueue (attr, None, port)
>>> q.add_files ('Output/Grid')
>>> vars = q.in_queue ('Output/Grid')
>>> vars.sort ()
>>> vars
['Elevation', 'Slope']

>>> q.next_print_time ()
10.0
>>> q.print_all (10.)
"""

import os
import sys

import numpy

import namespace as ns
from verbose import CMTVerbose
import csdms_utils
import csdms_utils.raster_file

from csdms_utils.raster_file import NCRasterFile, VTKUnstructuredFile
from csdms_utils.raster_file.element_set import RectilinearElementSet

verbose = CMTVerbose ()

class IGridPort (object):
  def get_raster_dimen (self, name):
    pass
  def get_raster_res (self, name):
    pass
  def get_raster_data (self, name):
    pass

  def get_element_set (self, name):
    pass
  def get_value_set (self, name):
    pass
  def get_value_set_data (self, name):
    pass

class GridPort (object):
  """
  >>> import numpy
  >>> grid = numpy.arange (12).reshape (2,6)
  >>> port = GridPort ()
  >>> port.add_grid (grid, 'Elevation')
  >>> port.get_raster_dimen ('Elevation')
  [2, 6]
  >>> port.get_raster_res ('Elevation')
  [1.0, 1.0]
  >>> port.get_raster_data ('Elevation')
  array([[ 0,  1,  2,  3,  4,  5],
         [ 6,  7,  8,  9, 10, 11]])

  """

  def __init__ (self):
    self._grids = {}
    self._grid = None
    self._values = {}

  def add_grid (self, grid, name, res=None):
    if res is None:
      res = [1]*len (grid.shape)
    else:
      res = [val for val in res]
    self._grids[name] = (grid, res)

    self._grid = RectilinearElementSet (grid.shape, res)
    self._values[name] = grid

  def get_raster_dimen (self, name):
    return self._grid.getDimen ()
    #return [val for val in self._grids[name][0].shape]
  def get_raster_res (self, name):
    return self._grid.getRes ()
    #return [val for val in self._grids[name][1]]
  def get_raster_data (self, name):
    return self._values[name]
    #return self._grids[name][0]

  def get_element_set (self, name):
    return self._grid
  def get_value_set (self, name):
    return self.get_value_set_data (name)
  def get_value_set_data (self, name):
    return self._values[name]

class MeshPort (IGridPort):
  def __init__ (self):
    self._mesh = None
    self._values = {}
  def add_mesh (self, elementSet):
    self._mesh = elementSet
  def add_value_set (self, valueSet, name):
    self._values[name] = valueSet

  def get_element_set (self, name):
    return self._mesh
  def get_value_set (self, name):
    return self.get_value_set_data (name)
  def get_value_set_data (self, name):
    return self._values[name]

class PrintQueue (object):
  def __init__ (self, attr, namespace, port):
    self._attr = attr
    if namespace is None:
      self._ns = '/'
    else:
      self._ns = namespace
    self._port = port

    # Find global queue attributes
    try:
      self._site = attr[ns.join (self._ns, 'SitePrefix')]
      self._case = attr[ns.join (self._ns, 'CasePrefix')]
    except KeyError as e:
      print '%s: Attribute dictionary does not contain required key' % e
      raise

    verbose (8, 'Site prefix: %s' % self._site)
    verbose (8, 'Case prefix: %s' % self._case)

    self._queues = {}
  def in_queue (self, name):
    return self._queues[name]['vars']

  def add_files (self, var_namespace):
    var_ns = ns.join (self._ns, var_namespace)
    verbose (8, 'Adding files from namespace: %s' % var_ns)

    attr = self._attr
    port = self._port

    q = {}

    # Find variable specific attributes
    q['path'] = attr[ns.join (var_ns, 'Dir')]
    try:
      q['format'] = attr[ns.join (var_ns, 'FileFormat')]
    except KeyError:
      q['format'] = 'NetCDF'

    # Look for variables in this namespace
    prefix = ns.join (var_ns, 'Var')
    all_vars = []
    for key in attr.keys ():
      (head, tail) = ns.split (key)
      if head == prefix:
        verbose (8, 'Found variable to print: %s' % key)
        all_vars.append (tail)

    q['files'] = csdms_utils.raster_file.RasterFiles ()
    q['vars'] = []
    for var in all_vars:
      file = attr[ns.join (var_ns, 'Var', var)]
      if not file.upper () in ['OFF', 'NO', 'FALSE']:
        q['vars'].append (var)
        file = file.replace ('<site>', self._site).replace ('<case>', self._case)

        # If the file doesn't have an extension, add one based on file format
        path = os.path.join (q['path'], file)
        (root, ext) = os.path.splitext (path)
        if len (ext)==0:
          if q['format'] == 'NetCDF':
            ext = '.nc'
          elif q['format'] == 'VTK':
            ext = '.vtu'
          path = root + ext

        if q['format'] == 'NetCDF':
          try:
            dimen = port.get_raster_dimen (var)
            res = port.get_raster_res (var)
            verbose (8, 'Output variable is %s' % var)
            verbose (8, 'Output file is %s' % path)
            verbose (8, 'Output file format is %s' % q['format'])
            verbose (8, 'Variable dimension is %s' %
                          ' x '.join ([str (val) for val in dimen]))
            verbose (8, 'Variable resolution is %s' %
                          ' x '.join ([str (val) for val in res]))

            new_file = csdms_utils.raster_file.RasterFileDB (NCRasterFile)
            q['files'].add_file (new_file, path, var)
          except Exception as e:
            print 'ERROR: Unable to add file: %s' % e
            raise
        else:
          new_file = csdms_utils.raster_file.RasterFileDB (VTKUnstructuredFile)
          q['files'].add_file (new_file, path, var)
          #print 'ERROR: format not supported yet: %s' % q['format']
      else:
        print 'OFF'
    verbose (8, 'Variables queued for printing %s' % ' '.join (q['vars']))

    # Find variable specific attributes
    if len (q['vars']) == 0:
      q['interval'] = sys.float_info.max
    else:
      q['interval'] = float (attr[ns.join (var_ns, 'Interval')])
    q['start_print'] = 0.
    q['next_print'] = q['interval']
    #q['next_print'] = q['start_print']

    verbose (8,'Print directory: %s' % q['path'])
    verbose (8,'Print interval: %f' % q['interval'])

    q['files'].open_all ()

    self._queues[var_namespace] = q

  def next_print_time (self):
    times = [q['next_print'] for q in self._queues.values ()]
    return min (times)

  def print_all (self, time):
    for q in self._queues.values ():
      if time >= q['next_print']:
        for var in q['vars']:
          try:
            verbose (8, 'Printing variable %s at %f' % (var, time))

            if q['format'] == 'NetCDF':
              dimen = self._port.get_raster_dimen (var)
              res = self._port.get_raster_res (var)
              grid = RectilinearElementSet (dimen, res)
            else:
              grid = self._port.get_element_set (var)

            verbose (8, 'Got element set')
            #verbose (8, 'Number of elements is %s', grid.getElementCount ())
            q['files'].set_grid (var, grid)
            verbose (8, 'Grid is set')

            verbose (8, 'Get values')
            values = self._port.get_value_set_data (var)
            verbose (8, 'Number of values is %d' % len (values))
            verbose (8, 'Got values')
            
            q['files'].append_val (var, values, time=time)
            verbose (8, 'Appended values')

            #data = self._port.get_raster_data (var)
            #verbose (8, 'Data size is' + 'x'.join ([str (val) for val in data.shape]))
            #q['files'].append_val (var, data, time=time)
          except Exception as e:
            print 'ERROR: Unable to write grid: %s' % e
            self._update_next_print (time, q)
            raise
        self._update_next_print (time, q)

  def close (self):
    for q in self._queues.values():
      q['files'].close_all ()

  def _update_next_print (self, time, q):
    time_next = q['next_print']
    dt = q['interval']
    q['next_print'] += (int ((time-time_next)/dt)+1)*dt

if __name__ == "__main__":
    import doctest
    doctest.testmod()


