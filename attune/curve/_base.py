"""Base curve behavior."""


import re
import os
import pathlib
import copy
import shutil
import collections

import numpy as np

import scipy

import matplotlib.pyplot as plt
import matplotlib.gridspec as grd

import WrightTools as wt
import tidy_headers
from ..interpolator import Linear, builtins
from ._dependent import Dependent


__all__ = ["Curve"]


# --- curve class ---------------------------------------------------------------------------------


class Curve:
    """Central object-type for all OPA tuning curves."""

    def __init__(
        self,
        setpoints,
        units,
        dependents,
        name,
        interaction,
        kind,
        method=Linear,
        subcurve=None,
        source_setpoints=None,
        fmt=None,
        setpoint_name="Setpoint",
    ):
        """Create a ``Curve`` object.

        Parameters
        ----------
        setpoints : array
            The setpoint destinations for the curve.
        units : str
            The setpoint units.
        dependents : list of Dependent objects
            Dependent positions for each setpoint.
        name : str
            Name of curve.
        kind : string
            The kind of curve (for saving).
        method : interpolation class
            The interpolation method to use.
        """
        # version
        from .. import __version__

        self.__version__ = __version__
        # inherit
        self.setpoints = np.array(setpoints)  # needs to be array for some interpolation methods
        self.units = units
        self.dependents = dependents
        self.name = name
        self.kind = kind
        self.subcurve = subcurve
        self.source_setpoints = source_setpoints
        self.interaction = interaction
        # set dependents as attributes of self
        for obj in self.dependents:
            setattr(self, obj.name, obj)
        # initialize function object
        self.method = builtins.get(method, method)
        if fmt is None:
            fmt = ["%.2f"] + ["%.5f"] * len(self.dependents)
        self.fmt = fmt
        self.setpoint_name = setpoint_name
        self.interpolate()

    def __repr__(self):
        # when you inspect the object
        outs = []
        outs.append("WrightTools.tuning.curve.Curve object at " + str(id(self)))
        outs.append("  name: " + self.name)
        outs.append("  interaction: " + self.interaction)
        outs.append(
            "  range: {0} - {1} ({2})".format(
                self.setpoints.min(), self.setpoints.max(), self.units
            )
        )
        outs.append("  number: " + str(len(self.setpoints)))
        return "\n".join(outs)

    def __getitem__(self, key):
        return self.dependents[wt.kit.get_index(self.dependent_names, key)]

    def __call__(self, value, units=None, full=True):
        return self.get_dependent_positions(value, units, full=full)

    @property
    def dependent_names(self, full=True):
        """Get dependent names.

        Parameters
        ----------
        full : boolean (optional)
            Toggle inclusion of dependent names from subcurve.

        Returns
        -------
        list of strings
            Dependent names.
        """
        if self.subcurve and full:
            subcurve_dependent_names = self.subcurve.dependent_names
        else:
            subcurve_dependent_names = []
        return subcurve_dependent_names + [m.name for m in self.dependents]

    @property
    def dependent_units(self, full=True):
        """Get dependent names.

        Parameters
        ----------
        full : boolean (optional)
            Toggle inclusion of dependent names from subcurve.

        Returns
        -------
        list of strings
            Dependent names.
        """
        if self.subcurve and full:
            subcurve_dependent_units = self.subcurve.dependent_units
        else:
            subcurve_dependent_units = []
        return subcurve_dependent_units + [m.units for m in self.dependents]

    def coerce_dependents(self):
        """Coerce the dependent positions to lie exactly along the interpolation positions.

        Can be thought of as 'smoothing' the curve.
        """
        self.map_setpoints(self.setpoints, units="same")

    def convert(self, units, *, convert_dependents=False):
        """Convert the setpoints to new units.

        Parameters
        ----------
        units : str
            The destination units.
        """
        self.setpoints = wt.units.converter(self.setpoints, self.units, units)
        if self.subcurve:
            positions = self.source_setpoints.positions
            self.source_setpoints.positions = wt.units.converter(positions, self.units, units)
        self.units = units
        if convert_dependents:
            for d in self.dependents:
                if wt.units.is_valed_conversion(d.units, units):
                    d.convert(units)

        self.interpolate()

    def copy(self):
        """Copy the curve object.

        Returns
        -------
        curve
            A deep copy of the curve object.
        """
        return copy.deepcopy(self)

    def get_setpoint(self, dependent_positions, units="same"):
        """Get the setpoint given a set of dependent positions.

        Parameters
        ----------
        dependent_positions : array
            The dependent positions.
        units : str (optional)
            The units of the returned setpoint.

        Returns
        -------
        float
            The current setpoint.
        """
        setpoints = []
        for dependent_index, dependent_position in enumerate(dependent_positions):
            setpoint = self.interpolator.get_setpoint(dependent_index, dependent_position)
            setpoints.append(setpoint)
        # TODO: decide how to handle case of disagreement between setpoints
        return setpoints[0]

    def get_limits(self, units="same"):
        """Get the edges of the curve.

        Parameters
        ----------
        units : str (optional)
            The units to return. Default is same.

        Returns
        -------
        list of floats
            [min, max] in given units
        """
        if units == "same":
            return [self.setpoints.min(), self.setpoints.max()]
        else:
            units_setpoints = wt.units.converter(self.setpoints, self.units, units)
            return [units_setpoints.min(), units_setpoints.max()]

    def get_dependent_positions(self, setpoint, units="same", full=True):
        """Get the dependent positions for a destination setpoint.

        Parameters
        ----------
        setpoint : number
            The destination setpoint. May be 1D array.
        units : str (optional)
            The units of the input setpoint.

        Returns
        -------
        np.ndarray
            The dependent positions. If setpoint is an array the output shape will
            be (dependents, setpoints).
        """
        # get setpoint in units
        if units == "same":
            pass
        else:
            setpoint = wt.units.converter(setpoint, units, self.units)
        # setpoint must be array

        if _is_numeric(setpoint):
            setpoint = np.array([setpoint])
        # evaluate
        if full and self.subcurve:
            out = []
            for c in setpoint:
                source_setpoint = np.array(
                    self.source_setpoint_interpolator.get_dependent_positions(c)
                )
                source_dependent_positions = np.array(
                    self.subcurve.get_dependent_positions(
                        source_setpoint, units=self.units, full=True
                    )
                ).squeeze()
                own_dependent_positions = np.array(
                    self.interpolator.get_dependent_positions(c)
                ).flatten()
                out.append(np.hstack((source_dependent_positions, own_dependent_positions)))
            out = np.array(out)
            return out.squeeze().T
        else:
            out = np.array([self.interpolator.get_dependent_positions(c) for c in setpoint])
            return out.T

    def get_source_setpoint(self, setpoint, units="same"):
        """Get setpoint of source curve.

        Parameters
        ----------
        setpoint : number or 1D array
            Setpoint(s).
        units : string (optional)
            Units. Default is same.

        Returns
        -------
        number or 1D array
            Source setpoint(s).
        """
        if not self.subcurve:
            return None
        # setpoint must be array
        if _is_numeric(setpoint):
            setpoint = np.array([setpoint])
        # get setpoint in units
        if units == "same":
            pass
        else:
            setpoint = wt.units.converter(setpoint, units, self.units)
        # evaluate
        return np.array(
            [self.source_setpoint_interpolator.get_dependent_positions(c) for c in setpoint]
        )

    def interpolate(self, interpolate_subcurve=True):
        """Generate the interploator object.

        Parameters
        ----------
        interpolate_subcurve : boolean (optional)
            Toggle interpolation of subcurve. Default is True.
        """
        self.interpolator = self.method(self.setpoints, self.units, self.dependents)
        if self.subcurve and interpolate_subcurve:
            self.source_setpoint_interpolator = self.method(
                self.setpoints, self.units, [self.source_setpoints]
            )

    def map_setpoints(self, setpoints, units="same"):
        """Map the curve onto new tune points using the curve's own interpolation method.

        Parameters
        ----------
        setpoints : int or array
            The number of new points (between current limits) or the new points
            themselves.
        units : str (optional.)
            The input units if given as array. Default is same. Units of curve
            object are not changed by map_setpoints.
        """
        # get new setpoints in input units
        if isinstance(setpoints, int):
            limits = self.get_limits(units)
            new_setpoints = np.linspace(limits[0], limits[1], setpoints)
        else:
            new_setpoints = setpoints
        # convert new setpoints to local units
        if units == "same":
            units = self.units
        new_setpoints = np.sort(wt.units.converter(new_setpoints, units, self.units))
        # ensure that dependent interpolators agree with current dependent positions
        self.interpolate(interpolate_subcurve=True)
        # map own dependents
        new_dependents = []
        for dependent_index, dependent in enumerate(self.dependents):
            positions = self.get_dependent_positions(new_setpoints, full=False)[dependent_index]
            new_dependent = Dependent(positions, dependent.name)  # new dependent objects
            new_dependents.append(new_dependent)
        # map source setpoints, subcurves
        if self.subcurve:
            new_source_setpoints = np.array(
                self.source_setpoint_interpolator.get_dependent_positions(new_setpoints)
            ).squeeze()
            self.subcurve.map_setpoints(new_source_setpoints, units=self.units)
            self.source_setpoints.positions = new_source_setpoints
        # finish
        self.setpoints = new_setpoints
        self.dependents = new_dependents
        for obj in self.dependents:
            setattr(self, obj.name, obj)
        self.interpolate(interpolate_subcurve=True)

    def offset_by(self, dependent, amount):
        """Offset a dependent by some ammount.

        Parameters
        ----------
        dependent : number or str
            The dependent index or name.
        amount : number
            The offset.

        See Also
        --------
        offset_to
        """
        # get dependent index
        dependent_index = wt.kit.get_index(self.dependent_names, dependent)

        # offset
        self.dependents[dependent_index].positions += amount
        self.interpolate()

    def offset_to(self, dependent, destination, setpoint, setpoint_units="same"):
        """Offset a dependent such that it evaluates to `destination` at `setpoint`.

        Parameters
        ----------
        dependent : number or str
            The dependent index or name.
        amount : number
            The dependent position at setpoint after offseting.
        setpoint : number
            The setpoint at-which to set the dependent to amount.
        setpoint_units : str (optional)
            The setpoint units. Default is same.

        See Also
        --------
        offset_by
        """
        # get dependent index
        dependent_index = wt.kit.get_index(self.dependent_names, dependent)
        # get offset
        current_positions = self.get_dependent_positions(setpoint, setpoint_units, full=False)
        offset = destination - current_positions[dependent_index]
        # apply using offset_by
        self.offset_by(dependent, offset)

    def plot(self, autosave=False, save_path="", title=None):
        """Plot the curve."""
        # count number of subcurves
        subcurve_count = 0
        total_dependent_count = len(self.dependents)
        current_curve = self
        all_curves = [self]
        while current_curve.subcurve:
            subcurve_count += 1
            total_dependent_count += len(current_curve.subcurve.dependents)
            current_curve = current_curve.subcurve
            all_curves.append(current_curve)
        all_curves = all_curves[::-1]
        # prepare figure
        num_subplots = total_dependent_count + subcurve_count
        fig = plt.figure(figsize=(8, 2 * num_subplots))
        axs = grd.GridSpec(num_subplots, 1, hspace=0)
        # assign subplot indicies
        ax_index = 0
        ax_dictionary = {}
        lowest_ax_dictionary = {}
        for curve_index, curve in enumerate(all_curves):
            for dependent_index, dependent in enumerate(curve.dependents):
                ax_dictionary[dependent.name] = axs[ax_index]
                lowest_ax_dictionary[curve.interaction] = axs[ax_index]
                ax_index += 1
            if curve_index != len(all_curves):
                ax_index += 1
        # add scatter
        for dependent_index, dependent_name in enumerate(self.dependent_names):
            ax = plt.subplot(ax_dictionary[dependent_name])
            xi = self.setpoints
            yi = self.get_dependent_positions(xi)[dependent_index]
            ax.scatter(xi, yi, c="k")
            ax.set_ylabel(dependent_name)
            plt.xticks(self.setpoints)
            plt.setp(ax.get_xticklabels(), visible=False)
        # add lines
        for dependent_index, dependent_name in enumerate(self.dependent_names):
            ax = plt.subplot(ax_dictionary[dependent_name])
            limits = curve.get_limits()
            xi = np.linspace(limits[0], limits[1], 1000)
            yi = self.get_dependent_positions(xi)[dependent_index].flatten()
            ax.plot(xi, yi, c="k")
        # get appropriate source setpoints
        source_setpoint_arrs = {}
        for curve_index, curve in enumerate(all_curves):
            current_curve = self
            current_arr = self.setpoints
            for _ in range(len(all_curves) - curve_index - 1):
                current_arr = current_curve.get_source_setpoint(current_arr)
                current_curve = current_curve.subcurve
            source_setpoint_arrs[current_curve.interaction] = np.array(current_arr).flatten()
        # add labels
        for curve in all_curves:
            ax = plt.subplot(lowest_ax_dictionary[curve.interaction])
            plt.setp(ax.get_xticklabels(), visible=True)
            ax.set_xlabel(curve.interaction + " setpoint ({})".format(curve.units))
            xtick_positions = self.setpoints
            xtick_labels = [str(np.around(x, 1)) for x in source_setpoint_arrs[curve.interaction]]
            plt.xticks(xtick_positions, xtick_labels, rotation=45)
        # formatting details
        xmin = self.setpoints.min() - np.abs(self.setpoints[0] - self.setpoints[1])
        xmax = self.setpoints.max() + np.abs(self.setpoints[0] - self.setpoints[1])
        for ax in ax_dictionary.values():
            ax = plt.subplot(ax)
            plt.xlim(xmin, xmax)
            plt.grid()
            ax.get_yaxis().get_major_formatter().set_useOffset(False)
            yticks = ax.yaxis.get_major_ticks()
            yticks[0].label1.set_visible(False)
            yticks[-1].label1.set_visible(False)
        # title
        if title is None:
            title = self.name
        plt.suptitle(title)
        # save
        if autosave:
            if save_path[-3:] != "png":
                image_path = save_path + self.name + ".png"
            else:
                image_path = save_path
            plt.savefig(image_path, transparent=True, dpi=300)
            plt.close(fig)

    @classmethod
    def read(cls, filepath, subcurve=None):
        filepath = pathlib.Path(filepath)
        headers = tidy_headers.read(filepath)
        arr = np.genfromtxt(filepath).T
        setpoints = arr[0]
        names = headers["name"]
        units = headers.get("units", [None] * len(names))
        dependents = []
        for a, n, u in zip(arr[1:], names[1:], units[1:]):
            dependents.append(Dependent(a, n, units=u))
        kwargs = {}
        kwargs["interaction"] = headers["interaction"]
        kwargs["kind"] = headers.get("kind", None)
        kwargs["method"] = builtins.get(headers.get("method", ""), Linear)
        kwargs["name"] = headers.get("curve name", filepath.stem)
        kwargs["fmt"] = headers.get("fmt", ["%.2f"] + ["%.5f"] * len(dependents))
        setpoint_name = names[0]
        # Handle pre-attune release curves
        if units[0] is None:
            try:
                match = re.match(r"(.*)\((.*)\).*", names[0])
                setpoint_name = match[1].strip()
                units[0] = match[2].strip()
            except TypeError:
                pass  # No units
        kwargs["setpoint_name"] = setpoint_name
        if subcurve is not None:
            kwargs["subcurve"] = subcurve
            kwargs["source_setpoints"] = Dependent(setpoints, setpoint_name, units=units[0])
        # finish
        curve = cls(setpoints, units[0], dependents, **kwargs)
        return curve

    def save(self, save_directory=None, plot=True, verbose=True, full=False):
        """Save the curve.

        Parameters
        ----------
        save_directory : str (optional)
            The save directory. If not supplied, current working directory is
            used.
        plot : bool (optional)
            Toggle saving plot along with curve. Default is True.
        verbose : bool (optional)
            Toggle talkback. Default is True.
        full : bool (optional)
            Include all files (if curve is stored in multiple files)

        Returns
        -------
        str
            The filepath of the saved curve.
        """
        # get save directory
        if save_directory is None:
            save_directory = pathlib.Path()
        else:
            save_directory = pathlib.Path(save_directory)
        # array
        out_arr = np.zeros([len(self.dependents) + 1, len(self.setpoints)])
        out_arr[0] = self.setpoints
        out_arr[1:] = np.array([dependent.positions for dependent in self.dependents])
        # filename
        timestamp = wt.kit.TimeStamp()
        out_name = self.name.split("-")[0] + "- " + timestamp.path
        out_path = (save_directory / out_name).with_suffix(".curve")
        # save
        headers = {}
        headers["curve name"] = self.name
        headers["file created"] = timestamp.RFC3339
        headers["interaction"] = self.interaction
        headers["kind"] = self.kind
        headers["method"] = self.method.__name__
        headers["units"] = [self.setpoint_units] + self.dependent_units
        headers["name"] = [f"{self.setpoint_name}"] + self.dependent_names
        tidy_headers.write(out_path, headers)
        with open(out_path, "at") as f:
            np.savetxt(f, out_arr.T, fmt=self.fmt, delimiter="\t")
        # save subcurve
        if self.subcurve:
            self.subcurve.save(save_directory=save_directory)
        # plot
        if plot:
            image_path = os.path.splitext(out_path)[0] + ".png"
            title = os.path.basename(os.path.splitext(out_path)[0])
            self.plot(autosave=True, save_path=image_path, title=title)
        # finish
        if verbose:
            print("curve saved at", out_path)
        return out_path


def _is_numeric(obj):
    attrs = ["__add__", "__sub__", "__mul__", "__pow__"]
    return all([hasattr(obj, attr) for attr in attrs] + [not hasattr(obj, "__len__")])
