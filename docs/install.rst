.. highlight:: shell

============
Installation
============

There are two ways to install *pymt* on your local machine:

* :ref:`stable-release`
* :ref:`from-source` (advanced option)

If you plan to use *pymt* to run and couple models,
installing a :ref:`stable release<stable-release>`
is a good option.
However, if you intend to develop with *pymt*,
possibly modifying it,
it's best to install it
:ref:`from source<from-source>`.

If you encounter any problems when installing *pymt*,
please visit us at the `CSDMS Help Desk`_
and explain what occurred.

.. _CSDMS Help Desk: https://github.com/csdms/help-desk


.. _stable-release:

Stable release
--------------

.. include:: installation-environment.rst

Install *pymt* into this conda environment with:

.. code-block:: console

    $ conda install pymt

Note that *pymt* is built on several open source software
libraries, so it may take a few minutes for conda to find,
download, and install them.

.. include:: installation-check.rst


.. _from-source:

From source
-----------

.. include:: installation-environment.rst

The source code for *pymt* can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/csdms/pymt

Or download the `tarball`_:

.. code-block:: console

    $ curl -OL https://github.com/csdms/pymt/tarball/master

Once you have a copy of the source,
install the *pymt* dependencies into the conda environment
you created above:

.. code-block:: console

    $ conda install --file=requirements.txt

Then install *pymt* with:

.. code-block:: console

    $ python setup.py install

.. include:: installation-check.rst


.. _Github repo: https://github.com/csdms/pymt
.. _tarball: https://github.com/csdms/pymt/tarball/master
