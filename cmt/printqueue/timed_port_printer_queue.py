#! /usr/bin/env python

from cmt.timeline import Timeline
from cmt.printqueue.port_printer_queue import get_printer_from_format


class TimedPortPrinterQueue(object):
    def __init__ (self, port):
        self._port = port
        self._print_timeline = Timeline()

    @property
    def next_print_time(self):
        return self._print_timeline.time_of_next_event

    def add(self, step, var_name, format='vtk'):
        printer = get_printer_from_format(format, self._port, var_name)
        self._print_timeline.add_recurring_event(printer, step)

    def open(self):
        for printer in self._print_timeline.events:
            printer.open()

    def close(self):
        for printer in self._print_timeline.events:
            printer.close()

    def write(self, time):
        for printer in self._print_timeline.pop_until(time):
            printer.write()
