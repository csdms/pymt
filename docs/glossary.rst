Glossary
========

A glossary of terms used with  *pymt*.
Because *pymt* is a Python package,
more information on many of these terms
can be found in the `Python Glossary`_.

.. _Python Glossary: https://docs.python.org/3/glossary.html


.. glossary::

   $

      The default shell prompt.

   >>>

      The default Python prompt.

   ...

      The Python prompt for interactively entering code in an indeted
      code block.

   Anaconda

      A Python distribution that includes libraries for scientific
      computing and a package manager. See
      https://www.anaconda.com/distribution for more information.

   Basic Model Interface (BMI)

      A set a functions that are used to interact with and control a
      model. See https://bmi.readthedocs.io for more information.

   Community Surface Dynamics Modeling System (CSDMS)

      CSDMS is an NSF-funded program that seeks to transform the
      science and practice of earth-surface dynamics modeling. For
      more information, visit https://csdms.colorado.edu.

   class

      A program that acts as a template for creating
      :term:`objects<object>`.

   conda

      The package manager for :term:`Anaconda`. Also an informal name
      for an Anaconda installation.

   conda-forge

      A community-led collection of recipes, build infrastructure,
      and distributions for the :term:`conda` package manager.
      See https://conda-forge.org.

   conda environment

      A :term:`conda` sub-installation that isolates a group of
      packages from the main conda installation. See also
      :doc:`conda-environments`.

   configuration file

      A file that contains information for setting up a :term:`model`.

   coupling

      See :term:`model coupling`.

   CSDMS

      See :term:`Community Surface Dynamics Modeling System (CSDMS)`.

   CSDMS Workbench

      An integrated system of software tools, technologies, and
      standards for building and coupling models. See
      https://csdms.colorado.edu/wiki/Workbench for more information.

   data

      Information held by an :term:`object`.

   import

      The process of bringing code from a Python :term:`module` into
      another module or into an interactive Python session.

   instance

      See :term:`object`.

   Jupyter Notebook

      Jupyter Notebook is an open-source web application for creating
      and sharing documents that contain live code, equations,
      visualizations, and narrative text.
      See https://jupyter.org/.

   mamba

      A faster, open-source, alternative to the :term:`conda` package
      manager.
      See https://mamba.readthedocs.io.

   Matplotlib

      A Python plotting library used in *pymt*. For more information,
      see https://matplotlib.org.

   method

      Programs that act upon the :term:`data` of an :term:`object`.

   model

      A computer program that attempts to describe a physical process
      with mathematical relationships that evolve over time and are
      solved numerically. For more information, see, for example,
      https://en.wikipedia.org/wiki/Numerical_modeling_(geology).

   model configuration file

      A file, usually in a text-based format, that lists the tunable
      parameters of a model and supplies their initial values.

   model coupling

      Models are *coupled* when they exchange inputs and outputs,
      often at the resolution of individual time steps. *One-way
      coupling* occurs when the outputs from one model are used as
      inputs to another model. *Two-way coupling* is when outputs from
      one model are used as inputs for another model, which in turn
      supplies its outputs to the first model as inputs, producing a
      feedback.

   module

      A file (with the ``.py`` extension) that contains Python code.

   NumPy

      A Python library that provides arrays. Outputs from *pymt* are
      NumPy arrays. See also http://www.numpy.org.

   object

      A variable that is a concrete example of a
      :term:`class`. Objects have :term:`data` and
      :term:`methods<method>` that act upon those data.

   package

      A directory of Python :term:`modules <module>` that contains a
      :term:`package definition file`. Packages can be installed into
      a Python distribution and :term:`imported <import>` into a
      Python session. Packages may define subpackages, each with their
      own package definition file.

   package definition file

      A file named ``__init__.py`` that denotes a directory contains a
      Python :term:`package`.

   Standard Names

      A semantic mediation technology developed at CSDMS for precisely
      matching variable names between models. For more information,
      see https://csdms.colorado.edu/wiki/CSDMS_Standard_Names.

   tarball

      An archive file that contains several other files, usually
      compressed.
