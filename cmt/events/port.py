from ..portprinter.port_printer import PortPrinter
import services


class PortEvent(object):
    def __init__(self, *args, **kwds):
        self._port = services.get_port(kwds['port'])

    def initialize(self):
        self._port.initialize()

    def run(self, time):
        self._port.run(time)

    def finalize(self):
        self._port.finalize()
