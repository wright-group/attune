"""COSET."""


# --- import --------------------------------------------------------------------------------------


import pathlib

import numpy as np


import WrightTools as wt
import tidy_headers

from ._base import Curve
from ._dependent import Dependent
from ..interpolator import Spline


# --- coset class ---------------------------------------------------------------------------------


class CoSet(Curve):
    """Interpolated correspondance between axes."""

    def __init__(
        self,
        control_name,
        control_units,
        control_points,
        offset_name,
        offset_units,
        offset_points,
        name="coset",
    ):
        """Create a ``CoSet`` object.

        Parameters
        ----------
        control_name : string
            Control name.
        control_units : string
            Control units.
        control_points : 1D array
            Control points.
        offset_name : string
            Offset name.
        offset_units : string
            Offset units.
        offset_points : 1D array
            Offset points.
        name : string (optional)
            Name. Default is 'coset'.
        """
        dependent = Dependent(offset_points, offset_name, units=offset_units)
        super(CoSet, self).__init__(
            control_points,
            control_units,
            [dependent],
            name,
            "coset",
            "coset",
            Spline,
            setpoint_name=control_name,
        )

    def __repr__(self):
        """Unambiguous representation."""
        # when you inspect the object
        outs = []
        outs.append("WrightTools.tuning.coset.CoSet object at " + str(id(self)))
        outs.append("  name: " + self.name)
        outs.append("  control: " + self.control_name)
        outs.append("  offset: " + self.offset_name)
        return "\n".join(outs)

    def save(self, save_directory=None, plot=True, verbose=True):
        """Save to a .coset file.

        Parameters
        ----------
        save_directory : string (optional).
            Save directory. Default is None.
        plot : boolean (optional)
            Toggle creation of plot. Default is True.
        verbose : boolean (optional)
            Toggle talkback. Default is True.
        """
        if save_directory is None:
            save_directory = pathlib.Path.cwd()
        time_stamp = wt.kit.TimeStamp()
        file_name = " - ".join([self.name, time_stamp.path]) + ".coset"
        file_path = pathlib.Path(save_directory) / file_name
        headers = {}
        headers["control"] = self.setpoint_name
        headers["control units"] = self.units
        headers["offset"] = self[0].name
        headers["offset units"] = self[0].units
        tidy_headers.write(file_path, headers)
        X = np.vstack([self.setpoints, self[0][:]]).T
        with open(file_path, "ab") as f:
            np.savetxt(f, X, fmt=str("%8.6f"), delimiter="\t")
        if plot:
            image_path = file_path.with_suffix(".png")
            self.plot(autosave=True, save_path=image_path)
        if verbose:
            print("coset saved at {}".format(file_path))

    @classmethod
    def read(cls, path):
        """Create a coset object from file.

        Parameters
        ----------
        path : string
            Filepath.

        Returns
        -------
        WrightTools.tuning.coset.Coset
        """
        # get raw information from file
        path = pathlib.Path(path)
        headers = tidy_headers.read(path)
        arr = np.genfromtxt(path).T
        name = path.name.split(" - ")[0]
        # construct coset object
        control_name = headers["control"]
        control_units = headers["control units"]
        control_points = arr[0]
        offset_name = headers["offset"]
        offset_units = headers["offset units"]
        offset_points = arr[1]
        coset = cls(
            control_name,
            control_units,
            control_points,
            offset_name,
            offset_units,
            offset_points,
            name=name,
        )
        # finish
        return coset
