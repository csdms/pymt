"""
>>> import StringIO

>>> contents = \"\"\"
... [inputdir]
... tab: Files and Directories
... var_name: InputDir
... help_msg: Read input from this directory
... label: Input directory
... default: /data/sims/sedflux/Adriatic
... type: String
... 
... [stoptime]
... tab: Parameters
... var_name: StopTime
... help_msg: Simulation stop time (years)
... label: Stop time
... default: 100
... type: Double
... range: 0,1000
...
... [timestep]
... tab: Parameters
... var_name: TimeStep
... help_msg: Simulation time step (seconds)
... label: Time step
... default: 1
... type: Double
... range: .1, 10
... \"\"\"

=== Scan a CMT ini file ===

>>> file = StringIO.StringIO (contents)

>>> import ini_file
>>> p = ini_file.ini_file ()
>>> p.readfp (file)

>>> sections = p.sections ()
>>> sections.sort ()
>>> sections
['inputdir', 'stoptime', 'timestep']

>>> options = p.options ('inputdir')
>>> options.sort ()
>>> options
['default', 'help_msg', 'label', 'tab', 'type', 'var_name']

>>> values = p.get_option_values ('tab')
>>> values.sort ()
>>> values
['Files and Directories', 'Parameters']

=== Find sections with an option ===

>>> file = StringIO.StringIO (contents)

>>> import ini_file
>>> p = ini_file.ini_file ()
>>> p.readfp (file)
>>> sections = p.sections_with_option ('tab', 'Parameters')
>>> sections.sort ()
>>> sections
['stoptime', 'timestep']

=== The CMT ini file is missing an option ===

>>> contents = \"\"\"
... [stoptime]
... tab: Parameters
... help_msg: Simulation stop time (years)
... label: Stop time
... default: 100
... range: 0,1000
... \"\"\"
>>> file = StringIO.StringIO (contents)
>>> p = ini_file.ini_file ()
>>> p.readfp (file) #doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
RequiredOptsError: stoptime: Section missing required option: type, var_name
>>> options = p.missing_opts ('stoptime')
>>> options.sort ()
>>> options
['type', 'var_name']

=== The CMT ini file contains an unknown option ===

>>> contents = \"\"\"
... [stoptime]
... tab: Parameters
... var_name: StopTime
... help_msg: Simulation stop time (years)
... label: Stop time
... default: 100
... type: Double
... gobbledy: gook
... range: 0,1000
... \"\"\"
>>> file = StringIO.StringIO (contents)
>>> p = ini_file.ini_file ()
>>> p.readfp (file) #doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
UnknownOptsError: stoptime: Section has unknown option: gobbledy
"""

import ConfigParser

required_opts = ['tab', 'var_name', 'help_msg', 'label', 'default', 'type']
optional_opts = ['range']

from types import StringTypes
class Error (Exception):
  def __init__ (self, section, options):
    self._section = section
    self._options = self._make_option_string (options)
  def _make_option_string (self, options):
    self._options = []
    if type (options) is StringTypes:
      option_str = options
    else:
      options = []
      for opt in options:
        options.append (opt)
      options.sort ()
      option_str = ', '.join (options)
    return option_str

class RequiredOptsError (Error):
  def __str__ (self):
    return '%s: Section missing required option: %s' % (self._section,
                                                        self._options)

class UnknownOptsError (Error):
  def __str__ (self):
    return '%s: Section has unknown option: %s' % (self._section,
                                                   self._options)

class ini_file ():

  def __init__ (self):
    self._file = ConfigParser.RawConfigParser ()

  def read (self, file):
    try:
      fp = open (file)
    except IOError:
      raise
    self.readfp (fp)

  def readfp (self, fp):
    self._file.readfp (fp)
    for section in self.sections ():

      missing = self.missing_opts (section)
      if len (missing)>0:
        raise RequiredOptsError (section, missing)

      unknown = self.unknown_opts (section)
      if len (unknown)>0:
        raise UnknownOptsError (section, unknown)

  def sections (self):
    return self._file.sections ()
  def options (self, section):
    return self._file.options (section)
  def get (self, section, option):
    return self._file.get (section, option)
  def get_option_values (self, option):
    values = set ()
    for section in self.sections ():
      if self._file.has_option (section, option):
        values.add (self.get (section, option))
    return [val for val in values]

  def sections_with_option (self, option, value):
    sections = []
    for section in self.sections ():
      if value == self.get (section, option):
        sections.append (section)
    return sections

  def missing_opts (self, section):
    opts = set (required_opts) - set (self.options (section))
    return [opt for opt in opts]
  def unknown_opts (self, section):
    opts = set (self.options (section)) - set (required_opts+optional_opts)
    return [opt for opt in opts]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
 
