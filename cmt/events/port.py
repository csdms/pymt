from ..portprinter.port_printer import PortPrinter
try:
    import services
except ImportError:
    warnings.warn('services has not been set')


class PortEvent(object):
    def __init__(self, *args, **kwds):
        self._port = services.get_port(kwds['port'])

    def initialize(self):
        self._port.initialize()

    def run(self, time):
        self._port.run(time)

    def finalize(self):
        self._port.finalize()
