from ..portprinter.port_printer import PortPrinter
from ..utils.run_dir import open_run_dir


class PrintEvent(object):
    def __init__(self, *args, **kwds):
        # self._printer = PortPrinter.from_dict(kwds)
        self._run_dir = kwds.pop("run_dir", ".")
        self._kwds = kwds

    def initialize(self, *args):
        with open_run_dir(self._run_dir):
            self._printer = PortPrinter.from_dict(self._kwds)
            self._printer.open()

    def run(self, time):
        with open_run_dir(self._run_dir):
            self._printer.write()

    def finalize(self):
        with open_run_dir(self._run_dir):
            self._printer.close()
