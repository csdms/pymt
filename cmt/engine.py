
class IEngine (object):
  def go (self):
    pass
  def run (self):
    pass
  def initialize (self):
    pass
  def finalize (self):
    pass

class Engine (object):
  def __init__ (self):
    self.log = None
    self.initialized = False

  def initialize (self):
    if not self.initialized:
      ports = get_active_ports ()

      create_port_queue (ports)
    else:
      self.log (1, "Already initialized")
      return

