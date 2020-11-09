__all__ = ["Tune"]


import WrightTools as wt
import numpy as np
import scipy.interpolate


class Tune:
    def __init__(self, independent, dependent, *, dep_units=None, **kwargs):
        """A Tune which maps one set of inputs to associated output points.

        Currently all tunes are assumed to have "nm" as their independent array units.
        All mappings are linear interpolations

        Parameters
        ----------
        independent: 1D array-like
            The independent axis for input values to be mapped.
            Must be the same shape as dependent.
        dependent: 1D array-like
            The depending axis for the mapping.
            Must be the same shape as independent.
        dep_units: str (optional)
            Units for the dependent axis

        Note: kwargs are provided to make the serialized dictionary with ind_units
        easy to initialize into a Tune object, but are currently ignored.
        """
        independent = np.asarray(independent)
        dependent = np.asarray(dependent)
        assert independent.size == dependent.size
        assert independent.ndim == dependent.ndim == 1
        self._ind_max = max(independent)
        self._ind_min = min(independent)
        self._ind_units = "nm"
        self._dep_units = dep_units
        self._interp = scipy.interpolate.interp1d(independent, dependent, fill_value="extrapolate")

    def __repr__(self):
        if self.dep_units is None:
            return f"Tune({repr(self.independent)}, {repr(self.dependent)})"
        return f"Tune({repr(self.independent)}, {repr(self.dependent)}, dep_units={repr(self.dep_units)})"

    def __call__(self, ind_value, *, ind_units=None, dep_units=None):
        if ind_units is not None and self._ind_units is not None:
            wt.units.convert(ind_value, ind_units, self._ind_units)
        ret = self._interp(ind_value)
        if dep_units is not None and self._dep_units is not None:
            ret = wt.units.convert(ret, self._dep_units, dep_units)
        return ret

    def __len__(self):
        return len(self.independent)

    def __eq__(self, other):
        if not np.allclose(self.independent, other.independent):
            return False
        if not np.allclose(self(self.independent), other(other.independent)):
            return False
        return self.ind_units == other.ind_units and self.dep_units == other.dep_units

    def as_dict(self):
        """Serialize this Tune as a python dictionary."""
        out = {}
        out["independent"] = list(self.independent)
        out["dependent"] = list(self.dependent)
        out["ind_units"] = self.ind_units
        out["dep_units"] = self.dep_units
        return out

    @property
    def independent(self):
        return self._interp.x.astype(float)

    @property
    def dependent(self):
        return self._interp.y.astype(float)

    @property
    def ind_max(self):
        return self._ind_max

    @property
    def ind_min(self):
        return self._ind_min

    @property
    def ind_units(self):
        return self._ind_units

    @property
    def dep_units(self):
        return self._dep_units
