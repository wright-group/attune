import WrightTools as wt

__all__ = ["Dependent"]


class Dependent:
    """Container class for dependent arrays."""

    def __init__(self, positions, name, units=None):
        """Create a ``Dependent`` object.

        Parameters
        ----------
        positions : 1D array
            Dependent positions.
        name : string
            Name.
        """
        self.positions = positions
        self.name = name
        self.units = units

    def __getitem__(self, key):
        return self.positions[key]

    def convert(units):
        wt.units.convert(self.positions, self.units, units)
        self.units = units
