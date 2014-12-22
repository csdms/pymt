import os
import tempfile
import shutil


class cd(object):
    def __init__(self, path, create=False):
        self._dir = os.path.abspath(path)
        self._starting_dir = os.path.abspath(os.getcwd())
        self._create = create

    def __enter__(self):
        if self._create and not os.path.isdir(self._dir):
            os.makedirs(self._dir)
        os.chdir(self._dir)
        return os.path.abspath(os.getcwd())

    def __exit__(self, exception_type, value, traceback):
        os.chdir(self._starting_dir)


class cd_temp(object):
    """Create a temporary directory and change to it.

    Parameters
    ----------
    kwds : dict (optional)
        All keywords are passed directory to *tempfile.mkdtemp*.

    Returns
    -------
    path : str
        Absolute path to the newly-created temporary directory.

    Examples
    --------
    >>> from cmt.utils.run_dir import cd_temp
    >>> import os
    >>> starting_dir = os.getcwd()
    >>> with cd_temp() as path:
    ...     temp_dir = os.getcwd()
    >>> temp_dir == path
    True
    >>> temp_dir != starting_dir
    True
    >>> os.path.exists(temp_dir)
    False
    """
    def __init__(self, **kwds):
        self._dir = os.path.abspath(tempfile.mkdtemp(**kwds))
        self._starting_dir = os.path.abspath(os.getcwd())

    def __enter__(self):
        os.chdir(self._dir)
        return os.path.abspath(os.getcwd())

    def __exit__(self, exception_type, value, traceback):
        os.chdir(self._starting_dir)
        shutil.rmtree(self._dir)


class RunDir(object):
    def __init__(self, directory, create=False):
        self._run_dir = directory
        self._create = create

    def __enter__(self):
        self._starting_dir = os.path.abspath(os.getcwd())
        if self._create and not os.path.isdir(self._run_dir):
            os.makedirs(self._run_dir)
        os.chdir(self._run_dir)

    def __exit__(self, exception_type, value, traceback):
        os.chdir(self._starting_dir)


def open_run_dir(directory, **kwds):
    return RunDir(directory, **kwds)
