from ez_setup import use_setuptools

use_setuptools ()

from setuptools import setup, find_packages

setup (name='cmt',
       version='0.1',
       description='Python utilities for use with CMT',
       author='Eric Hutton',
       author_email='huttone@colorado.edu',
       url='http://csdms.colorado.edu',
       packages=['cmt'],
       scripts=['scripts/scrape_html_block']
      )
