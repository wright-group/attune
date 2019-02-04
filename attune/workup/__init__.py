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


def _intensity(data, channel_name, tune_points, *, spline=True, **spline_kwargs):
    data.moment(axis=1, channel=channel_name, moment=1)
    offsets = data[f"{channel.natural_name}_1_moment_1"].points

    if spline:
        spline = wt.kit.Spline(tune_points, offsets, **spline_kwargs)
        return spline(tune_points)
    if np.allclose(data.axes[0].points, tune_points):
        return offsets
    else:
        raise ValueError("Data points and curve points do not match, and splining disabled")


def intensity(
    data, curve, channel, *, level=False, cutoff_factor=0.1, autosave=True, save_directory=None
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
    old_curve = curve.copy()
    old_curve.convert("wn")
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

    offsets = _intensity(data, channel.natural_name, tune_points)

    motors = []
    for motor_index, motor_name in enumerate([m.name for m in old_curve.motors]):
        if motor_name in motor_axis_name.split("_"):
            positions = old_curve.motors[motor_index].positions + offsets
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

    fig, _ = _plot.plot_intensity(
        data, channel, curve.motor_names[tuned_motor_index], curve, old_curve
    )

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
    data, curve, channel_name, level=False, cutoff_factor=0.01, autosave=True, save_directory=None
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
    curve = curve.copy()
    curve_native_units = curve.units
    curve.convert("wn")
    data = data.copy()
    data.bring_to_front(channel_name)
    data.transform(*data.axis_names[::-1])
    data.convert("wn")
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
    points = curve.colors.copy()
    offsets_splined = spline(points)  # wn
    # make curve ----------------------------------------------------------------------------------
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
