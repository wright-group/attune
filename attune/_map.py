__all__ = ["map_ind_points", "map_ind_limits"]

import copy
import WrightTools as wt
import numpy as np

from ._transition import Transition
from ._tune import Tune


def map_ind_points(instrument, arrangement, tune, setpoints, units=None):
    """Map the independent values of a tune onto new setpoints.

    Parameters
    ----------
    instrument: Instrument
        The instrument object to alter.
    arrangement: str
        The name of the arrangemnt to alter.
    tune: str
        The name of the tune to alter.
    setpoints: array-like
        The new setpoints to map the tune to.
    units: Optional[str]
        The units of the new setpoints, will be converted to the original units.
        If not given, original units are assumed.

    Returns
    -------
    Instrument
        The instrument with the tune remapped to new setpoints.
    """
    md = {"arrangement": arrangement, "tune": tune, "setpoints": setpoints, "units": units}
    to_replace = instrument[arrangement][tune]
    if units is not None:
        setpoints = wt.units.convert(setpoints, units, to_replace.ind_units)
    instr = copy.deepcopy(instrument)
    instr[arrangement]._tunes[tune] = Tune(
        setpoints, to_replace(setpoints), dep_units=to_replace.dep_units
    )
    instr._transition = Transition("map_ind_points", instrument, metadata=md)
    instr._load = None
    return instr


def map_ind_limits(instrument, arrangement, tune, min, max, units=None):
    """Map the independent values of a tune onto new limits.

    The resultant tune will have the same number of points as the original,
    evenly spaced between ``min`` and ``max``.

    Parameters
    ----------
    instrument: Instrument
        The instrument object to alter.
    arrangement: str
        The name of the arrangemnt to alter.
    tune: str
        The name of the tune to alter.
    min: float
        The new minimum setpoint.
    max: float
        The new maximum setpoint.
    units: Optional[str]
        The units of the new setpoints, will be converted to the original units.
        If not given, original units are assumed.

    Returns
    -------
    Instrument
        The instrument with the tune remapped to new setpoints.
    """
    to_replace = instrument[arrangement][tune]
    points = np.linspace(min, max, len(to_replace))
    instr = map_ind_points(instrument, arrangement, tune, points, units)
    md = {"arrangement": arrangement, "tune": tune, "min": min, "max": max, "units": units}
    instr._transition = Transition("map_ind_limits", instrument, metadata=md)
    return instr
