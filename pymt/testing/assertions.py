import os


def assert_isfile(filename):
    if not os.path.isfile(filename):
        raise AssertionError("%s is not a file" % filename)


def assert_isfile_and_remove(filename):
    try:
        assert_isfile(filename)
    except AssertionError:
        raise
    else:
        os.remove(filename)
