import types
import os

import yaml

from .component import Component


def get_exchange_item_mapping(items):
    """Construct a mapping for exchange items.

    Parameters
    ----------
    items : iterable
        List of exchange item names or (*dest*, *src*) tuples.

    Returns
    -------
    items : list
        List of (*dest*, *src*) tuples of name mappings.

    Examples
    --------
    >>> from cmt.component.model import get_exchange_item_mapping
    >>> get_exchange_item_mapping([('foo', 'bar'), 'baz'])
    [('foo', 'bar'), ('baz', 'baz')]
    >>> get_exchange_item_mapping([dict(source='bar',
    ...                                 destination='foo'), 'baz'])
    [('foo', 'bar'), ('baz', 'baz')]
    """
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
    def components(self):
        """Names of the components.
        """
        return self._components.keys()

    @property
    def driver(self):
        """Name of the driver component.
        """
        return self._driver

    @property
    def duration(self):
        """Length of time the model will run.
        """
        return self._duration

    def go(self, filename=None):
        """Start the model.
        """
        if filename:
            with open(filename, 'r') as f:
                model = yaml.load(f.read())
            self._driver, self._duration = (model['driver'], model['duration'])

        self._components[self.driver].go(self.duration)

    @classmethod
    def load(cls, source):
        """Construct a model from a YAML-formatted string.

        Parameters
        ----------
        source : str or file_like
            YAML-formatted model configuration.

        Returns
        -------
        model : Model
            A newly-created Model.

        Examples
        --------
        >>> from cmt.framework.services import del_component_instances
        >>> del_component_instances(['air_port'])

        >>> from cmt.component.model import Model
        >>> source = '''
        ... name: air_port
        ... class: AirPort
        ... connectivity: []
        ... '''
        >>> model = Model.load(source)
        >>> model.components
        ['air_port']
        """
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
        """Construct a list of model components from a string.

        Parameters
        ----------
        source : str or file_like
            YAML-formatted components configuration.
        with_connectivities : boolean (optional)
            Return connectivity dictionary along with components.

        Returns
        -------
        components : dict
            Dictionary of newly-created components.

        Examples
        --------
        >>> from cmt.framework.services import del_component_instances
        >>> del_component_instances(['air_port'])

        >>> from cmt.component.model import Model
        >>> source = '''
        ... name: air_port
        ... class: AirPort
        ... connectivity: []
        ... '''
        >>> components = Model.load_components(source)
        >>> components.keys()
        ['air_port']
        """
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

        if with_connectivities:
            return components, connectivities
        else:
            return components
