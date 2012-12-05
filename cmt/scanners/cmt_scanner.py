#! /usr/bin/env python

import sys
import os
import StringIO
import collections
from warnings import warn

from cmt.scanners import (InputParameterScanner, findall, adopt_children)
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
    def __init__ (self, type):
        self._type = type
    def __str__ (self):
        return self._type

from string import Template
pre_text = Template ("""
#@group General
#    @param SimulationName
#        @brief Simulation name
#        @description Name of the simulation
#        @default ${model_short_name}
#        @type string
#    @param run_duration = 100
#        @brief Run duration
#        @description Run duration
#        @type float
#        @units d
#        @range 1, inf
""")
#@file InputDir = GUI
#    @brief Input directory
#    @description Path to input files.
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
#    @param Dir = $${cwd}
#        @brief Output directory
#        @description Path to output files
#    @param Interval = 10
#        @brief Output interval
#        @description Interval between output files
#        @units d
#        @type int
#        @range 1, inf
#    @param FileFormat = NC
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
    'description': 'help_brief',
    'group': 'tab',
    'param': 'entry',
    'units': 'unit',
    'file': 'entry',
}
type_to_inf = {
    'float': str (sys.float_info.max),
    'int': str (2**32 / 2 - 1),
    #'int': str (sys.maxint),
}

type_map = {
    'BOOLEAN': 'Int',
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
    def update (self, that):
        this_model = self.root ().find ('model')
        that_model = that.root ().find ('model')

        adopt_children (this_model, that_model)

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
        if entry.attrib['name'] in ['model_version']:
            return 'string'
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

        # Any param tags without a group will be added to a new group
        # called "Params"
        orphans = CmtScanner.find_orphans (root, 'param', 'group')
        if len (orphans) > 0:
            new_parent = CmtScanner.adopt_orphans (root, orphans, 'group', 'Params')
            root.append (new_parent)

        # Map tag names to CMT names (param -> entry, etc.)
        for (from_tag, to_tag) in tag_map.items ():
            for node in findall (root, from_tag):
                node.tag = to_tag

        # If an entry doesn't have a label, set it to be the name of the
        # entry.
        for entry in findall (root, 'entry'):
            if entry.find ('label') is None:
                label = Element ('label')
                label.text = entry.attrib['name']
                entry.append (label)
                warn ('LABEL tag not present. Using NAME attribute.',
                     RuntimeWarning)

        # If an entry doesn't have a help tag, create one that is just whose
        # text is the same as the label.
        for entry in findall (root, 'entry'):
            if entry.find ('help_brief') is None:
                help = Element ('help_brief')
                help.text = entry.find ('label').text
                entry.append (help)
                warn ('HELP tag not present. Using LABEL tag.',
                     RuntimeWarning)

        # If an entry's type is a file or choice, add text to the end of the
        # help message to tell CMT to use dropdox, or combobox.
        for entry in findall (root, 'entry'):
            try:
                type = entry.find ('type')
                type_str = type.text
            except AttributeError:
                pass
            else:
                help = entry.find ('help_brief')
                if type_str.lower () == 'boolean':
                    type.text = 'choice[0,1]'
                    type_str = type.text

                if type_str.startswith ('choice'):
                    options = type_str[type_str.find ('[')+1: type_str.find (']')]
                    options = options.split (',')
                    options = [o.strip () for o in options]
                    help.text += '{' + ';'.join (['dl'] + options) + '}'
                    entry.remove (type)
                elif type_str.startswith ('file'):
                    default = entry.find ('default').text
                    if type_str.find (']') > type_str.find ('['):
                        options = type_str[type_str.find ('[')+1: type_str.find (']')]
                        options = options.split (',')
                        options = [o.strip () for o in options]
                    else:
                        options = []
                    options = [default, 'Path to file'] + options
                    help.text += '{' + ';'.join (['cb+bb'] + options) + '}'
                    entry.remove (type)

        # Guess at a type of an entry if one isn't provided.
        for entry in findall (root, 'entry'):
            if entry.find ('type') is None:
                type = Element ('type')
                type.text = CmtScanner.guess_type (entry)
                entry.append (type)
                warn ('TYPE tag not present. Using %s for TYPE.' % type.text,
                      RuntimeWarning)

        # Convert type names to proper CMT type names.
        for type in findall (root, 'type'):
            type.text = fix_type (type.text)

        # Set up ranges for an entry, if applicable. Convert the string "inf"
        # to appropriate float or int maximums (or mininums for "-inf").
        for entry in findall (root, 'entry'):
            (type, range) = (entry.find ('type'), entry.find ('range'))

            type_str = type.text.strip ().lower ()
            if type_str == 'string':
                continue

            if type_str not in type_to_inf.keys ():
                warn ('TYPE does not have a default range (%s).' % type_str,
                     RuntimeWarning)
                continue

            try:
                limits = range.text.split (',')
            except AttributeError:
                limits = ['-inf', 'inf']

                range = Element ('range')
                entry.append (range)
                warn ('LIMITS tag not present. Using -inf, inf')

            for (i, tag) in enumerate (['min', 'max']):
                e = Element (tag)
                e.text = limits[i].strip ()
                if e.text == 'inf':
                    e.text = type_to_inf[type_str]
                elif e.text == '-inf':
                    e.text = '-' + type_to_inf[type_str]
                range.append (e)
            range.text = ''

        tabs = findall (root, 'tab')
        names = [t.attrib['name'] for t in tabs]
        tab_count = collections.Counter (names)
        for tab in tab_count:
            if tab_count[tab] > 1:
                indices = [i for i, x in enumerate (names) if x == tab]
                for i in indices[1:]:
                    adopt_children (tabs[indices[0]], tabs[i])

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
    def find_orphans (root, child_tag, parent_tag, attrs={}):
        parent_map = dict((c, p) for p in root.getiterator() for c in p)

        children = findall (root, child_tag, attrs=attrs)

        orphans = []
        parents = set ()
        for child in children:
            parent = parent_map[child]
            if parent.tag != parent_tag:
                orphans.append (child)
            #else:
            #    parents.add (parent)
            #    try:
            #        parent_map[parent].remove (parent)
            #    except (KeyError, ValueError):
            #        pass

        return orphans

    @staticmethod
    def adopt_orphans (root, orphans, parent_tag, parent_name):

        if len (orphans) > 0:
            parent_map = dict((c, p) for p in root.getiterator() for c in p)

            existing_parents = findall (root, parent_tag)
            existing_parent_names = [g.attrib['name'] for g in existing_parents]

            unique_parent_name = parent_name
            i = 0
            while (unique_parent_name in existing_parent_names):
                unique_parent_name = '%s %d' % (parent_name, i)
                i += 1

            parent = Element (parent_tag)
            parent.attrib['name'] = unique_parent_name
            for orphan in orphans:
                parent_map[orphan].remove (orphan)
                parent.append (orphan)
        else:
            parent = None

        return parent

    @staticmethod
    def find_all_parents (root, child_tag, attrs={}):
        parents = set ()

        parent_map = dict((c, p) for p in root.getiterator() for c in p)
        children = findall (root, child_tag, attrs=attrs)
        for child in children:
            parent = parent_map[child]
            parents.add (parent)
            try:
                parent_map[parent].remove (parent)
            except (KeyError, ValueError):
                pass
        return list (parents)

    @staticmethod
    def group_file_params (roots):
        # Look for file tags and put them into a single group.
        #files_groups = []

        parent = Element ('group')
        parent.attrib['name'] = 'Input Files'

        for root in roots:
            parent_map = dict((c, p) for p in root.getiterator() for c in p)

            files = findall (root, 'file')
            if len (files) > 0:
                parent.extend (files)

            # NOTE: Remove children after iteration. Not doing this can cause odd behavior
            for file in files:
                orphans = []
                for child in iter (file):
                    if child.tag not in ['brief', 'description', 'default']:
                        orphans.append (child)

                for orphan in orphans:
                    file.remove (orphan)
                parent_map[file].extend (orphans)

        if len (list (parent)) > 0:
            return [parent]
        else:
            return []

    @staticmethod
    def group_output_params (root):
        output_groups = []

        orphans = CmtScanner.find_orphans (root, 'param', 'group', dict (arg='out'))
        if len (orphans) > 0:
            new_parent = CmtScanner.adopt_orphans (root, orphans, 'group', 'Output')
            output_groups.append (new_parent)

        output_groups.extend (CmtScanner.find_all_parents (root, 'param', dict (arg='out')))

        return output_groups
    @staticmethod
    def set_namespace (root, tag, ns, attrs={}):
        for node in findall (root, tag, attrs):
            node.attrib['name'] = os.path.join (ns, node.attrib['name'])

    @staticmethod
    def translate_files_group (root, md):
        ns = '/%s/Input/Var/%s/' % (md['model_short_name'], root.attrib['name'])

        CmtScanner.translate (root)

        entries = findall (root, 'entry')

        for entry in entries:
            default = entry.find ('default')
            #if not default:
            if default is None:
                default = Element ('default')
                default.text = '${SimulationName}'
                entry.append (default)
            default_file = default.text
            default.text = 'GUI'

            help = entry.find ('help_brief')
            help.text += '{' + ';'.join (['cb', 'GUI', 'Path to file']) + '}'

            replace = Element ('replace')
            replace.attrib['string'] = 'GUI'
            replace.text = '<![CDATA[<html>&#36;%s</html>]]>' % default_file
            entry.append (replace)

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
        files_groups = self.group_file_params (root.findall ('model'))
        for node in files_groups:
            self.translate_files_group (node, md)

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
        dialog.extend (pre + files_groups + tabs + output_groups + post)

        self.parent[0] = dialog

        return super (CmtScanner, self).to_xml ()

