.. highlight:: shell

==========================
Installation: From sources
==========================

.. include:: installation-environment.rst

The sources for *pymt* can be downloaded from the `Github repo`_.

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
