import os
import types
import warnings

from ..mappers.mapper import find_mapper
from ..mappers.pointtopoint import NearestVal
from ..portprinter.port_printer import PortPrinter
from ..component.grid import GridMixIn
from ..utils.run_dir import open_run_dir

try:
    import services
except ImportError:
    warnings.warn('services has not been set')


def get_port(port):
    if isinstance(port, types.StringTypes):
        return services.get_port(port)
    else:
        return port


class PortEvent(GridMixIn):
    def __init__(self, *args, **kwds):
        self._port = get_port(kwds['port'])
        self._init_args = kwds.get('init_args', [])
        self._run_dir = kwds.get('run_dir', '.')

        if isinstance(self._init_args, types.StringTypes):
            self._init_args = [self._init_args]
        self._status_fp = open(os.path.abspath(
            os.path.join(self._run_dir, '_time.txt')), 'w')
        GridMixIn.__init__(self)

    def initialize(self):
        with open_run_dir(self._run_dir):
            self._status_fp.write('%f' % 0.0)
            try:
                self._port.initialize(*self._init_args)
            except Exception as error:
                print self._port
                print self._init_args
                raise

    def run(self, time):
        with open_run_dir(self._run_dir):
            self._status_fp.write('\n%f' % time)
            self._status_fp.flush()
            self._port.run(time)

    def update(self, time):
        with open_run_dir(self._run_dir):
            self._port.update(time)

    def finalize(self):
        with open_run_dir(self._run_dir):
            self._status_fp.write('\ndone.')
            self._port.finalize()
        self._status_fp.close()


class PortMapEvent(object):
    def __init__(self, *args, **kwds):
        self._src = get_port(kwds['src_port'])
        self._dst = get_port(kwds['dst_port'])
        self._vars_to_map = kwds['vars_to_map']

        #self._mapper = NearestVal()
        ##self._mapper = find_mapper(self._dst, self._src)
        self._mapper = None

    def initialize(self):
        #self._mapper.initialize(self._dst, self._src, vars=self._vars_to_map)
        pass

    def run(self, stop_time):
        for (dst_name, src_name) in self._vars_to_map:
            #dst_values = self._dst.get_grid_values(dst_name)
            src_values = self._src.get_grid_values(src_name)

            ##dst_values = self._mapper.run(src_values, dest_values=dst_values)
            #dst_values = self._mapper.run(src_values)
            dst_values = src_values

            self._dst.set_grid_values(dst_name, dst_values)
            #self._destination.set_grid_values(dst_var_name, dst_values)

    def finalize(self):
        pass
