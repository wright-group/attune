import WrightTools as wt
import scipy.interpolate


class Tune:
    def __init__(self, independent, dependent, *, ind_units=None, dep_units=None):
        assert independent.size == dependent.size
        assert independent.ndim == dependent.ndim == 1
        self._independent = independent
        self._ind_units = ind_units
        self._interp = scipy.interpolate.interp1d(independent, dependent, fill_value="extrapolate")

    def __call__(self, ind_value, *, ind_units=None, dep_units=None):
        if ind_units is not None and self._ind_units is not None:
            wt.units.convert(ind_value, ind_units, self._ind_units)
        ret = self._interp(ind_value)
        if dep_units is not None and self._dep_units is not None:
            ret = wt.units.convert(ret, self._dep_units, dep_units)
        return ret

    @property
    def independent(self):
        return self._independent

    @property
    def ind_units(self):
        return self._ind_units

    @property
    def dep_units(self):
        return self._dep_units
