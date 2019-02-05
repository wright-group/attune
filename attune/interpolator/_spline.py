"""Spline interpolation."""


import scipy


class Spline:
    @property
    def functions(self):
        if self._functions is not None:
            return self._functions
        self._functions = [
            scipy.interpolate.UnivariateSpline(colors, motor.positions, k=3, s=1000)
            for motor in motors
        ]
        return self._functions
