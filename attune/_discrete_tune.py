__all__ = ["DiscreteTune"]

from typing import Dict, Tuple, Optional

import WrightTools as wt
import numpy as np


class DiscreteTune:
    def __init__(
        self, ranges: Dict[str, Tuple[float, float]], default: Optional[str] = None, **kwargs
    ):
        """A Tune which maps one set of inputs to associated output points.

        Currently all tunes are assumed to have "nm" as their independent units.

        Parameters
        ----------
        ranges: dict[str, tuple[float, float]]
            dictionary mapping the key (string identifier of a discrete position)
            to a 2-tuple of (min, max) for the range for which that identifier should be used.
            This dict is ordered, the first result with a matching range (inclusive of boundaries)
            will be the one returned when called.
        default: Optional[str]
            The result to return if no matching range is represented.
            Default is None

        Note: kwargs are provided to make the serialized dictionary with ind_units
        easy to initialize into a DiscreteTune object, but are currently ignored.
        """
        self._ind_units = "nm"
        self._ranges = {k: tuple(v) for k, v in ranges.items()}
        self._default = default

    def __repr__(self):
        return f"DiscreteTune({repr(self.ranges)}, {repr(self.default)})"

    def __call__(self, ind_value, *, ind_units=None):
        """Evaluate the DiscreteTune at specific independent value(s).

        Paramters
        ---------
        ind_val: float-like or ndarray
            The value or values at which to evaluate the DiscreteTune.
        ind_units: Optional[str]
            Units of the independent variable.  Default is "nm".

        Returns
        -------
        key: str or ndarray
            The string identifier for the independent value.
            For an array of ind_val, an array of identifiers is given.

        """
        if ind_units is not None and self._ind_units is not None:
            ind_value = wt.units.convert(ind_value, ind_units, self._ind_units)
        if isinstance(ind_value, np.ndarray):
            out = np.full(
                ind_value.shape,
                self.default,
                dtype=f"U{max([len(s) for s in self.ranges.keys()])}",
            )
            for key, (imin, imax) in self.ranges.items():
                out[(ind_value >= imin) & (ind_value <= imax)] = key
            return out
        else:
            for key, (imin, imax) in self.ranges.items():
                if imin <= ind_value <= imax:
                    return key
            return self.default

    def __eq__(self, other):
        return self.ranges == other.ranges and self.default == other.default

    def as_dict(self):
        """Serialize this Tune as a python dictionary."""
        out = {}
        out["ranges"] = self.ranges
        out["ind_units"] = self.ind_units
        out["default"] = self.default
        return out

    @property
    def ranges(self):
        """The ranges for discrete setpoints."""
        return self._ranges

    @property
    def ind_units(self):
        """The units of the independent (input) values."""
        return self._ind_units

    @property
    def default(self):
        """The value returned if no supplied range applies."""
        return self._default
