__all__ = ["Setable"]


class Setable(object):
    def __init__(self, name: str, **kwargs):
        """Setable object representation.

        Parameters
        ----------
        name: str
            The key for this setable
        """
        self.name = name

    def __repr__(self):
        return f"Setable({repr(self.name)})"

    def __eq__(self, other):
        return self.name == other.name

    def as_dict(self):
        """Representation as a JSON encodable dictionary."""
        out = {}
        out["name"] = self.name
        return out
