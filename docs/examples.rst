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

======================================================= =====================
Model                                                   Notebook
======================================================= =====================
:doc:`Frost Number Model <notebooks/frost_number>`      |binder-frost_number|
:doc:`Kudryavtsev Model <notebooks/ku>`                 |binder-ku|
:doc:`GIPL Model <notebooks/Example_01_Basic_Use_GIPL>` |binder-GIPL|
:doc:`ECSimpleSnow Model <notebooks/ECSnow_PyMT>`       |binder-ECSnow|
:doc:`Coastline Evolution Model <notebooks/cem>`        |binder-cem|
:doc:`Hydrotrend <notebooks/hydrotrend>`                |binder-hydrotrend|
:doc:`Sedflux3D <notebooks/sedflux3d>`                  |binder-sedflux3d|
:doc:`Flexural Subsidence <notebooks/subside>`          |binder-subside|
======================================================= =====================

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

========================================================================== ========================
Models                                                                     Notebook
========================================================================== ========================
:doc:`Coastline Evolution Model + Waves <notebooks/cem_and_waves>`         |binder-cem_and_waves|
:doc:`GIPL + ECSimpleSnow Models <notebooks/Example_02_GIPL_ECSimpleSnow>` |binder-GIPL_and_ECSnow|
========================================================================== ========================

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

      <notebooks/frost_number>
      <notebooks/ku>
      <notebooks/gipl>
      <notebooks/cem>
      <notebooks/hydrotrend>
      <notebooks/sedflux3d>
      <notebooks/subside>
      <notebooks/child>
      <notebooks/cem_and_waves>
      <notebooks/gipl_and_ecsimplesnow>
      <notebooks/sedflux3d_and_child>
      <notebooks/ecsimplesnow>
