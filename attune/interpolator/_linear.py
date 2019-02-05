"""Linear interpolation."""


import WrightTools as wt

from ._base import Interpolator


class Linear(Interpolator):
    """Linear interpolation."""

    @property
    def functions(self):
        if self._functions is not None:
            return self._functions
        self._functions = [
            wt.kit.Spline(self.setpoints, motor.positions, k=1, s=0) for motor in self.motors
        ]
        return self._functions
