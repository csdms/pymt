.. image:: _static/pymt-logo-header-text.png
    :align: center
    :scale: 75%
    :alt: Python Modeling Tool
    :target: https://pymt.readthedocs.org/

*pymt* is the *Python Modeling Toolkit*.
It is an Open Source Python package, developed by the
`Community Surface Dynamics Modeling System <https://csdms.colorado.edu>`_
(CSDMS), that provides the tools needed for coupling models that expose the
`Basic Model Interface <https://bmi-spec.readthedocs.io>`_ (BMI).

*pymt* in three points:

* Tools for coupling models of disparate time and space scales
* A collection of Earth-surface models
* Extensible plug-in framework for adding new models


What does it look like?  Here is an example of a simple *pymt* program:

.. code-block:: python

    from pymt.models import Cem, Waves

    waves = Waves()
    cem = Cem()

    waves.initialize(*waves.setup())
    cem.initialize(*cem.setup())

    for time in range(1000):
        waves.update()
        angle = waves.get_value("wave_angle")
        cem.set_value("wave_angle", angle)
        cem.update()


User Guide
----------

If you are looking for information on using *pymt* to run and couple models,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   Summary <readme>
   quickstart
   installation
   usage
   examples


API Reference
-------------

If you are looking for information on a specific function, class, or
method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api/index


Miscellaneous Pages
-------------------

.. toctree::
   :maxdepth: 2

   conda-environments
   contributing
   authors
   history
   license

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
