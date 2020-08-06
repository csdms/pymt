|PYMT|

The Python Modeling Toolkit (pymt)
==================================

|Build Status| |AppVeyor Status| |License| |Code Style| |Documentation Status| |Coverage Status| |Conda Version|
|Conda Installation| |Conda Downloads| |Codacy| |Binder|

Quick links:
* `User documentation <https://pymt.readthedocs.io/>`_
* `Installation instructions <https://pymt.readthedocs.io/en/latest/install.html>`_
* `List of available models <https://pymt.readthedocs.io/en/latest/models.html>`_

PyMT is an Open Source Python package, developed by the
`Community Surface Dynamics Modeling System <https://csdms.colorado.edu>`_
(CSDMS), that provides the necessary tools used for the coupling of models
that expose the
`Basic Model Interface <https://bmi-spec.readthedocs.io>`_
(BMI). It contains:

* Tools necessary for coupling models of disparate time and space
  scales (including grid mappers)
* Time-steppers that coordinate the sequencing of coupled models
* Exchange of data between BMI-enabled models
* Wrappers that automatically load BMI-enabled models into the PyMT
  framework
* Utilities that support open-source interfaces (UGRID, SGRID, CSDMS
  Standard Names, etc.)
* A collection of community-submitted models, written in a variety
  of programming languages, from a variety of process domains - but
  all usable from within the Python programming language
* A plug-in framework for adding additional BMI-enabled models to
  the framework

This material is based upon work
supported by the National Science Foundation
under Grant No. `1831623`_,
*Community Facility Support:
The Community Surface Dynamics Modeling System (CSDMS)*.

.. _1831623: https://nsf.gov/awardsearch/showAward?AWD_ID=1831623

.. |PYMT| image:: https://github.com/csdms/pymt/raw/master/docs/_static/pymt-logo-header-text.png
   :target: https://pymt.readthedocs.org/
.. |Build Status| image:: https://travis-ci.org/csdms/pymt.svg?branch=master
   :target: https://travis-ci.org/csdms/pymt
.. |AppVeyor Status| image:: https://ci.appveyor.com/api/projects/status/bf8g17c05ugvhvfe/branch/master
   :target: https://ci.appveyor.com/project/mcflugen/pymt/branch/master
.. |License| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
.. |Code Style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/csdms/pymt
.. |Documentation Status| image:: https://readthedocs.org/projects/pymt/badge/?version=latest
   :target: https://pymt.readthedocs.io/en/latest/?badge=latest
.. |Coverage Status| image:: https://coveralls.io/repos/github/csdms/pymt/badge.svg?branch=master
   :target: https://coveralls.io/github/csdms/pymt?branch=master
.. |Conda Version| image:: https://anaconda.org/conda-forge/pymt/badges/version.svg
   :target: https://anaconda.org/conda-forge/pymt
.. |Conda Installation| image:: https://anaconda.org/conda-forge/pymt/badges/installer/conda.svg
   :target: https://conda.anaconda.org/conda-forge
.. |Conda Downloads| image:: https://anaconda.org/conda-forge/pymt/badges/downloads.svg
   :target: https://anaconda.org/conda-forge/pymt
.. |Codacy| image:: https://app.codacy.com/project/badge/Grade/e8e273131ecb4d7d981fe9f4cf3e83d9
    :target: https://www.codacy.com/manual/mcflugen/pymt?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=csdms/pymt&amp;utm_campaign=Badge_Grade
.. |Binder| image:: https://static.mybinder.org/badge_logo.svg
   :target: https://static.mybinder.org/badge_logo.svg




