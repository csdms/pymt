#! /usr/bin/env python
from scripting.contexts import cd

from ..errors import BmiError
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
        for name in self._interpolators:
            try:
                self._interpolators[name].add_data([(self.time, self.get_value(name))])
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
                    self.bmi.update_until(then)
                except NotImplementedError:
                    pass

            self.reset()
            while self.time < then:
                if self.time + self.time_step > then:
                    self.add_data()
                self.update()

            if self.time > then:
                self.add_data()
