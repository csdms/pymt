#! /usr/bin/env python

from ConfigParser import ConfigParser
from StringIO import StringIO
import types
import warnings

try:
    import services
except ImportError:
    warnings.warn('services has not been set')

from ..bov.database import Database as BovDatabase
from ..vtk.vtu import Database as VtkDatabase
from ..nc.database import Database as NcDatabase
from ..utils.prefix import strip_prefix, names_with_prefix


from .utils import (_construct_port_as_field, _reconstruct_port_as_field,
                    construct_file_name, next_unique_file_name, )


class PortPrinter(object):
    def __init__(self, port, var_name):
        if isinstance(port, types.StringTypes):
            self._port = services.get_port(port)
        else:
            self._port = port
        self._var_name = var_name

        self._field = _construct_port_as_field(self._port, var_name)
        self._printer = self._printer_class()

    @property
    def var_name(self):
        return self._var_name

    @property
    def format(self):
        return self._format

    def open(self, clobber=False):
        file_name = construct_file_name(self.var_name, format=self.format,
                                        prefix='')
        if not clobber:
            file_name = next_unique_file_name(file_name)

        self._printer.open(file_name, self.var_name)

    def close(self):
        self._printer.close()
        self._printer = self._printer_class()

    def write(self):
        self.resync_field_to_port()
        self._printer.write(self._field)

    def resync_field_to_port(self):
        self._field = _reconstruct_port_as_field(self._port, self._field)

    @classmethod
    def from_string(cls, source, prefix='print'):
        config = ConfigParser()
        config.readfp(StringIO(source))
        return cls._from_config(config, prefix=prefix)

    @classmethod
    def from_path(cls, path, prefix='print'):
        config = ConfigParser()
        config.read(path)
        return cls._from_config(config, prefix=prefix)

    @classmethod
    def _from_config(cls, config, prefix='print'):
        printers = []
        for section in names_with_prefix(config.sections(), prefix):
            printers.append(cls.from_dict({
                'port': config.get(section, 'port'),
                'format': config.get(section, 'format'),
                'name': strip_prefix(section, prefix),
            }))
        if len(printers) == 1:
            return printers[0]
        else:
            return printers

    @classmethod
    def from_dict(cls, d):
        try:
            printer_class = _FORMAT_TO_PRINTER[d['format']]
        except KeyError:
            raise ValueError('%s: unknown printer format' % d['format'])
        return printer_class(d['port'], d['name'])


class VtkPortPrinter(PortPrinter):
    _format = 'vtk'
    _printer_class = VtkDatabase


class NcPortPrinter(PortPrinter):
    _format = 'nc'
    _printer_class = NcDatabase


class BovPortPrinter(PortPrinter):
    _format = 'bov'
    _printer_class = BovDatabase


_FORMAT_TO_PRINTER = {
    'vtk': VtkPortPrinter,
    'nc': NcPortPrinter,
    'bov': BovPortPrinter,
}
