You're now ready to start using *pymt*.
Check the installation by starting a Python session
and importing *pymt*:

.. code-block:: python

    >>> import pymt

A default set of models is included in the *pymt* install:

.. code-block:: python

    >>> for model in pymt.MODELS:
    ...     print(model)
    ...
    Avulsion
    Plume
    Sedflux3D
    Subside
    FrostNumber
    Ku
    Hydrotrend
    Child
    Cem
    Waves
