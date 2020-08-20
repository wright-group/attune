__all__ = ["Arrangement"]


from typing import Dict
from ._tune import Tune


class Arrangement:
    def __init__(self, name, tunes: Dict["str", Tune]):
        self._name = name
        self._tunes = tunes
        self._ind_units = "nm"
        self._ind_max = min([t.ind_max for t in self._tunes.values()])
        self._ind_min = max([t.ind_min for t in self._tunes.values()])

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.tunes != other.tunes:
            return False
        return True

    def as_dict(self):
        out = {}
        out["name"] = self._name
        out["tunes"] = {k: v.as_dict() for k, v in self._tunes.items()}
        return out

    @property
    def ind_max(self):
        return self._ind_max

    @property
    def ind_min(self):
        return self._ind_min

    @property
    def name(self):
        return self._name

    @property
    def tunes(self):
        return self._tunes
