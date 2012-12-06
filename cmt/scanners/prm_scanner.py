#! /usr/bin/env python

import os
import sys
from xml.etree.ElementTree import Element, tostring

from plex import *

class Error (Exception):
    pass
class BadKeyError (Error):
    def __init__ (self, key):
        self._key = key
    def __str__ (self):
        return self._key
class MissingKeyError (Error):
    def __init__ (self, key):
        self._key = key
    def __str__ (self):
        return self._key

class MatchError (Error):
    pass

def _findall (parent, tag, attrs={}):
    nodes = parent.findall (tag)
    matches = []
    for node in nodes:
        try:
            for (k, v) in attrs.items ():
                if node.attrib[k] != v:
                    raise MatchError
        except (KeyError, MatchError):
            pass
        else:
            matches.append (node)

    for child in parent:
        matches.extend (_findall (child, tag, attrs))

    return matches

def findall (parent, tag, attrs={}):
    # Find all nodes that have a given tag and set of attributes.

    matches = _findall (parent, tag, attrs=attrs)
    if parent.tag == tag:
        try:
            for (k, v) in attrs.items ():
                if parent.attrib[k] != v:
                    raise MatchError
        except (KeyError, MatchError):
            pass
        else:
            matches.insert (0, parent)
    assert (len (matches) == len (set (matches)))

    return matches

def find_with_attrib (parent, tag, attribs = {}):
    # Find the first child of a parent that has a given tag and
    # a given set of attributes. Returns an element instance or
    # None.

    for match in parent.findall (tag):
        if node_has_attributes (match, attribs):
            return match

    return None

def node_has_attributes (node, attribs, exclusive=False):
    # Does a node's attributes match those of a given dictionary? If 
    # the exclusive keyword is True, the node's attributes must be
    # limited to those of the given attriutes.
    if exclusive and set (node.attrib.keys ()) != set (attribs.keys ()):
        return False

    try:
        for (k, v) in attribs.items ():
            if node.attrib[k] != v:
                raise MatchError
    except (KeyError, MatchError):
        pass
    else:
        return True

    return False

valid_parents = set ([
    'root', 'param', 'file', 'group', 'model', 'document'
])
valid_keys = (
    set (['units', 'range', 'type', 'description', 'help',
          'brief', 'template', 'default', 'author', 'version',
          'date', 'warning', 'email', 'url', 'longname',
          'outparam']) |
    valid_parents
)
commands_with_args = (
    set (['param'])
)

letter = Range ('AZaz')
digit = Range ('09')
name = letter + Rep (letter | digit | Str ('_'))
number = Rep1 (digit)
space = Any (" \t\n")

spaces = Rep1 (Any (' \t'))
indentation = Rep (Str (" ")) | Rep (Str ("\t"))
lineterm = Str ("\n") | Eof
escaped_newline = Str ("\\\n")
comment = Str ('#') + Rep (AnyBut ('\n'))

#blank_line = indentation + Opt (comment) + Alt (lineterm, Eof)
blank_line = Rep (Any (' \t')) + lineterm

punct1 = Any (":,;+-*/|&<>=.%`~^${}")
punct2 = Str ("==", "<>", "!=", "<=", "<<", ">>", "**")
punctuation = punct1 | punct2

sq_string = (
    Str("'") + 
    Rep(AnyBut("\\\n'") | (Str("\\") + AnyChar)) + 
    Str("'"))

dq_string = (
    Str('"') +
    Rep(AnyBut('\\\n"') | (Str("\\") + AnyChar)) +
    Str('"'))

non_dq = AnyBut('"') | (Str('\\') + AnyChar)
tq_string = (
    Str('"""') +
    Rep(
        non_dq |
        (Str('"') + non_dq) |
        (Str('""') + non_dq)) + Str('"""'))
                  
stringlit = sq_string | dq_string | tq_string

command_start = Bol + Str ('#')
key = Str ('@') + name
command_arg = Str ('[') + name + Str (']')
command_text = Rep (AnyBut ('\n')) + lineterm
command = key + Opt (command_arg) + Rep (AnyBut ('\n')) + lineterm
multiline = (Str ('@description') | Str ('@help') | Str ('@brief') | Str ('@template')) + Rep (AnyBut ('\n'))

verbatim = (Str ('@verbatim') +
            Rep(AnyBut('\\\n"') | (Str("\\") + AnyChar)) +
            Rep (indentation) + command)

not_annotation = Rep1 (AnyBut ('#\n'))
annotation = Bol + Str ('#')

def _adopt_children (parent, foster_parent):
    adopted = []
    for child in foster_parent:
        match = parent_has_child (parent, child)
        if match is None:
            adopted.append ((child, foster_parent, parent))
        else:
            adopted.extend (_adopt_children (match, child))
    #parent.extend (adopted)

    return adopted

def adopt_children (parent, foster_parent):
    # Add children as elements of parent. If a parent element matches
    # one contained in children, that element will adopt the children
    # of the child element.
    if not isinstance (foster_parent, Element):
        raise TypeError ('A single Element must be given as a foster parent.')

    adopted = _adopt_children (parent, foster_parent)

    if len (adopted) > 0:
        for (o, p, np) in adopted:
            p.remove (o)

        for (o, p, np) in adopted:
            np.append (o)

def compare_nodes (node1, node2, keys=[]):
    if node1.tag == node2.tag:
        for key in keys:
            try:
                if node1.attrib[key] != node2.attrib[key]:
                    return False
            except KeyError:
                return False
    else:
        return False
    return True

def parent_has_child (parent, child):
    for my_child in iter (parent):
        if compare_nodes (my_child, child, keys=['name']):
            return my_child
    return None

class InputParameterScanner (object, Scanner):
    def __init__ (self, file):
        Scanner.__init__ (self, self.lexicon, file)
        self.indentation_stack = [0]
        self.begin ('')
        self.parent = [Element ('document')]
        self._last_element = self.parent[0]
        self._current_command = None
        self._current_args = []
        self._contents = []

    def __getitem__ (self, key):
        params = findall (self.root (), 'param', attrs=dict (name=key))
        if len (params) == 0:
            raise KeyError (key)
        assert (len (params) == 1)
        param = params[0]
        try:
            return param.find ('default').text
        except ValueError:
            return None

    def update (self, that):
        self.root ().extend (list (that.root ()))

    def find (self, tag):
        tags = findall (self.root (), tag)
        return [t.attrib['name'] for t in tags]

    def get_text (self, tag, attrib, default=None):
        tags = findall (self.root (), tag)
        try:
            return tags[0].find (attrib).text
        except IndexError:
            return default

    def as_dict (self):
        d = {}
        params = findall (self.root (), 'param')
        for param in params:
            if not param.attrib.has_key ('arg') or param.attrib['arg'] == 'in':
                try:
                    d[param.attrib['name']] = param.find ('default').text
                except AttributeError:
                    raise MissingKeyError (param.attrib['name'])
        return d

    def contents (self):
        #return os.linesep.join (self._contents)
        return ''.join (self._contents)

    def fill_contents (self):
        from string import Template
        try:
            return Template (self.contents ()).substitute (self.as_dict ())
        except KeyError as e:
            raise MissingKeyError (str (e))

    def current_level (self):
        return self.indentation_stack[-1]

    def newline_action (self, text):
        #self._contents.append (os.linesep)
        self._contents.append (text)
        return 'newline'

    def indentation_action (self, text):
        current_level = self.current_level ()
        new_level = len (text)
        if new_level > current_level:
            self.indent_to (new_level)
        elif new_level < current_level:
            self.dedent_to (new_level)
        self.begin ('annotation')

    def indent_to (self, new_level):
        self.indentation_stack.append (new_level)
        self.new_parent ()
        assert (len (self.indentation_stack) == len (self.parent))
        self.produce ('INDENT', '')

    def dedent_to (self, new_level):
        while new_level < self.current_level ():
            self.indentation_stack.pop ()
            self.parent.pop ()
            assert (len (self.indentation_stack) == len (self.parent))
            self.produce ('DEDENT', '')

    def eof (self):
        self.dedent_to (0)

    def current_parent (self):
        return self.parent[-1]
    def last_element (self):
        return self._last_element
    def last_element_name (self):
        return self._last_element.tag
    def new_parent (self):
        if self.last_element_name () in valid_parents:
            self.parent.append (self.last_element ())
        else:
            raise SyntaxError ('%s cannot have children' % self.last_element_name ())
    def have_child (self, child):
        self.current_parent ().append (child)
    def root (self):
        return self.parent[0]
    def to_xml (self):
        from xml.etree.ElementTree import tostring
        from xml.dom.minidom import parseString

        doc = parseString (tostring (self.root ()))
        return doc.toprettyxml ()

    def verbatim_action (self, text):
        pass

    def begin_multiline (self, text):
        try:
            (cmd, args) = text.split (None, 1)
        except ValueError:
            cmd = text
            args = ''
        cmd = cmd[1:]
        self.begin ('multiline')
        self._desc = (cmd, [args])

    def in_multiline (self, text):
        self._desc[1].append (text)
        return text

    def end_multiline (self, text):
        cmd = self._desc[0]
        desc = ''.join (self._desc[1])

        self.produce (cmd.upper (), desc)
        del self._desc

        self.begin ('')

        element = self.construct_element (cmd, desc)

        self.have_child (element)
        self._last_element = element

        indent = text.find ('@')
        if indent >= 0:
            self.indentation_action (text[:indent])
            self.command_action (text[indent:])
    def begin_annotation (self, text):
        self.begin ('annotation')

    def command_action (self, text):
        if not text.startswith ('@'):
            raise ParseError (text)

        cmd = text[1:]
        if cmd not in valid_keys:
            raise BadKeyError (cmd)

        self._current_command = cmd
        self.produce ('COMMAND', cmd)
        self.begin ('annotation_arg')

    def command_args_action (self, text):
        if not (text.startswith ('[') and text.endswith (']')):
            raise ParseError (text)

        args = text[1:-1].split (',')
        if self._current_command not in commands_with_args:
            raise BadKeyError (self._current_command)

        self._current_args = args
        self.produce ('COMMAND_ARG', ','.join (args))

    def no_arg_action (self, text):
        self.begin ('annotation_text')

    def command_text_action (self, text):
        element = self.construct_element (self._current_command, self._current_args, text)
        self.produce ('COMMAND_TEXT', text)
        self.begin ('')
        self.have_child (element)
        self._last_element = element

        self._current_command = None
        self._current_args = []


    def scan_file (self):
        while 1:
            token, text = self.read ()
            if token is None:
                break

    @staticmethod
    def construct_element (cmd, args, text):
        element = Element (cmd)
        if cmd in ['param', 'file']:
            try:
                (text, default) = text.split ('=')
                e = Element ('default')
                e.text = default.strip ()
                element.append (e)
            except ValueError:
                pass

        if len (args) > 0:
            element.attrib['arg'] = ','.join (args)

        if cmd in valid_parents:
            element.attrib['name'] = text.strip ()
        else:
            element.text = text.strip ()
        return element

    def not_annotation_action (self, text):
        self._contents.append (text)
        self.begin ('')

    def blank_annotation_action (self, text):
        self.begin ('')

    lexicon = Lexicon ([
        (annotation, begin_annotation),
        (not_annotation, not_annotation_action),
        (lineterm, newline_action),
        (blank_line, newline_action),

        State ('annotation', [
            (indentation, indentation_action),
            (key, command_action),
            (blank_line, blank_annotation_action),
        ]),

        State ('annotation_arg', [
            (command_arg, command_args_action),
            (space, no_arg_action),
        ]),

        State ('annotation_text', [
            (command_text, command_text_action),
        ]),
    ])

