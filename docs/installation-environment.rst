We strongly recommend using `conda`_ to install and run *pymt*. If
you don't have conda installed, the `Anaconda installation guide`_
can help you through the process.

.. _conda: https://conda.io/docs/
.. _Anaconda installation guide: http://docs.anaconda.com/anaconda/install/

Once you've installed conda,
add the *conda-forge* channel
to the list of enabled conda channels on your machine:

.. code-block:: console

    $ conda config --add channels conda-forge

We advise installing *pymt* into a conda environment
(see :ref:`conda-env` in the :doc:`quickstart` guide).
Conda environments can easily be discarded and recreated.
Create an environment for *pymt* with:

.. code-block:: console

    $ conda create -n pymt python=3

Once the conda environment has been created, activate it with:

.. code-block:: console

    $ source activate pymt
