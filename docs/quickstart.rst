Quickstart
==========

Here's the fast path to using *pymt*.
If you want to dig deeper,
links are provided at each step to more detailed information elsewhere.


Install conda
-------------

`Anaconda`_ is a free, open-source, Python distribution
that contains a comprehensive set of packages for scientific computing.
If you don't have conda installed, the `Anaconda installation guide`_
can help you through the process.

.. _Anaconda: https://www.anaconda.com/distribution/
.. _Anaconda installation guide: http://docs.anaconda.com/anaconda/install/


Install *pymt*
--------------

Once you've installed conda,
You can get *pymt* directly from `conda-forge`_:

.. code-block:: bash

  $ conda install pymt -c conda-forge 

Installing into a :doc:`conda environment<conda-environments>`
is strongly recommended.
Check the :doc:`installation guide<installation>`
for more detailed information about installing *pymt*.

.. _conda-forge: https://conda-forge.org/


.. _install-a-model:

Install a model
---------------

The `FrostNumber`_ model 
calculates a dimensionless ratio of freezing to thawing degree days
over a year to provide a simple prediction of the existence of permafrost
at a given location.
It's also one of the models available in *pymt*.
Install FrostNumber into *pymt* with:

.. code-block:: console

    $ conda install pymt_permamodel

Check that the model has been installed by starting a Python
session and importing *pymt*:

.. code-block:: python

    >>> import pymt
    => models: FrostNumber, Ku

Keep this Python session open;
we'll use it for the examples that follow.

.. _FrostNumber: https://csdms.colorado.edu/wiki/Model:Frost_Model

.. _run-a-model:

Run a model
-----------

Now that FrostNumber has been installed into *pymt*,
import it into your Python session and create an `instance`_:

.. code-block:: python

  >>> from pymt.models import FrostNumber
  >>> frost = FrostNumber()

To run a model,
*pymt* expects a model `configuration file`_.
Get the default configuration for the FrostNumber model:

.. code-block:: python

  >>> cfg_file, cfg_dir = frost.setup()

Start the model, setting its initial conditions,
by calling its *initialize* `method`_:

.. code-block:: python

  >>> frost.initialize(cfg_file, cfg_dir)

The model is now ready to run.
For reference, show the current time in the model.

.. code-block:: python

  >>> frost.get_current_time()
  0.0

Now call the *update* method to advance the model
by a single time step:

.. code-block:: python

  >>> frost.update()
  >>> frost.get_current_time()
  1.0

The FrostNumber model exposes three variables,
as shown by the *get_output_var_names* method:

.. code-block:: python

  >>> frost.get_output_var_names()
  ('frostnumber__air', 'frostnumber__surface', 'frostnumber__stefan')

With the *get_value* method,
get the current value of the air FrostNumber:

.. code-block:: python

  >>> frost.get_value('frostnumber__air')
  array([ 0.39614661])

Complete the model run by calling the *finalize* method:

.. code-block:: python

  >>> frost.finalize()

A more detailed example of using FrostNumber 
can be found in the :doc:`demos/frost_number`
Jupyter Notebook.
An expanded description of the *pymt* methods used in this example
can be found in the :doc:`usage` section.


.. _instance: https://en.wikipedia.org/wiki/Instance_(computer_science)
.. _configuration file: https://en.wikipedia.org/wiki/Configuration_file
.. _method: https://en.wikipedia.org/wiki/Method_(computer_programming)


View results
------------

.. todo::

   Get a variable from the model and plot it.
