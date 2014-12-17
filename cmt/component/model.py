import types
import os

import yaml

from .component import Component


def get_exchange_item_mapping(items):
    mapping = []
    for item in items:
        if isinstance(item, types.StringTypes):
            item_map = (item, item)
        else:
            try:
                item_map = (item['destination'], item['source'])
            except TypeError:
                item_map = item
        if len(item_map) != 2:
            raise ValueError(item)
        mapping.append(item_map)
    return mapping


class Model(object):
    def __init__(self, components, driver=None, duration=0.):
        self._components = dict(components)
        self._driver = driver
        self._duration = duration

    @property
    def driver(self):
        return self._driver

    @property
    def duration(self):
        return self._duration

    def go(self, filename=None):
        if filename:
            with open(filename, 'r') as f:
                model = yaml.load(f.read())
            self._driver, self._duration = (model['driver'], model['duration'])

        self._components[self.driver].go(self.duration)

    @classmethod
    def load(cls, source):
        components, connectivities = Model.load_components(
            source, with_connectivities=True)

        for (name, component) in components.items():
            for port in connectivities[name]:
                mapping = get_exchange_item_mapping(port['exchange_items'])
                component.connect(port['name'], components[port['connect']],
                                  vars_to_map=mapping)

        return cls(components)

    @staticmethod
    def load_components(source, with_connectivities=False):
        components = {}
        connectivities = {}

        prefix = os.getcwd()
        for section in yaml.load_all(source):
            try:
                section['run_dir'] = os.path.join(prefix,
                                                  section.get('run_dir', '.'))
            except AttributeError:
                raise ValueError(section)

            components[section['name']] = Component.from_dict(section)
            if with_connectivities:
                connectivities[section['name']] = section['connectivity']
                #if section['intent'] == 'driver':
                #    connectivities['__driver__'] = section['name']

        if with_connectivities:
            return components, connectivities
        else:
            return components
