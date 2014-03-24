#! /usr/bin/env python

class FrameworkServices(object):
    def getPort(self, port_name):
        raise NotImplementedError()

    def releasePort(self, port_name):
        raise NotImplementedError()
