#! /usr/bin/env python


from ..printqueue.port_printer import (VtkPortPrinter, NcPortPrinter,
                                       BovPortPrinter)


_PRINTERS = {
    'vtk': VtkPortPrinter,
    'nc': NcPortPrinter,
    'bov': BovPortPrinter,
}
_FORMAT_EXTENSION = {
    'nc': '.nc',
    'vtk': '.vtu',
    'bov': '.bov'
}


def normalize_format_name(format):
    if format.startswith('.'):
        format = format[1:]
    return format.lower()


def format_to_file_extension(format):
    try:
        return _FORMAT_EXTENSION[normalize_format_name(format)]
    except KeyError:
        raise BadFileFormatError(normalize_format_name(format))


def format_to_printer(format):
    try:
        return _PRINTERS[normalize_format_name(format)]
    except KeyError:
        raise BadFileFormatError(normalize_format_name(format))


def get_printer_from_format(format, *args):
    printer_class = format_to_printer(format)
    return printer_class(*args)


class PortPrinterQueue(object):
    def __init__(self, port):
        self._port = port
        self._queue = []

    def insert(self, index, var_name, format='vtk'):
        self._queue.insert(index, get_printer_from_format(format, self._port,
                                                          var_name))

    def append(self, var_name, **kwds):
        self.insert(len(self._queue), var_name, **kwds)

    def prepend(self, var_name, **kwds):
        self.insert(0, var_name, **kwds)

    def open(self):
        for printer in self._queue:
            printer.open()

    def write(self):
        for printer in self._queue:
            printer.write()

    def close(self):
        for printer in self._queue:
            printer.close()
