import tempfile
import attune
import WrightTools as wt
import numpy as np
import pathlib

import pytest

__here__ = pathlib.Path(__file__).parent


def test_single_channel():
    # collect
    d = wt.open(__here__ / "data.wt5")
    old = attune.open(__here__ / "old.json")
    reference = attune.open(__here__ / "new.json")
    # do
    d.transform("w1_Crystal_1", "w1_Delay_1", "wa")
    new = attune.holistic(
        data=d,
        channels="array_signal",
        arrangement="NON-NON-NON-Sig",
        tunes=["c1", "d1"],
        instrument=old,
        gtol=0.05,
        level=True,
        autosave=False,
        save_directory=__here__ / "out",
    )
    d.close()
    # check
    assert reference == new


def test_multiple_channels():
    # collect
    d = wt.open(__here__ / "data.wt5")
    old = attune.open(__here__ / "old.json")
    reference = attune.open(__here__ / "new.json")

    channel = "array_signal"
    d.level(channel, 0, -3)
    # take channel moments
    d.moment(axis=-1, channel=channel, resultant=wt.kit.joint_shape(*d.axes[:-1]), moment=0)
    d.moment(axis=-1, channel=channel, resultant=wt.kit.joint_shape(*d.axes[:-1]), moment=1)
    amplitudes = d.channel_names[-2]
    centers = -1

    # do calculation
    d.transform("w1_Crystal_1", "w1_Delay_1")
    new = attune.holistic(
        data=d,
        channels=(amplitudes, centers),
        arrangement="NON-NON-NON-Sig",
        tunes=["c1", "d1"],
        instrument=old,
        gtol=0.05,
        level=True,
        autosave=False,
        save_directory=__here__ / "out",
    )

    # check
    assert reference == new

    d.close()


if __name__ == "__main__":
    test_single_channel()
    # test_multiple_channels()
