#! /usr/bin/env python
import os
import textwrap

import click
import yaml
from tabulate import tabulate


def construct_rows(notebook_index=None):
    import pymt.models

    notebook_index = notebook_index or {}

    rows = []
    for name in pymt.models.__all__:
        summary = pymt.models.__dict__[name]().summary
        if name in notebook_index:
            summary = os.linesep.join(
                [
                    summary,
                    "",
                    f"|binder-{name}|",
                ]
            )
        rows.append((name, summary))

    return rows


@click.command()
@click.argument("dest", type=click.File("w"))
@click.option(
    "--notebook-index",
    type=click.File("r"),
    help="index mapping model names to notebooks",
)
def make_table(dest, notebook_index):
    if notebook_index:
        index = yaml.safe_load(notebook_index)
    else:
        index = {}

    header = """
        .. _available_models:

        Available Models
        ================

        The following table lists the models that are currently available through
        pymt.

    """
    print(textwrap.dedent(header).lstrip(), file=dest)

    rows = construct_rows(notebook_index=index)
    print(tabulate(sorted(rows), headers=("Summary",), tablefmt="rst"), file=dest)

    footer = []
    for name, notebooks in index.items():
        footer.append(
            f"""
            .. |binder-{name}| image:: https://mybinder.org/badge_logo.svg
                :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2F{notebooks[0]}
            """
        )
    print(textwrap.dedent(os.linesep.join(footer)), file=dest)


if __name__ == "__main__":
    make_table()
