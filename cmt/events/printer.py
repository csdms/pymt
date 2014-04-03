from ..portprinter.port_printer import PortPrinter


class PrintEvent(object):
    def __init__(self, *args, **kwds):
        self._printer = PortPrinter.from_dict(kwds)

    def initialize(self):
        self._printer.open()

    def run(self, time):
        self._printer.write()

    def finalize(self):
        self._printer.close()
