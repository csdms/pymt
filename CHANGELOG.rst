
Change Log
==========

All notable changes to landlab will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com/>`_
and this project adheres to `Semantic Versioning <http://semver.org/>`_.

This file was auto-generated using ``scripts/make_changelog.py``.

Version 0.2.3
-------------

*(released on 2018-09-06)*

Removed
^^^^^^^


* Removed dependency on nose

Version 0.2.2
-------------

*(released on 2018-07-02)*

Removed
^^^^^^^


* Removed dependency on nose

Fixed
^^^^^


* Fixed unit tests failing due to poorly named pytest fixtures.

Version 0.2.1
-------------

*(released on 2018-07-01)*

Removed
^^^^^^^


* Removed dependency on nose

Fixed
^^^^^


* Fixed unit tests failing due to poorly named pytest fixtures.
* Fixed formatting so that it is strict PEP8 package-wide
* Fixed bug in setup when creating a config file.
* Fixed bug that used relative path for initdir.
* Fixed coverage and upload results to coveralls.
* Fixed continuous integration.

Added
^^^^^


* Added support for "vector" grid type.
* Added code coverage with CI.
* Added support and testing for Python 3.
* Added new method for discovering component plugins
* Added grid mapper methods to components
* Added quick_plot method to plot a 2D BMI variable
* Added unstructured dataset to BmiCap
* Added change log and script
* Added plugin framework to dynamically load arbitrary components.
* Added a "cite as" section to component metadata and docstring.
* Added setter to change a component's time units.

Changed
^^^^^^^


* csdms/mdpiper/use-https [#27]
* Use tools from the model_metadata package for metadata and staging.
* Use Versioneer for versioning
* Allow multiple authors of components
* Changed to run update_until in model's initialization folder.
* Changed IRF methods to run from within the initialization folder
* Use jinja templates to generate BMI docstrings.

Version 0.2
-----------

*(released on 2016-12-28)*

Removed
^^^^^^^


* Removed dependency on nose

Fixed
^^^^^


* Fixed unit tests failing due to poorly named pytest fixtures.
* Fixed formatting so that it is strict PEP8 package-wide
* Fixed bug in setup when creating a config file.
* Fixed bug that used relative path for initdir.
* Fixed coverage and upload results to coveralls.
* Fixed continuous integration.

Added
^^^^^


* Added support for "vector" grid type.
* Added code coverage with CI.
* Added support and testing for Python 3.
* Added new method for discovering component plugins
* Added grid mapper methods to components
* Added quick_plot method to plot a 2D BMI variable
* Added unstructured dataset to BmiCap
* Added change log and script
* Added plugin framework to dynamically load arbitrary components.
* Added a "cite as" section to component metadata and docstring.
* Added setter to change a component's time units.

Changed
^^^^^^^


* csdms/mdpiper/use-https [#27]
* Use tools from the model_metadata package for metadata and staging.
* Use Versioneer for versioning
* Allow multiple authors of components
* Changed to run update_until in model's initialization folder.
* Changed IRF methods to run from within the initialization folder
* Use jinja templates to generate BMI docstrings.
* csdms/mcflugen/fix-for-new-bmi [#8]
