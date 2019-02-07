#! /usr/bin/env python
from scripting.contexts import cd

from ..errors import BmiError
from .bmi import bmi_call
from .timeinterp import TimeInterpolator


class BmiTimeInterpolator(object):
    def __init__(self, *args, **kwds):
        method = kwds.pop("method", "linear")
        self._interpolators = dict(
            [(name, None) for name in self.output_var_names if "__" in name]
        )
        self.reset(method=method)

        super(BmiTimeInterpolator, self).__init__(*args, **kwds)

    def reset(self, method="linear"):
        for name in self._interpolators:
            self._interpolators[name] = TimeInterpolator(method=method)

    def add_data(self):
        time = self.get_current_time()

        for name in self._interpolators:
            try:
                self._interpolators[name].add_data([(time, self.get_value(name))])
            except BmiError:
                self._interpolators.pop(name)
                print("unable to get value for {name}. ignoring".format(name=name))

    def interpolate(self, name, at):
        return self._interpolators[name].interpolate(at)

    def update_until(self, then, method=None, units=None):
        with cd(self.initdir):
            then = self.time_from(then, units)

            if hasattr(self.bmi, "update_until"):
                try:
                    bmi_call(self.bmi.update_until, then)
                except NotImplementedError:
                    pass

            self.reset()
            while self.get_current_time() < then:
                if self.get_current_time() + self.get_time_step() > then:
                    self.add_data()
                self.update()

            if self.get_current_time() > then:
                self.add_data()
