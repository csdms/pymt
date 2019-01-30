=====
Usage
=====

.. todo::

   Describe how each *pymt* method is used in running and coupling models.
   Think of this as an expanded version of the "Basic Concepts" section
   in the :doc:`quickstart`.


To use *pymt* in a project:

.. code-block:: python

    import pymt

Loading a model
+++++++++++++++

.. code-block:: python

  >>> from pymt.models import Waves
  >>> waves = Waves()
  >>> help(Waves)

Model setup
+++++++++++

.. code-block:: python

  >>> from pymt.models import Waves
  >>> waves = Waves()
  >>> waves.setup()

  >>> waves.setup(mean_wave_height=2.)

Model initialization
++++++++++++++++++++

.. code-block:: python

  >>> from pymt.models import Waves
  >>> waves = Waves()
  >>> config_file, config_dir = waves.setup()
  >>> waves.initialize(config_file, dir=config_dir)
