"""Linear interpolation."""

from scipy.interpolate import interp1d

from ._base import Interpolator


class Linear(Interpolator):
    """Linear interpolation."""

    @property
    def function(self):
        if self._function is not None:
            return self._function
        self._function = interp1d(self.setpoints[:], self.dependent[:], fill_value="extrapolate")
        return self._function
