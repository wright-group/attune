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


__all__ = ["Curve", "Motor"]



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


class Linear(Interpolator):
    """Linear interpolation."""

    @property
    def functions(self):
        if self._functions is not None:
            return self._functions
        self._functions = [
            wt.kit.Spline(self.colors, motor.positions, k=1, s=0) for motor in self.motors
        ]
        return self._functions


class Poly:
    """Polynomial interpolation."""

    def __init__(self, *args, **kwargs):
        self.deg = kwargs.pop("deg", 8)
        super(self, Interpolator).__init__(*args, **kwargs)

    @property
    def functions(self):
        if self._functions is not None:
            return self._functions
        self._functions = [
            np.polynomial.Polynomial.fit(self.colors, motor.positions, self.deg)
            for motor in self.motors
        ]
        return self._functions


class Spline:
    """Spline interpolation."""

    @property
    def functions(self):
        if self._functions is not None:
            return self._functions
        self._functions = [
            scipy.interpolate.UnivariateSpline(colors, motor.positions, k=3, s=1000)
            for motor in motors
        ]
        return self._functions


methods = {"Linear": Linear, "Spline": Spline, "Poly": Poly}

# --- curve class ---------------------------------------------------------------------------------


class Motor:
    """Container class for motor arrays."""

    def __init__(self, positions, name):
        """Create a ``Motor`` object.

        Parameters
        ----------
        positions : 1D array
            Motor positions.
        name : string
            Name.
        """
        self.positions = positions
        self.name = name

    def __getitem__(self, key):
        return self.positions[key]


class Curve:
    """Central object-type for all OPA tuning curves."""

    def __init__(
        self,
        colors,
        units,
        motors,
        name,
        interaction,
        kind,
        method=Linear,
        subcurve=None,
        source_colors=None,
        fmt=None,
    ):
        """Create a ``Curve`` object.

        Parameters
        ----------
        colors : array
            The color destinations for the curve.
        units : str
            The color units.
        motors : list of Motor objects
            Motor positions for each color.
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
        self.colors = np.array(colors)  # needs to be array for some interpolation methods
        self.units = units
        self.motors = motors
        self.name = name
        self.kind = kind
        self.subcurve = subcurve
        self.source_colors = source_colors
        self.interaction = interaction
        # set motors as attributes of self
        self.motor_names = [m.name for m in self.motors]
        for obj in self.motors:
            setattr(self, obj.name, obj)
        # initialize function object
        self.method = method
        if fmt is None:
            fmt = ["%.2f"] + ["%.5f"] * len(self.motors)
        self.fmt = fmt
        self.interpolate()

    def __repr__(self):
        # when you inspect the object
        outs = []
        outs.append("WrightTools.tuning.curve.Curve object at " + str(id(self)))
        outs.append("  name: " + self.name)
        outs.append("  interaction: " + self.interaction)
        outs.append(
            "  range: {0} - {1} ({2})".format(self.colors.min(), self.colors.max(), self.units)
        )
        outs.append("  number: " + str(len(self.colors)))
        return "\n".join(outs)

    def __getitem__(self, key):
        return self.motors[wt.kit.get_index(self.motor_names, key)]

    def __call__(self, value, units=None, full=True):
        return self.get_motor_positions(value, units, full=full)

    def coerce_motors(self):
        """Coerce the motor positions to lie exactly along the interpolation positions.

        Can be thought of as 'smoothing' the curve.
        """
        self.map_colors(self.colors, units="same")

    def convert(self, units):
        """Convert the colors to new units.

        Parameters
        ----------
        units : str
            The destination units.
        """
        self.colors = wt.units.converter(self.colors, self.units, units)
        if self.subcurve:
            positions = self.source_colors.positions
            self.source_colors.positions = wt.units.converter(positions, self.units, units)
        self.units = units
        self.interpolate()  # how did it ever work if this wasn't here?  - Blaise 2017-03-22

    def copy(self):
        """Copy the curve object.

        Returns
        -------
        curve
            A deep copy of the curve object.
        """
        return copy.deepcopy(self)

    def get_color(self, motor_positions, units="same"):
        """Get the color given a set of motor positions.

        Parameters
        ----------
        motor_positions : array
            The motor positions.
        units : str (optional)
            The units of the returned color.

        Returns
        -------
        float
            The current color.
        """
        colors = []
        for motor_index, motor_position in enumerate(motor_positions):
            color = self.interpolator.get_color(motor_index, motor_position)
            colors.append(color)
        # TODO: decide how to handle case of disagreement between colors
        return colors[0]

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
            return [self.colors.min(), self.colors.max()]
        else:
            units_colors = wt.units.converter(self.colors, self.units, units)
            return [units_colors.min(), units_colors.max()]

    def get_motor_names(self, full=True):
        """Get motor names.

        Parameters
        ----------
        full : boolean (optional)
            Toggle inclusion of motor names from subcurve.

        Returns
        -------
        list of strings
            Motor names.
        """
        if self.subcurve and full:
            subcurve_motor_names = self.subcurve.get_motor_names()
        else:
            subcurve_motor_names = []
        return subcurve_motor_names + [m.name for m in self.motors]

    def get_motor_positions(self, color, units="same", full=True):
        """Get the motor positions for a destination color.

        Parameters
        ----------
        color : number
            The destination color. May be 1D array.
        units : str (optional)
            The units of the input color.

        Returns
        -------
        np.ndarray
            The motor positions. If color is an array the output shape will
            be (motors, colors).
        """
        # get color in units
        if units == "same":
            pass
        else:
            color = wt.units.converter(color, units, self.units)
        # color must be array

        def is_numeric(obj):
            attrs = ["__add__", "__sub__", "__mul__", "__pow__"]
            return all([hasattr(obj, attr) for attr in attrs] + [not hasattr(obj, "__len__")])

        if is_numeric(color):
            color = np.array([color])
        # evaluate
        if full and self.subcurve:
            out = []
            for c in color:
                source_color = np.array(self.source_color_interpolator.get_motor_positions(c))
                source_motor_positions = np.array(
                    self.subcurve.get_motor_positions(source_color, units=self.units, full=True)
                ).squeeze()
                own_motor_positions = np.array(self.interpolator.get_motor_positions(c)).flatten()
                out.append(np.hstack((source_motor_positions, own_motor_positions)))
            out = np.array(out)
            return out.squeeze().T
        else:
            out = np.array([self.interpolator.get_motor_positions(c) for c in color])
            return out.T

    def get_source_color(self, color, units="same"):
        """Get color of source curve.

        Parameters
        ----------
        color : number or 1D array
            Color(s).
        units : string (optional)
            Units. Default is same.

        Returns
        -------
        number or 1D array
            Source color(s).
        """
        if not self.subcurve:
            return None
        # color must be array

        def is_numeric(obj):
            attrs = ["__add__", "__sub__", "__mul__", "__div__", "__pow__"]
            return all([hasattr(obj, attr) for attr in attrs] + [not hasattr(obj, "__len__")])

        if is_numeric(color):
            color = np.array([color])
        # get color in units
        if units == "same":
            pass
        else:
            color = wt.units.converter(color, units, self.units)
        # evaluate
        return np.array([self.source_color_interpolator.get_motor_positions(c) for c in color])

    def interpolate(self, interpolate_subcurve=True):
        """Generate the interploator object.

        Parameters
        ----------
        interpolate_subcurve : boolean (optional)
            Toggle interpolation of subcurve. Default is True.
        """
        self.interpolator = self.method(self.colors, self.units, self.motors)
        if self.subcurve and interpolate_subcurve:
            self.source_color_interpolator = self.method(
                self.colors, self.units, [self.source_colors]
            )

    def map_colors(self, colors, units="same"):
        """Map the curve onto new tune points using the curve's own interpolation method.

        Parameters
        ----------
        colors : int or array
            The number of new points (between current limits) or the new points
            themselves.
        units : str (optional.)
            The input units if given as array. Default is same. Units of curve
            object are not changed by map_colors.
        """
        # get new colors in input units
        if isinstance(colors, int):
            limits = self.get_limits(units)
            new_colors = np.linspace(limits[0], limits[1], colors)
        else:
            new_colors = colors
        # convert new colors to local units
        if units == "same":
            units = self.units
        new_colors = np.sort(wt.units.converter(new_colors, units, self.units))
        # ensure that motor interpolators agree with current motor positions
        self.interpolate(interpolate_subcurve=True)
        # map own motors
        new_motors = []
        for motor_index, motor in enumerate(self.motors):
            positions = self.get_motor_positions(new_colors, full=False)[motor_index]
            new_motor = Motor(positions, motor.name)  # new motor objects
            new_motors.append(new_motor)
        # map source colors, subcurves
        if self.subcurve:
            new_source_colors = np.array(
                self.source_color_interpolator.get_motor_positions(new_colors)
            ).squeeze()
            self.subcurve.map_colors(new_source_colors, units=self.units)
            self.source_colors.positions = new_source_colors
        # finish
        self.colors = new_colors
        self.motors = new_motors
        self.motor_names = [m.name for m in self.motors]
        for obj in self.motors:
            setattr(self, obj.name, obj)
        self.interpolate(interpolate_subcurve=True)

    def offset_by(self, motor, amount):
        """Offset a motor by some ammount.

        Parameters
        ----------
        motor : number or str
            The motor index or name.
        amount : number
            The offset.

        See Also
        --------
        offset_to
        """
        # get motor index
        motor_index = wt.kit.get_index(self.motor_names, motor)

        # offset
        self.motors[motor_index].positions += amount
        self.interpolate()

    def offset_to(self, motor, destination, color, color_units="same"):
        """Offset a motor such that it evaluates to `destination` at `color`.

        Parameters
        ----------
        motor : number or str
            The motor index or name.
        amount : number
            The motor position at color after offseting.
        color : number
            The color at-which to set the motor to amount.
        color_units : str (optional)
            The color units. Default is same.

        See Also
        --------
        offset_by
        """
        # get motor index
        if type(motor) in [float, int]:
            motor_index = motor
        elif isinstance(motor, str):
            motor_index = self.motor_names.index(motor)
        else:
            print("motor type not recognized in curve.offset_to")
        # get offset
        current_positions = self.get_motor_positions(color, color_units, full=False)
        offset = destination - current_positions[motor_index]
        # apply using offset_by
        self.offset_by(motor, offset)

    def plot(self, autosave=False, save_path="", title=None):
        """Plot the curve."""
        # count number of subcurves
        subcurve_count = 0
        total_motor_count = len(self.motors)
        current_curve = self
        all_curves = [self]
        while current_curve.subcurve:
            subcurve_count += 1
            total_motor_count += len(current_curve.subcurve.motors)
            current_curve = current_curve.subcurve
            all_curves.append(current_curve)
        all_curves = all_curves[::-1]
        # prepare figure
        num_subplots = total_motor_count + subcurve_count
        fig = plt.figure(figsize=(8, 2 * num_subplots))
        axs = grd.GridSpec(num_subplots, 1, hspace=0)
        # assign subplot indicies
        ax_index = 0
        ax_dictionary = {}
        lowest_ax_dictionary = {}
        for curve_index, curve in enumerate(all_curves):
            for motor_index, motor in enumerate(curve.motors):
                ax_dictionary[motor.name] = axs[ax_index]
                lowest_ax_dictionary[curve.interaction] = axs[ax_index]
                ax_index += 1
            if curve_index != len(all_curves):
                ax_index += 1
        # add scatter
        for motor_index, motor_name in enumerate(self.get_motor_names()):
            ax = plt.subplot(ax_dictionary[motor_name])
            xi = self.colors
            yi = self.get_motor_positions(xi)[motor_index]
            ax.scatter(xi, yi, c="k")
            ax.set_ylabel(motor_name)
            plt.xticks(self.colors)
            plt.setp(ax.get_xticklabels(), visible=False)
        # add lines
        for motor_index, motor_name in enumerate(self.get_motor_names()):
            ax = plt.subplot(ax_dictionary[motor_name])
            limits = curve.get_limits()
            xi = np.linspace(limits[0], limits[1], 1000)
            yi = self.get_motor_positions(xi)[motor_index].flatten()
            ax.plot(xi, yi, c="k")
        # get appropriate source colors
        source_color_arrs = {}
        for curve_index, curve in enumerate(all_curves):
            current_curve = self
            current_arr = self.colors
            for _ in range(len(all_curves) - curve_index - 1):
                current_arr = current_curve.get_source_color(current_arr)
                current_curve = current_curve.subcurve
            source_color_arrs[current_curve.interaction] = np.array(current_arr).flatten()
        # add labels
        for curve in all_curves:
            ax = plt.subplot(lowest_ax_dictionary[curve.interaction])
            plt.setp(ax.get_xticklabels(), visible=True)
            ax.set_xlabel(curve.interaction + " color ({})".format(curve.units))
            xtick_positions = self.colors
            xtick_labels = [str(np.around(x, 1)) for x in source_color_arrs[curve.interaction]]
            plt.xticks(xtick_positions, xtick_labels, rotation=45)
        # formatting details
        xmin = self.colors.min() - np.abs(self.colors[0] - self.colors[1])
        xmax = self.colors.max() + np.abs(self.colors[0] - self.colors[1])
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
        colors = arr[0]
        names = headers["name"]
        motors = []
        for a, n in zip(arr[1:], names[1:]):
            motors.append(Motor(a,n))
        kwargs = {}
        kwargs["interaction"] = headers["interaction"]
        kwargs["kind"] = headers.get("kind", None)
        kwargs["method"] = methods.get(headers.get("method", ""), Linear)
        kwargs["name"] = headers.get("curve name", filepath.stem)
        kwargs["fmt"] = headers.get("fmt", ["%.2f"] + ["%.5f"]*len(motors))
        units = re.match(r".*\((.*)\).*", names[0])[1]
        if subcurve is not None:
            kwargs["subcurve"] = subcurve
            kwargs["source_colors"] = Motor(colors, units)
        # finish
        curve = cls(colors, units, motors, **kwargs)
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
        out_arr = np.zeros([len(self.motors) + 1, len(self.colors)])
        out_arr[0] = self.colors
        out_arr[1:] = np.array([motor.positions for motor in self.motors])
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
        headers["name"] = [f"Color ({self.units})"] + [m.name for m in self.motors]
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
