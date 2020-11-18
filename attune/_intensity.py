"""Workup an instrument maximizing intensity of a single setable"""

import numpy as np
import WrightTools as wt

from ._instrument import Instrument
from ._arrangement import Arrangement
from ._setable import Setable
from ._tune import Tune
from ._transition import Transition
from ._plot import plot_intensity
from ._common import save


# --- processing methods --------------------------------------------------------------------------

__all__ = ["intensity"]


def _intensity(data, channel_name, tune_points, *, spline=True, **spline_kwargs):
    data.moment(axis=1, channel=channel_name, moment=1, resultant=data.axes[0].shape)
    offsets = data[f"{channel_name}_1_moment_1"].points

    if spline:
        spline = wt.kit.Spline(data.axes[0].points, offsets, **spline_kwargs)
        return spline(tune_points).clip(data.axes[1].min(), data.axes[1].max())
    if np.allclose(data.axes[0].points, tune_points):
        return offsets.clip(data.axes[1].min(), data.axes[1].max())
    elif np.allclose(data.axes[0].points, tune_points[::-1]):
        return offsets.clip(data.axes[1].min(), data.axes[1].max())[::-1]
    else:
        raise ValueError("Data points and instrument points do not match, and splining disabled")


def intensity(
    *,
    data,
    channel,
    arrangement,
    tune,
    instrument=None,
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
    arrangement: str
        name of the arrangement to modify in the instrument
    tune: str
        name of the tune to modify in the instrument
    instrument: attune.Instrument, optional
        instrument object to modify (Default None: make a new instrument)
    level: bool, optional
        toggle leveling data (Defalts to False)
    gtol: float, optional
        global tolerance for rejecting noise level relative to global maximum
    ltol: float, optional
        local tolerance for rejecting data relative to slice maximum
    autosave: bool, optional
        toggles saving of instrument file and images (Defaults to True)
    save_directory: Path-like
        where to save (Defaults to current working directory)
    **spline_kwargs: optional
        extra arguments to pass to spline creation (e.g. s=0, k=1 for linear interpolation)

    Returns
    -------
    attune.Instrument
        New instrument object.
    """
    metadata = {
        "channel": channel,
        "arrangement": arrangement,
        "tune": tune,
        "level": level,
        "gtol": gtol,
        "ltol": ltol,
        "spline_kwargs": spline_kwargs,
    }
    if not isinstance(channel, (int, str)):
        metadata["channel"] = channel.natural_name
    transition = Transition("intensity", instrument, metadata=metadata, data=data)
    data = data.copy()
    data.convert("nm")
    if instrument is not None:
        old_instrument = instrument.as_dict()
        setpoints = instrument[arrangement][tune].independent
    else:
        old_instrument = None
        setpoints = data.axes[0].points
    # TODO: units
    setpoints.sort()

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

    offsets = _intensity(data, channel.natural_name, setpoints, **spline_kwargs)
    print(setpoints)
    print(offsets)
    try:
        raw_offsets = _intensity(data, channel.natural_name, setpoints, spline=False)
    except ValueError:
        raw_offsets = None

    units = data.axes[1].units
    if units == "None":
        units = None

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

    fig, _ = plot_intensity(
        data, channel.natural_name, arrangement, tune, new_instrument, instrument, raw_offsets
    )

    if autosave:
        save(new_instrument, fig, "intensity", save_directory)
    return new_instrument
