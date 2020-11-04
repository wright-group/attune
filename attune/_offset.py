__all__ = ["offset_by", "offset_to"]

import copy

from ._transition import Transition
from ._tune import Tune


def offset_by(instrument, arrangement, tune, amount, amount_units=None):
    md = {
        "arrangement": arrangement,
        "tune": tune,
        "amount": amount,
        "amount_units": amount_units,
    }
    to_offset = instrument[arrangement][tune]
    if amount_units is not None:
        amount = wt.units.convert(amount, amount_units, to_offset.dep_units)
    instr = copy.deepcopy(instrument)
    instr[arrangement]._tunes[tune] = Tune(
        to_offset.independent,
        to_offset.dependent + amount,
        dep_units=to_offset.dep_units,
    )
    instr._transition = Transition("offset_by", instrument, metadata=md)
    instr._load = None
    return instr


def offset_to(
    instrument,
    arrangement,
    tune,
    destination,
    setpoint,
    destination_units=None,
    setpoint_units=None,
):
    to_offset = instrument[arrangement][tune]
    current = to_offset(setpoint, ind_units=setpoint_units, dep_units=destination_units)
    offset = destination - current
    instr = offset_by(instrument, arrangement, tune, offset)
    md = {
        "arrangement": arrangement,
        "tune": tune,
        "destination": destination,
        "setpoint": setpoint,
        "destination_units": destination_units,
        "setpoint_units": setpoint_units,
    }
    instr._transition = Transition("offset_to", instrument, metadata=md)
    return instr
