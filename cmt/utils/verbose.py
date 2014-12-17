from __future__ import print_function

import os
import sys
import logging


_LEVEL_STRING = {'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40}
_CMT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def log_level_string_to_int(level):
    if level.upper() in ['TRUE', 'YES', 'ON', 'ENABLED']:
        verbosity = sys.maxint
    elif level.upper() in ['FALSE', 'NO', 'OFF', 'DISABLED']:
        verbosity = 0 
    else:
        try:
            verbosity = _LEVEL_STRING[level]
        except KeyError:
            raise ValueError(level)

    return verbosity


def get_log_level_from_environ(level):
    try:
        level = int(os.environ['CMT_VERBOSE'])
    except KeyError:
        pass
    except ValueError:
        level = log_level_string_to_int(level)

    return level


def setup_cmt_logging_channel():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(_CMT_LOG_FORMAT)
    ch.setFormatter(formatter)
    return ch


class CmtLogger(logging.Logger):
    def __init__(self, name, level):
        level = get_log_level_from_environ(level)

        logging.Logger.__init__(self, name, level=level)
        ch = setup_cmt_logging_channel()
        self.addHandler(ch)


class Verbose(object):
    def __init__ (self, verbosity=0, log=sys.stderr):
        self._verbosity = verbosity
        self._log = log

    def __call__ (self, verbosity, msg):
        if verbosity <= self._verbosity:
            print(self._construct_msg(verbosity, msg), file=self._log)

    def _construct_msg(self, verbosity, msg):
        if verbosity == 0:
            return msg
        else:
            return '*' * verbosity + ' ' + msg


class CmtVerbose(Verbose):
    """
    >>> if 'CMT_VERBOSE' in os.environ: del os.environ['CMT_VERBOSE']
    >>> verbose = CmtVerbose (1, log=sys.stdout)
    >>> verbose (1, "Level one")
    #CMT Level one
    >>> verbose (2, "Level two")
    >>> verbose (0, "Level %d" % 0)
    #CMT Level 0

    >>> os.environ['CMT_VERBOSE'] = '3'
    >>> verbose = CmtVerbose (log=sys.stdout)
    >>> verbose (1, "Level one")
    #CMT Level one
    >>> verbose (2, "Level two")
    #CMT Level two
    >>> verbose (4, "Level %d" % 0)

    >>> os.environ['CMT_VERBOSE'] = 'False'
    >>> verbose = CmtVerbose (log=sys.stdout)
    >>> verbose (0, 'No message')
    #CMT No message
    >>> verbose (1, 'No message')

    >>> os.environ['CMT_VERBOSE'] = 'True'
    >>> verbose = CmtVerbose (log=sys.stdout)
    >>> verbose (1, 'No message')
    #CMT No message
    >>> verbose (0, 'No message')
    #CMT No message
    """
    def __init__(self, verbosity=1, log=sys.stderr):
        if 'CMT_VERBOSE' in os.environ:
            level = os.environ['CMT_VERBOSE']
            if level.upper() in ['TRUE', 'YES', 'ON', 'ENABLED']:
                verbosity = sys.maxint
            elif level.upper() in ['FALSE', 'NO', 'OFF', 'DISABLED']:
                verbosity = 0 
            else:
                try:
                    verbosity = int(level)
                except ValueError:
                    verbosity = 0

        Verbose.__init__(self, verbosity, log)

    def _construct_msg(self, verbosity, msg):
        return '#CMT ' + msg.strip ()
