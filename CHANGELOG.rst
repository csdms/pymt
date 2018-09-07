
Change Log
==========

All notable changes to landlab will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com/>`_
and this project adheres to `Semantic Versioning <http://semver.org/>`_.

This file was auto-generated using ``scripts/make_changelog.py``.

[v0.2.3] 2018-09-06
-------------------

Removed
^^^^^^^


* Removed dependency on nose [Eric Hutton]

[v0.2.2] 2018-07-02
-------------------

Removed
^^^^^^^


* Removed dependency on nose [Eric Hutton]

Fixed
^^^^^


* Fixed unit tests failing due to poorly named pytest fixtures. [Eric Hutton]

[v0.2.1] 2018-07-01
-------------------

Removed
^^^^^^^


* Removed dependency on nose [Eric Hutton]

Fixed
^^^^^


* Fixed unit tests failing due to poorly named pytest fixtures. [Eric Hutton]
* Fixed formatting so that it is strict PEP8 package-wide [Eric Hutton]
* Fixed bug in setup when creating a config file. [Eric Hutton]
* Fixed bug that used relative path for initdir. [Eric Hutton]
* Fixed coverage and upload results to coveralls. [Eric Hutton]
* Fixed continuous integration. [Eric Hutton]

Added
^^^^^


* Added support for "vector" grid type. [Eric Hutton]
* Added code coverage with CI. [Eric Hutton]
* Added support and testing for Python 3. [Eric Hutton]
* Added new method for discovering component plugins [Eric Hutton]
* Added grid mapper methods to components [Eric Hutton]
* Added quick_plot method to plot a 2D BMI variable [Eric Hutton]
* Added unstructured dataset to BmiCap [Eric Hutton]
* Added change log and script [Eric Hutton]
* Added plugin framework to dynamically load arbitrary components. [Eric Hutton]
* Added a "cite as" section to component metadata and docstring. [Eric Hutton]
* Added setter to change a component's time units. [Eric Hutton]

Changed
^^^^^^^


* csdms/mdpiper/use-https [#27] [Mark Piper]
* Use tools from the model_metadata package for metadata and staging. [Eric Hutton]
* Use Versioneer for versioning [Eric Hutton]
* Allow multiple authors of components [Eric Hutton]
* Changed to run update_until in model's initialization folder. [Eric Hutton]
* Changed IRF methods to run from within the initialization folder [Eric Hutton]
* Use jinja templates to generate BMI docstrings. [Eric Hutton]

[v0.2] 2016-12-28
-----------------

Removed
^^^^^^^


* Removed dependency on nose [Eric Hutton]

Fixed
^^^^^


* Fixed unit tests failing due to poorly named pytest fixtures. [Eric Hutton]
* Fixed formatting so that it is strict PEP8 package-wide [Eric Hutton]
* Fixed bug in setup when creating a config file. [Eric Hutton]
* Fixed bug that used relative path for initdir. [Eric Hutton]
* Fixed coverage and upload results to coveralls. [Eric Hutton]
* Fixed continuous integration. [Eric Hutton]

Added
^^^^^


* Added support for "vector" grid type. [Eric Hutton]
* Added code coverage with CI. [Eric Hutton]
* Added support and testing for Python 3. [Eric Hutton]
* Added new method for discovering component plugins [Eric Hutton]
* Added grid mapper methods to components [Eric Hutton]
* Added quick_plot method to plot a 2D BMI variable [Eric Hutton]
* Added unstructured dataset to BmiCap [Eric Hutton]
* Added change log and script [Eric Hutton]
* Added plugin framework to dynamically load arbitrary components. [Eric Hutton]
* Added a "cite as" section to component metadata and docstring. [Eric Hutton]
* Added setter to change a component's time units. [Eric Hutton]

Changed
^^^^^^^


* csdms/mdpiper/use-https [#27] [Mark Piper]
* Use tools from the model_metadata package for metadata and staging. [Eric Hutton]
* Use Versioneer for versioning [Eric Hutton]
* Allow multiple authors of components [Eric Hutton]
* Changed to run update_until in model's initialization folder. [Eric Hutton]
* Changed IRF methods to run from within the initialization folder [Eric Hutton]
* Use jinja templates to generate BMI docstrings. [Eric Hutton]
* csdms/mcflugen/fix-for-new-bmi [#8] [Eric Hutton]
