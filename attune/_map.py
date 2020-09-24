__all__ = ["map_ind_points", "map_ind_limits"]

import copy

import numpy as np

from ._transition import Transition
from ._tune import Tune


def map_ind_points(instrument, arrangement, tune, setpoints, units=None):
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
    to_replace = instrument[arrangement][tune]
    points = np.linspace(min, max, len(to_replace))
    instr = map_ind_points(instrument, arrangement, tune, points, units)
    md = {"arrangement": arrangement, "tune": tune, "min": min, "max": max, "units": units}
    instr._transition = Transition("map_ind_limits", instrument, metadata=md)
    return instr
