.. highlight:: shell

============
Installation
============

We strongly recommend using `conda`_ to install and run *pymt*. If
you don't have it installed, the `Anaconda installation guide`_
can help you through the process.

.. _conda: https://conda.io/docs/
.. _Anaconda installation guide: http://docs.anaconda.com/anaconda/install/

Stable release
--------------

If you haven't already done so,
add the *conda-forge* channel
to the list of enabled conda channels on your machine:

.. code-block:: console

    $ conda config --add channels conda-forge

We advise installing *pymt* into a conda environment.
Environments in conda can easily be set up and town down.
Create an environment and install *pymt* in it with:

.. code-block:: console

    $ conda create -n pymt python=3.7 pymt

Note that that *pymt* is built on several open source software
libraries, so it may take a few minutes for conda to locate,
download, and install them.

Once the conda environment has been installed, activate it with:

.. code-block:: console

    $ source activate pymt


You're now ready to start using *pymt*.
Check the installation by starting a Python session
and importing *pymt*:

.. code-block:: python

    >>> import pymt
    => plugins: (none)

By default, no model components are installed with *pymt*.
Instructions for installing model components into *pym*
are given in *TODO*.

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
