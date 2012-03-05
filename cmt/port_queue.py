class IRFPort (object):
  def initialize (self, properties):
    pass
  def run (self, time):
    pass
  def finalize (self):
    pass
  def get_time_span (self):
    return (0, 1e12)

class Server (object):
  def __init__ (self, name):
    self.active = True
    self.name = name
    self.map_to_value = None
    self.map_from_value = None
    self.map_method = None
  def initialize (self, properties):
    print '%s: Initializing' % self.name
  def run (self, time):
    print '%s: Running' % self.name
  def finalize (self):
    print '%s: Finalizing' % self.name
  def get_name (self):
    return self.name

class Services (object):
  def getPort (self, name):
    pass
  def releasePort (self, name):
    pass

class PortQueue (object):
  """
  >>> q = PortQueue (Server ('sedflux'))

  >>> q.configure (['sedflux.ini', 'child.ini'])

  >>> q.initialize ('propery=value')
  Elevation: Initializing
  WaterDepth: Initializing

  >>> q.run (10.)
  WaterDepth: Running
  Elevation: Running

  >>> q.map_values ()
  depth_port: Depth -> Depth
  elevation_port: Elevation -> z

  >>> q.finalize ()
  Elevation: Finalizing
  WaterDepth: Finalizing

  """
  def __init__ (self, client):
    self._queue = []
    self._names = set ()

    self._name = client.name ()

    self._init_queue = []
    self._run_queue = []
    self._finalize_queue = []

    self._services = None
    self._client = client
    self._servers = {}

    self._ports = {}
    self._mappers = {}
    self._names = set ()

  def set_services (self, services):
    if self._services is None:
      self._services = services
    else:
      print 'Error: services has already been set.'

  def add_port (self, server):
    self._servers[server] = None

  def add_ports (self, servers):
      for server in servers.split (','):
          self.add_port (server.strip ())

  def initialize (self, properties):
    for name in self._init_queue:
      self._servers[name].initialize (properties)

  def run (self, time):
    for name in self._run_queue:
      self._servers[name].run (time)

  def finalize (self):
    for name in self._finalize_queue:
      self._servers[name].finalize ()

  def check_time_spans(self, start, end):
    bad_ports = []
    for (name, port) in self._ports.items ():
      span = port.get_time_span ()
      if span[1]<end:
        bad_ports.append (name)
    return len (bad_ports)==0

  def read_conf (self, files):
    import configparser
    p = configparser.ConfigParser ()
    p.read (files)

    # Look for section <component_name>.ports
    if p.has_subsection ([self._name, 'ports']):
      section = p.section_name ([self._name, 'ports'])

      names = p.get (section, 'names').split (':')
      self._init_queue = p.get (section, 'init_order').split (':')
      self._run_queue = p.get (section, 'run_order').split (':')
      self._finalize_queue = p.get (section, 'finalize_order').split (':')
    else:
      names = []

    # Look for port sections, <component_name>.<port_name>
    for name in names:
      section = p.section_name ([self._name, name])

      port = Server (p.get (section, 'name'))
      port.map_to_name = p.get (section, 'map_to_name')
      port.map_from_name = p.get (section, 'map_from_name')
      port.map_method = p.get (section, 'map_method')

      self._servers[name] = port

  def read_user (self, dict):
    base = namespace.join (self._name, 'Port')
    d = namespace.extract_base (dict, base)
    for key in d.keys ():
      if namespace.len (key)==1:
        if d[key].upper in ['YES', 'ON', 'TRUE']:
          self._servers[key].active = True
        else:
          self._servers[key].active = False

  def connect_ports (self):
    pass

  def disconnect (self):
    pass

  def get_port (self, name):
    pass
  def initialize_mapper (self, name, element_set):
    pass
  def map_value (self, dst_value, src_value):
    pass
  def map_values (self):
    for (name, port) in self._servers.items ():
      print '%s: %s -> %s' % (name, port.map_to_name, port.map_from_name)
  def get_mapped_value (self, name, value):
    pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()
 
