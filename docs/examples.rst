Examples
========

Here are some examples that demonstrate how to run models using pymt.
The examples in the first list run only single models. While the models
do not couple with other models, they may couple with external data
sets. The examples in the second list show how multiple models
can be coupled together by exchanging data.

If you would like to run these examples yourself, in addition to
`installing pymt <installation.rst#Installation>`_, you will
have to first install Jupyter notebook:

.. code-block:: bash

    $ conda install notebook


Single Models
-------------

* :doc:`Frost Number Model <demos/frost_number>` (macOS, Linux, Windows)
* :doc:`Kudryavtsev Model <demos/ku>` (macOS, Linux, Windows)
* :doc:`Coastline Evolution Model <demos/cem>` (macOS, Linux)
* :doc:`Hydrotrend<demos/hydrotrend>` (macOS, Linux)
* :doc:`Sedflux3D <demos/sedflux3d>` (macOS, Linux)
* :doc:`Flexural Subsidence <demos/subside>` (macOS, Linux)


Coupled Models
--------------

* :doc:`Coastline Evolution Model + Waves <demos/cem_and_waves>` (macOS, Linux)

..
   Sphinx emits a warning if documents aren't in a toctree.
   Make a hidden toctree for the items above.

.. toctree::
   :maxdepth: 1
   :hidden:

      <demos/frost_number>
      <demos/ku>
      <demos/cem>
      <demos/hydrotrend>
      <demos/sedflux3d>
      <demos/subside>
      <demos/child>
      <demos/cem_and_waves>
      <demos/sedflux3d_and_child>
