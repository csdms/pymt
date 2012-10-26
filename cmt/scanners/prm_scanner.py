#! /usr/bin/env python

import os
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
#command = command_start + Rep (indentation) + key + Rep (AnyBut ('\n'))
key = Str ('@') + name
command_arg = Str ('[') + name + Str (']')
command_text = Rep (AnyBut ('\n')) + lineterm
command = key + Opt (command_arg) + Rep (AnyBut ('\n')) + lineterm
multiline = (Str ('@description') | Str ('@help') | Str ('@brief') | Str ('@template')) + Rep (AnyBut ('\n'))

verbatim = (Str ('@verbatim') +
            Rep(AnyBut('\\\n"') | (Str("\\") + AnyChar)) +
            Rep (indentation) + command)

#not_annotation = Bol + AnyBut ('#') + Rep (AnyBut ('\n')) + lineterm
not_annotation = Rep1 (AnyBut ('#\n'))
annotation = Bol + Str ('#')

class InputParameterScanner (object, Scanner):
    def __init__ (self, file):
        Scanner.__init__ (self, self.lexicon, file)
        self.indentation_stack = [0]
        #self.begin ('indent')
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
        return os.linesep.join (self._contents)

    def fill_contents (self):
        from string import Template
        try:
            return Template (self.contents ()).substitute (self.as_dict ())
        except KeyError as e:
            raise MissingKeyError (str (e))

    def current_level (self):
        return self.indentation_stack[-1]

    def newline_action (self, text):
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
        #print 'start annotation: %s' % text
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


    def command_action_old (self, text):
        start_of_command = text.find ('@')
        #(cmd, args) = text[start_of_command+1:].split (None, 1)
        #self.indentation_action (text[1:start_of_command])
        #print 'Indent is', start_of_command-1

        (cmd, args) = text.split (None, 1)
        cmd = cmd[1:]

        if cmd not in valid_keys:
            raise BadKeyError (cmd)

        self.begin ('')
        self.produce (cmd.upper (), ' '.join (args.split ()))

        element = self.construct_element (cmd, args)

        self.have_child (element)
        self._last_element = element

    def scan_file (self):
        while 1:
            token, text = self.read ()
            #print token, text
            if token is None:
                break

    @staticmethod
    def construct_element (cmd, args, text):
        element = Element (cmd)
        if cmd == 'param':
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
        #print 'not annotation: >%s<' % text.strip ()
        self._contents.append (text.strip ())
        self.begin ('')

    def blank_annotation_action (self, text):
        self.begin ('')

    lex = Lexicon ([
        (name, 'name'),
        (number, 'number'),
        (stringlit, 'string'),
        (punctuation, TEXT),
        (lineterm, newline_action),
        (comment, IGNORE),
        (spaces, IGNORE),
        (escaped_newline, IGNORE),
        #(verbatim, verbatim_action),
        State ('indent', [
            (blank_line, IGNORE),
            (indentation, indentation_action),
        ]),
        (multiline, begin_multiline),
        State ('multiline', [
            (Eof | Empty | (Rep (indentation) + command), end_multiline),
            (Rep1 (name | punctuation | number | indentation) + Str ('\n'), in_multiline),
        ]),
        (command, command_action),
    ])

    lexicon = Lexicon ([
        #(name, 'name'),
        #(number, 'number'),
        #(stringlit, 'string'),
        #(punctuation, TEXT),
        #(comment, IGNORE),
        #(spaces, IGNORE),
        #(escaped_newline, IGNORE),
        #(verbatim, verbatim_action),
        (annotation, begin_annotation),
        (not_annotation, not_annotation_action),
        (lineterm, newline_action),
        #State ('indent', [
        #    (blank_line, IGNORE),
        #    (indentation, indentation_action),
        #]),
        #(multiline, begin_multiline),
        #State ('multiline', [
        #    (Eof | Empty | (Rep (indentation) + command), end_multiline),
        #    (Rep1 (name | punctuation | number | indentation) + Str ('\n'), in_multiline),
        #]),
        #(command, command_action),

        State ('annotation', [
            #(name, 'name'),
            #(number, 'number'),
            #(stringlit, 'string'),
            #(punctuation, TEXT),
            #(lineterm, newline_action),
            #(comment, IGNORE),
            #(spaces, IGNORE),
            #(escaped_newline, IGNORE),
            (indentation, indentation_action),
            (key, command_action),
            #(command_arg, command_args_action),
            #(command_text, command_text_action),
            (blank_line, blank_annotation_action),
            #(not_annotation, not_annotation_action),
            #(lineterm, newline_action),
        ]),

        State ('annotation_arg', [
            (command_arg, command_args_action),
            (space, no_arg_action),
        ]),

        State ('annotation_text', [
            (command_text, command_text_action),
        ]),

        (blank_line, IGNORE),
    ])

