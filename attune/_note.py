__all__ = ["Note"]


from typing import Dict
from ._setable import Setable


class Note:
    def __init__(self, setables, setable_positions, arrangement_name, **kwargs):
        self.setables: Dict["str", Setable] = setables
        self.setable_positions: Dict["str", float] = setable_positions
        self.arrangement_name: str = arrangement_name
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getitem__(self, k):
        return self.setable_positions[k]

    def __repr__(self):
        return f"Note({self.setables}, {self.setable_positions}, {self.arrangement_name})"

    def items(self):
        return self.setable_positions.items()

    def keys(self):
        return self.setable_positions.keys()

    def values(self):
        return self.setable_positions.values()
