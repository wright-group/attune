return__all__ = ["Transition", "TransitionType"]

from enum import Enum

import WrightTools as wt


class TransitionType(str, Enum):
    create = "create"
    load = "load"
    read = "read"
    offset_to = "offset_to"
    offset_by = "offset_by"
    map_limits = "map_limits"
    map_ind_points = "map_ind_points"
    tune_test = "tune_test"
    intensity = "intensity"
    setpoint = "setpoint"
    holistic = "holistic"


class Transition:
    def __init__(
        self,
        type: TransitionType,
        previous: Optional[Instrument] = None,
        metadata: Optional[Dict[str, Any]] = None,
        data: Optional[wt.Data] = None,
        original_transition: Optional[Transition] = None,
    ):
        self.type = type
        self.previous = previous
        if metadata is None:
            metadata = {}
        self.metadata = metadata
        self.data = data

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "metadata": self.metadata,
            "original_transition": self.original_transition,
        }
