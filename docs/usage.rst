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

The *setup* method configures a model run.
It's used to:

* set individual model input variables,
* generate a model configuration file, and
* create a run directory for the model.

Depending on a user's preference,
*setup* can be invoked in different ways.
For example,
given the Waves instance from the previous section,
a basic call to *setup* would be:

.. code-block:: python

  >>> cfg_file, cfg_dir = model.setup()

This creates a model configuration file with default parameters
in a run directory in a temporary location on the filessytem.
It returns the name of configuration file and
the path to the run directory:

.. code-block:: python

  >>> print(cfg_file, cfg_dir)
  waves.txt /tmp/tmpeydq6usd

Note that the two outputs could also be grouped
into a single variable; e.g.:

.. code-block:: python

  >>> args = model.setup()

Alternately,
the run directory can be specified.
For example,
to run the model in the current directory:

.. code-block:: python

  >>> cfg_dir = '.'
  >>> model.setup(cfg_dir)

Here,
we didn't need the outputs from *setup*
because the run directory has been specified,
and the configuration file is created within it.

Model inputs can also be configured with *setup*.
Find the default values of the inputs by querying the
*parameters* property of the model:

.. code-block:: python

  >>> for name, value in model.parameters:
  ...     print(name, '=', value)
  ...
  run_duration = 3650
  incoming_wave_height = 2.0
  incoming_wave_period = 7.0
  angle_highness_factor = 0.2
  angle_asymmetry = 0.5

For example,
configure the model to use an incoming wave height of 3.5 meters:

.. code-block:: python

  >>> waves.setup(cfg_dir, incoming_wave_height=3.5)

Check the *parameters* property to verify that the model inputs
have been updated.


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
