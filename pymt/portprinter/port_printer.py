#! /usr/bin/env python

import six
from six.moves.configparser import ConfigParser

from ..framework import services
from ..printers.nc.database import Database as NcDatabase

# from ..printers.vtk.vtu import Database as VtkDatabase
from ..utils.prefix import names_with_prefix, strip_prefix
from .utils import (
    construct_file_name,
    construct_port_as_field,
    next_unique_file_name,
    reconstruct_port_as_field,
)


class PortPrinter(object):
    _format = ""
    _printer_class = None

    def __init__(self, port, var_name, filename=None):
        if isinstance(port, six.string_types):
            self._port = services.get_component_instance(port)
        else:
            self._port = port
        self._var_name = var_name
        self._filename = filename
        if filename is None:
            self._filename = var_name

        self._field = construct_port_as_field(self._port, var_name)
        self._printer = self._printer_class()

    @property
    def var_name(self):
        return self._var_name

    @property
    def format(self):
        return self._format

    def open(self, clobber=False):
        file_name = construct_file_name(self._filename, fmt=self.format, prefix="")
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
        self._field = reconstruct_port_as_field(self._port, self._field)

    @classmethod
    def from_string(cls, source, prefix="print"):
        config = ConfigParser()
        config.readfp(six.StringIO(source))
        return cls._from_config(config, prefix=prefix)

    @classmethod
    def from_path(cls, path, prefix="print"):
        config = ConfigParser()
        config.read(path)
        return cls._from_config(config, prefix=prefix)

    @classmethod
    def _from_config(cls, config, prefix="print"):
        printers = []
        for section in names_with_prefix(config.sections(), prefix):
            printers.append(
                cls.from_dict(
                    {
                        "port": config.get(section, "port"),
                        "format": config.get(section, "format"),
                        "name": strip_prefix(section, prefix),
                    }
                )
            )
        if len(printers) == 1:
            return printers[0]
        else:
            return printers

    @classmethod
    def from_dict(cls, d):
        try:
            printer_class = _FORMAT_TO_PRINTER[d["format"]]
        except KeyError:
            raise ValueError("%s: unknown printer format" % d["format"])
        return printer_class(
            d["port"], d["name"], filename=d.get("filename", d["name"])
        )


# class VtkPortPrinter(PortPrinter):
#     _format = "vtk"
#     _printer_class = VtkDatabase


class NcPortPrinter(PortPrinter):
    _format = "nc"
    _printer_class = NcDatabase


_FORMAT_TO_PRINTER = {
    # "vtk": VtkPortPrinter,
    "nc": NcPortPrinter,
    "netcdf": NcPortPrinter,
}
