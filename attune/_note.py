__all__ = ["Note"]


from typing import Dict, Union
from ._setable import Setable


class Note:
    def __init__(
        self,
        setables: Dict[str, Setable],
        setable_positions: Dict[str, Union[float, str]],
        arrangement_name: str,
    ):
        """A particular set of motor positions.

        Parameters
        ----------
        setables: Dict[str, Setable]
            The setables represented in the note
        setable_positions: Dict[str, Union[float, str]]
            Mapping of setable keys to positions
        arrangement_name: str
            The name of the arrangement used to make this note
        """
        self.setables: Dict[str, Setable] = setables
        self.setable_positions: Dict[str, Union[str, float]] = setable_positions
        self.arrangement_name: str = arrangement_name

    def __getitem__(self, k):
        return self.setable_positions[k]

    def __repr__(self):
        return f"Note({self.setables}, {self.setable_positions}, {repr(self.arrangement_name)})"

    def items(self):
        """Items in the Note."""
        return self.setable_positions.items()

    def keys(self):
        """Settable keys in the Note."""
        return self.setable_positions.keys()

    def values(self):
        """Settable values."""
        return self.setable_positions.values()
