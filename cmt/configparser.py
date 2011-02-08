import types
import ConfigParser as CP

class ConfigParser (CP.ConfigParser):
  def __init__ (self):
    defaults = {'finalize_order': '%(names)s',
                'init_order': '%(names)s',
                'run_order': '%(names)s',
                'map_to_value': '%(name)s',
                'map_from_value': '%(name)s'}
    CP.ConfigParser.__init__ (self, defaults)

  def namespaces (self):
    namespaces = set ()
    for section in self.sections ():
      i = section.find ('.')
      if i>0:
        namespaces.add (section[:i])
      else:
        namespaces.add ('.')
    return [ns for ns in namespaces]

  def subsections (self):
    return self.namespaces ()

  def subsection (self, name):
    subsections = []
    for section in self.sections ():
      if section.startswith (name):
        subsections.append (section)
    return subsections

  def has_subsection (self, sections):
    return self.has_section ('.'.join (sections))

  def section_name (self, sections):
    if type (sections) in types.StringTypes:
      return sections
    else:
      return '.'.join (sections)

