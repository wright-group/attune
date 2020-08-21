__all__ = ["Tune"]


import WrightTools as wt
import numpy as np
import scipy.interpolate


class Tune:
    def __init__(self, independent, dependent, *, dep_units=None, **kwargs):
        independent = np.asarray(independent)
        dependent = np.asarray(dependent)
        assert independent.size == dependent.size
        assert independent.ndim == dependent.ndim == 1
        self._independent = independent
        self._ind_max = max(self._independent)
        self._ind_min = min(self._independent)
        self._ind_units = "nm"
        self._dep_units = dep_units
        self._interp = scipy.interpolate.interp1d(
            independent, dependent, fill_value="extrapolate"
        )

    def __call__(self, ind_value, *, ind_units=None, dep_units=None):
        if ind_units is not None and self._ind_units is not None:
            wt.units.convert(ind_value, ind_units, self._ind_units)
        ret = self._interp(ind_value)
        if dep_units is not None and self._dep_units is not None:
            ret = wt.units.convert(ret, self._dep_units, dep_units)
        return ret

    def __eq__(self, other):
        if not np.allclose(self.independent, other.independent):
            return False
        if not np.allclose(self(self.independent), other(other.independent)):
            return False
        return self.ind_units == other.ind_units and self.dep_units == other.dep_units

    def as_dict(self):
        out = {}
        out["independent"] = [float(i) for i in self.independent]
        out["dependent"] = [float(self._interp(v)) for v in self._independent]
        out["ind_units"] = self.ind_units
        out["dep_units"] = self.dep_units
        return out

    @property
    def independent(self):
        return self._independent

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
