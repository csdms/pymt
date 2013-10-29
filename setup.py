from ez_setup import use_setuptools

use_setuptools ()

from setuptools import setup, find_packages


setup(name='Cmt',
      version='0.1',
      description='The Component Modeling Tools',
      author='Eric Hutton',
      author_email='huttone@colorado.edu',
      url='http://csdms.colorado.edu',
      install_requires = ['Shapely'],
      packages=['cmt', 'cmt.vtk', 'cmt.bov', 'cmt.nc', 'cmt.components',
                {'cmt.bmi', 'cmt.grids', 'cmt.mappers', 'cmt.scanners'],
      scripts=['scripts/scrape_html_block',
               'scripts/vtu2ncu.py',
               'scripts/quickstart.py',
               'scripts/prmscan.py',
               'scripts/prm2template.py',
               'scripts/prm2input.py',
              ],
)
