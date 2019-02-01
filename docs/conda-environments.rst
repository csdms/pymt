Conda environments
==================

*conda* environments is probably what you want to use for developing *pymt*
applications.

What problem does conda environments solve?  Chances are that you want to use it
for other projects besides your *pymt* script.  But the more projects you
have, the more likely it is that you will be working with different
versions of Python itself, or at least different versions of Python
libraries.  Let's face it: quite often libraries break backwards
compatibility, and it's unlikely that any serious application will have
zero dependencies.  So what do you do if two or more of your projects have
conflicting dependencies?

*conda* environments to the rescue!  *conda* environments enables multiple
side-by-side installations of Python, one for each project.  It doesn't actually
install separate copies of Python, but it does provide a clever way to
keep different project environments isolated.

If you are on Mac or Linux, and have *conda* installed, from a terminal you
can run the following to create a new Python environment,

.. code-block:: bash

  $ conda create -n myproject python

Now, whenever you want to work on a project, you only have to activate the
corresponding environment.  On OS X and Linux, do the following,

.. code-block:: bash

  $ conda activate myproject

To get out of the environment,

.. code-block:: bash

  $ conda deactivate

To remove the environment,

.. code-block:: bash

  $ conda remove -n myproject --all

With this environment activated, you can install *pymt* into it with the
following,

.. code-block:: bash

  $ conda install pymt -c conda-forge

