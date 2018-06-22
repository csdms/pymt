<h1 align="center">PyMT</h1>
<h2 align="center">The Python Modeling Toolkit</h2>

<p align="center">
<a href="https://travis-ci.org/csdms/pymt"><img alt="Build Status" src="https://travis-ci.org/csdms/pymt.svg?branch=master"></a>
<a href="https://coveralls.io/github/csdms/pymt?branch=master"><img alt="Coverage Status" src="https://coveralls.io/repos/github/csdms/pymt/badge.svg?branch=master"></a>
<a href="https://landscape.io/github/csdms/pymt/master"><img alt="Code Health" src="https://landscape.io/github/csdms/pymt/master/landscape.svg"></a>
<a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
<a href="https://github.com/csdms/pymt"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
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
