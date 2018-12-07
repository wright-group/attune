"""Methods for processing OPA 800 tuning data."""


# --- import --------------------------------------------------------------------------------------


from __future__ import absolute_import, division, print_function, unicode_literals

import os

import matplotlib.pyplot as plt

import numpy as np

import WrightTools as wt
from .. import curve as attune_curve

# from . import fit


# --- define --------------------------------------------------------------------------------------


cmap = wt.artists.colormaps["default"]
cmap.set_bad([0.75] * 3, 1.)
cmap.set_under([0.75] * 3)

# --- processing methods --------------------------------------------------------------------------


def intensity(
    data,
    curve,
    channel,
    *,
    level=False,
    cutoff_factor=0.1,
    autosave=True,
    save_directory=None,
):
    """Workup a generic intensity plot for a single motor.

    Parameters
    ----------
    data : wt.data.Data objeect
        should be in (setpoint, motor)

    Returns
    -------
    curve
        New curve object.
    """
    # TODO: documentation

    data = data.copy()
    # TODO: transform?
    if isinstance(channel, (int, str)):
        channel = data.channels[wt.kit.get_index(data.channel_names, channel)]
    channel_index = wt.kit.get_index(data.channels, channel)
    tune_points = curve.colors

    # TODO: check if level does what we want
    if level:
        data.level(channel.natural_name, 0, -3)
    cutoff = channel.max() * cutoff_factor
    channel.clip(min=cutoff)

    # TODO: not sure this is what we want
    motor_axis_name = data.axes[1].natural_name

    data.moment(axis=1, channel=channel.natural_name, moment=1)
    offsets = data[f"{channel.natural_name}_1_moment_1"].points

    # Should just work
    spline = wt.kit.Spline(tune_points, offsets)
    offsets_splined = spline(tune_points)
    old_curve = curve.copy()
    old_curve.convert("wn")
    motors = []
    for motor_index, motor_name in enumerate([m.name for m in old_curve.motors]):
        if motor_name in motor_axis_name.split("_"):
            positions = old_curve.motors[motor_index].positions + offsets_splined
            motor = attune_curve.Motor(positions, motor_name)
            motors.append(motor)
            tuned_motor_index = motor_index
        else:
            motors.append(old_curve.motors[motor_index])

    kind = old_curve.kind
    interaction = old_curve.interaction
    curve = attune_curve.Curve(
        tune_points,
        "wn",
        motors,
        name=old_curve.name.split("-")[0],
        kind=kind,
        interaction=interaction,
    )

    # Why did we have to map colors?
    curve.map_colors(old_curve.colors)

    # TODO: This is a common setup among tuning methods, should extract to a method
    def _plot():
        fig, gs = wt.artists.create_figure(
            nrows=2, default_aspect=0.5, cols=[1, "cbar"]
        )
        ax = plt.subplot(gs[0, 0])
        xi = old_curve.colors
        yi = old_curve.motors[tuned_motor_index].positions
        ax.plot(xi, yi, c="k", lw=1)
        xi = curve.colors
        yi = curve.motors[tuned_motor_index].positions
        ax.plot(xi, yi, c="k", lw=5, alpha=0.5)
        ax.grid()
        ax.set_xlim(tune_points.min(), tune_points.max())
        ax.set_ylabel(curve.motor_names[tuned_motor_index], fontsize=18)
        plt.setp(ax.get_xticklabels(), visible=False)

        ax = plt.subplot(gs[1, 0])
        ax.pcolor(data, channel=channel.natural_name, cmap=cmap)
        ax.grid()
        ax.axhline(c="k", lw=1)
        xi = curve.colors
        yi = offsets
        ax.plot(xi, yi, c="grey", lw=5, alpha=0.5)
        xi = curve.colors
        yi = offsets_splined
        ax.plot(xi, yi, c="k", lw=5, alpha=0.5)

        # units_string = r"$\mathsf{\left(" + wt.units.color_symbols[curve.units] + r"\right)}$"
        # ax.set_xlabel(" ".join(["setpoint", units_string]), fontsize=18)
        # ax.set_ylabel(
        #    " ".join(["$\mathsf{\Delta}$", curve.motor_names[tuned_motor_index]]), fontsize=18
        # )
        cax = plt.subplot(gs[1, -1])
        label = channel.natural_name
        ticks = np.linspace(0, channel.max(), 7)
        wt.artists.plot_colorbar(cax=cax, cmap=cmap, label=label, ticks=ticks)
        return fig

    fig = _plot()

    if autosave:
        if save_directory is None:
            # TODO: Formal decision on whether this should be cwd or data/curve location
            save_directory = os.getcwd()
        curve.save(save_directory=save_directory, full=True)
        # Should we timestamp the image?
        p = os.path.join(save_directory, "intensity.png")
        wt.artists.savefig(p, fig=fig)
    return curve


def tune_test(
    data,
    curve,
    channel_name,
    level=False,
    cutoff_factor=0.01,
    autosave=True,
    save_directory=None,
):
    """Workup a Tune Test.

    Parameters
    ----------
    data : wt.data.Data object
        should be in (setpoint, detuning)
    curve : attune_curve object
        tuning curve used to do tune_test
    channel_nam : str
        name of the signal chanel to evalute
    level : bool (optional)
        does nothing, default is False
    cutoff_factor : float (optoinal)
        minimum value for datapoint/max(datapoints) for point to be included
        in the fitting procedure, default is 0.01
    autosave : bool (optional)
        saves output curve if True, default is True
    save_directory : str
        directory to save new curve, default is None which uses the data source
        directory

    Returns
    -------
    curve
        New curve object.
    """
    # make data object
    data = data.copy()
    data.bring_to_front(channel_name)
    data.transform(*data.axis_names[::-1])
    # process data --------------------------------------------------------------------------------
    # cutoff
    channel_index = data.channel_names.index(channel_name)
    channel = data.channels[channel_index]
    cutoff = channel.max() * cutoff_factor
    channel[channel < cutoff] = np.nan
    # fit
    data.moment(axis=0, channel=channel_name, moment=1)
    outs = data.channels[-1]
    # spline
    xi = data.axes[1].points
    yi = outs.points
    print(xi.shape, yi.shape)
    spline = wt.kit.Spline(xi, yi)
    offsets_splined = spline(xi)  # wn
    # make curve ----------------------------------------------------------------------------------
    curve = curve.copy()
    curve_native_units = curve.units
    curve.convert("wn")
    points = curve.colors.copy()
    curve.colors += offsets_splined
    curve.map_colors(points, units="wn")
    curve.convert(curve_native_units)
    # plot ----------------------------------------------------------------------------------------
    data.axes[1].convert(curve_native_units)
    fig, gs = wt.artists.create_figure(default_aspect=0.5, cols=[1, "cbar"])
    fig, gs = wt.artists.create_figure(default_aspect=0.5, cols=[1, "cbar"])
    # heatmap
    ax = plt.subplot(gs[0, 0])
    xi = data.axes[1].points
    yi = data.axes[0].points
    zi = data.channels[channel_index][:]
    X, Y, Z = wt.artists.pcolor_helper(xi, yi, zi)
    ax.pcolor(X, Y, Z, vmin=0, vmax=np.nanmax(zi), cmap=cmap)
    ax.set_xlim(xi.min(), xi.max())
    ax.set_ylim(yi.min(), yi.max())
    # lines
    print(outs.units, outs.natural_name)
    # outs.convert(curve_native_units)
    xi = data.axes[1].points
    yi = outs.points
    ax.plot(xi, yi, c="grey", lw=5, alpha=0.5)
    ax.plot(xi, offsets_splined, c="k", lw=5, alpha=0.5)
    ax.axhline(c="k", lw=1)
    ax.grid()
    # units_string = "$\mathsf{(" + wt.units.color_symbols[curve.units] + ")}$"
    # ax.set_xlabel(r" ".join(["setpoint", units_string]), fontsize=18)
    # ax.set_ylabel(r"$\mathsf{\Delta" + wt.units.color_symbols["wn"] + "}$", fontsize=18)
    # colorbar
    cax = plt.subplot(gs[:, -1])
    label = channel_name
    ticks = np.linspace(0, np.nanmax(zi), 7)
    wt.artists.plot_colorbar(cax=cax, cmap=cmap, label=label, ticks=ticks)
    # finish --------------------------------------------------------------------------------------
    if autosave:
        if save_directory is None:
            save_directory = os.path.dirname(data.source)
        curve.save(save_directory=save_directory, full=True)
        p = os.path.join(save_directory, "tune test.png")
        wt.artists.savefig(p, fig=fig)
    return curve
