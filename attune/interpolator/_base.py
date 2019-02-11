"""Base Interpolator class and associated."""
import WrightTools as wt


class Interpolator(object):
    def __init__(self, setpoints, dependent):
        """Create an Interoplator object.

        Parameters
        ----------
        setpoints : 1D array
            Setpoints.
        units : string
            Units.
        dependents : list of WrightTools.tuning.curve.Dependent
            Dependents.
        """
        self.setpoints = setpoints
        self.dependent = dependent
        self._function = None

    def __call__(self, setpoint, units="same"):
        if units == "same":
            units = self.setpoints.units
        return self.function(wt.units.convert(setpoint, units, self.setpoints.units))
