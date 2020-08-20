"""Methods for processing OPA 800 tuning data."""

import numpy as np
import WrightTools as wt

from .. import Curve, Dependent, Setpoints
from ._plot import plot_setpoint
from ._common import save


# --- processing methods --------------------------------------------------------------------------

__all__ = ["setpoint"]


def _setpoint(data, channel_name, tune_points, *, spline=True, **spline_kwargs):
    offsets = []
    chops = data.chop(1)
    for c in chops.values():
        xi = c.axes[0].points
        yi = c[channel_name].points
        xi, yi = wt.kit.remove_nans_1D(xi, yi)
        if np.all(np.isnan(yi)):
            offsets.append(np.nan)
        elif np.nanmin(yi) <= 0 <= np.nanmax(yi):
            p = np.polynomial.Polynomial.fit(yi, xi, 2)
            offsets.append(p(0))
        else:
            offsets.append(np.nan)

    offsets = np.array(offsets)
    if spline:
        spline = wt.kit.Spline(data.axes[0].points, offsets, **spline_kwargs)
        return spline(tune_points).clip(data.axes[1].min(), data.axes[1].max())
    if np.allclose(data.axes[0].points, tune_points):
        return offsets[::-1].clip(data.axes[1].min(), data.axes[1].max())
    else:
        raise ValueError("Data points and curve points do not match, and splining disabled")


def setpoint(
    data, channel, dependent, curve=None, *, autosave=True, save_directory=None, **spline_kwargs
):
    """Workup a generic setpoint plot for a single dependent.

    Parameters
    ----------
    data : wt.data.Data object
        should be in (setpoint, dependent)
    channel: wt.data.Channel or int or str
        channel to process
    dependent: str
        name of the dependent to modify in the curve
    curve: attune.Curve, optional
        curve object to modify (Default None: make a new curve)
    autosave: bool, optional
        toggles saving of curve file and images (Defaults to True)
    save_directory: Path-like
        where to save (Defaults to current working directory)
    **spline_kwargs: optional
        extra arguments to pass to spline creation (e.g. s=0, k=1 for linear interpolation)

    Returns
    -------
    attune.Curve
        New curve object.
    """
    data = data.copy()
    # data.convert("wn")
    if curve is not None:
        old_curve = curve.copy()
        # old_curve.convert("wn")
        setpoints = old_curve.setpoints
    else:
        old_curve = None
        setpoints = Setpoints(data.axes[0].points, data.axes[0].expression, data.axes[0].units)
    # TODO: units

    if isinstance(channel, (int, str)):
        channel = data.channels[wt.kit.get_index(data.channel_names, channel)]

    dims = [1] * data.ndim
    dims[0] = setpoints[:].size  # TODO: be more robust, don't assume 0 index
    channel -= setpoints[:].reshape(dims)

    offsets = _setpoint(data, channel.natural_name, setpoints[:], **spline_kwargs)
    try:
        raw_offsets = _setpoint(data, channel.natural_name, setpoints[:], spline=False)
    except ValueError:
        raw_offsets = None

    units = data.axes[1].units
    if units == "None":
        units = None

    new_curve = Curve(
        setpoints, [Dependent(offsets, dependent, units, differential=True)], name="setpoint",
    )

    if curve is not None:
        curve = old_curve + new_curve
    else:
        curve = new_curve

    # Why did we have to map setpoints?
    curve.map_setpoints(setpoints[:])

    fig, _ = plot_setpoint(data, channel.natural_name, dependent, curve, old_curve, raw_offsets)

    if autosave:
        save(curve, fig, "setpoint", save_directory)
    return curve
