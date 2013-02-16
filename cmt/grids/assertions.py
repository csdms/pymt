#! /usr/bin/env

def assert_is_uniform_rectilinear (grid, strict=True):
    try:
        assert (callable (grid.get_spacing))
        assert (callable (grid.get_origin))
        assert (callable (grid.get_shape))
    except (AssertionError, AttributeError):
        raise AssertionError ('Grid is not uniform rectilinear')

def assert_is_rectilinear (grid, strict=True):
    try:
        assert (callable (grid.get_shape))
        assert (callable (grid.get_xyz_coordinates))
    except (AssertionError, AttributeError):
        raise AssertionError ('Grid is not rectilinear')

    if strict:
        try:
            assert_is_uniform_rectilinear (grid)
        except AssertionError:
            pass
        else:
            raise AssertionError ('Grid is not strictly rectilinear')

def assert_is_structured (grid, strict=True):
    try:
        assert (callable (grid.get_shape))
    except (AssertionError, AttributeError):
        raise AssertionError ('Grid is not structured')

    if strict:
        for assertion in [assert_is_rectilinear,
                          assert_is_uniform_rectilinear]:
            try:
                assertion (grid)
            except AssertionError:
                pass
            else:
                raise AssertionError ('Grid is not strictly structured')

def assert_is_unstructured (grid, strict=True):
    if strict:
        for assertion in [assert_is_rectilinear,
                          assert_is_uniform_rectilinear,
                          assert_is_structured]:
            try:
                assertion (grid)
            except AssertionError:
                pass
            else:
                raise AssertionError ('Grid is not strictly unstructured')

def is_uniform_rectilinear (grid, **kwds):
    try:
        assert_is_uniform_rectilinear (grid, **kwds)
    except AssertionError:
        return False
    else:
        return True

def is_rectilinear (grid, **kwds):
    try:
        assert_is_rectilinear (grid, **kwds)
    except AssertionError:
        return False
    else:
        return True

def is_structured (grid, **kwds):
    try:
        assert_is_structured (grid, **kwds)
    except AssertionError:
        return False
    else:
        return True

def is_unstructured (grid, **kwds):
    try:
        assert_is_unstructured (grid, **kwds)
    except AssertionError:
        return False
    else:
        return True

