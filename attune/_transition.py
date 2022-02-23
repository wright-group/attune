return__all__ = ["Transition", "TransitionType"]

from enum import Enum
from typing import Any, Optional, Dict, TYPE_CHECKING


if TYPE_CHECKING:
    import WrightTools as wt

    from ._instrument import Instrument


class TransitionType(str, Enum):
    create = "create"
    read = "read"
    restore = "restore"
    rename = "rename"
    offset_to = "offset_to"
    offset_by = "offset_by"
    map_limits = "map_limits"
    map_ind_points = "map_ind_points"
    tune_test = "tune_test"
    intensity = "intensity"
    setpoint = "setpoint"
    holistic = "holistic"
    update_merge = "update_merge"


class Transition:
    def __init__(
        self,
        type: TransitionType,
        previous: Optional["Instrument"] = None,
        metadata: Optional[Dict[str, Any]] = None,
        data: Optional["wt.Data"] = None,
    ):
        """Represent one processing step of an instrument.

        Parameters
        ----------
        type: TransitionType
            Indentity of the type of transition
        previous: Optional["Instrument"]
            The instrument which was modified in the transition.
        metadata: Optional[Dict[str, Any]]
            JSON serializable metadata associated with the transition.
        data: Optional["wt.Data"]
            A WrightTools Data object that was used to generate the transition.
        """
        self.type = type
        self.previous = previous
        if metadata is None:
            metadata = {}
        self.metadata = metadata
        self.data = data

    def __repr__(self):
        return f"Transition({repr(self.type)}, {repr(self.previous)}, {repr(self.metadata)})"

    def as_dict(self) -> Dict[str, Any]:
        """JSON serializable representation of the transition."""
        return {
            "type": self.type,
            "metadata": self.metadata,
        }
