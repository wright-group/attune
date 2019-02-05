"""Base Interpolator class and associated."""


class Interpolator:
    def __init__(self, colors, units, motors):
        """Create an Interoplator object.

        Parameters
        ----------
        colors : 1D array
            Setpoints.
        units : string
            Units.
        motors : list of WrightTools.tuning.curve.Motor
            Motors.
        """
        self.colors = colors
        self.units = units
        self.motors = motors
        self._functions = None

    def get_motor_positions(self, color):
        """Get motor positions.

        Parameters
        ----------
        color : number
            Destination, in units.

        Returns
        -------
        list of numbers
            Motor positions.
        """
        return [f(color) for f in self.functions]
