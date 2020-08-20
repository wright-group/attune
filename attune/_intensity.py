"""Methods for processing OPA 800 tuning data."""

import numpy as np
import WrightTools as wt

from .. import Curve, Dependent, Setpoints
from ._plot import plot_intensity
from ._common import save


# --- processing methods --------------------------------------------------------------------------

__all__ = ["intensity"]


def _intensity(data, channel_name, tune_points, *, spline=True, **spline_kwargs):
    data.moment(axis=1, channel=channel_name, moment=1, resultant=data.axes[0].shape)
    offsets = data[f"{channel_name}_1_moment_1"].points

    if spline:
        spline = wt.kit.Spline(tune_points, offsets, **spline_kwargs)
        return spline(tune_points).clip(data.axes[1].min(), data.axes[1].max())
    if np.allclose(data.axes[0].points, tune_points):
        return offsets.clip(data.axes[1].min(), data.axes[1].max())
    else:
        raise ValueError("Data points and curve points do not match, and splining disabled")


def intensity(
    data,
    channel,
    dependent,
    curve=None,
    *,
    level=False,
    gtol=0.01,
    ltol=0.1,
    autosave=True,
    save_directory=None,
    **spline_kwargs,
):
    """Workup a generic intensity plot for a single dependent.

    Parameters
    ----------
    data : wt.data.Data
        should be in (setpoint, dependent)
    channel: wt.data.Channel or int or str
        channel to process
    dependent: str
        name of the dependent to modify in the curve
    curve: attune.Curve, optional
        curve object to modify (Default None: make a new curve)
    level: bool, optional
        toggle leveling data (Defalts to False)
    gtol: float, optional
        global tolerance for rejecting noise level relative to global maximum
    ltol: float, optional
        local tolerance for rejecting data relative to slice maximum
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
        orig_channel = data.create_channel(
            f"{channel.natural_name}_orig", channel, units=channel.units
        )

    # TODO: check if level does what we want
    if level:
        data.level(channel.natural_name, 0, -3)

    # TODO: gtol/ltol should maybe be moved to wt
    cutoff = channel.max() * gtol
    channel.clip(min=cutoff)
    max_axis = tuple(i for i, v in enumerate(data.axes[0].shape) if v > 1)
    cutoff = np.nanmax(channel[:], axis=1, keepdims=True) * ltol
    channel.clip(min=cutoff)

    offsets = _intensity(data, channel.natural_name, setpoints[:], **spline_kwargs)
    try:
        raw_offsets = _intensity(data, channel.natural_name, setpoints[:], spline=False)
    except ValueError:
        raw_offsets = None

    units = data.axes[1].units
    if units == "None":
        units = None

    new_curve = Curve(
        setpoints, [Dependent(offsets, dependent, units, differential=True)], name="intensity",
    )

    if curve is not None:
        curve = old_curve + new_curve
    else:
        curve = new_curve

    # Why did we have to map setpoints?
    curve.map_setpoints(setpoints[:])

    fig, _ = plot_intensity(data, channel.natural_name, dependent, curve, old_curve, raw_offsets)

    if autosave:
        save(curve, fig, "intensity", save_directory)
    return curve
