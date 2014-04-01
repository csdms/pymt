from collections import OrderedDict


def prefix_is_empty(prefix):
    """Check if a namespace prefix is empty. A prefix is empty if it's None,
    just a '.' or an empty string.

    Return ``True`` if empty, otherwise ``False``.
    """
    return prefix is None or prefix == '.' or len(prefix) == 0


def names_with_prefix(names, prefix):
    """Find names that begin with a common *prefix*. In this case, names
    are a series ``.``-separated words, much like module names.

    Returns a ``list`` of all names that begin with *prefix*. The order of
    matched names is maintained.

    >>> names_with_prefix(['foo.bar', 'foobar.baz'], 'foo')
    ['foo.bar']
    >>> names_with_prefix(['foo.bar', 'foo.bar', 'foo.foo'], 'foo')
    ['foo.bar', 'foo.baz', 'foo.foo']
    """
    if prefix_is_empty(prefix):
        return set(names)

    if not prefix.endswith('.'):
        prefix = prefix + '.'

    matching_names = OrderedDict()
    for name in names:
        if name.startswith(prefix):
            matching_names[name] = None

    return matching_names.keys()


def strip_prefix(name, prefix):
    """Remove a prefix from a name, including any leading ``.``s.

    >>> strip_prefix('foo.bar', 'foo')
    'bar'
    >>> strip_prefix('foo.bar', '')
    'foo.bar'
    """
    if prefix_is_empty(prefix):
        return name

    if not prefix.endswith('.'):
        prefix += '.'

    if name.startswith(prefix):
        return name[len(prefix):]
    else:
        raise ValueError('%s does not start with %s' % (name, prefix))
