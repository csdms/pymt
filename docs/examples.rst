Examples
========

Here are some examples that demonstrate how to run models using *pymt*.
The examples in the first list run only single models. While the models
do not couple with other models, they may couple with external data
sets. The examples in the second list show how multiple models
can be coupled together by exchanging data.

If you would like to run these examples yourself, in addition to
`installing pymt <installation.rst#Installation>`_, you will
have to install Jupyter Notebook:

.. code-block:: bash

    $ conda install notebook


Single Models
-------------

=================================================== =====================
Model                                               Notebook
=================================================== =====================
:doc:`Frost Number Model <demos/frost_number>`      |binder-frost_number|
:doc:`Kudryavtsev Model <demos/ku>`                 |binder-ku|
:doc:`GIPL Model <demos/Example_01_Basic_Use_GIPL>` |binder-GIPL|
:doc:`ECSimpleSnow Model <demos/ECSnow_PyMT>`       |binder-ECSnow|
:doc:`Coastline Evolution Model <demos/cem>`        |binder-cem|
:doc:`Hydrotrend <demos/hydrotrend>`                |binder-hydrotrend|
:doc:`Sedflux3D <demos/sedflux3d>`                  |binder-sedflux3d|
:doc:`Flexural Subsidence <demos/subside>`          |binder-subside|
=================================================== =====================

.. |binder-frost_number| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Ffrost_number.ipynb

.. |binder-ku| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fku.ipynb

.. |binder-GIPL| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2FExample_01_Basic_Use_GIPL.ipynb

.. |binder-ECSnow| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2FECSnow_PyMT.ipynb

.. |binder-cem| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fcem.ipynb

.. |binder-hydrotrend| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fhydrotrend.ipynb

.. |binder-sedflux3d| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fsedflux3d.ipynb

.. |binder-subside| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fsubside.ipynb


Coupled Models
--------------

====================================================================== ========================
Models                                                                 Notebook
====================================================================== ========================
:doc:`Coastline Evolution Model + Waves <demos/cem_and_waves>`         |binder-cem_and_waves|
:doc:`GIPL + ECSimpleSnow Models <demos/Example_02_GIPL_ECSimpleSnow>` |binder-GIPL_and_ECSnow|
====================================================================== ========================

.. |binder-cem_and_waves| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fcem_and_waves.ipynb

.. |binder-GIPL_and_ECSnow| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2FExample_02_GIPL_ECSimpleSnow.ipynb


..
   Sphinx emits a warning if documents aren't in a toctree.
   Make a hidden toctree for the items above.

.. toctree::
   :maxdepth: 1
   :hidden:

      <demos/frost_number>
      <demos/ku>
      <demos/Example_01_Basic_Use_GIPL>
      <demos/cem>
      <demos/hydrotrend>
      <demos/sedflux3d>
      <demos/subside>
      <demos/child>
      <demos/cem_and_waves>
      <demos/Example_02_GIPL_ECSimpleSnow>
      <demos/sedflux3d_and_child>
      <demos/ECSnow_PyMT>
