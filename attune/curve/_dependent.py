import WrightTools as wt

__all__ = ["Setpoints", "Dependent"]


class Variable(object):
    def __init__(self, positions, name, units=None):
        self.positions = positions
        self.name = name
        self.units = units

    def __getitem__(self, key):
        return self.positions[key]

    def __setitem__(self, key, value):
        self.positions[key] = value

    def __len__(self):
        return len(self.positions)

    def convert(self, units):
        self.positions = wt.units.convert(self.positions, self.units, units)
        self.units = units


class Setpoints(Variable):
    pass


class Dependent(Variable):
    """Container class for dependent arrays."""

    def __init__(self, positions, name, units=None, differential=False, index=None):
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
        self.index = index

    def __call__(self, val, units="same"):
        return self.interpolator(val, units)
