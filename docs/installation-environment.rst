We strongly recommend using :term:`mamba` to install and run *pymt*. If
you don't have *mamba* installed, the `Anaconda installation guide`_
can help you through the process.

Once you've installed *Anaconda*/*conda*, we suggest using the
`mamba`_ package manager.  *mamba* is pretty much the same as *conda*,
only faster. If you would rather stick with *conda*, just
replace occurances of *mamba* with *conda*.

.. code-block:: console

    $ conda install mamba

add the :term:`conda-forge` channel
to the list of enabled conda channels on your machine:

.. code-block:: console

    $ mamba config --add channels conda-forge

We advise installing *pymt* into a :term:`conda environment`.
Conda environments can easily be created and discarded.
Create an environment for *pymt* with:

.. code-block:: console

    $ mamba create -n pymt python=3

Once the conda environment has been created, activate it with:

.. code-block:: console

    $ conda activate pymt

.. _Anaconda installation guide: http://docs.anaconda.com/anaconda/install/

.. _mamba: https://medium.com/@QuantStack/open-software-packaging-for-science-61cecee7fc23
