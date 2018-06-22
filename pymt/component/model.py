import types
import os

import yaml
import six

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
    >>> from pymt.component.model import get_exchange_item_mapping
    >>> get_exchange_item_mapping([('foo', 'bar'), 'baz'])
    [('foo', 'bar'), ('baz', 'baz')]
    >>> get_exchange_item_mapping([dict(source='bar',
    ...                                 destination='foo'), 'baz'])
    [('foo', 'bar'), ('baz', 'baz')]
    """
    mapping = []
    for item in items:
        if isinstance(item, six.string_types):
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

    def __getitem__(self, name):
        return self._components[name]

    @property
    def components(self):
        """Names of the components.
        """
        return list(self._components.keys())

    @property
    def driver(self):
        """Name of the driver component.
        """
        return self._driver

    @driver.setter
    def driver(self, driver):
        """Set the driver component.
        """
        if driver in self.components:
            self._driver = driver
        else:
            raise ValueError('%s not a component of the model' % driver)

    @property
    def duration(self):
        """Length of time the model will run.
        """
        return self._duration

    @duration.setter
    def duration(self, duration):
        """Set length of time the model will run.
        """
        self._duration = duration

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
        >>> from pymt.framework.services import del_component_instances
        >>> del_component_instances(['air_port'])

        >>> from pymt.component.model import Model
        >>> source = '''
        ... name: air_port
        ... class: AirPort
        ... connectivity: []
        ... '''
        >>> model = Model.load(source)
        >>> model.components
        ['air_port']
        >>> model.driver is None
        True
        >>> model.duration
        0.0

        >>> model.driver = 'air_port'
        >>> model.duration = 1.
        >>> model['air_port'].current_time
        0.0
        >>> model.go() # doctest: +NORMALIZE_WHITESPACE
        {name: air_port, status: running, time: 1.0}
        >>> model['air_port'].current_time
        1.0
        """
        components, connectivities = Model.load_components(
            source, with_connectivities=True)

        for (name, component) in components.items():
            for port in connectivities[name]:
                mapping = get_exchange_item_mapping(port['exchange_items'])
                component.connect(port['name'], components[port['connect']],
                                  vars_to_map=mapping)

        return cls(components)

    @classmethod
    def from_file(cls, filename):
        """Construct a Model from the contents of a file.

        Parameters
        ----------
        filename : str
            Name of the model configuration file.

        Returns
        -------
        model : Model
            A newly-created model.
        """
        with open(filename, 'r') as fp:
            return cls.load(fp)

    @classmethod
    def from_file_like(cls, file_like):
        """Construct a Model from the contents of a file-like object.

        Parameters
        ----------
        file_like : file_like
            A file-like object that contains the model configuration.

        Returns
        -------
        model : Model
            A newly-created model.
        """
        return cls.load(file_like)

    @classmethod
    def from_string(cls, contents):
        """Construct a Model from a string.

        Parameters
        ----------
        contents : str
            A string that contains the model configuration.

        Returns
        -------
        model : Model
            A newly-created model.
        """
        return cls.load(contents)

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
        >>> from pymt.framework.services import del_component_instances
        >>> del_component_instances(['air_port'])

        >>> from pymt.component.model import Model
        >>> source = '''
        ... name: air_port
        ... class: AirPort
        ... connectivity: []
        ... '''
        >>> components = Model.load_components(source)
        >>> list(components.keys())
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
