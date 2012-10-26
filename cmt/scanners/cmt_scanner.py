#! /usr/bin/env python

import sys
import os
import StringIO
from warnings import warn

from cmt.scanners import (InputParameterScanner, findall)
from xml.etree.ElementTree import Element

class Error (Exception):
    pass
class MissingTags (Error):
    def __init__ (self, tags):
        self._tags = tags
    def __str__ (self):
        return ', '.join (self._tags)
class BadUnits (Error):
    def __init__ (self, units):
        self._units = units
    def __str__ (self):
        return ', '.join (self._units)
class BadType (Error):
    def __init__ (self, typ):
        self._type = type
    def __str__ (self):
        return ', '.join (self._type)

from string import Template
pre_text = Template ("""
#@group Input File and Directories
#    @param InputDir
#        @brief Input directory
#        @description Path to input files.
#        @type file[GUI]
#        @default GUI
#    @param SimulationName
#        @brief Simulation name
#        @description Name of the simulation
#        @default ${model_short_name}
#        @type string
""")
post_text = Template ("""
#@group About
#    @param model_name = ${model_long_name}
#        @brief Model
#        @description Name of the model
#    @param model_author = ${model_author}
#        @brief Author
#        @description Model author(s)
#    @param model_version = ${model_version}
#        @brief Version
#        @description Model version number
""")
output_text = Template ("""
#    @param dir = $${cwd}
#        @brief Output directory
#        @description Path to output files
#    @param interval = 10
#        @brief Output interval
#        @description Interval between output files
#        @units d
#        @type int
#    @param format = NC
#        @brief File format
#        @description File format for output files
#        @type choice[NC, VTK]
""")

required_tags = [
    'model',
    'model/longname',
    'model/author',
    'model/version',
]


tag_map = {
    'brief': 'label',
    'description': 'help',
    'group': 'tab',
    'param': 'entry',
}
type_to_inf = {
    'float': str (sys.float_info.max),
    'int': str (sys.maxint),
}

type_map = {
    'INTEGER': 'Int',
    'INT': 'Int',
    'LONG': 'Int',
    'FLOAT': 'Float',
    'DOUBLE': 'Float',
    'STRING': 'String',
}

def fix_type (type):
    try:
        return type_map[type.upper ()]
    except KeyError:
        raise BadType (type)

class CmtScanner (InputParameterScanner):
    @staticmethod
    def hook (buffer):
        from tempfile import TemporaryFile
        with TemporaryFile () as f:
            f.write (buffer)
            f.seek (0)
            scanner = InputParameterScanner (f)
            scanner.scan_file ()
        #CmtScanner.translate (scanner.root ())
        return list (scanner.root ())

    @staticmethod
    def model_metadata (root):
        md = dict (
            model_short_name = root.find ('model').attrib['name'],
            model_long_name = root.find ('model/longname').text,
            model_author = root.find ('model/author').text,
            model_version = root.find ('model/version').text,
        )
        return md

    @staticmethod
    def guess_type (entry):
        type = 'string'
        try:
            default_str = entry.find ('default').text
            try:
                int (default_str)
                type = 'Int'
            except ValueError:
                try:
                    float (default_str)
                    type = 'Float'
                except ValueError:
                    pass
        except AttributeError:
            pass
        return type

    @staticmethod
    def translate (root):

        for (from_tag, to_tag) in tag_map.items ():
            for node in findall (root, from_tag):
                node.tag = to_tag

        for entry in findall (root, 'entry'):
            if entry.find ('label') is None:
                label = Element ('label')
                label.text = entry.attrib['name']
                entry.append (label)
                warn ('LABEL tag not present. Using NAME attribute.',
                     RuntimeWarning)

        for entry in findall (root, 'entry'):
            if entry.find ('help') is None:
                help = Element ('help')
                help.text = entry.find ('label').text
                entry.append (help)
                warn ('HELP tag not present. Using LABEL tag.',
                     RuntimeWarning)

        for entry in findall (root, 'entry'):
            try:
                type = entry.find ('type')
                type_str = type.text
            except AttributeError:
                pass
            else:
                help = entry.find ('help')
                if type_str.startswith ('choice'):
                    options = type_str[type_str.find ('[')+1: type_str.find (']')]
                    options = options.split (',')
                    options = [o.strip () for o in options]
                    help.text += '{' + ';'.join (['dl'] + options) + '}'
                    entry.remove (type)
                elif type_str.startswith ('file'):
                    options = type_str[type_str.find ('[')+1: type_str.find (']')]
                    options = options.split (',')
                    options = [o.strip () for o in options]
                    options = ['Enter path to file'] + options
                    help.text += '{' + ';'.join (['cb+bb'] + options) + '}'
                    entry.remove (type)

        for entry in findall (root, 'entry'):
            if entry.find ('type') is None:
                type = Element ('type')
                type.text = CmtScanner.guess_type (entry)
                entry.append (type)
                warn ('TYPE tag not present. Using %s for TYPE.' % type.text,
                      RuntimeWarning)

        for type in findall (root, 'type'):
            type.text = fix_type (type.text)

        for entry in findall (root, 'entry'):
            range = entry.find ('range')
            try:
                limits = range.text.split (',')
            except AttributeError:
                range = Element ('range')
                limits = ['-inf', 'inf']
                warn ('LIMITS tag not present. Using -inf, inf')

            type = entry.find ('type')
            if type.text not in type_to_inf.keys ():
                continue

            for (i, tag) in enumerate (['min', 'max']):
                e = Element (tag)
                e.text = limits[i].strip ()
                if e.text == 'inf':
                    e.text = type_to_inf[type.text]
                elif e.text == '-inf':
                    e.text = '-' + type_to_inf[type.text]
                range.append (e)
            range.text = ''

    @staticmethod
    def check_required (root):
        missing = []
        for tag in required_tags:
            if root.find (tag) is None:
                missing.append (tag)
        if len (missing)>0:
            raise MissingTags (missing)

    @staticmethod
    def check_units (root):
        import cfunits as cf
        bad_units = []
        for units in findall (root, 'units'):
            try:
                if units.text == '-':
                    units.text = '1'
                cf.Units (units.text)
            except TypeError:
                bad_units.append (units.text)
        if len (bad_units) > 0:
            raise BadUnits (bad_units)

    @staticmethod
    def output_params (root):
        params = findall (root, 'param')
        vars = []
        for param in params:
            try:
                if param.attrib['arg'] == 'out':
                    vars.append (param)
            except KeyError:
                pass
        return vars

    @staticmethod
    def group_output_params (root):
        parent_map = dict((c, p) for p in root.getiterator() for c in p)

        #params = CmtScanner.output_params (root)
        params = findall (root, 'param', dict (arg='out'))

        orphans = []
        groups = set ()
        for var in params:
            parent = parent_map[var]
            if parent.tag != 'group':
                orphans.append (var)
            else:
                groups.add (parent)
                try:
                    parent_map[parent].remove (parent)
                except (KeyError, ValueError):
                    pass

        if len (orphans) > 0:
            group_names = [g.attrib['name'] for g in groups]
            group_name = 'Output'
            i = 0
            while (not group_name in group_names):
                group_name = 'Output %d' % i
                i += 1

            group = Element ('group')
            group.attrib['name'] = group_name
            for orphan in orphans:
                parent_map[orphan].remove (orphan)
                group.append (orphan)
            groups.add (group)

        return list (groups)

    @staticmethod
    def set_namespace (root, tag, ns, attrs={}):
        for node in findall (root, tag, attrs):
            node.attrib['name'] = os.path.join (ns, node.attrib['name'])

    @staticmethod
    def translate_output_group (root, md):
        ns = '/%s/Output/%s/' % (md['model_short_name'], root.attrib['name'])

        output_vars = findall (root, 'param', dict (arg='out'))

        md.update (dict (group_name=root.attrib['name']))
        tab_entries = CmtScanner.hook (output_text.substitute (md))
        for entry in tab_entries[::-1]:
            root.insert (0, entry)
        CmtScanner.set_namespace (root, 'param', ns)

        CmtScanner.translate (root)

        for var in output_vars:
            name = os.path.basename (var.attrib['name'])
            var.clear ()

            var.attrib['name'] = os.path.join (ns, 'Var', name)
            var.attrib['class'] = 'OutputFile'

        #from xml.etree.ElementTree import tostring
        #from xml.dom.minidom import parseString

        #doc = parseString (tostring (root))
        #print doc.toprettyxml ()

    def to_xml (self):
        root = self.root ()

        md = self.model_metadata (root)

        self.check_required (root)
        self.check_units (root)

        #self.set_namespace (root, 'param',
        #                    '/%s/Input/Var/' % md['model_short_name'])

        output_groups = self.group_output_params (root.find ('model'))
        for node in output_groups:
            self.translate_output_group (node, md)

        pre = self.hook (pre_text.substitute (md))
        post = self.hook (post_text.substitute (md))
        for node in pre + post + [root]:
            self.translate (node)
            self.set_namespace (node, 'entry',
                                '/%s/Input/Var/' % md['model_short_name'])

        dialog = Element ('dialog')
        tabs = findall (root, 'tab')
        dialog.extend (pre + tabs + output_groups + post)

        self.parent[0] = dialog

        return super (CmtScanner, self).to_xml ()

