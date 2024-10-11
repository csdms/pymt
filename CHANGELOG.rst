Release Notes
=============

.. towncrier release notes start

1.3.2 (2024-10-11)
------------------

Bug Fixes
`````````

- Fixed failing NetCDF tests related to a now non-existant THREDDS server. (`#150 <https://github.com/csdms/pymt/issues/150>`_)
- Fixed the *environment.yml* file needed for running notebooks on Binder. (`#153 <https://github.com/csdms/pymt/issues/153>`_)


Other Changes and Additions
```````````````````````````

- Fixed broken environment-docs.yml file. (`#145 <https://github.com/csdms/pymt/issues/145>`_)
- Fixed the successful, but 0%, coverage score reported by Coveralls through the coveralls-python Action. (`#146 <https://github.com/csdms/pymt/issues/146>`_)
- Reformat code for the newest version of *black*. (`#154 <https://github.com/csdms/pymt/issues/154>`_)
- Setup `towncrier <https://towncrier.readthedocs.io/en/actual-freaking-docs/>`_ to manage the changelog. (`#155 <https://github.com/csdms/pymt/issues/155>`_)
- Moved static project metadata into pyproject.toml. (`#156 <https://github.com/csdms/pymt/issues/156>`_)
- Removed dependency on ``six`` since we don't support Python 2 and updated code
  to use Python 3.8+ syntax. (`#159 <https://github.com/csdms/pymt/issues/159>`_)
- Updated *pymt* for the latest version of *gimli.units*, which changed
  its interface slightly. (`#169 <https://github.com/csdms/pymt/issues/169>`_)
- Removed a bunch of lint that had built up over the years. (`#170 <https://github.com/csdms/pymt/issues/170>`_)
- Added support for Python 3.10, and dropped support for older versions. (`#171 <https://github.com/csdms/pymt/issues/171>`_)
- Updated *pymt* to work with the newest version of both *shapely* and
  *scipy*. (`#174 <https://github.com/csdms/pymt/issues/174>`_)


1.3.1 (2021-03-18)
------------------

Documentation Enhancements
``````````````````````````

- Added text on the CSDMS Workbench to the README and docs. (`#129 <https://github.com/csdms/pymt/issues/129>`_)


Other Changes and Additions
```````````````````````````

- Added GitHub actions for continuous integration, building and testing on all
  platforms and Python 3.7+. (`#132 <https://github.com/csdms/pymt/issues/132>`_)
- Removed pymt.udunits in favor of gimli.units for the parsing and converting of units. (`#133 <https://github.com/csdms/pymt/issues/133>`_)
- Added GitHub Actions workflow to test notebooks, for Linux and Mac with Python 3.9. (`#133 <https://github.com/csdms/pymt/issues/133>`_)
- Added GitHub Actions workflow to build the docs. (`#134 <https://github.com/csdms/pymt/issues/134>`_)


1.3.0 (2020-10-21)
------------------

New Features
````````````

- Added ``ModelCollection`` class and ``MODELS`` instance to hold the currently loaded models. (`#128 <https://github.com/csdms/pymt/issues/128>`_)


Bug Fixes
`````````

- Fixed an issue in quick_plot when trying to plot unstructured meshes. (`#127 <https://github.com/csdms/pymt/issues/127>`_)


1.2.1 (2020-09-22)
------------------

Bug Fixes
`````````

- Fixed model metadata discovery by using the `model_metadata <https://github.com/csdms/model_metadata>`_ package to look for metadata files. (`#125 <https://github.com/csdms/pymt/issues/125>`_)


1.2.0 (2020-09-11)
------------------

New Features
````````````

- Added a cythonized *udunits2* module. (`#120 <https://github.com/csdms/pymt/issues/120>`_)


Other Changes and Additions
```````````````````````````

- Use *micromamba* and *mamba* in place of *conda* and *miniconda* for our CI both on
  Travis and AppVeyor. *mamba* is significantly faster than *conda* is Open Source. (`#124 <https://github.com/csdms/pymt/issues/124>`_)


1.1.3 (2020-04-23)
------------------

Documentation Enhancements
``````````````````````````

- Updated the *pymt* example notebooks. (`#112 <https://github.com/csdms/pymt/issues/112>`_)
- Updated the README file for the notebooks. (`#114 <https://github.com/csdms/pymt/issues/114>`_)


Other Changes and Additions
```````````````````````````

- Included the *cfunits* xml data with the *pymt* installation. (`#113 <https://github.com/csdms/pymt/issues/113>`_)


1.1.2 (2020-04-08)
------------------

Documentation Enhancements
``````````````````````````

- Fixed build of *pymt* documentation on readthedocs.io. (`#110 <https://github.com/csdms/pymt/issues/110>`_)


Other Changes and Additions
```````````````````````````

- Changed behavior of ``grid_x``, ``grid_y``, and ``grid_z`` for rectilinear
  grids (as described in `csdms/bmi#65 <https://github.com/csdms/bmi/issues/65>`_).
  These functions now return, respectively, a vector of length *number
  of columns*, *number of rows*, and *number of z-levels*, not a vector of length
  *number of nodes*. (`#107 <https://github.com/csdms/pymt/issues/107>`_)
- Removed deployment of *pymt* to PyPI. (`#111 <https://github.com/csdms/pymt/issues/111>`_)


1.1.0 (2020-02-26)
------------------

New Tutorial Notebooks
``````````````````````

- Added a new notebook for the ``ECSimpleShow`` model. (`#96 <https://github.com/csdms/pymt/issues/96>`_)


New Features
````````````

- Added the ``SensibleBMI`` class that provides a user-centric interface to a
  BMI component. (`#86 <https://github.com/csdms/pymt/issues/86>`_)
- Added support for the BMI *structured_quadrilateral* grid type. (`#89 <https://github.com/csdms/pymt/issues/89>`_)
- Added support for the BMI *rectilinear* grid type. (`#90 <https://github.com/csdms/pymt/issues/90>`_)


Bug Fixes
`````````

- Fixed issues with the sedflux and Child notebooks. (`#94 <https://github.com/csdms/pymt/issues/94>`_)


Documentation Enhancements
``````````````````````````

- Added Binder to *pymt* documentation. (`#97 <https://github.com/csdms/pymt/issues/97>`_)
- Added a table of all models available from pymt. Rows contain a
  summary of the model and a link to a notebook, if available, that
  demonstrates how to use the model. The links are to both a binder as well as a
  static html page of the notebook. (`#99 <https://github.com/csdms/pymt/issues/99>`_)
- Fixed broken links in the documentation. (`#100 <https://github.com/csdms/pymt/issues/100>`_)
- Added links in the documentation to the `CSDMS Help Desk <https://github.com/csdms/help-desk>`_. (`#103 <https://github.com/csdms/pymt/issues/103>`_)
- Updated the Github links in the example notebooks. (`#105 <https://github.com/csdms/pymt/issues/105>`_)


Other Changes and Additions
```````````````````````````

- Fixed some failing unit tests. (`#93 <https://github.com/csdms/pymt/issues/93>`_)


1.0.3 (2019-05-15)
------------------

Other Changes and Additions
```````````````````````````

- Included a copy of *cfunits* package as part of *pymt*. (`#85 <https://github.com/csdms/pymt/issues/85>`_)


1.0.2 (2019-05-14)
------------------

Bug Fixes
`````````

- Fixed an error getting the metadata path from BMI class. (`#83 <https://github.com/csdms/pymt/issues/83>`_)
- Fixed a *cfunits* import error on Windows. (`#84 <https://github.com/csdms/pymt/issues/84>`_)


1.0.1 (2019-05-13)
------------------

Bug Fixes
`````````

- Fixed an incorrect path from METADATA attribute. (`#82 <https://github.com/csdms/pymt/issues/82>`_)


1.0.0 (2019-02-18)
------------------

- Added a more pythonic BMI (#55)

- Remove support from Python 2.7

- Fixed CEM notebook (#64)

- Fixed int error on some platforms (#58)

- Improved documentation

- Improved tests


0.2.9 (2019-02-09)
------------------

- Fixed the quickstart tutorial (#55)

- Removed the old way of loading models (i.e. from a package called `csdms`) (#54)

0.2.8 (2019-02-07)
------------------

- Code clean-up (#50, #52)

- Improved the HydroTrend notebook

- Added continuous integration on Windows using AppVeyor (#48)

0.2.7 (2019-01-23)
------------------

- Fixed installation issue where tests folder was installed (#43)

- Removed utility scripts from installation (#42)

- Make installation of ESMF optional (#41)

- Added pymt example notebooks to docs (#40)

- Improved documentation


0.2.6 (2018-10-24)
------------------

- Load pymt plugins as components (#38)


0.2.5 (2018-10-04)
------------------

- Fixed for new model_metadata API (#36)


0.2.4 (2018-09-07)
------------------

- Improved documentation

- Improved continuous integration


0.2.3 (2018-07-06)
------------------

- Removed dependency on nose


0.2.2 (2018-07-02)
------------------

- Removed dependency on nose

- Fixed unit tests failing due to poorly named pytest fixtures.

0.2.1 (2018-07-01)
------------------

- Removed dependency on nose

- Fixed unit tests failing due to poorly named pytest fixtures.

- Fixed formatting so that it is strict PEP8 package-wide

- Fixed bug in setup when creating a config file.

- Fixed bug that used relative path for initdir.

- Fixed coverage and upload results to coveralls.

- Fixed continuous integration.

- Added support for "vector" grid type.

- Added code coverage with CI.

- Added support and testing for Python 3.

- Added new method for discovering component plugins

- Added grid mapper methods to components

- Added quick_plot method to plot a 2D BMI variable

- Added unstructured dataset to BmiCap

- Added change log and script

- Added plugin framework to dynamically load arbitrary components.

- Added a "cite as" section to component metadata and docstring.

- Added setter to change a component's time units.

- csdms/mdpiper/use-https [#27]

- Use tools from the model_metadata package for metadata and staging.

- Use Versioneer for versioning

- Allow multiple authors of components

- Changed to run update_until in model's initialization folder.

- Changed IRF methods to run from within the initialization folder

- Use jinja templates to generate BMI docstrings.


0.2.0 (2016-12-28)
------------------

- Removed dependency on nose

- Fixed unit tests failing due to poorly named pytest fixtures.

- Fixed formatting so that it is strict PEP8 package-wide

- Fixed bug in setup when creating a config file.

- Fixed bug that used relative path for initdir.

- Fixed coverage and upload results to coveralls.

- Fixed continuous integration.

- Added support for "vector" grid type.

- Added code coverage with CI.

- Added support and testing for Python 3.

- Added new method for discovering component plugins

- Added grid mapper methods to components

- Added quick_plot method to plot a 2D BMI variable

- Added unstructured dataset to BmiCap

- Added change log and script

- Added plugin framework to dynamically load arbitrary components.

- Added a "cite as" section to component metadata and docstring.

- Added setter to change a component's time units.

- csdms/mdpiper/use-https [#27]

- Use tools from the model_metadata package for metadata and staging.

- Use Versioneer for versioning

- Allow multiple authors of components

- Changed to run update_until in model's initialization folder.

- Changed IRF methods to run from within the initialization folder

- Use jinja templates to generate BMI docstrings.

- csdms/mcflugen/fix-for-new-bmi [#8]
