.. _transitions:

Transitions
===========

:class:`~attune.Transition` is a class which represents a transformation from one :class:`~attune.Instrument` to another.

Each :class:`~attune.Transition` has a :class:`~attune._transition.TransitionType`, a string indicating what was done to create the :class:`~attune.Instrument`.
If it exists, the :class:`~attune.Transition` also references the previous :class:`~attune.Instrument` object that was an input to whatever transformation was applied, aswell as a JSON encodable dictionary of metadata to represent parameters that may be useful when analyzing instrument history.
Additionally, the :class:`~attune.Transition` can reference a WrightTools Data object that was used as an input to the transformation, if it exists.
The data object is placed into the attune store when stored, but not included in the JSON serialization.

create transition
-----------------

:code:`create` is the default transition for a new :class:`~attune.Instrument` which is not based on a previous :class:`~attune.Instrument`.

This is what is applied when you create an instrument using the Python constructor (:class:`~attune.Instrument`).

map transitions
---------------

:code:`map` transitions come in two flavors: :meth:`attune.map_ind_points` and :meth:`attune.map_ind_limits`.
:code:`map` transitions involve interpolating tunes onto new independent values using the outputs of the existing tunes.

:meth:`attune.map_ind_points` is given an array of new independent values to use as independent values for a particular tune in a particular arrangement.

.. code-block:: python

   out = attune.map_ind_points(instr, "arr", "tune", [400, 600, 800], units="nm")

:meth:`attune.map_ind_limits` is similar, but instead only cares about setting the bounding limits of the tune.
Here, the number of points in the tune is preserved, but remapped onto a linear space from :code:`min` to :code:`max`.

.. code-block:: python

   out = attune.map_ind_limits(instr, "arr", "tune", 12500, 25000, units="wn")

Each of these optionally allow specifying units, and in the case of :meth:`attune.map_ind_limits` the points will be linearly spaced in the units provided, but converted to the native units of the instrument for interpolation.

offset transitions
------------------

Like :code:`map` transitions, :code:`offset` transitions come in two flavors: :meth:`attune.offset_by` and :meth:`attune.offset_to`.
:code:`offset` transitions apply a static scalar offset to all dependent values in a tune.

For :meth:`attune.offset_by`, you provide the relative value of the change which is directly added to the dependent values of the specified tune.

.. code-block:: python

   # Add pi to the output values of the "tune" tune in the "arr" arrangement
   out = attune.offset_by(instr, "arr", "tune", 3.14)

For :meth:`attune.offset_to`, you instead provide the absolute dependent value of the tune at a specific indepedent value of the specified tune.

.. code-block:: python

   # Offset by the scalar value which makes instr(532, "arr")["tune"] == 2.71
   out = attune.offset_to(instr, "arr", "tune", 2.71, 532) 

restore transition
------------------

:code:`restore` is the transition which is created when you use :meth:`attune.restore` to bring an old instrument object back to the head of the Attune Store.

See :ref:`Store` for more information.

rename transition
-----------------

:code:`rename` is the transition created by :meth:`attune.rename`.
Since the name is the key for the Attune Store, this transition breaks the history tracking, though the old name is provided for reference in the metadata.

.. code-block:: python

   out = attune.rename(instr, "out")

update_merge transition
-----------------------

:code:`update_merge` is the transition created by :meth:`attune.update_merge`.
This transition allows the merging of two instrument objects into a single instrument object.
This is useful for operations such as Spectral Delay Correction, where an instrument is generated indpendent of a previous instrument, but must be integrated to logically group arrangements together.
 
.. code-block:: python

   out = attune.update_merge(instr1, instr2)

If the input instruments do not share any arrangements, then this operation is equivalent to simply creating a new instrument with all of the arrangements of both inputs.
If the input instruments do share arrangements, then :code:`instr2` will take precedence on a tune by tune basis.

:code:`instr1` is considered the previous instrument and is used to determine the name field of the output instrument.

tuning transitions
------------------

There are four tuning methods which incorporate measured data to generate or update :class:`~attune.Instrument` objects: :meth:`attune.tune_test`, :meth:`attune.intensity`, :meth:`attune.setpoint`, and :meth:`attune.holistic`.
More information can be found at :ref:`Tuning Transitions`.
