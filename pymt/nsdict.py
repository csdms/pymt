#! /usr/bin/env python

"""
>>> d = NamespaceDict()
>>> d['/foo/bar'] = 'baz'
>>> d['/foo/bar']
'baz'
>>> d['/foo/bar/']
'baz'

>>> d['/foo']
NamespaceDict({'/bar': 'baz'})
>>> d['/foo/baz'] = 'bar'
>>> keys = d['/foo'].keys()
>>> keys == set(['/bar', '/baz', '/'])
True

>>> d = NamespaceDict(sep='.')
>>> d['.foo.bar'] = 'baz'
>>> d['.foo.bar']
'baz'
>>> d['.foo.bar.']
'baz'

>>> d['.foo']
NamespaceDict({'.bar': 'baz'})
>>> d['.foo.baz'] = 'bar'
>>> keys = d['.foo'].keys()
>>> keys == set(['.', '.bar', '.baz'])
True

>>> d = NamespaceDict({'/foo/bar/': 'baz', '/foo/baz': 'bar'})
>>> set(d.keys()) == set(['/', '/foo', '/foo/bar', '/foo/baz'])
True
>>> set(d.values()) == set(['baz', 'bar'])
True
"""
from collections import defaultdict


def normpath(func):
    def _wrap(self, *args):
        return func(self, self._norm(args[0]), *(args[1:]))

    return _wrap


class NamespaceDict(dict):
    def __init__(self, *args, **kwds):
        self._sep = kwds.pop("sep", "/")
        self._ref_count = defaultdict(int)
        self._ref_count[self._sep] = 1

        for item in self._args_as_items(*args, **kwds):
            self[item[0]] = item[1]

    def get(self, *args):
        try:
            return self[args[0]]
        except KeyError:
            if len(args) == 2:
                return args[1]
            else:
                raise

    def keys(self):
        return set(self._ref_count.keys())

    def has_key(self, name):
        return name in self

    def update(self, new_dict):
        if isinstance(new_dict, NamespaceDict):
            dict.update(self, new_dict)
        else:
            self.update(NamespaceDict(new_dict))

    def pop(self, name, *args):
        value = self.get(name, *args)
        if name in self:
            self.__delitem__(name)
        return value

    @normpath
    def extract(self, base):
        if base == self._sep:
            base = ""

        new_dict = dict()
        for key in self._iter_sub_paths(base):
            try:
                new_dict[key] = dict.__getitem__(self, self._join(base, key))
            except KeyError:
                pass

        if len(new_dict) == 0:
            raise KeyError(base)
        else:
            return NamespaceDict(new_dict, sep=self._sep)

    @normpath
    def __setitem__(self, path, value):
        for part in self._iter_paths(path):
            if part in self._leaves():
                self.__delitem__(part)
        if path in self:
            self.__delitem__(path)

        dict.__setitem__(self, path, value)

        self._increment_path_references(path)

    @normpath
    def __getitem__(self, path):
        try:
            return dict.__getitem__(self, path)
        except KeyError:
            return self.extract(path)

    @normpath
    def __delitem__(self, name):
        for leaf in self._leaves():
            if leaf.startswith(name):
                self._decrement_parent_path_references(leaf)
                dict.__delitem__(self, leaf)

    def __len__(self):
        return len(self._ref_count)

    @normpath
    def __contains__(self, name):
        return name in self._ref_count

    def __repr__(self):
        return "NamespaceDict(%s)" % dict.__repr__(self)

    def __str__(self):
        return dict.__str__(self)

    @staticmethod
    def _args_as_items(*args, **kwds):
        return dict(*args, **kwds).items()

    def _join(self, *p):
        return self._sep.join(p)

    def _norm(self, path):
        return self._sep + self._sep.join(self._split(path))

    def _split(self, path):
        return [part for part in path.split(self._sep) if len(part) > 0]

    def _iter_paths(self, path):
        yield self._sep
        parts = self._split(path)
        base = ""
        for part in parts:
            base = self._join(base, part)
            yield base

    def _paths(self, path):
        return set(self._iter_paths(path))

    @normpath
    def _iter_sub_paths(self, base):
        if base == self._sep:
            base = ""
        for key in self._ref_count.keys():
            if key.startswith(base):
                try:
                    yield key[len(base) + 1 :]
                except IndexError:
                    yield key[len(base) :]

    def _sub_paths(self, base):
        return [name for name in self._iter_sub_paths(base)]

    def _increment_path_references(self, path):
        for part in self._iter_paths(path):
            self._ref_count[part] += 1

    def _decrement_parent_path_references(self, name):
        for part in self._iter_paths(name):
            assert part in self._ref_count, (part, name)

            self._ref_count[part] -= 1
            if self._ref_count[part] == 0:
                del self._ref_count[part]
            elif self._ref_count[part] < 0:
                raise KeyError(part)

    def _leaves(self):
        return set(dict.keys(self))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
