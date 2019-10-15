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


SSingle Models
-------------
* Frost Number Model |binder-frost_number|
.. |binder-frost_number| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Ffrost_number.ipynb

* Kudryavtsev Model |binder-ku|
.. |binder-ku| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fku.ipynb

* GIPL Model |binder-GIPL|
.. |binder-GIPL| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2FExample_01_Basic_Use_GIPL.ipynb

* ECSimpleSnow Model |binder-ECSnow|
.. |binder-ECSnow| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2FECSnow_PyMT.ipynb

* Coastline Evolution Model |binder-cem|
.. |binder-cem| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fcem.ipynb

* Hydrotrend |binder-hydrotrend|
.. |binder-hydrotrend| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fhydrotrend.ipynb

* Sedflux3D |binder-sedflux3d|
.. |binder-sedflux3d| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fsedflux3d.ipynb

* Flexural Subsidence |binder-subside|
.. |binder-subside| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fsubside.ipynb


Coupled Models
--------------

* Coastline Evolution Model + Waves |binder-cem_and_waves|
.. |binder-cem_and_waves| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fcem_and_waves.ipynb

* GIPL + ECSimpleSnow Models |binder-GIPL_and_ECSnow|
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
