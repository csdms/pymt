#! /usr/bin/env python

import numpy as np

from ..ordered_task_status import OrderedTaskStatus


class FrameworkServices(object):
    def __init__(self):
        pass

    def createTypeMap(self):
        pass

    def getPort(self, name):
        pass

    def releasePort(self, name):
        pass


class ParameterPortFactory(object):
    def initParameterData(self, user_input, title):
        pass

    def setBatchTitle(self, user_input, title):
        pass

    def setGroupName(self, user_input, group):
        pass

    def addRequestDouble(self, user_input, name, help, label, default,
                        lower_limit, upper_limit):
        pass

    def addRequestInt(self, user_input, name, help, label, default,
                      lower_limit, upper_limit):
        pass

    def addRequestString(self, user_input, name, help, label, default):
        pass

    def addParameterPort(self, user_input, services):
        pass


class TimeSteppingClient(object):
    def __init__(self):
        self._time = 0.
        self._stop_time = 10.
        self._time_step = 1.

    def prepare(self):
        pass

    def run(self, stop_time):
        times = np.arange(self._time + self._time_step,
                          stop_time + self._time_step, self._time_step)

        if len(times) > 0:
            times[-1] = stop_time
        else:
            times = np.array(stop_time)

        for time in times:
            self.update()

    def update(self):
        self._time += self._time_step

    def finish(self):
        self._time = 0.

    def get_end_time(self):
        return self._stop_time

    def get_current_time(self):
        return self._time


class Error(Exception):
    pass


class StatusIncrementError(Error):
    def __init__(self, current, next):
        self._current = current
        self._next = next

    def __str__(self):
        return '%s to %s' % (self._current, self._next)


class ZeroIncrementError(StatusIncrementError):
    pass


class NegativeIncrementError(StatusIncrementError):
    pass


class ComponentHandlerBase(object):
    """
    >>> client = TimeSteppingClient()
    >>> handler = ComponentHandlerBase('time_stepper', client)
    >>> handler.go()
    >>> client.get_current_time()
    0.0

    >>> handler.initialize()
    >>> handler.run(client.get_end_time())
    >>> client.get_current_time()
    10.0
    >>> handler.finalize()
    >>> client.get_current_time()
    0.0

    """
    def __init__(self, name, client):
        self._name = name
        self._client = client
        self._env = dict(status=OrderedTaskStatus())

        self.status.start_task('create')

        super(ComponentHandlerBase, self).__init__()

        self.status.complete_task()

    @property
    def name(self):
        return self._name

    @property
    def client(self):
        return self._client

    @property
    def status(self):
        return self._env['status']

    def go(self):
        self.initialize()
        self.run(self.client.get_end_time())
        self.finalize()

    def initialize(self):
        self.status.start_task('initialize')

        self.client.prepare()

        self.status.complete_task()

    def run(self, stop_time):
        self.status.start_task('update')

        self.client.run(stop_time)

        self.status.complete_task()

    def finalize(self):
        self.status.start_task('finalize')

        self.client.finish()

        self.status.complete_task()


class ConfigurationHandlerMixIn(object):
    def __init__(self):
        self._config = dict()

        super(ConfigurationHandlerMixIn, self).__init__()

    @property
    def config(self):
        return self._config

    def read_config_file(self, filenames):
        self._config = cmt.component_info.from_config_file(filenames, self.name)

    def get_config_param(self, name):
        return self._config[name]

    def set_config_param(self, key, value):
        self._config[key] = value


class DialogHandlerMixIn(object):
    def __init__(self):
        self._dialog_file = cmt.dialog.read_from_file(
            self.get_config_param('dialog_xml_file'))

        super(DialogHandlerMixIn, self).__init__()

    @property
    def dialog_file(self):
        return self._dialog_file


class UserInputHandlerMixIn(object):
    def __init__(self):
        self._user_input = dict()
        super(UserInputHandlerMixIn, self).__init__()

    @property
    def user_input(self):
        return self._user_input

    def update(self, new_user_input):
        self._user_input.update(new_user_input)


class TemplateFilesHandlerMixIn(object):
    def __init__(self):
        self._template_files = CMTTemplateFiles()

        template_files = self.get_config_param('template_files').items()
        for (in_file, out_file) in template_files:
            self._template_files.add_files(in_file, out_file)

        super(TemplateFilesHandlerMixIn, self).__init__()

    def write_template_files(self):
        self._template_files.substitute(self._user_input,
                                        '/%s/Input/Var/' % self.name,
                                        os.getcwd(), self.dialog_file)

    def initialize(self):
        self.write_template_files()


def run_plugin_methods(plugins, method_name, *args):
    for plugin in plugins:
        try:
            method = getattr(plugin, method_name)
            method(*args)
        except (AttributeError, NotImplementedError):
            pass


#class ComponentHandler(ComponentHandlerBase, ConfigurationHandlerMixIn,
#                       DialogHandlerMixIn, UserInputHandlerMixIn):
class ComponentHandler(ComponentHandlerBase, ConfigurationHandlerMixIn):
    """
    >>> client = TimeSteppingClient()
    >>> handler = ComponentHandler('time_stepper', client)
    >>> handler.set_config_param('stop_time', 100.)
    >>> handler.get_config_param('stop_time')
    100.0
    >>> handler.go()
    >>> client.get_current_time()
    0.0

    >>> handler.initialize()
    >>> handler.run(client.get_end_time())
    >>> client.get_current_time()
    10.0
    >>> handler.finalize()
    >>> client.get_current_time()
    0.0
    """
    def __init__(self, name, client):
        ComponentHandlerBase.__init__(self, name, client)

        self._plugins = [
            StatusHandlerPlugin(),
            #PortQueueHandlerPlugin(),
            #PrintQueueHandlerPlugin()
        ]

        for plugin in self._plugins:
            setattr(plugin, '_env', self._env)

    def initialize(self):
        run_plugin_methods(self._plugins, 'pre_initialize')

        super(ComponentHandler, self).initialize()

        run_plugin_methods(self._plugins, 'post_initialize')

    def run(self, stop_time):
        run_plugin_methods(self._plugins, 'pre_run', stop_time)

        super(ComponentHandler, self).run(stop_time)

        run_plugin_methods(self._plugins, 'post_run', stop_time)

    def finalize(self):
        run_plugin_methods(self._plugins, 'pre_finalize')

        super(ComponentHandler, self).finalize()

        run_plugin_methods(self._plugins, 'post_finalize')


class HandlerPluginInterface(object):
    def initialize(self):
        raise NotImplementedError

    def run(self, stop_time):
        raise NotImplementedError

    def finalize(self):
        raise NotImplementedError


class StatusHandlerPlugin(HandlerPluginInterface):
    def __init__(self):
        pass

    def pre_initialize(self):
        print 'Status: %s' % self._env['tasks'].status

    def post_initialize(self):
        print 'Status: %s' % self._env['tasks'].status

    #def initialize(self):
    #    print 'Status: %s' % self._env['status']

    def pre_run(self, stop_time):
        print 'Status: %s' % self._env['tasks'].status
        print 'Running until %f' % stop_time

    def post_run(self, stop_time):
        print 'Status: %s' % self._env['tasks'].status
        print 'Ran until %f' % stop_time

    #def run(self, stop_time):
    #    print 'Status: %s' % self._env['status']
    #    print 'Running until %f' % stop_time

    def pre_finalize(self):
        print 'Status: %s' % self._env['tasks'].status

    def post_finalize(self):
        print 'Status: %s' % self._env['tasks'].status

    #def finalize(self):
    #    print 'Status: %s' % self._env['status']


class PortQueueHandlerPlugin(object):
    def __init__(self, handler_services):
        self._port_queue = cmt.PortQueue(self.client, self.services)
        self._port_queue_dt = self.get_config_param('PORT_QUEUE_DT')

    @property
    def port_queue(self):
        return self._port_queue

    @property
    def port_queue_dt(self):
        return self._port_queue_dt

    def initialize(self):
        port_names = self.get_config_param('PORT_NAMES')
        optional_ports = self.get_config_param('OPTIONAL_PORT_NAMES')

        self.port_queue.add_ports(port_names)
        self.port_queue.add_optional_ports(optional_ports)
        self.port_queue.connect_all_ports()

        self.port_queue.initialize_all_ports(None)

    def run(self, stop_time):
        now = self.client.get_current_time()
        times = np.arange(now + self.port_queue_dt,
                          stop_time + self.port_queue_dt, self.port_queue_dt)

        print times
        if len(times) > 0:
            times[-1] = stop_time
        else:
            times = np.array([stop_time])

        for time in times:
            self.port_queue.run_all_ports(now)
            self.port_queue.run_all_mappers()

            self.client.run(time)
            now = self.client.get_current_time()

    def finalize(self):
        self.port_queue.finalize_all_ports()


class PrintQueueHandlerPlugin(object):
    def __init__(self):
        self._print_queue = cmt.PrintQueue()

    @property
    def print_queue(self):
        return self._print_queue

    def initialize(self):
        output_ns = self.get_config_param('OUTPUT_FILE_NS')
        self.print_queue.initialize(self._user_input, '/%s/' % self.name,
                                    self.client)
        self.print_queue.add_files_from_list(output_ns)

    def run(self, stop_time):
        print_time = self.print_queue.next_print_time()
        now = self.client.get_current_time()

        while print_time > now and print_time < stop_time:
            self.run_component(print_time)
            print_time = self.print_queue.next_print_time()
            now = self.client.get_current_time()

        self.print_queue.print_all(stop_time)

    def finalize(self):
        self.print_queue.close()


_DEFAULT_CONFIG_FILES = ''
_DEFAULT_CONFIG_FILE_PATH = ''


class _ComponentHandler(object):
    def __init__(self, client, name, services):
        self._user_input = dict()
        self._port_queue = cmt.PortQueue()
        self._print_queue = cmt.PrintQueue()
        self._name = name

        self._cfg = cmt.component_info.from_config_file(filenames, name)
        self._dialog = cmt.dialog.read_from_file(self._cfg['dialog_xml_file'])

        self._template_files = ComponentTemplateFiles(
            self._cfg['template_files'].items())

        # An object with a CMI
        self._client = client

        # getPort, releasePort, createTypeMap, etc.
        self._services = services

        self.status = cmt.status.CREATED

    @property
    def status(self):
        return self._status

    @property
    def name(self):
        return self._name

    def set_up(self):
        pass

    def go(self):
        self.init_component(None)
        self.run_component(self._user_input['run_duration'])
        self.finalize_component()

    def init_component(self, config_file):
        if self._status >= cmt.status.INITIALIZING:
            return
        else:
            self._status = cmt.status.INITIALIZING

        all_ports = self._cfg['ports']
        opt_ports = self._cfg['optional_ports']

        self._port_queue.initialize(self._services, self._client)
        self._port_queue.add_ports(all_ports)
        self._port_queue.add_optional_ports(opt_ports)
        self._port_queue.connect_all_ports()

        sim_name = self._user_input.get(
            '%s/Input/Var/simulation_name' % self.name, self.name)
        sim_name['/%s/simulation_name' % self.name] = sim_name

        self._template_files.substitute(self._user_input,
                                        '/%s/Input/Var/' % self.name,
                                        os.getcwd(), self.dialog_file)

        self._client.prepare(self._cfg['initialize_arg'])

        output_namespace = self._cfg['output_file_namespace']
        self._print_queue.initialize(self._user_input, '/%s/' % self.name,
                                     self._client)
        self._print_queue.add_files_from_list(output_namespace)

        self._port_queue.initialize_all_ports(None)
        self._port_queue.add_mappers(self._cfg['mappers'])

        # Not sure about this. Do we need to run at this point?
        #self._port_queue.run_ports(init_port_names, 0.)
        self._port_queue.run_mappers_for_ports(self._cfg['init_ports'])
        self._port_queue.disable_ports(self._cfg['init_ports'])

        if self._port_queue.get_active_port_count() == 0:
            self._port_queue_dt = sys.float_info.max
        else:
            self._port_queue_dt = self._cfg['port_queue_dt']

        self._status = cmt.status.INITIALIZED

    def run_component(self, time_interval):
        if self._status == cmt.status.UPDATING:
            return True
        else:
            self._status = cmt.status.UPDATING

        if time_interval < 0:
            time_interval = self._client.CMI_get_end_time()

        print_time = self._print_queue.next_print_time()
        now = self._client.CMI_get_current_time()
        while print_time > now and print_time < time_interval:
            self._status = cmt.status.UPDATED
            self.run_component(print_time)
            print_time = self.print_queue.next_print_time()
            now = self.client.CMI_get_current_time()

        now = self._client.CMI_get_current_time()
        port_queue_dt = self._port_queue_dt

        times = np.arange(now, time_interval, port_queue_dt) + port_queue_dt
        try:
            times[-1] = time_interval
        except IndexError:
            times = np.array(time_interval, dtype=np.float)

        for time in times:
            self._port_queue.run_all_ports(now)
            self._port_queue.run_all_mappers()
            if not self._client.run(time):
                raise BmiError()
            now = self._client.CMI_get_current_time()

        self._print_queue.print_all(time_interval)
        self._status = cmt.status.UPDATED

    def finalize_component(self):
        self._status = cmt.status.FINALIZING
        
        self._client.finish()
        self._port_queue.finalize_all_ports()
        self._print_queue.close()

        self._status = cmt.status.FINALIZED
