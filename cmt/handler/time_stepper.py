#! /usr/bin/env python

import numpy as np


class TimeSteppingClient(object):
    def __init__(self):
        self._time = 0.
        self._stop_time = 10.
        self._time_step = 1.

    def prepare(self):
        pass

    def run(self, stop_time):

        n_time_steps = (stop_time - self._time) / (self._time_step)
        for _ in xrange(int(n_time_steps)):
            self.update()

        (self._time_step, saved_time_step) = (stop_time - self._time,
                                             self._time_step)
        self.update()
        self._time_step = saved_time_step

        #times = np.arange(self._time + self._time_step,
        #                  stop_time + self._time_step, self._time_step)

        #if len(times) > 0:
        #    times[-1] = stop_time
        #else:
        #    times = np.array([stop_time])

        #for time in times:
        #    self.update()

    def update(self):
        self._time += self._time_step

    def finish(self):
        self._time = 0.

    def get_end_time(self):
        return self._stop_time

    def get_current_time(self):
        return self._time

    def get_grid_shape(self, var_name):
        return (4, 5)

    def get_grid_spacing(self, var_name):
        return (1., 1.)

    def get_grid_origin(self, var_name):
        return (0., 0.)

    def get_grid_values(self, var_name):
        return np.ones(self.get_grid_shape(var_name)) * self._time
