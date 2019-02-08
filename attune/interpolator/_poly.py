"""Polynomial interpolation."""


import numpy as np

from ._base import Interpolator


class Poly(Interpolator):
    def __init__(self, *args, **kwargs):
        self.deg = kwargs.pop("deg", 8)
        super(self, Interpolator).__init__(*args, **kwargs)

    @property
    def functions(self):
        if self._functions is not None:
            return self._functions
        self._functions = [
            np.polynomial.Polynomial.fit(self.setpoints, dependent.positions, self.deg)
            for dependent in self.dependents
        ]
        return self._functions
