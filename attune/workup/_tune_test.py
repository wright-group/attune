"""Methods for processing OPA 800 tuning data."""


import numpy as np

import WrightTools as wt

from ._plot import plot_tune_test
from ._common import save

__all__ = ["tune_test"]


def _offsets(data, channel_name, tune_points, *, spline=True, **spline_kwargs):
    data.moment(axis=1, channel=channel_name, moment=1, resultant=data.axes[0].shape)
    offsets = data[f"{channel_name}_1_moment_1"].points

    if spline:
        spline = wt.kit.Spline(data.axes[0].points, offsets, **spline_kwargs)
        return spline(tune_points).clip(data.axes[1].min(), data.axes[1].max())
    if np.allclose(data.axes[0].points, tune_points):
        return offsets.clip(data.axes[1].min(), data.axes[1].max())
    else:
        raise ValueError("Data points and curve points do not match, and splining disabled")


def tune_test(
    data,
    channel,
    curve=None,
    *,
    level=False,
    gtol=0.01,
    ltol=0.1,
    autosave=True,
    save_directory=None,
    **spline_kwargs,
):
    """Workup a Tune Test.

    Parameters
    ----------
    data : wt.data.Data
        should be in (setpoint, dependent)
    channel: wt.data.Channel or int or str
        channel to process
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
    # make data object
    if curve is not None:
        old_curve = curve.copy()
        old_curve.convert("wn")
        setpoints = old_curve.setpoints
    else:
        old_curve = None
        setpoints = Setpoints(data.axes[0].points, data.axes[0].expression, data.axes[0].units)

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

    offsets = _offsets(data, channel.natural_name, setpoints[:], **spline_kwargs)
    try:
        raw_offsets = _offsets(data, channel.natural_name, data.axes[0].points, spline=False)
    except ValueError:
        raw_offsets = None

    # make curve ----------------------------------------------------------------------------------
    new_curve = old_curve.copy()
    new_curve.setpoints.positions += offsets
    new_curve.interpolate()
    new_curve.map_setpoints(setpoints[:], units=setpoints.units)
    new_curve.convert(curve.setpoints.units)
    data.axes[0].convert(curve.setpoints.units)

    # plot ----------------------------------------------------------------------------------------

    fig, _ = plot_tune_test(
        data, channel.natural_name, new_curve, used_offsets=offsets, raw_offsets=raw_offsets,
    )

    # finish --------------------------------------------------------------------------------------
    if autosave:
        save(new_curve, fig, "tune_test", save_directory)
    return new_curve
