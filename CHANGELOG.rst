Changelog for pymt
==================

1.2.0 (unreleased)
------------------

- Added a cythonized udunits2 module (#120)

- Documentation improvements

- Use mamba for our continuous integration (#122)


1.1.3 (2020-04-23)
------------------

- Included the cfunits xml data with pymt install (#113)

- Updated notebook readme (#114)

- Updated example notebooks (#112)


1.1.2 (2020-04-08)
------------------

- Removed deployment to PyPI (#111)

- Fixed build of docs on readthedocs (#110)

- Changed behavior of grid_x, y, and z for rectilinear grids (#107)


1.1.0 (2020-02-26)
------------------

- Fixed failing tests (#93)

- Improved documentation (#94, #96, #99, #100, #103, #105)

- Added binder to documentation (#97)

- Added example notebooks for GIPL

- Added support for BMI *rectilinear* grid type (#90)

- Added support for BMI *structured_quadrilateral* grid type (#89)

- Added a sensible BMI class (#86)


1.0.3 (2019-05-15)
------------------

- Include a copy of cfunits package as part of pymt (#85)


1.0.2 (2019-05-14)
------------------

- Fixed cfunits import error on Windows (#84)

- Fixed error getting metadata path from BMI class (#83)


1.0.1 (2019-05-13)
------------------

- Fixed incorrect path from METADATA attribute (#82)

- Imporoved documentation

- Improved example notebooks


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
