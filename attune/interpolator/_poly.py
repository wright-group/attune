"""Polynomial interpolation."""


import numpy as np

from ._base import Interpolator


class Poly(Interpolator):
    def __init__(self, *args, **kwargs):
        self.deg = kwargs.pop("deg", 8)
        super(self, Interpolator).__init__(*args, **kwargs)

    @property
    def function(self):
        if self._function is not None:
            return self._function
        self._function = np.polynomial.Polynomial.fit(
            self.setpoints[:], self.dependent[:], self.deg
        )
        return self._function
