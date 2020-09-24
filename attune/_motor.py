__all__ = ["Motor"]


class Motor(object):
    def __init__(self, name, **kwargs):
        self.name = name

    def __repr__(self):
        return f"Motor({repr(self.name)})"

    def __eq__(self, other):
        return self.name == other.name

    def as_dict(self):
        out = {}
        out["name"] = self.name
        return out
