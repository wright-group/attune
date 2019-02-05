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
            wt.kit.Spline(self.setpoints, dependent.positions, k=1, s=0)
            for dependent in self.dependents
        ]
        return self._functions
