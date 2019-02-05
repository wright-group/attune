"""Base Interpolator class and associated."""


class Interpolator:
    def __init__(self, setpoints, units, dependents):
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
        self.units = units
        self.dependents = dependents
        self._functions = None

    def get_dependent_positions(self, setpoint):
        """Get dependent positions.

        Parameters
        ----------
        setpoint : number
            Destination, in units.

        Returns
        -------
        list of numbers
            Dependent positions.
        """
        return [f(setpoint) for f in self.functions]
