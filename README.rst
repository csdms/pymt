.. role:: raw-html-m2r(raw)
   :format: html


.. raw:: html

   <p align="center">
      <a href='https://pymt.readthedocs.org/'>
         <img src='https://github.com/csdms/pymt/raw/master/docs/_static/pymt-logo-header-text.png'/>
      </a>
   </p>


.. raw:: html

   <h2 align="center">The Python Modeling Toolkit</h2>



.. raw:: html

   <p align="center">

   <a href='https://pymt.readthedocs.io/en/latest/?badge=latest'>
     <img src='https://readthedocs.org/projects/pymt/badge/?version=latest' alt='Documentation Status' /></a>
   <a href="https://travis-ci.org/csdms/pymt">
     <img alt="Build Status" src="https://travis-ci.org/csdms/pymt.svg?branch=master"></a>
   <a href="https://ci.appveyor.com/project/mcflugen/pymt/branch/master">
     <img src="https://ci.appveyor.com/api/projects/status/bf8g17c05ugvhvfe/branch/master"></a>
   <a href="https://coveralls.io/github/csdms/pymt?branch=master">
     <img alt="Coverage Status" src="https://coveralls.io/repos/github/csdms/pymt/badge.svg?branch=master"></a>
   <a href="https://landscape.io/github/csdms/pymt/master">
     <img alt="Code Health" src="https://landscape.io/github/csdms/pymt/master/landscape.svg"></a>
   <a href="https://opensource.org/licenses/MIT">
     <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
   <a href="https://github.com/csdms/pymt">
     <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
   <a href="https://www.codacy.com/app/mcflugen/pymt?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=csdms/pymt&amp;utm_campaign=Badge_Grade">
     <img src="https://api.codacy.com/project/badge/Grade/e8e273131ecb4d7d981fe9f4cf3e83d9"/></a>

   </p>

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
