from ..portprinter.port_printer import PortPrinter
import types
import warnings

try:
    import services
except ImportError:
    warnings.warn('services has not been set')


class PortEvent(object):
    def __init__(self, *args, **kwds):
        if isinstance(kwds['port'], types.StringTypes):
            self._port = services.get_port(kwds['port'])
        else:
            self._port = kwds['port']

    def initialize(self):
        self._port.initialize()

    def run(self, time):
        self._port.run(time)

    def finalize(self):
        self._port.finalize()
