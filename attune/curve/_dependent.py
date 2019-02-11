import WrightTools as wt

__all__ = ["Setpoints", "Dependent"]


class Variable(object):
    def __init__(self, positions, name, units=None):
        self.positions = positions
        self.name = name
        self.units = units

    def __getitem__(self, key):
        return self.positions[key]

    def convert(self, units):
        wt.units.convert(self.positions, self.units, units)
        self.units = units


class Setpoints(Variable):
    pass


class Dependent(Variable):
    """Container class for dependent arrays."""

    def __init__(self, positions, name, units=None, differential=False):
        """Create a ``Dependent`` object.

        Parameters
        ----------
        positions : 1D array
            Dependent positions.
        name : string
            Name.
        """
        super(Dependent, self).__init__(positions, name, units=units)
        self.interpolator = None
        self.differential = differential

    def __call__(self, val, units="same"):
        return self.interpolator(val, units)
