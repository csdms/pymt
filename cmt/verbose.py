from __future__ import print_function

import os
import sys
import logging


level_string = {'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40}

class CMTLogger (logging.Logger):
    def __init__ (self, name, level):
        try:
            level = int (os.environ['CMT_VERBOSE'])
        except KeyError:
            pass
        except ValueError:
            try:
                level = level_string[level]
            except KeyError:
                pass

        logging.Logger.__init__ (self, name, level=level)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter ('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter (formatter)
        self.addHandler (ch)

class Verbose (object):
  def __init__ (self, verbosity=0, log=sys.stderr):
    self._verbosity = verbosity
    self._log = log
  def __call__ (self, verbosity, msg):
    if verbosity <= self._verbosity:
      print (self.construct_msg (verbosity, msg), file=self._log)
  def construct_msg (self, verbosity, msg):
    if verbosity == 0:
      return msg
    else:
      return '*'*verbosity + ' ' + msg

class CMTVerbose (Verbose):
  """
  >>> verbose = CMTVerbose (1, log=sys.stdout)
  >>> verbose (1, "Level one")
  #CMT Level one
  >>> verbose (2, "Level two")
  >>> verbose (0, "Level %d" % 0)
  #CMT Level 0

  >>> os.environ['CMT_VERBOSE'] = '3'
  >>> verbose = CMTVerbose (log=sys.stdout)
  >>> verbose (1, "Level one")
  #CMT Level one
  >>> verbose (2, "Level two")
  #CMT Level two
  >>> verbose (4, "Level %d" % 0)

  >>> os.environ['CMT_VERBOSE'] = 'False'
  >>> verbose = CMTVerbose (log=sys.stdout)
  >>> verbose (0, 'No message')
  #CMT No message
  >>> verbose (1, 'No message')

  >>> os.environ['CMT_VERBOSE'] = 'True'
  >>> verbose = CMTVerbose (log=sys.stdout)
  >>> verbose (1, 'No message')
  #CMT No message
  >>> verbose (0, 'No message')
  #CMT No message

  """

  def __init__ (self, verbosity=1, log=sys.stderr):
    if os.environ.has_key ('CMT_VERBOSE'):
      level = os.environ['CMT_VERBOSE']
      if level.upper () in ['TRUE', 'YES', 'ON', 'ENABLED']:
        verbosity = sys.maxint
      elif level.upper () in ['FALSE', 'NO', 'OFF', 'DISABLED']:
        verbosity = 0 
      else:
        try:
          verbosity = int (level)
        except ValueError:
          verbosity = 0
    Verbose.__init__ (self, verbosity, log)
  def construct_msg (self, verbosity, msg):
    return '#CMT ' + msg.strip ()

    Verbose.__init__ (self, verbosity, log)

