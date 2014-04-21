import types
import warnings

from ..mappers.mapper import find_mapper
from ..mappers.pointtopoint import NearestVal
from ..portprinter.port_printer import PortPrinter

try:
    import services
except ImportError:
    warnings.warn('services has not been set')


def get_port(port):
    if isinstance(port, types.StringTypes):
        return services.get_port(port)
    else:
        return port


class PortEvent(object):
    def __init__(self, *args, **kwds):
        self._port = get_port(kwds['port'])

    def initialize(self):
        self._port.initialize()

    def run(self, time):
        self._port.run(time)

    def finalize(self):
        self._port.finalize()


class PortMapEvent(object):
    def __init__(self, *args, **kwds):
        self._src = get_port(kwds['src_port'])
        self._dst = get_port(kwds['dst_port'])
        self._vars_to_map = kwds['vars_to_map']

        self._mapper = NearestVal()
        #self._mapper = find_mapper(self._dst, self._src)

    def initialize(self):
        self._mapper.initialize(self._dst, self._src)

    def run(self, stop_time):
        for (dst_name, src_name) in self._vars_to_map:
            dst_values = self._dst.get_grid_values(dst_name)
            src_values = self._src.get_grid_values(src_name)

            self._mapper.run(src_values, dest_values=dst_values)

            #self._destination.set_grid_values(dst_var_name, dst_values)

    def finalize(self):
        pass
