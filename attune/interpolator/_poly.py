"""Polynomial interpolation."""


import numpy as np


class Poly:
    def __init__(self, *args, **kwargs):
        self.deg = kwargs.pop("deg", 8)
        super(self, Interpolator).__init__(*args, **kwargs)

    @property
    def functions(self):
        if self._functions is not None:
            return self._functions
        self._functions = [
            np.polynomial.Polynomial.fit(self.setpoints, motor.positions, self.deg)
            for motor in self.motors
        ]
        return self._functions
