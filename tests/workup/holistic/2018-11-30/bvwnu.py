import matplotlib

matplotlib.use("TkAgg")

import tempfile
import attune
import WrightTools as wt
import numpy as np
import pathlib

import pytest

__here__ = pathlib.Path(__file__).parent


@pytest.mark.xfail
def test_single_channel():
    # collect
    d = wt.open(__here__ / "data.wt5")

    curve_paths = [__here__ / "old" / "OPA1 (10743) base - 2018-10-26 40490.crv"]
    old = attune.TopasCurve.read(curve_paths, interaction_string="NON-NON-NON-Sig")

    curve_paths = [__here__ / "out" / "OPA- 2019-09-18 53345.crv"]
    reference = attune.TopasCurve.read(curve_paths, interaction_string="NON-NON-NON-Sig")

    # do calculation
    d.transform("w1_Crystal_1", "w1_Delay_1", "wa")
    new = attune.workup.holistic(
        d,
        "array_signal",
        ["0", "1"],
        old,
        gtol=0.05,
        level=True,
        autosave=False,
        save_directory=__here__ / "out",
    )

    # check
    np.testing.assert_allclose(old.setpoints[:], new.setpoints[:])
    for r, n in zip(reference.dependents.values(), new.dependents.values()):
        print(r[:].dtype, n[:].dtype)
        np.testing.assert_allclose(r[:], n[:], rtol=0.01)

    d.close()


@pytest.mark.xfail
def test_multiple_channels():
    # collect
    d = wt.open(__here__ / "data.wt5")
    channel = "array_signal"
    d.level(channel, 0, -3)
    # take channel moments
    d.moment(axis=-1, channel=channel, resultant=wt.kit.joint_shape(*d.axes[:-1]), moment=0)
    d.moment(axis=-1, channel=channel, resultant=wt.kit.joint_shape(*d.axes[:-1]), moment=1)
    amplitudes = d.channel_names[-2]
    centers = -1

    curve_paths = [__here__ / "old" / "OPA1 (10743) base - 2018-10-26 40490.crv"]
    old = attune.TopasCurve.read(curve_paths, interaction_string="NON-NON-NON-Sig")

    curve_paths = [__here__ / "out" / "OPA- 2019-09-18 53345.crv"]
    reference = attune.TopasCurve.read(curve_paths, interaction_string="NON-NON-NON-Sig")

    # do calculation
    d.transform("w1_Crystal_1", "w1_Delay_1")
    new = attune.workup.holistic(
        d,
        (amplitudes, centers),
        ["0", "1"],
        old,
        gtol=0.05,
        level=True,
        autosave=False,
        save_directory=__here__ / "out",
    )

    # check
    np.testing.assert_allclose(old.setpoints[:], new.setpoints[:])
    for r, n in zip(reference.dependents.values(), new.dependents.values()):
        print(r[:].dtype, n[:].dtype)
        np.testing.assert_allclose(r[:], n[:], rtol=0.01)

    d.close()
