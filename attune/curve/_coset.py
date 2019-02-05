"""COSET."""


# --- import --------------------------------------------------------------------------------------


from __future__ import absolute_import, division, print_function, unicode_literals

import os
import copy
import collections

import numpy as np

import scipy

import WrightTools as wt
import tidy_headers

from ._base import Curve


# --- coset class ---------------------------------------------------------------------------------


class CoSet(Curve):
    """Interpolated correspondance between axes."""

    def __add__(self, coset):
        # TODO: proper checks and warnings...
        # copy
        other_copy = coset.__copy__()
        self_copy = self.__copy__()
        # coerce other to own units
        other_copy.convert_control_units(self.control_units)
        other_copy.convert_offset_units(self.offset_units)
        # find new control points
        other_limits = other_copy.get_limits()
        self_limits = self_copy.get_limits()
        min_limit = max(other_limits[0], self_limits[0])
        max_limit = min(other_limits[1], self_limits[1])
        num_points = max(other_copy.control_points.size, self_copy.control_points.size)
        new_control_points = np.linspace(min_limit, max_limit, num_points)
        # coerce to new control points
        other_copy.map_control_points(new_control_points)
        self_copy.map_control_points(new_control_points)
        # add
        self_copy.offset_points += other_copy.offset_points
        return self_copy

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
        self.control_name = control_name
        self.control_units = control_units
        self.control_points = control_points
        self.offset_name = offset_name
        self.offset_units = offset_units
        self.offset_points = offset_points
        self.name = name
        self.sort()
        self.interpolate()

    def __repr__(self):
        """Unambiguous representation."""
        # when you inspect the object
        outs = []
        outs.append("WrightTools.tuning.coset.CoSet object at " + str(id(self)))
        outs.append("  name: " + self.name)
        outs.append("  control: " + self.control_name)
        outs.append("  offset: " + self.offset_name)
        return "\n".join(outs)

    def coerce_offsets(self):
        """Coerce the offsets to lie exactly along the interpolation positions.

        Can be thought of as 'smoothing' the coset.
        """
        self.map_control_points(self.control_points, units="same")

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
            save_directory = os.getcwd()
        time_stamp = wt.kit.TimeStamp()
        file_name = " - ".join([self.name, time_stamp.path]) + ".coset"
        file_path = os.path.join(save_directory, file_name)
        headers = collections.OrderedDict()
        headers["control"] = self.control_name
        headers["control units"] = self.control_units
        headers["offset"] = self.offset_name
        headers["offset units"] = self.offset_units
        tidy_headers.write(file_path, headers)
        X = np.vstack([self.control_points, self.offset_points]).T
        with open(file_path, "ab") as f:
            np.savetxt(f, X, fmt=str("%8.6f"), delimiter="\t")
        if plot:
            image_path = file_path.replace(".coset", ".png")
            self.plot(autosave=True, save_path=image_path)
        if verbose:
            print("coset saved at {}".format(file_path))

    @classmethod
    def read(path):
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
        headers = tidy_headers.read_headers(path)
        arr = np.genfromtxt(path).T
        name = os.path.basename(path).split(" - ")[0]
        # construct coset object
        control_name = headers["control"]
        control_units = headers["control units"]
        control_points = arr[0]
        offset_name = headers["offset"]
        offset_units = headers["offset units"]
        offset_points = arr[1]
        coset = CoSet(
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
