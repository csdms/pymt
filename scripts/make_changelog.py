#! /usr/bin/env python
from __future__ import print_function

import os
import sys
import subprocess
from collections import defaultdict

import jinja2


CHANGELOG = """
# Change Log
All notable changes to PyMT will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

This file was auto-generated using `scripts/make_changelog.py`.

{% for tag, sections in releases.iteritems() %}
## [{{ tag }}] {{ release_date[tag] }}
{% for section, changes in sections.iteritems() %}
### {{section}}
{% for change in changes -%}
* {{ change }}
{% endfor -%}
{% endfor -%}
{% endfor -%}
""".strip()

SECTIONS = ['Added', 'Changed', 'Deprecated', 'Removed', 'Fixed', 'Security']


def git_log(start=None, stop='HEAD'):
    cmd = ['git', 'log', '--first-parent', '--merges', '--topo-order',
           '--oneline']
    if start:
        cmd.append('{start}..{stop}'.format(start=start, stop=stop))

    return subprocess.check_output(cmd).strip()


def git_tag():
    return subprocess.check_output(['git', 'tag']).strip()


def git_tag_date(tag):
    return subprocess.check_output(['git', 'show', tag,
                                    '--pretty=%ci']).strip().split()[0]


def releases():
    return git_tag().split(os.linesep)


def brief(start=None, stop='HEAD'):
    changes = []
    for change in git_log(start=start, stop=stop).split(os.linesep):
        try:
            changes.append(change[change.index(' ') + 1:-1])
        except ValueError:
            pass

    return changes


def group_changes(changes):
    groups = defaultdict(list)
    for change in changes:
        if change.startswith('Merge'):
            continue

        if change.startswith('Add'):
            group = 'Added'
        elif change.startswith('Deprecate'):
            group = 'Deprecated'
        elif change.startswith('Remove'):
            group = 'Removed'
        elif change.startswith('Fix'):
            group = 'Fixed'
        elif change.startswith('Security'):
            group = 'Security'
        else:
            group = 'Changed'
        groups[group].append(change)
    return groups


def main():
    tags = releases()
    tags.append('HEAD')
    changelog = defaultdict(dict)
    release_date = dict()
    for start, stop in zip(tags[:-1], tags[1:]):
        changelog[stop] = group_changes(brief(start=start, stop=stop))
        release_date[stop] = git_tag_date(stop)

    env = jinja2.Environment(loader=jinja2.DictLoader({'changelog': CHANGELOG}))
    print(env.get_template('changelog').render(releases=changelog,
                                               release_date=release_date))


if __name__ == '__main__':
    sys.exit(main())
