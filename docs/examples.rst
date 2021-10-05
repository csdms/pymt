Examples
========

Here are some examples that demonstrate how to run models using *pymt*.
The examples in the first list run only single models. While the models
do not couple with other models, they may couple with external data
sets. The examples in the second list show how multiple models
can be coupled together by exchanging data.

If you would like to run these examples yourself, in addition to
`installing pymt <installation.rst#Installation>`_, you will
have to install :term:`Jupyter Notebook`:

.. code-block:: bash

    $ conda install notebook

If you encounter any problems when running these notebooks,
please visit us at the `CSDMS Help Desk`_
and explain what occurred.

.. _CSDMS Help Desk: https://github.com/csdms/help-desk


Single Models
-------------

============================ =====================
Notebook                     Run on Binder...
============================ =====================
`Frost Number Model`_        |binder-frost_number|
`Kudryavtsev Model`_         |binder-ku|
`GIPL Model`_                |binder-GIPL|
`ECSimpleSnow Model`_        |binder-ECSnow|
`Coastline Evolution Model`_ |binder-cem|
`Hydrotrend`_                |binder-hydrotrend|
`Hydrotrend Ganges`_         |binder-hydrotrend_Ganges|
`Sedflux3D`_                 |binder-sedflux3d|
`Flexural Subsidence`_       |binder-subside|
============================ =====================

.. _Frost Number Model: https://github.com/csdms/pymt/blob/master/notebooks/frost_number.ipynb
.. |binder-frost_number| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Ffrost_number.ipynb

.. _Kudryavtsev Model: https://github.com/csdms/pymt/blob/master/notebooks/ku.ipynb
.. |binder-ku| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fku.ipynb

.. _GIPL Model: https://github.com/csdms/pymt/blob/master/notebooks/gipl.ipynb
.. |binder-GIPL| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fgipl.ipynb

.. _ECSimpleSnow Model: https://github.com/csdms/pymt/blob/master/notebooks/ecsimplesnow.ipynb
.. |binder-ECSnow| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fecsimplesnow.ipynb

.. _Coastline Evolution Model: https://github.com/csdms/pymt/blob/master/notebooks/cem.ipynb
.. |binder-cem| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fcem.ipynb

.. _Hydrotrend: https://github.com/csdms/pymt/blob/master/notebooks/hydrotrend.ipynb
.. |binder-hydrotrend| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fhydrotrend.ipynb

.. _Hydrotrend Ganges: https://github.com/csdms/pymt/blob/master/notebooks/hydrotrend_Ganges.ipynb
.. |binder-hydrotrend_Ganges| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fhydrotrend_Ganges.ipynb

.. _Sedflux3D: https://github.com/csdms/pymt/blob/master/notebooks/sedflux3d.ipynb
.. |binder-sedflux3d| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fsedflux3d.ipynb

.. _Flexural Subsidence: https://github.com/csdms/pymt/blob/master/notebooks/subside.ipynb
.. |binder-subside| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fsubside.ipynb


Coupled Models
--------------

==================================== ========================
Notebook                             Run on Binder...
==================================== ========================
`Coastline Evolution Model + Waves`_ |binder-cem_and_waves|
`GIPL + ECSimpleSnow Models`_        |binder-GIPL_and_ECSnow|
==================================== ========================

.. _Coastline Evolution Model + Waves: https://github.com/csdms/pymt/blob/master/notebooks/cem_and_waves.ipynb
.. |binder-cem_and_waves| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fcem_and_waves.ipynb

.. _GIPL + ECSimpleSnow Models: https://github.com/csdms/pymt/blob/master/notebooks/gipl_and_ecsimplesnow.ipynb
.. |binder-GIPL_and_ECSnow| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fgipl_and_ecsimplesnow.ipynb
