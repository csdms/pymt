#! /usr/bin/env python


from ..ordered_task_status import OrderedTaskStatus


class ComponentHandlerBase(object):
    """
    >>> from cmt.handler.time_stepper import TimeSteppingClient
    >>> client = TimeSteppingClient()
    >>> handler = ComponentHandlerBase('time_stepper', client)
    >>> handler.go()
    >>> client.get_current_time()
    0.0

    >>> client = TimeSteppingClient()
    >>> handler = ComponentHandlerBase('time_stepper', client)
    >>> handler.initialize_client()
    >>> handler.run_client(client.get_end_time() / 2.)
    >>> client.get_current_time()
    5.0
    >>> handler.run_client(client.get_end_time())
    >>> client.get_current_time()
    10.0
    >>> handler.finalize_client()
    >>> client.get_current_time()
    0.0

    """
    def __init__(self, name, client):
        self._name = name
        self._client = client
        #self._env = dict(tasks=OrderedTaskStatus())

        #self.tasks.start_task('create')

        super(ComponentHandlerBase, self).__init__()

        #self.tasks.complete_task()

    @property
    def name(self):
        return self._name

    @property
    def client(self):
        return self._client

    #@property
    #def tasks(self):
    #    return self._env['tasks']

    #@property
    #def task(self):
    #    return self._env['tasks'].task

    #@property
    #def status(self):
    #    return self._env['tasks'].status

    def go(self):
        self.initialize_client()
        self.run_client(self.client.get_end_time())
        self.finalize_client()

    def initialize_client(self):
        #self.tasks.start_task('initialize')

        self.client.prepare()

        #self.tasks.complete_task()

    def run_client(self, stop_time):
        #self.tasks.start_task('update', allow_restart=True)

        self.client.run(stop_time)

        #self.tasks.complete_task()

    def finalize_client(self):
        #self.tasks.start_task('finalize')

        self.client.finish()

        #self.tasks.complete_task()
