[![Build Status](https://travis-ci.org/csdms/pymt.svg?branch=master)](https://travis-ci.org/csdms/pymt)
[![Coverage Status](https://coveralls.io/repos/csdms/pymt/badge.png?branch=master)](https://coveralls.io/r/csdms/pymt?branch=master)
[![Code Health](https://landscape.io/github/csdms/pymt/master/landscape.svg)](https://landscape.io/github/csdms/pymt/master)

PyMT
====

PyMT is an Open Source Python package, developed by the Community Surface Dynamics Modeling System, that provides the necessary tools used for the coupling of models that expose the Basic Modeling Interface (BMI). It contains:

* Tools necessary for coupling models of disparate time and space scales (including grid mappers)
* Time-steppers that coordinate the sequencing of coupled models
* Exchange of data between BMI-enabled models
* Wrappers that automatically load BMI-enabled models into the PyMT framework
* Utilities that support open-source interfaces (UGRID, SGRID, CSDMS Standard Names, etc.)
* A collection of community-submitted models, written in a variety of programming languages, from a variety of process domains - but all usable from within the Python programming language
* A plug-in framework for adding additional BMI-enabled models to the framework


Modeling Infrastructure Questionnaire
=====================================

Author Name
-----------
Eric Hutton <eric.hutton@colorado.edu>

Full Name
---------
Python Modeling Toolkit

Short Name or Acronym
---------------------
PyMT

Point of contact
----------------
Eric Hutton <eric.hutton@colorado.edu>

Target Audience
---------------
Earth-Systems modelers

Applied Domains
---------------
Terrestrial, Coastal, Marine, Hydrology, Tectonics

Current Usage
-------------
CSDMS

Website
-------
https://github.com/csdms/pymt

Is the software open source
---------------------------
Yes

Open Source License
-------------------
MIT

How to download
---------------
Source is publicly available from GitHub. Binary distributions
are available from the csdms-stack channel on Anaconda Cloud.
*  https://github.com/csdms/pymt
*  https://anaconda.org/csdms-stack/pymt

Support
-------
Email, GitHub issue tracker, meetings

Code Change Management
----------------------
GitHub pull requests

Architecture
============

This section asks questions about architectural characteristics of
the infrastructure.

Components
----------
*Which of the following best describes the infrastructure's
representation of model components? If none apply, please
use the other category and describe the infrastructure's
component construct.*

Both of these:
*  There is a component construct based on registering with the
   infrastructure function pointers to user-written code
*  There is a component construct based on implementing an interface
   in an object-oriented lanaguage (e.g., Python or Java)

Calling vs. Called
------------------
*Is the infrastructure a calling framework (in which user-written
methods or subroutines are registered and invoked) or called
(such as a traditional library or "toolbox")? Check all that apply.*

*  The infrastructure is a calling framework, invoking user-written
   methods or subroutines

Init/Run/Finalize
-----------------
*Does the infrastructure require init, run, and finalize
methods/subroutine to be written?*

Yes

Multiple Phases
---------------
*Does the infrastructure allow init, run, and finalize
methods/subroutines to have multiple phases?*

Yes

Nested Components
-----------------
*Does the infrastructure explicitly implement a mechanism
for nesting components?*

Yes

Generic Coupler Components
--------------------------
*To what degree are generic coupler components provided and what
level of customization is expected?*

Fully generic coupler component(s) is/are provided and no
customization is required

Generic Driver Components
-------------------------
*To what degree are generic driver components provided and what
level of customization is expected?*

Fully generic driver component(s) is/are provided and no
customization is required

Ensembles
---------
*Does the infrastructure allow the same model to be instantiated
multiple times for ensemble runs?*

Yes

Ensemble Memory Space
---------------------
*Can ensemble members run in the same memory space or must they
be on disjoint processors?*
Yes (but depends on a component's implementation)

Execution Sequence Customization
--------------------------------
*How can the model execution sequence be modified? Check all
that apply.*

* By specializing a generic driver
* By changing the configuration metadata

Execution Concurrency
---------------------
*Do models execute sequentially, concurrently, or both? Check
all that apply.*

* Sequentially

Multi-executable
----------------
*Which components, if any, can run as separate executables in
a coupled system? Check all that apply.*

* Entire can run as a single executable

Comments on this Section
------------------------

Do you have any additional comments about the questions in this section? Were all questions relevant and clear? For multiple choice questions, were the possible responses adequate? Are there any missing questions that should be added? Please provide any comments that will help improve future versions of this questionnaire.


Implementation
==============

This section asks questions about how the infrastructure is implemented.

Language
--------
*What language(s) is the infrastructure itself written in? Choose
all that apply.*
*  C
*  C++
*  Fortran
*  Python

Binding Language
----------------
*What language bindings are supported for interfacing with the
infrastructure? These are the languages that someone writes code
in to use the infrastructure. Choose all that apply.*

Python

Programming Language Interoperability
-------------------------------------
*What is the level of support for programming language
interoperability, i.e., mediating between models written in
different programming languages?*

The infrastructure specifically provides interoperability between
models written in different programming languages

Required Software Dependencies
------------------------------
*List any required software dependencies (e.g., MPI, NetCDF).*

*  NetCDF
*  UDUNITS
*  ESMPy
*  scipy

Optional Software Dependencies
------------------------------
*List any optional software dependencies.*

None

Supported Operating Systems
---------------------------
*On what operating systems will the infrastructure execute?
Choose all that apply.*

* Linux
* Mac

Supported Platforms
-------------------
*On what class of computing platform/hardware will the
infrastructure execute? Choose all that apply.*

*  Desktop/laptop
*  Cluster
*  HPC

Supported Compilers
-------------------
*List the set of supported compilers and versions.*

*  gcc 4.2+
*  Python 2.7

Massively Parallel Codes
------------------------
*What is the largest amount of parallelism (in terms of
concurrent threads or processes) that the infrastructure supports?*

No parallelism
(Components can be parallel, though)


Distributed Memory Parallelism
------------------------------
*To what degree does the infrastructure provide parallel data
structures/operators for distributed memory (i.e., by abstracting
MPI communication)?*

MPI or similar library is not used (or used only trivially) within the infrastructure

Shared Memory Parallelism
-------------------------
*To what degree does the infrastructure provide parallel data
structures/operators in shared memory, e.g., abstractions over
a threading library like pthreads?*

No explicit provision of parallel data structures/operators for
multi-threaded environments

Hardware Accelerators
---------------------
*Does the infrastructure provide functions to explicitly recognize
and exploit hardware accelerators?*

No

Comments on this Section
------------------------
Do you have any additional comments about the questions in this section? Were all questions relevant and clear? For multiple choice questions, were the possible responses adequate? Are there any missing questions that should be added? Please provide any comments that will help improve future versions of this questionnaire.


Mediation Services
==================

This category contains questions about mediation services supported
by the modeling infrastructure. For each question, selecting
"Directly provided by the infrastructure" means there is an API
or similar mechanism to access the service "out of the box" with
little coding required by the user.  Selecting "Supplied by user"
means that there is a place where the user needs to provide his or
her own code to complete the mediation.  "No support" means
implementing the mediation is outside the scope of the infrastructure.

Spatial Interpolation
---------------------
*What is the level of support for spatial interpolation?*

Directly provided by the infrastructure

Temporal Interpolation
----------------------
*What is the level of support for temporal interpolation?*

Directly provided by the infrastructure

Calendars
---------
*What is the level of support for different kinds of calendars
(i.e., to manage model time)?*

Directly provided by the infrastructure (as provided by cfunits)

Unit Conversion
---------------
*What is the level of support for unit conversion?*

Directly provided by the infrastructure

Angle Conversion
----------------
*What is the level of support for angle conversion, i.e.,
transforming angles to a different reference line?*

Directly provided by the infrastructure (yes, but limited. azimuth <-> math)

Field Merging
-------------
*What is the level of support for field merging?*

* No support (I don't really know what this means so I'm going with
  "no support")

Domain Interface Consistency Checking
-------------------------------------
*What is the level of support for ensuring domain consistency,
e.g., checking for consistent land/sea masks?*

*  Supplied by user (through CSDMS Standard Names)

Serial-to-Parallel Repartitioning
---------------------------------
*What is the level of support for parallel to serial repartitioning
(often called scatter/gather)?*

*  No support

Parallel-to-Parallel Repartitioning
-----------------------------------
*What is the level of support for parallel-to-parallel
repartitioning (often called MxN redistribution)?*

*  No support

Scientific Mediation
--------------------
*What is the level of support for scientific or domain-specific
mediation (e.g., flux calculations)?*

*  Supplied by user

Load Balancing
--------------
*What is the level of support for load balancing?*

*  No support

Halo Exchange
-------------
*What is the level of support for halo exchanges (i.e., filling
in field values on one process that are owned by a neighboring
process)?*

*  No support

Comments on this Section
------------------------
Do you have any additional comments about the questions in this section? Were all questions relevant and clear? For multiple choice questions, were the possible responses adequate? Are there any missing questions that should be added? Please provide any comments that will help improve future versions of this questionnaire.

Assumptions about Grids and Data Representation
===============================================

This category is about assumptions that this infrastructure makes about spatial/geographic grids. In each question, only choose an option if it represents an assumption that ALWAYS made.

Assumptions about the topological structure
-------------------------------------------
*Which of the following does the modeling infrastructure ALWAYS
ASSUME about the model grid topological structure? Do not check
an option unless it is ALWAYS ASSUMED. Choose one.*

*  none of these are ALWAYS ASSUMED

Assumptions about the topological dimensions
--------------------------------------------
*Which of the following does the modeling infrastructure ALWAYS
ASSUME about model grid topological dimensions? Do not check an
option unless it is ALWAYS ASSUMED. Choose one.*

*  none of these are ALWAYS ASSUMED

Assumptions about the coordinate dimensions
-------------------------------------------
*Which of the following does the modeling infrastructure ALWAYS
ASSUME about the grid's coordinate dimensionality (i.e., the
number of coordinates associated with a point)? Note this may
be greater than the topological dimensionality. Choose one.*

* none of these are ALWAYS ASSUMED

Assumptions about the coordinate system
---------------------------------------
*Which of the following does the modeling infrastructure ALWAYS
ASSUME about the grid's coordinate system? Choose one.*

*  Cartesian

Assumptions about the distance measure
--------------------------------------
*Which of the following does the modeling infrastructure ALWAYS
ASSUME about the distance measure used between points? Choose one.*

*  Straight line distance

Assumptions about the parallel decomposition
--------------------------------------------
*Which of the following does the modeling infrastructure ALWAYS
ASSUME about the grid's parallel decomposition? Choose one.*

N/A

Assumptions about the parallel decomposition specification
----------------------------------------------------------
*Which of the following does the modeling infrastructure ALWAYS
ASSUME about specifying the parallel decomposition? Choose one.*

N/A

Comments on this Section
------------------------
Do you have any additional comments about the questions in this section? Were all questions relevant and clear? For multiple choice questions, were the possible responses adequate? Are there any missing questions that should be added? Please provide any comments that will help improve future versions of this questionnaire.


Grids and Data Representation
=============================

This section describes how spatial/geographic grids are represented
in this infrastructure. 

Grid Construct
--------------
*Does the infrastructure have an explicit data structure or object
for representing model grids?*

*  Yes


Topological Structure
---------------------
*What grid topological structures are supported? Check all that apply.*

*  Logically rectangular uniform
*  Logically rectangular rectilinear
*  Logically rectangular curvilinear
*  Unstructured
*  Point cloud / point list

Topological Dimensions
----------------------
*How many topological dimensions are supported (i.e., the dimension
of the modeled surface, volume, etc?) Check all that apply.*

*  One dimension
*  Two dimensions
*  Three dimensions

Coordinate System
-----------------
*What coordinate systems are supported by the modeling
infrastructure? Check all that apply.*

*  Cartesian

*How many coordinate dimensions are supported (this may be greater
than the number of topological dimensions)? Check all that apply.*

* Three dimensions

Distance Measure
----------------
*What distance measure(s) can be used (e.g., for calculating
interpolation weights)? Check all that apply.*

*  Straight line distance

Max Polygon Edges
-----------------
*If unstructured grids/meshes are supported, what is the max number
of polygon edges?*

None (if using ESMF mapper - field mapping is limited by whatever ESMPy
provides)

Poles
-----
*Describe any supported options for representing poles.*

None

Parallel Decomposition Data Structures
--------------------------------------
*What kinds of decomposition specification does the infrastructure
support natively?*

None

Parallel Decomposition Specification
------------------------------------
*How are parallel decompositions specified to the infrastructure?
Check all that apply.*

None

Masking
-------
*Can grid cells be masked, indicating that some cells have no
value (e.g., land/sea mask)? Choose one.*

*  Yes

Multi-Tile
----------
*Can grids made up of multiple tiles be represented within the
infrastructure? Choose one.*

*  No

Nested Grids
------------
*Can nested grids (i.e., a finer resolution grid embedded in a
coarser grid) be represented by the infrastructure? Choose one.*

*  No

Adaptive Grids
--------------
*Can adaptive grids (i.e., that change in structure over time) be
represented by the infrastructure? Choose one.*

*  Yes but the user must manage the adaptions (e.g. by re-specifying the grid)

Field Construct
---------------
*Does the infrastructure have an explicit data structure or
object for representing model fields, i.e., data situated on
a model grid?*

*  Yes

Field Priming
-------------
*Which of the following does the infrastructure support (e.g.,
APIs) for initializing a field's data? Check all that apply.*

*  From file
*  From a constant or function
*  From memory

Field Options
-------------
*What additional field options are supported? Check all that apply.*

*  Bundles (i.e., collections of related fields)
*  Vectors

Comments on this Section
------------------------
Do you have any additional comments about the questions in this section? Were all questions relevant and clear? For multiple choice questions, were the possible responses adequate? Are there any missing questions that should be added? Please provide any comments that will help improve future versions of this questionnaire.

Interpolation
=============

This section asks questions about support for interpolation.

Sparse Matrix Multiplication
----------------------------
*Is a sparse matrix multiple function provided? Choose one.*

*  Yes (through scipy, does that count?)

Weight Generation Interpolation Method
--------------------------------------
*When generating weights and addresses, what interpolation
method(s) are supported? Check all that apply.*

+Nearest neighbour
+Bilinear/Trilinear
+Higher order non-conservative
+First order conservative
+Non-geometrical (e.g. runoffs, calving, etc)
+Extrapolation outside of the source domain
+Other:

Weight Application Method
-------------------------
*How are interpolation weights applied?*

-With a sparse matrix multiplication operation
-Not supported
-Other :

Weight Generation Execution
---------------------------
*How are interpolation weights and addresses generated? Check
all that apply.*

*  During the model run in serial

Weight Application Execution
----------------------------
*How can interpolation weights and addresses be applied? Check
all that apply.*

*  Online, i.e., during a coupled model run

Temporal Transformations
------------------------
*What temporal transformations can be supported? Check all that apply.*

*  Averaging
*  Interpolation - linear
*  Extrapolation

Comments on this Section
------------------------
Do you have any additional comments about the questions in this section? Were all questions relevant and clear? For multiple choice questions, were the possible responses adequate? Are there any missing questions that should be added? Please provide any comments that will help improve future versions of this questionnaire.

Assumptions about Driving and Time Integration
==============================================

This category is about assumptions that the modeling infrastructure
makes about the driving and the model's iterative properties,
such as time stepping. In each question, only choose an option
if it represents an assumption ALWAYS made by the infrastructure.

Assumptions about the time stepping scheme
------------------------------------------
*Which of the following does the modeling infrastructure ALWAYS
ASSUME about the model's stepping scheme? Select one.*

*  none of these are ALWAYS ASSUMED

Assumptions about the time step size
------------------------------------
*Which of the following does the modeling infrastructure ALWAYS
ASSUME about the model's step size? Select one.*

*  none of these are ALWAYS ASSUMED

Coupling Frequency
------------------
*Which of the following does the modeling infrastructure ALWAYS
ASSUME about the frequency of coupling data exchanges? Choose one.*

*  none of these are ALWAYS ASSUMED

Dynamic Composition
-------------------
*Which of the following does the modeling infrastructure ALWAYS
ASSUME about the models participating in a coupled simulation?
Choose one.*

*  The set of models participating in a coupled simulation start
   together, run the entire length of the simulation, and stop together.

Comments on this Section
------------------------
Do you have any additional comments about the questions in this section? Were all questions relevant and clear? For multiple choice questions, were the possible responses adequate? Are there any missing questions that should be added? Please provide any comments that will help improve future versions of this questionnaire.


Drivers and Time Integration
============================

This section asks questions about the infrastructure's driving and
iterative properties.

Time Stepping Scheme
--------------------
*Which time stepping schemes does the infrastructure support?
Check all that apply.*

*  Explicit time step (dependence only on previous step)

Time Step Size
--------------
*What kinds of step sizes are supported by the infrastructure?
Check all that apply.*

*  Goblal fixed (time step size is fixed in space and time)
*  Global adaptive (time step size varies in time but applies to
   the whole domain)

Coupling Frequency
------------------
*Which of the following does the modeling infrastructure support?*

*  Fixed coupling frequency between any two models
*  The coupling frequency can change dynamically

Dynamic Composition
-------------------
*Which of the following does the modeling infrastructure support?*

*  The set of models participating in a coupled simulation start
   together, run the entire length of the simulation, and stop together.
*  The set of models in a simulation can change dynamically
   (e.g. models can join and leave the simulation at runtime).

Comments on this Section
------------------------
Do you have any additional comments about the questions in this section? Were all questions relevant and clear? For multiple choice questions, were the possible responses adequate? Are there any missing questions that should be added? Please provide any comments that will help improve future versions of this questionnaire.


Infrastructure Configuration
============================

These questions have to do with how the infrastructure is
configured, e.g., via API calls, files, etc. 

Grid Configuration
------------------
*How is the infrastructure configured with information about the
model grid? Check all that apply.*

*  API call(s)

Parallel Decomposition
----------------------
*How is the infrastructure configured with information about the
parallel decomposition? Check all that apply.*

N/A

Temporal Properties
-------------------
*How is the infrastructure configured with information about
the model's temporal properties (start, stop, step size)?
Check all that apply.*

*  API call(s)

Time Stepping Scheme
--------------------
*How is the infrastructure configured with information about
the model's stepping scheme? Check all that apply.*

*  API call(s)

List of Input Fields
--------------------
*How is the infrastructure configured with information about
the model's input fields? Check all that apply.*

*  API call(s)

List of Output Fields
---------------------
*How is the infrastructure configured with information about
the model's output fields? Check all that apply.*

*  API call(s)
*  Configuration file in an infrastructure-specific format

Execution Methods
-----------------
*How is the infrastructure configured with information about the
model's execution methods (e.g., initialize, run, finalize)? Check
all that apply.*

*  Assumed

Comments on this Section
------------------------
Do you have any additional comments about the questions in this section? Were all questions relevant and clear? For multiple choice questions, were the possible responses adequate? Are there any missing questions that should be added? Please provide any comments that will help improve future versions of this questionnaire.


Metadata
========

This sections asks questions about the infrastructure's use of metadata.

Metadata at Runtime
-------------------
*What model metadata can be queried at runtime? Check all that apply.*

*  Temporal metadata
*  Stepping method
*  List of input fields
*  List of output fields
*  Field connections (between models that are coupled)
*  Field coupling frequency
*  Grid properties
*  Execution methods

Metadata at Compile Time
------------------------
*What model metadata can be queried prior to execution (i.e.,
statically)? Check all that apply.*

*  Temporal metadata
*  Stepping method
*  List of input fields
*  List of output fields
*  Execution methods
*  Field connections (between models that are coupled)
*  Field coupling frequency

Metadata Output
---------------
*If the infrastructure outputs metadata, what standards are
supported (e.g. CF, CIM)?*

*  CSDMS Standard Names (CF)
*  udunits
*  ugrid

Metadata Output Format
----------------------
*List any metadata formats that the infrastructure can output
(e.g. xml, csv, json). If none indicate such.*

*  netcdf

Metadata Input
--------------
*If the infrastructure inputs metadata, what standards are
supported (e.g. CF, CIM)?*

*  CSDMS Standard Names (CF)
*  udunits

Metadata Input Format
---------------------
*List any metadata formats that the infrastructure can input (e.g.
xml, csv, json). If none, indicate such.*

*  YAML

Comments on this Section
------------------------
Do you have any additional comments about the questions in this section? Were all questions relevant and clear? For multiple choice questions, were the possible responses adequate? Are there any missing questions that should be added? Please provide any comments that will help improve future versions of this questionnaire.
