Attune Data Structures
======================

The data structures in :code:`attune` take inspiration from drawing parallels to nomenclature in music.
The experimenter is the conductor of an orchestra of several :class:`~attune.Instrument` objects.

At a high level, the :class:`~attune.Instrument` is what users will directly interact with.
An :class:`~attune.Instrument` represents a collection of motors which must follow interpolated curves to produce one logical "one to many" mapping of logical position to motor positions.
This collection can be as simple as a Spectral Delay Correction (SDC) mapping a color of light onto a single motor position to account for arrival time differences due to color of light.
Alternatively, it can be a complex collection of several motors as in an Optical Parametric Amplifier (OPA), which requires all motors to be set to produce light of a selected color.
When called like a function, the :class:`~attune.Instrument` provides a :class:`~attune.Note` which maps a given position to underlying motor positions.

An :class:`~attune.Instrument` may consist of several different modes (:class:`~attune.Arrangement` s) which can allow for things like different mixing processes in OPAs or multiple correction factors for SDC.
Each :class:`~attune.Arrangement` in turn consists of :class:`~attune.Tune` objects, which provide individual mappings for input to output.
By default a :class:`~attune.Tune` maps an input to a motor position or :class:`~attune.Setable`, however :class:`~attune.Arrangement` s may be nested allowing for references to lower level arrangements.
This behavior allows the tuning curve for OPA mixing processes (such as Second Harmonic of Signal) to be built by adding one (or more) additional :class:`~attune.Setable` to an existing Signal :class:`~attune.Arrangement`.
Parent :class:`~attune.Arrangement` s may override the position of :class:`~attune.Setable` s in the child arrangement.

These data structures are treated as "immutable" objects. This means that once created the values and the relationships of the objects are not changed.
Instead, we have a system of :ref:`transitions` which provide *new*, updated :class:`~attune.Instrument` instances.
This allows the context of how instruments were created to be preserved.


Setable
-------

A :class:`~attune.Setable` consists of only two pieces of information: a name (a string) and a default position (None or string or float).

If the default is set, then any :class:`~attune.Note` which does not explicitly set that :class:`~attune.Setable` will inherit the default position.
If there is no default, then the :class:`~attune.Note` will simply not specify the :class:`~attune.Setable` at all.

In most cases, :class:`~attune.Setable` objects are not required to be explicitly created, unless you wish to take advantage of default behavior.

:class:`~attune.Setable` provides an :meth:`~attune.Setable.as_dict` method to allow for serialization.

.. code-block:: python

   no_default = attune.Setable("no_default")
   default = attune.Setable("default", default=1.2)

Tune
----

A :class:`~attune.Tune` represents a continuous transformation from an independent variable to a dependent variable.

Currently the :class:`~attune.Tune` class assumes the independent variable is in units of :code:`nm` to simplify the code.
The dependent variable units can be specified using the :code:`dep_units` kwarg to :meth:`~attune.Tune.__init__`.

The :class:`~attune.Tune` object can be called as a function, which returns the linear interpolation of the independent to dependent variable mapping.
The units of the input and/or desired output can be specified using keyword arguments.


:class:`~attune.Tune` provides an :meth:`~attune.Tune.as_dict` method to allow for serialization.
:class:`~attune.Tune` also provides convenience attributes to access the limits of the tune: :attr:`~attune.Tune.ind_min` and :attr:`~attune.Tune.ind_max`.

.. code-block:: python

   tune = attune.Tune([400, 500, 600, 700], [0, 1, 4, 9], dep_units="mm")
   val = tune(555) # returns 2.65
   val = tune(555, dep_units="cm") # returns 0.265
   val = tune(20555, ind_units="wn") # returns 0.86499635


DiscreteTune
------------

A :class:`~attune.DiscreteTune` represents a discrete transform from a continuous independent variable to discrete string output dependent values.

Currently the :class:`~attune.DiscreteTune` class assumes the independent variable is in units of :code:`nm` to simplify the code.

The outputs are stored as a dictionary of output key string to 2-tuple of ranges (min, max), and a default value as fallback.
The dictionary is ordered, and the first valid range (inclusive of endpoints) is the value returned.
Notably, this  construction does limit each potential output to a single range, thus limiting (though not eliminating) the ability to have non-consecutive ranges which evaluate to the same output value.
You can, however, place higher priority (earlier) ranges inside of other ranges to allow for some cases of non-consecutive ranges, as well as using default to get a similar effect.

:class:`~attune.DiscreteTune` provides an :meth:`~attune.DiscreteTune.as_dict` method to allow for serialization.

.. code-block:: python
   
   dt = attune.DiscreteTune({"hi": (100, 200), "lo": (10, 20), "inner": (50, 60), "med": (20, 100)}, default="def")
   dt(5) == np.array("def")
   dt(15) == np.array("lo")
   dt(20) == np.array("lo")
   dt(30) == np.array("med")
   dt(55) == np.array("inner")
   dt(70) == np.array("med")
   dt(100) == np.array("hi")
   dt(150) == np.array("hi")
   dt(500) == np.array("def")



Arrangement
-----------

An :class:`~attune.Arrangment` provides a dict-like set of string names to :class:`~attune.Tune` and :class:`~attune.DiscreteTune` objects.
The tunes may represent either :class:`~attune.Setable` (the default) or an :class:`~attune.Arrangement` (when the :class:`~attune.Instrument` contains an :class:`~attune.Arrangement` of that name).
When it represents an :class:`~attune.Arrangement`, the :class:`~attune.Instrument` will recursively evaluate for all :class:`~attune.Setable` s.

All of the tunes must have the same independent units and must overlap (the former is easy since all tunes currently have :code:`nm` units).

:class:`~attune.Arrangement` provides an :meth:`~attune.Arrangement.as_dict` method to allow for serialization.

.. code-block:: python

   arr = attune.Arrangement("arr", {"continuous": tune, "discrete": dt})

Instrument
----------

An :class:`~attune.Instrument` is the top level representation of the system, the one which users most directly interact with.
An :class:`~attune.Instrument` provides a dict-like access to a set of :class:`~attune.Arrangement` s as well as a secondary dict of :class:`~attune.Setable` s.
Additionally, :class:`~attune.Instrument` provide a system of tracking history via :class:`~attune.Transition` object (See also :ref:`Transitions`).

Most commonly, :class:`~attune.Instrument` objects are called like functions to provide :class:`~attune.Setable` positions (as a :class:`~attune.Note`) for a particular independent value.
If the independent value is valid for only a single arrangement, then the arrangement does not need to be specified.
If, however, the independent value is valid for multiple arrangements, it must be specified.

The setables may be ignored if there is no need for defaults.

:class:`~attune.Instrument` provides both :meth:`~attune.Instrument.as_dict` and :meth:`~attune.Instrument.save` to allow for serialization.

.. code-block:: python

    tune = attune.Tune([0, 1], [0, 1])
    tune1 = attune.Tune([0.5, 1.5], [0, 1])
    first = attune.Arrangement("first", {"tune": tune})
    second = attune.Arrangement("second", {"tune": tune1})
    inst = attune.Instrument({"first": first, "second": second}, {"tune": attune.Setable("tune")})
    inst(0.25)["tune"] == 0.25
    inst(1.25)["tune"] == 0.75
    inst(0.75) # raises exception because it is valid for both arrangements
    inst(0.75, "first")["tune"] == 0.75
    inst(0.75, "second")["tune"] == 0.25

Loading from files
``````````````````

The native format for :class:`~attune.Instrument` is JSON encodable as provided by :meth:`~attune.Instrument.save`.
To read back an attune JSON file you can use :meth:`attune.open`.

.. code-block:: python

   instr = attune.open("instrument.json")


Alternatively, some formats such as Light Conversion TOPAS4 files can be parsed into attune :class:`~attune.Instrument` s.
TOPAS4 tuning curves are made up of multiple files which contain the information needed to recreate the :class:`~attune.Instrument`, so the method points to a folder which contains the files.

.. code-block:: python

   instr = attune.io.from_topas4("path/to/topas4/")

Note
----

A :class:`~attune.Note` is the type returned when an :class:`~attune.Instrument` is called as a function.
It is little more than a dict-like mapping of setable names to positions plus an indication of which arrangement was used to generate those positions.
A :class:`~attune.Note` also contains a dictionary of setables for convenience.
