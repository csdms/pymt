=====
Usage
=====

In this section,
we describe the primary programmatic elements of *pymt*
and explain how to use them to
configure, run, and couple models.

We assume here that you have
installed *pymt*,
following the instructions in the :doc:`installation` guide.
Below,
we'll use the `CEM`_ and `Waves`_ models.
Install them with:

.. code-block:: console

    $ conda install pymt_cem

.. _CEM: https://csdms.colorado.edu/wiki/Model:CEM
.. _Waves: https://csdms.colorado.edu/wiki/Model_help:Waves


Loading *pymt*
--------------

*pymt* is distributed as a Python `package`_.
To use *pymt*,
it has to be `imported`_ into a Python session.
For example,
the entire package can be loaded with a single import:

.. code-block:: python

    >>> import pymt

Alternately,
models that have been installed into *pymt*
can be imported individually:

.. code-block:: python

  >>> from pymt.models import Waves

Either technique is acceptable,
but there's a slight Pythonic preference
for loading individual models as needed.
We'll use this technique in the remainder of this section.
In either case,
*pymt* must always be imported into a Python session
before it can be used.

.. _package: https://docs.python.org/3/glossary.html#term-package
.. _imported: https://docs.python.org/3/glossary.html#term-importing


Instantiating a model
---------------------

After importing a *pymt* model into a Python session,
you can create an `instance`_  of it
(also known as an `object`_):

.. code-block:: python

  >>> model = Waves()

It is through an instance
that we can configure, interact with, and run a model in *pymt*.
The instance we've created here, ``model``, contains information
(called `properties`_ or data) about the Waves model
(e.g., its inputs and outputs, its time step, its spatial domain),
as well as programs (called `methods`_)
that allow access to these data.
The sections below describe some of the data and methods
that are associated with a model instance in *pymt*.

.. _instance: https://en.wikipedia.org/wiki/Instance_(computer_science)
.. _object: https://docs.python.org/3/glossary.html#term-object
.. _properties: https://en.wikipedia.org/wiki/Property_(programming)
.. _methods: https://en.wikipedia.org/wiki/Method_(computer_programming)


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


Updating model state
--------------------

update method.


Getting and setting variables
-----------------------------

get_value and set_value methods.
