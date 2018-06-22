#! /usr/bin/env python
import types
import collections

import six
from six.moves import configparser


_KEY_TYPES = {
    'output_file_namespace': str,
    'config_xml_file': str,
    'initialize_arg': str,
    'mappers': list,
    'ports': list,
    'optional_ports': list,
    'init_ports': list,
    'port_queue_dt': float,
    'template_files': dict,
}
_VALID_KEYS = set(_KEY_TYPES.keys())
_KEYS_BY_TYPE = collections.defaultdict(set)
for (key, key_type) in _KEY_TYPES.items():
    _KEYS_BY_TYPE[key_type].add(key)


class Error(Exception):
    pass


class InfoKeyError(Error):
    def __init__(self, keys):
        if isinstance(keys, six.string_types):
            self._keys = keys
        else:
            self._keys = ', '.join(keys)

    def __str__(self):
        return self._keys


class MissingKeyError(InfoKeyError):
    pass


class UnknownKeyError(InfoKeyError):
    pass


def get_missing_keys(found_keys, required_keys):
    return set(required_keys) - set(found_keys)


def get_unknown_keys(found_keys, known_keys):
    return set(found_keys) - set(known_keys)


def assert_no_missing_keys(found_keys, required_keys):
    missing_keys = get_missing_keys(found_keys, required_keys)
    if len(missing_keys) > 0:
        raise MissingKeyError(missing_keys)


def assert_no_unknown_keys(found_keys, known_keys):
    unknown_keys = get_unknown_keys(found_keys, known_keys)
    if len(unknown_keys) > 0:
        raise UnknownKeyError(unknown_keys)


def prefix_is_empty(prefix):
    return prefix is None or prefix == '.' or len(prefix) == 0


def names_with_prefix(names, prefix):
    if prefix_is_empty(prefix):
        return set(names)

    if not prefix.endswith('.'):
        prefix = prefix + '.'

    matching_names = set()
    for name in names:
        if name.startswith(prefix):
            matching_names.add(name)
    return matching_names


def strip_prefix(name, prefix):
    if prefix_is_empty(prefix):
        return name

    if not prefix.endswith('.'):
        prefix += '.'

    if name.startswith(prefix):
        return name[len(prefix):]
    else:
        raise ValueError('%s does not start with %s' % (name, prefix))


def config_value_to_list(config_value):
    return [item.strip() for item in config_value.split(',') if len(item.strip()) > 0]


def config_value_to_string(config_value):
    return str(config_value).strip()


def config_value_to_float(config_value):
    return float(config_value)


def config_value_to_mapping(config_value):
    mapping = {}
    if len(config_value.strip()) > 0:
        for item in config_value.split(','):
            (key, value) = item.split('->')
            mapping[key.strip()] = value.strip()
    return mapping


def list_to_config_value(names):
    return ','.join(names)


def string_to_config_value(string):
    return string.strip()


def float_to_config_value(float_value):
    return str(float_value)


def mapping_to_config_value(mapping):
    if len(mapping) == 0:
        return ''

    map_pairs = []
    for item in mapping.items():
        map_pairs.append('->'.join(item))
    return ','.join(map_pairs)


class ComponentInfo(object):
    _keys = {
        'str': set(['output_file_namespace', 'config_xml_file',
                    'initialize_arg', ]),
        'list': set([ 'mappers', 'ports', 'optional_ports', 'init_ports', ]),
        'float': set(['port_queue_dt', ]),
        'mapping': set(['template_files', ])
    }

    def __init__(self, *args, **kwds):
        """ ComponentInfo(name, mapping) -> new object initialized from a
                mapping object's (key, value) pairs
            ComponentInfo(name, iterable) -> new object initialized as if via:
                d = {}
                for k, v in iterable:
                    d[k] = v
            ComponentInfo(name, **kwds) -> new object initialized with the
                name=value pairs in the keyword argument list.
        """
        params = dict(*args, **kwds)

        #self._all_keys = self._get_all_keys(self._keys)
        self._all_keys = _VALID_KEYS

        self.assert_no_missing_keys(params)
        self.assert_no_unknown_keys(params)

        self._params = dict()
        self._set_parameters(params)

    #@staticmethod
    #def _get_all_keys(key_types):
    #    all_keys = set()
    #    for key_type in key_types.values():
    #        for key in key_type:
    #            if key in all_keys:
    #                raise ValueError('%s: Duplicate' % key)
    #            else:
    #                all_keys.add(key)
    #    return all_keys

    @property
    def params(self):
        return set(self._params)

    @property
    def dict(self):
        return self._params

    @property
    def size(self):
        return len(self._params)

    def _set_parameters(self, params):
        for name in _KEYS_BY_TYPE[str]:
            self._params[name] = config_value_to_string(params[name])

        for name in _KEYS_BY_TYPE[float]:
            self._params[name] = config_value_to_float(params[name])

        for name in _KEYS_BY_TYPE[list]:
            self._params[name] = config_value_to_list(params[name])

        for name in _KEYS_BY_TYPE[dict]:
            self._params[name] = config_value_to_mapping(params[name])

        for item in self._params.items():
            setattr(self, item[0], item[1])

    def assert_no_missing_keys(self, found_keys):
        assert_no_missing_keys(found_keys, self._all_keys)

    def assert_no_unknown_keys(self, found_keys):
        assert_no_unknown_keys(found_keys, self._all_keys)

    def __getitem__(self, key):
        return self._params[key]

    #def __setitem__(self, key, value):
    #    self._params[key] = value


#ALL_PARAMETER_NAMES = set()
#ALL_PARAMETER_NAMES.update(*ComponentInfo._keys.values())


def from_config_file(filenames, prefix='csdms.cmi.'):
    config = configparser.RawConfigParser()
    config.read(filenames)

    component_infos = dict()
    for section in names_with_prefix(config.sections(), prefix):
        component_name = strip_prefix(section, prefix)
        component_infos[component_name] = ComponentInfo(config.items(section))

    return component_infos


def to_config_file(filename, section, params):
    all_params = collections.defaultdict(str)
    all_params.update(params)

    config = configparser.SafeConfigParser()
    config.add_section(section)
    for key in _VALID_KEYS:
        if key in _KEYS_BY_TYPE[str]:
            config.set(section, key, all_params[key])
        elif key in _KEYS_BY_TYPE[float]:
            config.set(section, key, str(all_params[key]))
        elif key in _KEYS_BY_TYPE[list]:
            config.set(section, key, list_to_config_value(all_params[key]))
        elif key in _KEYS_BY_TYPE[dict]:
            config.set(section, key, mapping_to_config_value(all_params[key]))

    with open(filename, 'w') as configfile:
        config.write(configfile)


def component_from_config_file(filenames, name, prefix='csdms.cmi.'):
    infos = from_config_file(filenames, prefix=prefix)
    try:
        return infos[name].dict
    except KeyError:
        raise
