=====
Usage
=====

.. todo::

   Describe how each *pymt* method is used in running and coupling models.
   Think of this as an expanded version of the "Basic Concepts" section
   in the :doc:`quickstart`.


Importing a model into Python
-----------------------------

To use *pymt* in a project:

.. code-block:: python

    >>> import pymt

.. code-block:: python

  >>> from pymt.models import Waves
  >>> waves = Waves()
  >>> help(Waves)


Instantiating a model
---------------------

.. code-block:: python

  >>> from pymt.models import Waves
  >>> waves = Waves()
  >>> help(Waves)


Model setup
-----------

Setup method and arguments.

.. code-block:: python

  >>> from pymt.models import Waves
  >>> waves = Waves()
  >>> waves.setup()

  >>> waves.setup(mean_wave_height=2.)


Lifecycle methods
-----------------

Initialize and finalize methods.
Describe initialize arguments.

.. code-block:: python

  >>> from pymt.models import Waves
  >>> waves = Waves()
  >>> config_file, config_dir = waves.setup()
  >>> waves.initialize(config_file, dir=config_dir)


Getting variable names
----------------------


Time methods
------------


Updating the model state
------------------------

update method.


Getting and setting variables
-----------------------------

get_value and set_value methods.
