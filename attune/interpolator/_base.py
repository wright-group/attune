"""Base Interpolator class and associated."""


class Interpolator:
    def __init__(self, setpoints, units, motors):
        """Create an Interoplator object.

        Parameters
        ----------
        setpoints : 1D array
            Setpoints.
        units : string
            Units.
        motors : list of WrightTools.tuning.curve.Motor
            Motors.
        """
        self.setpoints = setpoints
        self.units = units
        self.motors = motors
        self._functions = None

    def get_motor_positions(self, setpoint):
        """Get motor positions.

        Parameters
        ----------
        setpoint : number
            Destination, in units.

        Returns
        -------
        list of numbers
            Motor positions.
        """
        return [f(setpoint) for f in self.functions]
