"""Workup an instrument such that the output is the expected color"""

import numpy as np
import WrightTools as wt

from ._instrument import Instrument
from ._arrangement import Arrangement
from ._setable import Setable
from ._tune import Tune
from ._transition import Transition
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
    elif np.allclose(data.axes[0].points, tune_points[::-1]):
        return offsets[::-1].clip(data.axes[1].min(), data.axes[1].max())[::-1]
    else:
        raise ValueError("Data points and instrument points do not match, and splining disabled")


def setpoint(
    *,
    data,
    channel,
    arrangement,
    tune,
    instrument=None,
    autosave=True,
    save_directory=None,
    **spline_kwargs
):
    """Workup a generic setpoint plot for a single tune.

    Parameters
    ----------
    data : wt.data.Data object
        should be in (setpoint, tune)
    channel: wt.data.Channel or int or str
        channel to process
    arrangement: str
        name of the arrangement to modify
    tune: str
        name of the tune to modify in the instrument
    instrument: attune.Curve, optional
        instrument object to modify (Default None: make a new instrument)
    autosave: bool, optional
        toggles saving of instrument file and images (Defaults to True)
    save_directory: Path-like
        where to save (Defaults to current working directory)
    **spline_kwargs: optional
        extra arguments to pass to spline creation (e.g. s=0, k=1 for linear interpolation)

    Returns
    -------
    attune.Curve
        New instrument object.
    """
    metadata = {
        "channel": channel,
        "arrangement": arrangement,
        "tune": tune,
        "spline_kwargs": spline_kwargs,
    }
    if not isinstance(channel, (int, str)):
        metadata["channel"] = channel.natural_name
    transition = Transition("setpoint", instrument, metadata=metadata, data=data)
    data = data.copy()
    data.convert("nm")
    if instrument is not None:
        old_instrument = instrument.as_dict()
        setpoints = instrument[arrangement][tune].independent
    else:
        setpoints = data.axes[0].points
    # TODO: units
    setpoints.sort()

    if isinstance(channel, (int, str)):
        channel = data.channels[wt.kit.get_index(data.channel_names, channel)]

    dims = [1] * data.ndim
    dims[0] = setpoints.size  # TODO: be more robust, don't assume 0 index
    channel -= setpoints.reshape(dims)

    offsets = _setpoint(data, channel.natural_name, setpoints, **spline_kwargs)
    try:
        raw_offsets = _setpoint(data, channel.natural_name, setpoints, spline=False)
    except ValueError:
        raw_offsets = None

    if instrument is not None:
        old_instrument["arrangements"][arrangement]["tunes"][tune]["independent"] = setpoints
        old_instrument["arrangements"][arrangement]["tunes"][tune]["dependent"] += offsets
        try:
            del old_instrument["transition"]
        except KeyError:
            pass
        new_instrument = Instrument(**old_instrument, transition=transition)
    else:
        arr = Arrangement(arrangement, {tune: Tune(setpoints, offsets)})
        new_instrument = Instrument(
            {arrangement: arr}, {tune: Setable(tune)}, transition=transition
        )

    fig, _ = plot_setpoint(
        data, channel.natural_name, arrangement, tune, new_instrument, instrument, raw_offsets
    )

    if autosave:
        save(new_instrument, fig, "setpoint", save_directory)
    return new_instrument
