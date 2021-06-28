__all__ = ["Setable"]

from typing import Union, Optional


class Setable(object):
    def __init__(self, name: str, default: Optional[Union[str, float]] = None, **kwargs):
        """Setable object representation.

        Parameters
        ----------
        name: str
            The key for this setable
        """
        self.name = name
        self.default = default

    def __repr__(self):
        return f"Setable({repr(self.name)}, {repr(self.default)})"

    def __eq__(self, other):
        return self.name == other.name and self.default == other.default

    def as_dict(self):
        """Representation as a JSON encodable dictionary."""
        out = {}
        out["name"] = self.name
        out["default"] = self.default
        return out
