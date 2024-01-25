__all__ = ["Arrangement"]


from typing import Dict, Union

import numpy as np

from ._tune import Tune
from ._discrete_tune import DiscreteTune


def mktune(dict_):
    if "ranges" in dict_:
        return DiscreteTune(**dict_)
    return Tune(**dict_)


class Arrangement:
    def __init__(self, name: str, tunes: Dict[str, Union[DiscreteTune, Tune, dict]]):
        """Arrangement of several Tunes to form one cohesive set.

        Tunes may represent either motors or other arrangements, however
        semantic meaning is provided by the Instrument which contains the
        Arrangement, to the arrangement, they are all string keys mapped to tunes.

        All tunes *must* have the same independent units, and must overlap.

        Parameters
        ----------
        name: str
            A name for this Arrangement, used to identify this Arrangement
            from other Arrangements which may depend on this one.
        tunes: Dict[str, Tune]
            Mapping of names to Tune objects which compose the Arrangement
        """
        self._name: str = name
        self._tunes: Dict[str, Union[DiscreteTune, Tune]] = {
            k: mktune(v) if isinstance(v, dict) else v for k, v in tunes.items()
        }
        self._ind_units: str = "nm"

    def _print_tunes(self, prefix):
        for i, (name, tune) in enumerate(self.tunes.items()):
            if i + 1 == len(self.tunes):
                b = "└── "
            else:
                b = "├── "
            s = prefix + b + "{0}: {1}".format(name, tune._leaf)
            print(s)

    def __repr__(self):
        return f"Arrangement({repr(self.name)}, {repr(self.tunes)})"

    def __getitem__(self, key):
        return self.tunes[key]

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.tunes != other.tunes:
            return False
        return True

    @property
    def independent(self):
        """Returns a 1-dimensional numpy array with the set of all unique independent points.

        Points closer together than 1/1000th of the total dynamic range are considered identical.

        Only returns points within range of all tunes.
        """
        out = np.unique(
            np.concatenate([t.independent for t in self._tunes.values() if isinstance(t, Tune)], 0)
        )
        tol = 1e-3 * (self.ind_max - self.ind_min)
        diff = np.append(tol * 2, np.diff(out))
        out = out[diff > tol]
        out = out[out <= self.ind_max]
        out = out[out >= self.ind_min]
        return out

    def keys(self):
        """Return the names of the tunes in the arrangment."""
        return self.tunes.keys()

    def values(self):
        """Return the tunes in the arrangment."""
        return self.tunes.values()

    def items(self):
        """Return the names and tunes in the arrangment."""
        return self.tunes.items()

    def as_dict(self):
        """Dictionary representation of the Arrangement"""
        out = {}
        out["name"] = self._name
        out["tunes"] = {k: v.as_dict() for k, v in self._tunes.items()}
        return out

    @property
    def ind_max(self):
        """The maximum independant (input) value for this arrangement."""
        return min([t.ind_max for t in self._tunes.values() if isinstance(t, Tune)])

    @property
    def ind_min(self):
        """The minimum independant (input) value for this arrangement."""
        return max([t.ind_min for t in self._tunes.values() if isinstance(t, Tune)])

    @property
    def name(self):
        """The name of the arrangement."""
        return self._name

    @property
    def tunes(self):
        """The tunes in the arrangement."""
        return self._tunes
