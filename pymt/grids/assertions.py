def is_callable_method(obj, method):
    return hasattr(obj, method) and callable(getattr(obj, method))


def assert_is_uniform_rectilinear(grid):
    if not is_uniform_rectilinear(grid):
        raise AssertionError("Grid is not uniform rectilinear")


def assert_is_rectilinear(grid, strict=True):
    if not is_rectilinear(grid, strict=strict):
        if strict:
            raise AssertionError("Grid is not strictly rectilinear")
        else:
            raise AssertionError("Grid is not rectilinear")


def assert_is_structured(grid, strict=True):
    if not is_structured(grid, strict=strict):
        if strict:
            raise AssertionError("Grid is not strictly structured")
        else:
            raise AssertionError("Grid is not structured")


def assert_is_unstructured(grid, strict=True):
    if not is_unstructured(grid, strict=True):
        if strict:
            raise AssertionError("Grid is not strictly unstructured")
        else:
            raise AssertionError("Grid is not unstructured")


def is_uniform_rectilinear(grid):
    return (
        is_callable_method(grid, "get_spacing")
        and is_callable_method(grid, "get_origin")
        and is_callable_method(grid, "get_shape")
    )


def is_rectilinear(grid, strict=True):
    loosely_rectilinear = is_callable_method(grid, "get_shape") and is_callable_method(
        grid, "get_xyz_coordinates"
    )
    if not strict:
        return loosely_rectilinear
    else:
        return loosely_rectilinear and not is_uniform_rectilinear(grid)


def is_structured(grid, strict=True):
    loosely_structured = is_callable_method(grid, "get_shape")

    if not strict:
        return loosely_structured
    else:
        return loosely_structured and not (
            is_rectilinear(grid) or is_uniform_rectilinear(grid)
        )


def is_unstructured(grid, strict=True):
    if not strict:
        return True
    else:
        return not (
            is_structured(grid) or is_rectilinear(grid) or is_uniform_rectilinear(grid)
        )
