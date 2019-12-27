"""Base curve behavior."""


import re
import pathlib
import copy as copy_

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.gridspec as grd

import WrightTools as wt
import tidy_headers
from ..interpolator import Linear, builtins
from ._dependent import Setpoints, Dependent


__all__ = ["Curve"]


# --- curve class ---------------------------------------------------------------------------------


class Curve:
    """Central object-type for all OPA tuning curves."""

    def __init__(
        self,
        setpoints,
        dependents,
        name,
        interaction=None,
        kind="curve",
        method=Linear,
        subcurve=None,
        source_setpoints=None,
        fmt=None,
        **kwargs,
    ):
        """Create a ``Curve`` object.

        Parameters
        ----------
        setpoints : attune.Setpoints
            The setpoint destinations for the curve.
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
        self.setpoints = setpoints
        if isinstance(dependents, Dependent):
            dependents = [dependents]
        if isinstance(dependents, dict):
            self.dependents = dependents
        else:
            self.dependents = {d.name: d for d in dependents}
        self.name = name
        self.kind = kind
        self.subcurve = subcurve
        self.source_setpoints = source_setpoints
        self.interaction = interaction
        # set dependents as attributes of self
        for obj in self.dependents.values():
            if len(obj) != len(self.setpoints):
                raise ValueError("Dependents must be the same length as setpoints")
            setattr(self, obj.name, obj)
        # initialize function object
        self.method = builtins.get(method, method)
        if fmt is None:
            fmt = ["%.2f"] + ["%.5f"] * len(self.dependents)
        self.fmt = fmt
        self.interpolate()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __add__(self, other):
        # copy
        self_ = self.copy()
        other = other.copy()
        # coerce other to own units
        other.convert(self_.setpoints.units)
        # find new control points
        other_limits = other.get_limits()
        self_limits = self_.get_limits()
        min_limit = max(other_limits[0], self_limits[0])
        max_limit = min(other_limits[1], self_limits[1])
        if min_limit > max_limit:
            raise ValueError("Curves must overlap")
        num_points = max(other.setpoints[:].size, self_.setpoints[:].size)
        new_setpoints = np.linspace(min_limit, max_limit, num_points)
        # coerce to new control points
        other.map_setpoints(new_setpoints)
        self_.map_setpoints(new_setpoints)
        # add
        self_keys = set(self_.dependents.keys())
        other_keys = set(other.dependents.keys())

        for k in self_keys | other_keys:
            if k in self_keys and k in other_keys:
                if wt.units.is_valid_conversion(other[k].units, self[k].units):
                    other[k].convert(self[k].units)
                else:
                    raise ValueError(
                        f"Invalid unit conversion: {other[k].units} -> {self[k].units}"
                    )
                if self_[k].differential and other[k].differential:
                    self_[k][:] += other[k][:]
                elif self_[k].differential or other[k].differential:
                    self_[k][:] += other[k][:]
                    self_[k].differential = False
                else:
                    raise ValueError(f"Cannot add two Dependents which are both absolute: {k}")
            elif k in other_keys:
                self_.dependents[k] = copy_.deepcopy(other[k])

        self_.interpolate()
        return self_

    def __getitem__(self, key):
        if key in self.dependents:
            return self.dependents[key]
        return self.subcurve[key]

    def __setitem__(self, key, value):
        value = copy_.deepcopy(value)
        value.name = key
        if value.interpolator is not None:
            value.positions = value(self.setpoints[:], self.setpoints.units)
        elif len(value) != len(self.setpoints):
            raise ValueError(
                f"Incorrect number of points in dependent: {len(value)} for number of setpoints: {len(self.setpoints)}"
            )
        value.interpolator = self.method(self.setpoints, value)
        self.dependents[key] = value

    def __call__(self, value, units=None, full=True):
        return self.get_dependent_positions(value, units, full=full)

    @property
    def dependent_names(self):
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
        if self.subcurve:
            subcurve_dependent_names = self.subcurve.dependent_names
        else:
            subcurve_dependent_names = []
        return [m.name for m in self.dependents.values()] + subcurve_dependent_names

    @property
    def dependent_units(self):
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
        if self.subcurve:
            subcurve_dependent_units = self.subcurve.dependent_units
        else:
            subcurve_dependent_units = []
        return [m.units for m in self.dependents.values()] + subcurve_dependent_units

    def coerce_dependents(self):
        """Coerce the dependent positions to lie exactly along the interpolation positions.

        Can be thought of as 'smoothing' the curve.
        """
        self.map_setpoints(self.setpoints[:], units="same")

    def convert(self, units, *, convert_dependents=False):
        """Convert the setpoints to new units.

        Parameters
        ----------
        units : str
            The destination units.
        """
        self.setpoints.convert(units)
        if self.subcurve:
            if wt.units.is_valid_conversion(self.source_setpoints.units, units):
                self.source_setpoints.convert(units)
        if convert_dependents:
            for d in self.dependents:
                if wt.units.is_valid_conversion(d.units, units):
                    d.convert(units)

        self.interpolate()

    def copy(self):
        """Copy the curve object.

        Returns
        -------
        curve
            A deep copy of the curve object.
        """
        return copy_.deepcopy(self)

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
            return [self.setpoints[:].min(), self.setpoints[:].max()]
        else:
            units_setpoints = wt.units.convert(self.setpoints[:], self.setpoints.units, units)
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
        out = {}
        for k, v in self.dependents.items():
            out[k] = v(setpoint, units)
        if full and self.subcurve:
            out.update(
                self.subcurve(
                    self.source_setpoints(setpoint, units), self.source_setpoints.units, full
                )
            )
        return out

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
        return self.source_setpoints(setpoint, units)

    def interpolate(self, interpolate_subcurve=True):
        """Generate the interploator object.

        Parameters
        ----------
        interpolate_subcurve : boolean (optional)
            Toggle interpolation of subcurve. Default is True.
        """
        for d in self.dependents.values():
            d.interpolator = self.method(self.setpoints, d)
        if self.subcurve and interpolate_subcurve:
            self.source_setpoints.interpolator = self.method(self.setpoints, self.source_setpoints)

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
            units = self.setpoints.units
        new_setpoints = np.sort(wt.units.converter(new_setpoints, units, self.setpoints.units))
        # ensure that dependent interpolators agree with current dependent positions
        self.interpolate()
        # map own dependents
        new_dependents = {}
        for k, v in self.dependents.items():
            positions = v(new_setpoints)
            new_dependent = Dependent(
                positions, k, v.units, v.differential, v.index
            )  # new dependent objects
            new_dependents.update({k: new_dependent})
        # map source setpoints, subcurves
        if self.subcurve:
            new_source_setpoints = self.source_setpoints(new_setpoints)
            self.source_setpoints = Dependent(
                new_source_setpoints,
                self.source_setpoints.name,
                self.source_setpoints.units,
                index=self.source_setpoints.index,
            )
        # finish
        self.setpoints = Setpoints(new_setpoints, self.setpoints.name, self.setpoints.units)
        self.dependents = new_dependents
        for obj in self.dependents.values():
            setattr(self, obj.name, obj)
        self.interpolate()

    def sort(self):
        order = self.setpoints[:].argsort()
        self.setpoints[:] = self.setpoints[order]
        try:
            self.source_setpoints[:] = self.source_setpoints[order]
        except (AttributeError, TypeError):
            pass  # no subcurve setpoints
        for d in self.dependents.values():
            d[:] = d[order]
        self.interpolate()

    def offset_by(self, dependent, amount):
        """Offset a dependent by some ammount.

        Parameters
        ----------
        dependent : str
            The dependent name.
        amount : number
            The offset.

        See Also
        --------
        offset_to
        """
        # offset
        self.dependents[dependent].positions += amount
        self.interpolate()

    def offset_to(self, dependent, destination, setpoint, setpoint_units="same"):
        """Offset a dependent such that it evaluates to `destination` at `setpoint`.

        Parameters
        ----------
        dependent : str
            The dependent name.
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
        offset = destination - self[dependent](setpoint, setpoint_units)
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
            for dependent in curve.dependents:
                ax_dictionary[dependent] = axs[ax_index]
                lowest_ax_dictionary[curve.name] = axs[ax_index]
                ax_index += 1
            if curve_index != len(all_curves):
                ax_index += 1
        # add scatter
        for dependent in self.dependent_names:
            ax = plt.subplot(ax_dictionary[dependent])
            xi = self.setpoints[:]
            yi = self(xi)[dependent]
            ax.scatter(xi, yi, c="k")
            limits = curve.get_limits()
            xi = np.linspace(limits[0], limits[1], 1000)
            yi = self(xi)[dependent]
            ax.plot(xi, yi, c="k")
            ax.set_ylabel(dependent)
            plt.xticks(self.setpoints[:])
            plt.setp(ax.get_xticklabels(), visible=False)
        # get appropriate source setpoints
        source_setpoint_arrs = {}
        for curve_index, curve in enumerate(all_curves):
            current_curve = self
            current_arr = self.setpoints[:]
            for _ in range(len(all_curves) - curve_index - 1):
                current_arr = current_curve.get_source_setpoint(current_arr)
                current_curve = current_curve.subcurve
            source_setpoint_arrs[current_curve.name] = np.array(current_arr).flatten()
        # add labels
        for curve in all_curves:
            ax = plt.subplot(lowest_ax_dictionary[curve.name])
            plt.setp(ax.get_xticklabels(), visible=True)
            ax.set_xlabel(curve.name + " setpoint ({})".format(self.setpoints.units))
            if curve.interaction is not None:
                ax.set_xlabel(curve.interaction + " setpoint ({})".format(self.setpoints.units))
            xtick_positions = self.setpoints[:]
            xtick_labels = [str(np.around(x, 1)) for x in source_setpoint_arrs[curve.name]]
            plt.xticks(xtick_positions, xtick_labels, rotation=45)
        # formatting details
        xmin = self.setpoints[:].min() - np.abs(self.setpoints[0] - self.setpoints[1])
        xmax = self.setpoints[:].max() + np.abs(self.setpoints[0] - self.setpoints[1])
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
            save_path = pathlib.Path(save_path)
            image_path = save_path.with_suffix(".png")
            plt.savefig(image_path, transparent=True, dpi=300)
            plt.close(fig)

    def rename_dependent(self, old_name, new_name):
        try:
            dep = self.dependents[old_name]
        except KeyError:
            raise ValueError(f"Dependent '{old_name}' not found")
        dep.name = new_name
        delattr(self, old_name)
        setattr(self, new_name, dep)
        self.dependents = {k if k != old_name else new_name: v for k, v in self.dependents.items()}
        self.interpolate()

    @classmethod
    def read(cls, filepath, subcurve=None):
        filepath = pathlib.Path(filepath)
        headers = tidy_headers.read(filepath)
        arr = np.genfromtxt(filepath).T
        names = headers["name"]
        units = headers.get("units", [None] * len(names))
        differential = headers.get("differential", [False] * len(names))
        dependents = []
        for a, n, u, d in zip(arr[1:], names[1:], units[1:], differential[1:]):
            dependents.append(Dependent(a, n, units=u, differential=d))
        kwargs = {}
        kwargs["interaction"] = headers.get("interaction", None)
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
        setpoints = Setpoints(arr[0], setpoint_name, units[0])
        if subcurve is not None:
            kwargs["subcurve"] = subcurve
            kwargs["source_setpoints"] = Dependent(setpoints[:], setpoint_name, units=units[0])
        # finish
        curve = cls(setpoints, dependents, **kwargs)
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
        out_arr[0] = self.setpoints[:]
        out_arr[1:] = np.array([dependent.positions for dependent in self.dependents.values()])
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
        headers["units"] = [self.setpoints.units] + [d.units for d in self.dependents.values()]
        headers["differential"] = [None] + [d.differential for d in self.dependents.values()]
        headers["name"] = [f"{self.setpoints.name}"] + [d.name for d in self.dependents.values()]
        tidy_headers.write(out_path, headers)
        with open(out_path, "at") as f:
            np.savetxt(f, out_arr.T, fmt=self.fmt, delimiter="\t")
        # save subcurve
        if full and self.subcurve:
            self.subcurve.save(save_directory=save_directory, full=True, verbose=verbose)
        # plot
        if plot:
            image_path = out_path.with_suffix(".png")
            title = out_path.stem
            self.plot(autosave=True, save_path=image_path, title=title)
        # finish
        if verbose:
            print("curve saved at", out_path)
        return out_path
