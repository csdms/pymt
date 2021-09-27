from ..portprinter.port_printer import PortPrinter
from ..utils import as_cwd


class PrintEvent:
    def __init__(self, *args, **kwds):
        # self._printer = PortPrinter.from_dict(kwds)
        self._run_dir = kwds.pop("run_dir", ".")
        self._kwds = kwds

    def initialize(self, *args):
        with as_cwd(self._run_dir):
            self._printer = PortPrinter.from_dict(self._kwds)
            self._printer.open()

    def run(self, time):
        with as_cwd(self._run_dir):
            self._printer.write()

    def finalize(self):
        with as_cwd(self._run_dir):
            self._printer.close()
