#! /usr/bin/env python
from __future__ import print_function

import os
import re
import subprocess
import sys
from collections import OrderedDict, defaultdict
from pkg_resources import parse_version

import click
import jinja2
import m2r

__version__ = "0.1.1"

CHANGELOG = """
# Change Log
All notable changes to landlab will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

This file was auto-generated using `scripts/make_changelog.py`.

{% for tag, sections in releases.items() %}
## Version {{ tag }}
*(released on {{ release_date[tag] }})*

{% for section, changes in sections.items() %}
### {{section}}
{% for change in changes -%}
* {{ change }}
{% endfor -%}
{% endfor -%}
{% endfor -%}
""".strip()

SECTIONS = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]


def git_log(start=None, stop="HEAD"):
    cmd = [
        "git",
        "log",
        "--first-parent",
        "master",
        "--merges",
        "--topo-order",
        # '--pretty=message: %s+author:%an+body: %b'],
        # "--pretty=%s [%an]",
        "--pretty=%s",
        # '--oneline',
    ]
    if start:
        cmd.append("{start}..{stop}".format(start=start, stop=stop))
    return subprocess.check_output(cmd).strip().decode("utf-8")


def git_tag():
    return subprocess.check_output(["git", "tag"]).strip().decode("utf-8")


def git_tag_date(tag):
    return (
        subprocess.check_output(["git", "show", tag, "--pretty=%ci"])
        .strip()
        .split()[0]
        .decode("utf-8")
    )


def git_top_level():
    return (
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
        .strip()
        .decode("utf-8")
    )


def releases(ascending=True):
    tags = git_tag().splitlines() + ["HEAD"]
    if ascending:
        return tags
    else:
        return tags[::-1]


def format_pr_message(message):
    m = re.match(
        "Merge pull request (?P<pr>#[0-9]+) "
        "from (?P<branch>[\S]*)"
        "(?P<postscript>[\s\S]*$)",
        message,
    )
    if m:
        return "{branch} [{pr}]{postscript}".format(**m.groupdict())
    else:
        raise ValueError("not a pull request")


def format_changelog_message(message):
    m = re.match("(?P<first>\w+)(?P<rest>[\s\S]*)$", message)
    word = m.groupdict()["first"]
    if word in ("Add", "Fix", "Deprecate"):
        return word + "ed" + m.groupdict()["rest"]
    elif word in ("Change", "Remove"):
        return word + "d" + m.groupdict()["rest"]
    else:
        return message


def prettify_message(message):
    if message.startswith("Merge branch"):
        return None

    try:
        message = format_pr_message(message)
    except ValueError:
        message = format_changelog_message(message)
    return message


def brief(start=None, stop="HEAD"):
    changes = []
    for change in git_log(start=start, stop=stop).splitlines():
        if change:
            message = prettify_message(change)
            if message:
                changes.append(message)

    return changes


def group_changes(changes):
    groups = defaultdict(list)
    for change in changes:
        if change.startswith("Add"):
            group = "Added"
        elif change.startswith("Deprecate"):
            group = "Deprecated"
        elif change.startswith("Remove"):
            group = "Removed"
        elif change.startswith("Fix"):
            group = "Fixed"
        elif change.startswith("Security"):
            group = "Security"
        else:
            group = "Changed"
        groups[group].append(change)
    return groups


def render_changelog(format="rst"):
    tags = releases(ascending=False)

    changes_by_version = defaultdict(list)
    release_date = dict()
    for start, stop in zip(tags[1:], tags[:-1]):
        if stop.startswith("v"):
            version = ".".join(parse_version(stop[1:]).base_version.split(".")[:2])
        else:
            version = stop
        changes_by_version[version] += brief(start=start, stop=stop)
        release_date[version] = git_tag_date(stop)

    changelog = OrderedDict()
    for version, changes in changes_by_version.items():
        changelog[version] = group_changes(changes)

    env = jinja2.Environment(loader=jinja2.DictLoader({"changelog": CHANGELOG}))
    contents = env.get_template("changelog").render(
        releases=changelog, release_date=release_date
    )
    if format == "rst":
        contents = m2r.convert(contents)
    return contents


@click.command()
@click.argument("output", type=click.File("w"), default="-")
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help=(
        "Don't emit non-error messages to stderr. Errors are still emitted, "
        "silence those with 2>/dev/null."
    ),
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help=(
        "Also emit messages to stderr about files that were not changed or were "
        "ignored due to --exclude=."
    ),
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Overwrite an existing change log without prompting.",
)
@click.version_option(version=__version__)
@click.option(
    "--format",
    type=click.Choice(["md", "rst"]),
    default="rst",
    help="Format to use for the CHANGELOG.",
)
@click.option(
    "--batch",
    is_flag=True,
    help="Run in batch mode.",
)
def main(output, quiet, verbose, format, force, batch):

    contents = render_changelog(format=format)

    if not batch:
        click.echo_via_pager(contents)
    path_to_changelog = os.path.join(git_top_level(), "CHANGELOG." + format)
    if os.path.isfile(path_to_changelog) and not force:
        click.secho(
            "{0} exists. Use --force to overwrite".format(path_to_changelog),
            fg="red",
            err=True,
        )
        sys.exit(1)

    with open(path_to_changelog, "w") as fp:
        fp.write(contents)
    click.secho("Fresh change log at {0}".format(path_to_changelog), bold=True, err=True)


if __name__ == "__main__":
    main(auto_envvar_prefix="CHANGELOG")
