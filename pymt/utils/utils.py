import contextlib
import os
from functools import partial

import click


@contextlib.contextmanager
def as_cwd(path):
    prev_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_cwd)


out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)
