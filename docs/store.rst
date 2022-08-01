The Attune Store
================

The Attune Store provides a timestamped history of saved instrument JSON files.

Saving an instrument
--------------------

An :class:`~attune.Instrument` can be saved to the Attune Store by using :meth:`attune.store`.
In order to use store, the instrument must have a name.

.. code-block:: python

   attune.store(instr)


If transitions have been applied in memory, the whole chain will be stored with a single call.


Listing available instruments
-----------------------------

A list of available instrument histories can be obtained using :meth:`attune.catalog`.

.. code-block:: python

   attune.catalog()

By default, this provides a simple list of string names of instruments.

If you pass the argument :code:`full` as :code:`True`, then :meth:`attune.catalog` will instead return a dictionary of names to loaded :class:`~attune.Instrument` objects.

.. code-block:: python

   attune.catalog(True)

Retrieving an instrument
------------------------

An individual :class:`~attune.Instrument` can be retrieved using :meth:`attune.load`, given its name.

.. code-block:: python

   attune.load("instr")

If you wish to select the instrument which was active at some time in the past, you can pass either a :class:`~datetime.datetime` object or a date string.
If passed as a string, either a timestamp such as an ISO8601 format or certain phrasings of natural language can be passed.
In general phrasing as "<X> <units> ago" is likely to yield good results.


Similarly if you want to find the *next* instrument object from a certain date, you can pass the date as well as set :code:`reverse` to False to set the search direction to forward.

.. code-block:: python

   from dateutil import tz
   import datetime
   attune.load("instr", datetime.datetime(2022, 7, 15, tz=tz.UTC)) # Load the instrument from midnight UTC on July 15, 2022
   attune.load("instr", "3 days ago") # Load using a relative and natural language time
   attune.load("instr", "3 days ago", False) # Load the next instrument created after "3 days ago"


Instrument history
------------------

Since the attune store retains a permanent history, we have methods to interact with that history beyond simply loading

restore
```````

:meth:`attune.restore` works exactly like :meth:`attune.load`, except instead of returning the instrument to use immediately, it returns the older instrument to the head (active) so that it will be retrieved with :meth:`attune.load` without additional arguments.
In doing so, it applies a :code:`restore` transition indicating the time passed in to restore it.
Restoring to the currently active instrument is a no-op and so the time argument is required.

.. code-block:: python

   attune.restore("instr", "1 week ago")
   instr = attune.load("instr")  # Now the same as it was 1 week prior


undo
````

:meth:`attune.undo` provides the instrument from prior to the latest transition.
If the transitions have occurred in memory (i.e. not stored to the Attune Store) then it simply provides the previous instrument object directly.
If instead the Instrument was loaded, it retrieves the instrument from 1 millisecond prior to the current instrument (the resolution of the Attune Store) and loads it from disk.

.. code-block:: python

   attune.undo(instr)
