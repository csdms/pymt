.. highlight:: shell

============
Installation
============


Stable release
--------------

Installing `landlab` from the `conda-forge` channel can be achieved
by adding `conda-forge` to your channels with:

.. code-block:: console

    $ conda config --add channels conda-forge

Once the `conda-forge` channel has been enabled, `landlab` can be
installed with:

.. code-block:: console

    $ conda install landlab

It is possible to list all of the versions of `landlab` available
on your platform with:

.. code-block:: console

    $ conda search landlab --channel conda-forge

If you don't have `conda`_ installed, the `Anaconda installation guide`_ can
help you through the process.

.. _conda: https://conda.io/docs/
.. _Anaconda installation guide: http://docs.anaconda.com/anaconda/install/

From sources
------------

The sources for pymt can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/csdms/pymt

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/mcflugen/pymt/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/csdms/pymt
.. _tarball: https://github.com/csdms/pymt/tarball/master
