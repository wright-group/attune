"""Methods for processing OPA 800 tuning data."""

import pathlib

import numpy as np
import WrightTools as wt

from .. import Curve, Dependent, Setpoints
from ._plot import plot_intensity


# --- processing methods --------------------------------------------------------------------------

__all__ = ["setpoint"]


def _setpoint(data, channel_name, tune_points, *, spline=True, **spline_kwargs):
    data[channel_name] -= tune_points
    offsets = []
    chops = data.chop(1)
    for c in chops:
        xi = data.axes[0].points
        yi = data[channel_name].points
        xi, yi = wt.kit.remove_nans_1D(xi, yi)
        if yi.min() <= 0 <= yi.max():
            p = np.polynomial.Polynomial.fit(yi, xi, 2)
            offsets.append(p(0))
        else:
            offsets.append(np.nan)

    offsets = np.array(offsets)
    if spline:
        spline = wt.kit.Spline(tune_points, offsets, **spline_kwargs)
        return spline(tune_points)
    if np.allclose(data.axes[0].points, tune_points):
        return offsets
    else:
        raise ValueError("Data points and curve points do not match, and splining disabled")


def setpoint(
    data,
    channel,
    dependent,
    curve=None,
    *,
    autosave=True,
    save_directory=None,
):
    """Workup a generic intensity plot for a single dependent.

    Parameters
    ----------
    data : wt.data.Data object
        should be in (setpoint, dependent)

    Returns
    -------
    curve
        New curve object.
    """
    data = data.copy()
    data.convert("wn")
    if curve is not None:
        old_curve = curve.copy()
        old_curve.convert("wn")
        setpoints = old_curve.setpoints
    else:
        old_curve = None   
        setpoints = Setpoints(data.axes[0].points, data.axes[0].expression, data.axes[0].units)
    # TODO: units

    if isinstance(channel, (int, str)):
        channel = data.channels[wt.kit.get_index(data.channel_names, channel)]

    offsets = _setpoint(data, channel.natural_name, setpoints[:])

    units = data.axes[1].units
    if units == "None":
        units = None

    new_curve = Curve(
        setpoints, [Dependent(offsets, dependent, units, differential=True)], name="setpoint"
    )

    if curve is not None:
        curve = old_curve + new_curve
    else:
        curve = new_curve

    # Why did we have to map setpoints?
    curve.map_setpoints(setpoints[:])

    fig, _ = plot_setpoint(data, channel.natural_name, dependent, curve, old_curve)

    if autosave:
        if save_directory is None:
            # TODO: Formal decision on whether this should be cwd or data/curve location
            save_directory = "."
        save_directory = pathlib.Path(save_directory)
        curve.save(save_directory=save_directory, full=True)
        # Should we timestamp the image?
        p = save_directory / "setpoint.png"
        wt.artists.savefig(p, fig=fig)
    return curve
