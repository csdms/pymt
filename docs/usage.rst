=====
Usage
=====

In this section,
we describe the primary programmatic elements of *pymt*
and explain how to use them to
configure, run, and couple models.

We assume here that you have
installed *pymt*,
following the instructions in the :doc:`install` guide.
Below,
we'll use the `CEM`_ and `Waves`_ models.
Install them with:

.. code-block:: console

    $ mamba install pymt_cem -c conda-forge


Loading *pymt*
--------------

*pymt* is distributed as a Python :term:`package`.
To use *pymt*,
it has to be :term:`imported <import>` into a Python session.
For example,
the entire package can be loaded with a single import:

.. code-block:: python

    >>> import pymt

Alternately,
models that have been installed into *pymt*
can be imported individually:

.. code-block:: python

  >>> from pymt.models import Waves
  => models: Cem, Waves

Either technique is acceptable,
but there's a slight Pythonic preference
for loading individual models as needed.
We'll use this technique in the remainder of this section.
In either case,
*pymt* must always be imported into a Python session
before it can be used.


.. _instantiating-a-model:


Instantiating a model
---------------------

After importing a *pymt* model into a Python session,
you can create an :term:`instance` of it
(also known as an :term:`object`):

.. code-block:: python

  >>> model = Waves()

It is through an instance
that we can configure, interact with, and run a model in *pymt*.
The instance we've created here, ``model``, contains information
(called properties or :term:`data`) about the Waves model
(e.g., its inputs and outputs, its time step, its spatial domain),
as well as programs (called :term:`methods <method>`)
that allow access to these data.
The sections below describe some of the data and methods
that are associated with a model instance in *pymt*.


Model setup
-----------

The *setup* method configures a model run.
It's used to:

* set individual model input variables,
* generate a model configuration file for a run, and
* make a run directory.

Depending on a user's preference,
*setup* can be invoked in different ways.
For example,
given a Waves instance like the one created
in the previous section,
a basic call to *setup* would be:

.. code-block:: python

  >>> cfg_file, cfg_dir = model.setup()

This creates a :term:`model configuration file` with default parameters
in a run directory in a temporary location on the filessytem.
It returns the name of configuration file and
the path to the run directory:

.. code-block:: python

  >>> print(cfg_file, cfg_dir)
  waves.txt /tmp/tmpeydq6usd

Note that the two outputs could also be grouped
into a single variable; e.g.:

.. code-block:: python

  >>> args = model.setup()

Alternately,
the run directory can be specified.
For example,
to run the model in the current directory:

.. code-block:: python

  >>> cfg_dir = '.'
  >>> model.setup(cfg_dir)

Here,
we didn't use the outputs from *setup*
because the run directory has been specified,
and the configuration file is created within it.

Model inputs can also be configured with *setup*.
Find the default values of the inputs by querying the
*parameters* property of the model:

.. code-block:: python

  >>> for name, value in model.parameters:
  ...     print(name, '=', value)
  ...
  run_duration = 3650
  incoming_wave_height = 2.0
  incoming_wave_period = 7.0
  angle_highness_factor = 0.2
  angle_asymmetry = 0.5

Configure the model to use an incoming wave height of 3.5,
instead of the default 2.0, meters:

.. code-block:: python

  >>> model.setup(cfg_dir, incoming_wave_height=3.5)

Check the *parameters* property to verify that the model inputs
have been updated.


Lifecycle methods
-----------------

The *initialize* and *finalize* methods
are used to start and complete a model run.
*Initialize* sets the initial conditions for a model,
while *finalize* cleans up any resources
allocated for the model run.

*Initialize* requires a model configuration file.
The run directory is an optional argument;
if it's not provided, the current directory is assumed.

Using the Waves model as an example,
the steps to import, instantiate, set up,
and initialize the model are:

.. code-block:: python

  >>> from pymt.models import Waves
  >>> waves = Waves()
  >>> config_file, config_dir = waves.setup()
  >>> waves.initialize(config_file, dir=config_dir)

Note that if the outputs from *setup*
had been stored in a single variable,
the values could be unpacked in the call to *initialize*:

.. code-block:: python

  >>> config = waves.setup()
  >>> waves.initialize(*config)

Further, if a model configuration file already exists,
it can be passed directly to *initialize*,
and the call to *setup* could be omitted.

*Finalize* ends a model run.
It takes no arguments:

.. code-block:: python

  >>> waves.finalize()

No further operations can be performed on a model
after it has been finalized.


Time
----

The start time, end time, and current time in a model
are reported through a model's
:term:`Basic Model Interface <Basic Model Interface (BMI)>`
and made available in *pymt* through three properties:
*start_time*, *end_time*, and *time*.
To demonstrate these properties,
create and initialize a new instance of the Waves model:

.. code-block:: python

  >>> waves = Waves()
  >>> config = waves.setup()
  >>> waves.initialize(*config)

then access these time properties with:

.. code-block:: python

  >>> waves.start_time
  0.0
  >>> waves.end_time
  3650.0
  >>> waves.time
  0.0

Use the *time_units* property to see the
units associated with these time values:

.. code-block:: python

  >>> waves.time_units
  'd'

CSDMS recommends using time unit conventions from Unidata’s `UDUNITS`_ package.

Finally,
find the model time step through the 
*time_step* property:

.. code-block:: python

  >>> waves.time_step
  1.0


Updating model state
--------------------

A model can be advanced through time,
one step at a time,
with the the *update* method.

Update the instance of Waves created in the previous section
by a single time step,
checking the time before and after the update:

.. code-block:: python

  >>> waves.time
  0.0
  >>> waves.update()
  >>> waves.time
  1.0

Although we verified that the model time has been updated,
it would be more interesting to see model variables change.
In the next two sections,
we'll find what variables a model exposes,
and how to get their values.


Getting variable names
----------------------

What variables does a model expose for input and output,
for exchange with other models?
These aren't internal variables in the model source code
(like loop counters),
but rather variables that have CSDMS :term:`Standard Names`
and are exposed through a model's
:term:`Basic Model Interface <Basic Model Interface (BMI)>`.

The *input_var_names* and *output_var_names* properties
list the variables exposed by a model.
Find the variables exposed by our Waves instance:

.. code-block:: python

  >>> waves.input_var_names
  ('sea_surface_water_wave__height',
   'sea_surface_water_wave__period',
   'sea_shoreline_wave~incoming~deepwater__ashton_et_al_approach_angle_highness_parameter',
   'sea_shoreline_wave~incoming~deepwater__ashton_et_al_approach_angle_asymmetry_parameter')
  
  >>> waves.output_var_names
  ('sea_surface_water_wave__min_of_increment_of_azimuth_angle_of_opposite_of_phase_velocity',
   'sea_surface_water_wave__azimuth_angle_of_opposite_of_phase_velocity',
   'sea_surface_water_wave__mean_of_increment_of_azimuth_angle_of_opposite_of_phase_velocity',
   'sea_surface_water_wave__max_of_increment_of_azimuth_angle_of_opposite_of_phase_velocity',
   'sea_surface_water_wave__height',
   'sea_surface_water_wave__period')

In each case,
the variable names are returned in a tuple.
The names tend to be quite descriptive,
in order to aid in semantic matching between models.
In practice,
it's often convenient to use a common short name for a variable
instead of its Standard Name.


Getting and setting variables
-----------------------------

The values of variables exposed by a model
can be accessed with the *get_value* method
and modified with the *set_value* method.
Each of these methods takes a variable name
(a CSDMS :term:`Standard Name <Standard Names>`) as input.

As shown in the section above,
the variable ``sea_surface_water_wave__height``
is both an input and an output variable in Waves.
Find its current value:

.. code-block:: python

  >>> waves.get_value('sea_surface_water_wave__height')
  array([ 2.])

In *pymt*,
variable values are stored as :term:`NumPy` arrays.

Assign a new wave height value in the model:

.. code-block:: python

  >>> waves.set_value('sea_surface_water_wave__height', 3.5)

and check the result with *get_value*:

.. code-block:: python

  >>> waves.get_value('sea_surface_water_wave__height')
  array([ 3.5])


.. Links

.. _CEM: https://csdms.colorado.edu/wiki/Model:CEM
.. _Waves: https://csdms.colorado.edu/wiki/Model_help:Waves
.. _UDUNITS: https://www.unidata.ucar.edu/software/udunits
