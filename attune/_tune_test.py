"""Methods for processing OPA 800 tuning data."""


import numpy as np

import WrightTools as wt

from ._instrument import Instrument
from ._transition import Transition
from ._plot import plot_tune_test
from ._common import save
from ._map import map_ind_points

__all__ = ["tune_test"]


def _offsets(data, channel_name, tune_points, *, spline=True, **spline_kwargs):
    data.moment(axis=1, channel=channel_name, moment=1, resultant=data.axes[0].shape)
    offsets = data[f"{channel_name}_1_moment_1"].points

    if spline:
        return wt.kit.Spline(data.axes[0].points, offsets, **spline_kwargs)
    if np.allclose(data.axes[0].points, tune_points):
        return offsets.clip(data.axes[1].min(), data.axes[1].max())
    if np.allclose(data.axes[0].points, tune_points[::-1]):
        return offsets.clip(data.axes[1].min(), data.axes[1].max())[::-1]
    else:
        raise ValueError("Data points and instrument points do not match, and splining disabled")


def tune_test(
    *,
    data,
    channel,
    arrangement,
    instrument,
    level=False,
    gtol=0.01,
    ltol=0.1,
    restore_setpoints=True,
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
    arrangement: str
        name of the arrangment to modify
    instrument: attune.Instrument
        instrument object to modify
    level: bool, optional
        toggle leveling data (Defalts to False)
    gtol: float, optional
        global tolerance for rejecting noise level relative to global maximum
    ltol: float, optional
        local tolerance for rejecting data relative to slice maximum
    restore_setpoints: bool, optional
        toggles remapping onto original setpoints for each tune (default is True)
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
        "level": level,
        "gtol": gtol,
        "ltol": ltol,
        "spline_kwargs": spline_kwargs,
    }
    if not isinstance(channel, (int, str)):
        metadata["channel"] = channel.natural_name
    transition = Transition("tune_test", instrument, metadata=metadata, data=data)

    data = data.copy()
    data.convert("nm")

    setpoints = data.axes[0].points
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

    offset_spline = _offsets(data, channel.natural_name, setpoints, **spline_kwargs)
    try:
        raw_offsets = _offsets(data, channel.natural_name, setpoints, spline=False)
    except ValueError:
        raw_offsets = None

    old_instrument = instrument.as_dict()
    for tune in old_instrument["arrangements"][arrangement]["tunes"].values():
        print(tune)
        tune["independent"] += offset_spline(tune["independent"])
    new_instrument = Instrument(**old_instrument)

    if restore_setpoints:
        for tune in new_instrument[arrangement].keys():
            new_instrument = map_ind_points(
                new_instrument, arrangement, tune, instrument[arrangement][tune].independent
            )

    new_instrument._transition = transition

    fig, _ = plot_tune_test(
        data,
        channel.natural_name,
        used_offsets=offset_spline(setpoints),
        raw_offsets=raw_offsets,
    )

    if autosave:
        save(new_instrument, fig, "tune_test", save_directory)
    return new_instrument
