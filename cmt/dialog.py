"""
>>> contents = \"\"\"
... <dialog>
...   <tab name="Parameters">
...     <entry name="StopTime">
...       <label><![CDATA[Stop <b>time</b> &deg;]]></label>
...       <help_brief>Simulation stop time (in years)</help_brief>
...       <default>100</default>
...       <range>
...         <min>1</min>
...         <max>10000</max>
...       </range>
...       <type>Float</type>
...     </entry>
...     <entry name="TimeStep">
...       <label>Time step</label>
...       <help_brief>Simulation time step (in years)</help_brief>
...       <default>1</default>
...       <range>
...         <min>.01</min>
...         <max>10</max>
...       </range>
...       <type>Float</type>
...     </entry>
...     <entry name="NNodes">
...       <label>Number of nodes</label>
...       <help_brief>Number of computational nodes</help_brief>
...       <default>101</default>
...       <range>
...         <min>3</min>
...         <max>100000</max>
...       </range>
...       <type>Int</type>
...     </entry>
...   </tab>
...   <tab name="Files and Directories">
...     <entry name="InputDir">
...       <label>Input directory</label>
...       <help_brief>Directory containing input files</help_brief>
...       <default>/data/sims/sedflux/Adriatic</default>
...       <type>String</type>
...     </entry>
...     <entry name="OutputDir">
...       <label>Output directory</label>
...       <help_brief>Directory containing output files</help_brief>
...       <default>${cwd}</default>
...       <type>String</type>
...     </entry>
...   </tab>
... </dialog>
... \"\"\"

>>> import StringIO
>>> file = StringIO.StringIO (contents)

>>> dialog = ConfigDialog ()
>>> dialog.read (file)

>>> dialog.tab_names ()
[u'Parameters', u'Files and Directories']

>>> dialog.entry_names ('Parameters')
[u'StopTime', u'TimeStep', u'NNodes']
>>> dialog.entry_names ('Files and Directories')
[u'InputDir', u'OutputDir']

>>> dialog.label ('Parameters', 'StopTime')
u'Stop <b>time</b> &deg;'
>>> dialog.help ('Parameters', 'StopTime')
u'Simulation stop time (in years)'
>>> dialog.type ('Parameters', 'StopTime')
<type 'float'>
>>> dialog.default ('Parameters', 'StopTime')
100.0
>>> dialog.range ('Parameters', 'StopTime')
[1.0, 10000.0]

>>> dialog.type ('Parameters', 'NNodes')
<type 'int'>
>>> dialog.default ('Parameters', 'NNodes')
101
>>> dialog.range ('Parameters', 'NNodes')
[3, 100000]
>>> dialog.label ('Parameters', 'NNodes')
u'Number of nodes'
>>> dialog.help ('Parameters', 'NNodes')
u'Number of computational nodes'

=== Get an entry as a dictionary ===

>>> entry = dialog.get_entry ('Parameters', 'NNodes').items ()
>>> entry.sort ()
>>> entry #doctest: +NORMALIZE_WHITESPACE
[('default', 101),
 ('help', u'Number of computational nodes'),
 ('label', u'Number of nodes'),
 ('name', u'NNodes'),
 ('range', [3, 100000]),
 ('type', <type 'int'>)]

>>> entry = dialog.get_entry ('Parameters', 'NNodes')
>>> entry['type'] == types.IntType
True

=== Get a tab as a list of entry dictionaries ===

>>> tab = dialog.get_tab ('Files and Directories')
>>> for entry in tab: #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
...   t = entry.items ()
...   t.sort ()
...   t
[('default', u'/data/sims/sedflux/Adriatic'),
 ('help', u'Directory containing input files'),
 ('label', u'Input directory'),
 ('name', u'InputDir'),
 ('range', None),
 ('type', (<type 'str'>, <type 'unicode'>))]
[('default', ...),
 ('help', u'Directory containing output files'),
 ('label', u'Output directory'),
 ('name', u'OutputDir'),
 ('range', None),
 ('type', (<type 'str'>, <type 'unicode'>))]

>>> import os
>>> entry = dialog.get_entry ('Files and Directories', 'OutputDir')
>>> entry['default'] == os.getcwd ()
True

>>> [tab.name () for tab in dialog]
[u'Parameters', u'Files and Directories']

=== Define an OutputFile entry ===

>>> contents = \"\"\"
... <dialog>
...   <tab name="Output Files">
...     <entry name="Depth" class="OutputFile"/>
...     <entry name="Slope" class="OutputFile"/>
...   </tab>
... </dialog>
... \"\"\"

>>> import StringIO
>>> file = StringIO.StringIO (contents)

>>> dialog = ConfigDialog ()
>>> dialog.read (file)
>>> dialog.entry_names ('Output Files')
[u'Depth', u'Slope']
>>> dialog.entry_type ('Output Files', 'Depth')
u'OutputFile'
>>> tab = dialog.get_tab ('Output Files')
>>> for entry in tab: #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
...   t = entry.items ()
...   t.sort ()
...   t
[('default', u'OFF'),
 ('help', u'Output file prefix for variable, Depth {cb;OFF;<site>_<case>_Depth}'),
 ('label', u'Depth file'),
 ('name', u'Depth'),
 ('range', None),
 ('type', (<type 'str'>, <type 'unicode'>))]
[('default', u'OFF'),
 ('help', u'Output file prefix for variable, Slope {cb;OFF;<site>_<case>_Slope}'),
 ('label', u'Slope file'),
 ('name', u'Slope'),
 ('range', None),
 ('type', (<type 'str'>, <type 'unicode'>))]

#>>> dialog = ConfigDialog ()
#>>> dialog.read ('/data1/progs/cca/project/csdms_eric/data/Child.xml')
#>>> dialog.entry_names ('Output Grids')

=== Type names are case insensitive ===

>>> contents = \"\"\"
... <dialog>
...   <tab name="Parameters">
...     <entry name="StopTime">
...       <label><![CDATA[Stop <b>time</b> &deg;]]></label>
...       <help_brief>Simulation stop time (in years)</help_brief>
...       <default>100</default>
...       <range>
...         <min>1</min>
...         <max>10000</max>
...       </range>
...       <type>fLoAt</type>
...     </entry>
...   </tab>
... </dialog>
... \"\"\"

>>> import StringIO
>>> file = StringIO.StringIO (contents)

>>> dialog = ConfigDialog ()
>>> dialog.read (file)

>>> dialog.type ('Parameters', 'StopTime')
<type 'float'>

=== Double is synonymous with Float ===

In addition, 'int', 'integer', and 'long' are synonyms for one
another.

>>> contents = \"\"\"
... <dialog>
...   <tab name="Parameters">
...     <entry name="StopTime">
...       <label><![CDATA[Stop <b>time</b> &deg;]]></label>
...       <help_brief>Simulation stop time (in years)</help_brief>
...       <default>100</default>
...       <range>
...         <min>1</min>
...         <max>10000</max>
...       </range>
...       <type>Double</type>
...     </entry>
...     <entry name="NNodes">
...       <label>Number of nodes</label>
...       <help_brief>Number of computational nodes</help_brief>
...       <default>101</default>
...       <range>
...         <min>3</min>
...         <max>100000</max>
...       </range>
...       <type>long</type>
...     </entry>
...   </tab>
... </dialog>
... \"\"\"

>>> import StringIO
>>> file = StringIO.StringIO (contents)

>>> dialog = ConfigDialog ()
>>> dialog.read (file)

>>> dialog.type ('Parameters', 'StopTime')
<type 'float'>
>>> dialog.type ('Parameters', 'NNodes')
<type 'int'>

"""

import os
import types
import commands

import xml.dom.minidom

import namespace as ns

def sanity ():
  """
  Import sanity.

  >>> from dialog import Error
  >>> from dialog import BadFileError
  >>> from dialog import ParseError

  >>> from dialog import ConfigEntry
  >>> from dialog import ConfigEntryOutputFile
  >>> from dialog import ConfigEntryComboBox
  >>> from dialog import ConfigEntryDropDownList
  >>> from dialog import ConfigEntryFileBrowser
  >>> from dialog import ConfigTab
  >>> from dialog import ConfigDialog

  """

def check_method (method):
  if not hasattr (method, '__call__'):
    print method, ' not callable'

def interface ():
  """
  Test Entry interface

  >>> from dialog import ConfigEntry

  Make sure standard methods exist

  >>> entry = ConfigEntry ('Label', 'Float')
  >>> check_method (entry.set_label)
  >>> check_method (entry.set_help)
  >>> check_method (entry.set_range)
  >>> check_method (entry.set_default)
  >>> check_method (entry.items)
  """

class Error (Exception):
  """Base class for exceptions in this module"""
  pass

class BadFileError (Error):
  """Exception raised for error in input files"""
  def __init__ (self, file, msg):
    self.file = file
    self.msg = msg
  def __str__ (self):
    return self.msg

class ParseError (Error):
  """Exception raised if an input file has trouble parsing"""
  def __init__ (self, file, msg):
    self.file = file
    self.msg = msg
  def __str__ (self):
    return self.msg

class ConfigEntry (object):
  """
  >>> entry = ConfigEntry ('NNodes', 'Int')
  >>> entry['name']
  u'NNodes'
  >>> entry['type']
  <type 'int'>
  >>> entry.set_label ('Number of nodes')
  >>> entry.set_help ('Number of computational nodes')
  >>> entry.set_default (100)
  >>> entry.set_range ((1,10000))

  >>> entry['label']
  u'Number of nodes'
  >>> entry['help']
  u'Number of computational nodes'
  >>> entry['default']
  100
  >>> entry['range']
  [1, 10000]
  """
  def __init__ (self, name, type, default=None, help=None, label=None,
                      range=None):
    """Create a key/value type entry

    'name' is a string that identifies the entry.

    'type' identifies the type of the entry.  A type is either a string that
    indicates the type or type from the type module.  Valid strings are
    'Float', 'Int', and 'String'.  These corespond to FloatType, IntType,
    and StringTypes.

    'default', if given, provides a default value for the entry.

    'help', if given, provides a brief help message for the entry.

    'label', if given, is a string that 

    'range', if given, is a tuple that gives minimum and maximum values for
    the entry.  This value is only applicable for 'Int', and 'Float' entries.
    """
    attr = {}
    attr['name'] = unicode (name)
    attr['type'] = self._get_type (type)
    attr['help'] = help
    attr['label'] = label
    if default is not None:
      attr['default'] = self._get_default (default)
    else:
      attr['default'] = None
    if range is not None:
      attr['range'] = self._get_range (range)
    else:
      attr['range'] = None
    self.d = attr

  def set_label (self, label):
    self.d['label'] = unicode (label)
  def set_help (self, help):
    self.d['help'] = unicode (help)
  def set_range (self, range):
    if range is not None:
      self.d['range'] = self._get_range (range)
  def set_default (self, default):
    self.d['default'] = self._get_default (default)

  def _get_range (self, range):
    entry_type = self.d['type']
    if (isinstance (range[0], self.d['type']) and
        isinstance (range[1], self.d['type'])):
      return list (range)
    else:
      if entry_type is types.FloatType:
        return [float (val) for val in range]
      elif entry_type is types.IntType:
        return [int (val) for val in range]
      else:
        BadRangeError ()

  def _get_default (self, default):
    entry_type = self.d['type']
    if entry_type is types.FloatType:
      return float (default)
    elif entry_type is types.IntType:
      return int (default)
    else:
      return unicode (default)
  def _get_type (self, type):
    if isinstance (type, types.StringTypes):
      if type.lower () in ['float', 'double']:
        return types.FloatType
      elif type.lower () in ['int', 'integer', 'long']:
        return types.IntType
      elif type.lower () == 'string':
        return types.StringTypes
      else:
        raise InvalidEntryType (type)
    elif isinstance (type, types.TypeType) or type == types.StringTypes:
      return type

  def items (self):
    return self.d.items ()
  def __getitem__ (self, name):
    return self.d[name]

class ConfigEntryOutputFile (ConfigEntry):
  def __init__ (self, name):
    ConfigEntry.__init__ (self, name, 'String')
    (head, tail) = ns.split (name)
    self.set_label ('%s file' % tail)
    self.set_help ('Output file prefix for variable, %s {cb;OFF;<site>_<case>_%s}' % (tail, tail))
    self.set_default ('OFF')

class ConfigEntryComboBox (ConfigEntry):
  """
  >>> entry = ConfigEntryComboBox ('Options')
  >>> entry.add_option ('Option 1')
  >>> entry.add_option ('Option 2')
  >>> entry['help']
  u'{cb;Option 1;Option 2}'
  """
  def __init__ (self, name):
    ConfigEntry.__init__ (self, name, 'String')
    self._options = []
    self.set_help ('')
  def add_option (self, name):
    self._options.append (name)
  def __getitem__ (self, name):
    value = ConfigEntry.__getitem__ (self, name)
    if name == 'help':
      return value + self._option_string ()
    else:
      return value
  def _option_string (self):
    return '{cb;' + ';'.join (self._options) + '}'

class ConfigEntryDropDownList (ConfigEntryComboBox):
  def _option_string (self):
    return '{dl;' + ';'.join (self._options) + '}'
  
class ConfigEntryFileBrowser (ConfigEntry):
  """
  >>> entry = ConfigEntryFileBrowser ('OutputDir')
  >>> entry['help']
  u'Select a path {bb}'
  """
  def __init__ (self, name):
    ConfigEntry.__init__ (self, name, 'String')
    self.set_label ('File')
    self.set_help ('Select a path')
    self.set_default (os.getcwd ())
  def __getitem__ (self, name):
    value = ConfigEntry.__getitem__ (self, name)
    if name == 'help':
      return value + ' {bb}'
    else:
      return value

  
class ConfigTab (object):
  """
  >>> tab = ConfigTab ('Parameters')
  >>> entry = ConfigEntry ('TimeStep', types.FloatType)
  >>> tab.append (entry)
  >>> entry = ConfigEntry ('StopTime', types.FloatType)
  >>> tab.append (entry)
  >>> [entry['name'] for entry in tab]
  [u'TimeStep', u'StopTime']
  """
  def __init__ (self, name):
    self._name = name
    self._entries = []
  def name (self):
    return self._name
  def append (self, entry):
    self._entries.append (entry)
  def __iter__ (self):
    for item in self._entries:
      yield item
    raise StopIteration

class ConfigDialog (object):

  def __init__ (self):
    self._dom = None
    self._namespace = ''

  def read (self, file):

    if type (file) in types.StringTypes:
      if (not os.path.isabs (file) and
          os.environ.has_key ('CMT_PROJECT_DIALOG_PATH')):
        paths = os.environ['CMT_PROJECT_DIALOG_PATH'].split (':')
        for path in paths:
          test_file = os.path.join (path, file)
          if (os.path.isfile (test_file)):
            file = test_file
            break
        #file = os.path.join (os.environ['CMT_PROJECT_DIALOG_PATH'], file)

    #print 'Reading xml file', file
    try:
      self._dom = xml.dom.minidom.parse (file)
    except IOError as err:
      raise BadFileError (file, err.strerror)
    else:
      dialog = self._dom.childNodes
      if len (dialog)>1:
        raise ParseError (file, "XML file describes more than one dialog")
      elif len (dialog)==0:
        raise ParseError (file, "XML file does not describe a dialog")
      else:
        dialog = dialog[0]
    if dialog.tagName != 'dialog':
      raise ParseError (file, "XML file does contain a dialog node")
    if dialog.attributes.has_key ('namespace'):
      self._namespace = dialog.attributes['namespace'].value

  def tab_names (self):
    tabs = []
    for tab in self._dom.getElementsByTagName ('tab'):
      tabs.append (tab.attributes['name'].value)
    return tabs

  def tab (self, name):
    for tab in self._dom.getElementsByTagName ('tab'):
      if tab.attributes['name'].value == name:
        return tab
    return None

  def entry_names (self, name):
    tab = self.tab (name)
    entries = []
    for entry in tab.getElementsByTagName ('entry'):
      entries.append (entry.attributes['name'].value)
    return entries

  def entry (self, tab_name, name):
    tab = self.tab (tab_name)
    for entry in tab.getElementsByTagName ('entry'):
      if entry.attributes['name'].value == name:
        return entry
    return None

  def entry_type (self, tab_name, name):
    tab = self.tab (tab_name)
    for entry in tab.getElementsByTagName ('entry'):
      if entry.attributes['name'].value == name:
        try:
          return entry.attributes['class'].value
        except KeyError:
          return 'Editable'
    
  def label (self, tab, entry):
    return self.data (tab, entry, 'label')
  def help (self, tab, entry):
    return self.data (tab, entry, 'help_brief')
  def default (self, tab, entry):
    type = self.type (tab, entry)
    val = self.data (tab, entry, 'default')
    if type is types.StringTypes:
      return val
    elif type is types.FloatType:
      return float (val)
    elif type is types.IntType:
      return int (val)
    else:
      raise TypeConversionError (type)
  def type (self, tab, entry):
    type = self.data (tab, entry, 'type')
    if type.lower () in ['float', 'double']:
      return types.FloatType
    elif type.lower () in ['int', 'integer', 'long']:
      return types.IntType
    elif type.lower () == 'string':
      return types.StringTypes
    else:
      raise InvalidEntryType (type)
  def range (self, tab, entry):
    type = self.type (tab, entry)
    if type is types.StringTypes:
      return None
    else:
      range = self.entry (tab, entry)
      min = range.getElementsByTagName ('min')
      max = range.getElementsByTagName ('max')
      min_max = (min[0].childNodes[0].data, max[0].childNodes[0].data)
      if type is types.FloatType:
        return [float (val) for val in min_max]
      elif type is types.IntType:
        return [int (val) for val in min_max]

  def data (self, tab_name, entry_name, data_name):
    entry = self.entry (tab_name, entry_name)
    labels = entry.getElementsByTagName (data_name)
    label = labels[0]

    try:
      str = label.attributes['value'].value
    except KeyError:
      str = label.childNodes[0].data

    data_str = self._substitute (str)
    #data_str = self._substitute (labels[0].childNodes[0].data)
    return data_str

  def _substitute (self, str):
    from string import Template
    import os
    s = Template (str)
    return s.substitute (cwd=os.getcwd ())

  def get_entry (self, tab, entry_name):
    if self.entry_type (tab, entry_name) == 'OutputFile':
      (head, tail) = ns.split (entry_name)
      #entry = ConfigEntryOutputFile (tail)
      entry = ConfigEntryOutputFile (entry_name)
    elif self.entry_type (tab, entry_name) == 'FileBrowser':
      entry = ConfigEntryFileBrowser (entry_name)
    else:
      entry = ConfigEntry (entry_name, self.type (tab, entry_name))

      entry.set_label (self.label (tab, entry_name))
      entry.set_help (self.help (tab, entry_name))
      entry.set_default (self.default (tab, entry_name))
      entry.set_range (self.range (tab, entry_name))

    return entry

  def get_tab (self, tab_name):
    tab = ConfigTab (tab_name)
    for entry in self.entry_names (tab_name):
      tab.append (self.get_entry (tab_name, entry))
    return tab

  def __iter__ (self):
    for tab in self._dom.getElementsByTagName ('tab'):
      yield self.get_tab (tab.attributes['name'].value)
    raise StopIteration

if __name__ == "__main__":
    import doctest
    doctest.testmod()


