.. highlight:: shell

============
Installation
============

We strongly recommend using `conda`_ to install and run *pymt*. If
you don't have conda installed, the `Anaconda installation guide`_
can help you through the process.

.. _conda: https://conda.io/docs/
.. _Anaconda installation guide: http://docs.anaconda.com/anaconda/install/

Stable release
--------------

Start by adding the *conda-forge* channel
to the list of enabled conda channels on your machine:

.. code-block:: console

    $ conda config --add channels conda-forge

We advise installing *pymt* into a conda environment
(see :ref:`conda-env` in the :doc:`quickstart` guide).
Conda environments can easily be set up and torn down.
Create an environment and install *pymt* in it with:

.. code-block:: console

    $ conda create -n pymt python=3 pymt

Note that that *pymt* is built on several open source software
libraries, so it may take a few minutes for conda to find,
download, and install them.

Once the conda environment has been created, activate it with:

.. code-block:: console

    $ source activate pymt


You're now ready to start using *pymt*.
Check the installation by starting a Python session
and importing *pymt*:

.. code-block:: python

    >>> import pymt
    => plugins: (none)

By default, no models are installed with *pymt*.
Instructions for installing models into *pymt*
are given in :ref:`installing-a-model`.

From sources
------------

The sources for *pymt* can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/csdms/pymt

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/csdms/pymt/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/csdms/pymt
.. _tarball: https://github.com/csdms/pymt/tarball/master
