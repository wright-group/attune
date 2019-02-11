"""Spline interpolation."""


import WrightTools as wt
from ._base import Interpolator


class Spline(Interpolator):
    @property
    def function(self):
        if self._function is not None:
            return self._function
        self._function = wt.kit.Spline(self.setpoints[:], self.dependent[:], k=3, s=1000)
        return self._function
