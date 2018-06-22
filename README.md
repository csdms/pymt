<h1 align="center">PyMT</h1>
<h2 align="center">The Python Modeling Toolkit</h2>

<p align="center">
[![Build Status](https://travis-ci.org/csdms/pymt.svg?branch=master)](https://travis-ci.org/csdms/pymt)
[![Coverage Status](https://coveralls.io/repos/csdms/pymt/badge.png?branch=master)](https://coveralls.io/r/csdms/pymt?branch=master)
[![Code Health](https://landscape.io/github/csdms/pymt/master/landscape.svg)](https://landscape.io/github/csdms/pymt/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/csdms/pymt)
</p>

PyMT is an Open Source Python package, developed by the Community
Surface Dynamics Modeling System, that provides the necessary tools
used for the coupling of models that expose the Basic Modeling
Interface (BMI). It contains:

*  Tools necessary for coupling models of disparate time and space
   scales (including grid mappers)
*  Time-steppers that coordinate the sequencing of coupled models
*  Exchange of data between BMI-enabled models
*  Wrappers that automatically load BMI-enabled models into the PyMT
   framework
*  Utilities that support open-source interfaces (UGRID, SGRID, CSDMS
   Standard Names, etc.)
*  A collection of community-submitted models, written in a variety
   of programming languages, from a variety of process domains - but
   all usable from within the Python programming language
*  A plug-in framework for adding additional BMI-enabled models to
   the framework
