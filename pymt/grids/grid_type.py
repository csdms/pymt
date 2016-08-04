
class GridType(object):
    _type = None

    def __eq__(self, that):
        return isinstance(that, self.__class__) or str(self) == str(that)

    def __str__(self):
        return self._type

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class GridTypeRectilinear(GridType):
    _type = 'rectilinear'


class GridTypeStructured(GridType):
    _type = 'structured'


class GridTypeUnstructured(GridType):
    _type = 'unstructured'
